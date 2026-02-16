"""
In-process scheduler for recurring jobs.
"""
import asyncio
import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.services.facebook_ads_sync_service import FacebookAdsDataSyncService
from app.services.google_ads_sync_service import GoogleAdsDataSyncService
from sqlalchemy import text
from sqlalchemy.engine import Connection

logger = logging.getLogger("app.scheduler")
SCHEDULER_LOCK_NAME = "bi_ads_hourly_sync_lock"


def acquire_scheduler_lock() -> Connection | None:
    """获取调度器全局锁，确保多 worker 场景只有一个实例执行任务"""
    try:
        conn = engine.connect()
        locked = conn.execute(
            text("SELECT GET_LOCK(:name, 0)"),
            {"name": SCHEDULER_LOCK_NAME},
        ).scalar()
        if int(locked or 0) == 1:
            logger.info("scheduler lock acquired: %s", SCHEDULER_LOCK_NAME)
            return conn

        conn.close()
        logger.info("scheduler lock already held by another worker: %s", SCHEDULER_LOCK_NAME)
        return None
    except Exception:
        logger.exception("failed to acquire scheduler lock")
        return None


def release_scheduler_lock(conn: Connection | None) -> None:
    """释放调度器锁"""
    if conn is None:
        return
    try:
        conn.execute(
            text("SELECT RELEASE_LOCK(:name)"),
            {"name": SCHEDULER_LOCK_NAME},
        )
    except Exception:
        logger.exception("failed to release scheduler lock")
    finally:
        conn.close()
        logger.info("scheduler lock released: %s", SCHEDULER_LOCK_NAME)


def _compute_date_range(days: int, include_today: bool) -> Tuple[str, str]:
    if days < 1:
        raise ValueError("DAILY_SYNC_DAYS must be >= 1")
    today = date.today()
    end = today if include_today else today - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def _compute_hourly_incremental_range(days: int) -> Tuple[str, str]:
    """整点任务使用短窗口增量同步，降低每小时全量覆盖成本"""
    return _compute_date_range(days=max(1, days), include_today=True)


def _normalize_hour(hour: int) -> int:
    return max(0, min(int(hour), 23))


def _next_top_of_hour(now: datetime) -> datetime:
    hour_start = now.replace(minute=0, second=0, microsecond=0)
    return hour_start + timedelta(hours=1)


def _run_google_ads_sync(start_date: str, end_date: str, sync_mode: str = "hourly") -> None:
    customer_id = (settings.GOOGLE_ADS_CUSTOMER_ID or "").replace("-", "")
    if not customer_id:
        logger.error("missing GOOGLE_ADS_CUSTOMER_ID; skip google sync")
        return

    proxy_url: Optional[str] = settings.GOOGLE_ADS_PROXY_URL_EFFECTIVE or None
    db = SessionLocal()
    try:
        service = GoogleAdsDataSyncService(db)
        result = service.sync_campaigns(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            proxy_url=proxy_url,
            clear_existing=True,
            use_concurrent=True,
            max_workers=settings.GOOGLE_ADS_MAX_WORKERS,
        )
    finally:
        db.close()

    if result.get("success"):
        logger.info("google sync(%s) success: %s", sync_mode, result.get("message"))
    else:
        logger.error("google sync(%s) failed: %s", sync_mode, result.get("message"))
        for err in result.get("errors", []):
            logger.error("google sync error: %s", err)


def _normalize_facebook_accounts(raw_accounts: str, fallback_account: str) -> List[str]:
    accounts = []
    if raw_accounts:
        accounts = [acct.strip() for acct in raw_accounts.split(",") if acct.strip()]
    elif fallback_account:
        accounts = [fallback_account]
    return accounts


def _normalize_facebook_account_id(ad_account_id: str) -> tuple[str, str]:
    if ad_account_id.startswith("act_"):
        return ad_account_id, ad_account_id.replace("act_", "")
    return f"act_{ad_account_id}", ad_account_id


def _run_facebook_ads_sync(start_date: str, end_date: str, sync_mode: str = "hourly") -> None:
    access_token = settings.FACEBOOK_ACCESS_TOKEN or ""
    if not access_token:
        logger.error("missing FACEBOOK_ACCESS_TOKEN; skip facebook sync")
        return

    account_ids = _normalize_facebook_accounts(
        settings.FACEBOOK_DAILY_SYNC_ACCOUNT_IDS,
        settings.FACEBOOK_AD_ACCOUNT_ID,
    )
    if not account_ids:
        logger.error("missing Facebook ad account IDs; skip facebook sync")
        return

    proxy_url: Optional[str] = settings.FACEBOOK_PROXY_URL_EFFECTIVE or None
    db = SessionLocal()
    try:
        service = FacebookAdsDataSyncService(db, performance_profile=settings.FACEBOOK_DAILY_SYNC_PROFILE)
        for ad_account_id in account_ids:
            api_account_id, db_account_id = _normalize_facebook_account_id(ad_account_id)
            logger.info("facebook sync(%s) account=%s window=%s -> %s", sync_mode, api_account_id, start_date, end_date)
            result = service.sync_ads(
                access_token=access_token,
                ad_account_id=api_account_id,
                start_date=start_date,
                end_date=end_date,
                account_id_for_db=db_account_id,
                proxy_url=proxy_url,
            )
            if result.get("success"):
                logger.info("facebook sync(%s) success: %s", sync_mode, result.get("message"))
            else:
                logger.error("facebook sync(%s) failed: %s", sync_mode, result.get("message"))
                for err in result.get("errors", []):
                    logger.error("facebook sync error: %s", err)
    finally:
        db.close()


async def _google_ads_daily_sync_loop() -> None:
    while True:
        now = datetime.now()
        next_run = _next_top_of_hour(now)
        sleep_secs = (next_run - now).total_seconds()
        if sleep_secs > 0:
            logger.info("next Google sync at %s", next_run.strftime("%Y-%m-%d %H:%M:%S"))
            try:
                await asyncio.sleep(sleep_secs)
            except asyncio.CancelledError:
                return

        run_time = datetime.now()
        try:
            start_date, end_date = _compute_hourly_incremental_range(
                settings.GOOGLE_ADS_HOURLY_SYNC_DAYS,
            )
        except Exception as exc:
            logger.error("invalid google hourly sync range: %s", exc)
            await asyncio.sleep(60)
            continue

        try:
            logger.info("google hourly sync window: %s -> %s", start_date, end_date)
            await asyncio.to_thread(_run_google_ads_sync, start_date, end_date, "hourly")

            if settings.GOOGLE_ADS_BACKFILL_ENABLED and run_time.hour == _normalize_hour(settings.GOOGLE_ADS_BACKFILL_HOUR):
                backfill_start, backfill_end = _compute_date_range(
                    settings.GOOGLE_ADS_DAILY_SYNC_DAYS,
                    settings.GOOGLE_ADS_DAILY_SYNC_INCLUDE_TODAY,
                )
                if (backfill_start, backfill_end) != (start_date, end_date):
                    logger.info("google daily backfill window: %s -> %s", backfill_start, backfill_end)
                    await asyncio.to_thread(_run_google_ads_sync, backfill_start, backfill_end, "backfill")
        except asyncio.CancelledError:
            return
        except Exception as exc:
            logger.exception("google sync loop exception: %s", exc)
            await asyncio.sleep(60)


async def _facebook_ads_daily_sync_loop() -> None:
    while True:
        now = datetime.now()
        next_run = _next_top_of_hour(now)
        sleep_secs = (next_run - now).total_seconds()
        if sleep_secs > 0:
            logger.info("next Facebook sync at %s", next_run.strftime("%Y-%m-%d %H:%M:%S"))
            try:
                await asyncio.sleep(sleep_secs)
            except asyncio.CancelledError:
                return

        run_time = datetime.now()
        try:
            start_date, end_date = _compute_hourly_incremental_range(
                settings.FACEBOOK_HOURLY_SYNC_DAYS,
            )
        except Exception as exc:
            logger.error("invalid facebook hourly sync range: %s", exc)
            await asyncio.sleep(60)
            continue

        try:
            logger.info("facebook hourly sync window: %s -> %s", start_date, end_date)
            await asyncio.to_thread(_run_facebook_ads_sync, start_date, end_date, "hourly")

            if settings.FACEBOOK_BACKFILL_ENABLED and run_time.hour == _normalize_hour(settings.FACEBOOK_BACKFILL_HOUR):
                backfill_start, backfill_end = _compute_date_range(
                    settings.FACEBOOK_DAILY_SYNC_DAYS,
                    settings.FACEBOOK_DAILY_SYNC_INCLUDE_TODAY,
                )
                if (backfill_start, backfill_end) != (start_date, end_date):
                    logger.info("facebook daily backfill window: %s -> %s", backfill_start, backfill_end)
                    await asyncio.to_thread(_run_facebook_ads_sync, backfill_start, backfill_end, "backfill")
        except asyncio.CancelledError:
            return
        except Exception as exc:
            logger.exception("facebook sync loop exception: %s", exc)
            await asyncio.sleep(60)


def start_google_ads_daily_sync_task() -> asyncio.Task:
    return asyncio.create_task(_google_ads_daily_sync_loop())


def start_facebook_ads_daily_sync_task() -> asyncio.Task:
    return asyncio.create_task(_facebook_ads_daily_sync_loop())
