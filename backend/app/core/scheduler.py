"""
In-process scheduler for recurring jobs.
"""
import asyncio
from datetime import date, datetime, time as dt_time, timedelta
from typing import List, Optional, Tuple

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.facebook_ads_sync_service import FacebookAdsDataSyncService
from app.services.google_ads_sync_service import GoogleAdsDataSyncService


def _compute_date_range(days: int, include_today: bool) -> Tuple[str, str]:
    if days < 1:
        raise ValueError("DAILY_SYNC_DAYS must be >= 1")
    today = date.today()
    end = today if include_today else today - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def _next_midnight(now: datetime) -> datetime:
    next_day = now.date() + timedelta(days=1)
    return datetime.combine(next_day, dt_time.min)


def _run_google_ads_sync(start_date: str, end_date: str) -> None:
    customer_id = (settings.GOOGLE_ADS_CUSTOMER_ID or "").replace("-", "")
    if not customer_id:
        print("❌ [scheduler] Missing GOOGLE_ADS_CUSTOMER_ID; skipping Google Ads sync.")
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
        print(f"✅ [scheduler] Google Ads sync success: {result.get('message')}")
    else:
        print(f"❌ [scheduler] Google Ads sync failed: {result.get('message')}")
        for err in result.get("errors", []):
            print(f"   - {err}")


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


def _run_facebook_ads_sync(start_date: str, end_date: str) -> None:
    access_token = settings.FACEBOOK_ACCESS_TOKEN or ""
    if not access_token:
        print("❌ [scheduler] Missing FACEBOOK_ACCESS_TOKEN; skipping Facebook Ads sync.")
        return

    account_ids = _normalize_facebook_accounts(
        settings.FACEBOOK_DAILY_SYNC_ACCOUNT_IDS,
        settings.FACEBOOK_AD_ACCOUNT_ID,
    )
    if not account_ids:
        print("❌ [scheduler] Missing Facebook ad account ID(s); skipping Facebook Ads sync.")
        return

    proxy_url: Optional[str] = settings.FACEBOOK_PROXY_URL_EFFECTIVE or None
    db = SessionLocal()
    try:
        service = FacebookAdsDataSyncService(db, performance_profile=settings.FACEBOOK_DAILY_SYNC_PROFILE)
        for ad_account_id in account_ids:
            api_account_id, db_account_id = _normalize_facebook_account_id(ad_account_id)
            print(f"🚀 [scheduler] Facebook Ads sync {api_account_id}: {start_date} -> {end_date}")
            result = service.sync_ads(
                access_token=access_token,
                ad_account_id=api_account_id,
                start_date=start_date,
                end_date=end_date,
                account_id_for_db=db_account_id,
                proxy_url=proxy_url,
            )
            if result.get("success"):
                print(f"✅ [scheduler] Facebook Ads sync success: {result.get('message')}")
            else:
                print(f"❌ [scheduler] Facebook Ads sync failed: {result.get('message')}")
                for err in result.get("errors", []):
                    print(f"   - {err}")
    finally:
        db.close()


async def _google_ads_daily_sync_loop() -> None:
    while True:
        now = datetime.now()
        next_run = _next_midnight(now)
        sleep_secs = (next_run - now).total_seconds()
        if sleep_secs > 0:
            print(f"🕛 [scheduler] Next Google Ads sync at {next_run:%Y-%m-%d %H:%M:%S}")
            try:
                await asyncio.sleep(sleep_secs)
            except asyncio.CancelledError:
                return

        try:
            start_date, end_date = _compute_date_range(
                settings.GOOGLE_ADS_DAILY_SYNC_DAYS,
                settings.GOOGLE_ADS_DAILY_SYNC_INCLUDE_TODAY,
            )
        except Exception as exc:
            print(f"❌ [scheduler] Invalid sync range: {exc}")
            await asyncio.sleep(60)
            continue

        print(f"🚀 [scheduler] Google Ads sync: {start_date} -> {end_date}")
        try:
            await asyncio.to_thread(_run_google_ads_sync, start_date, end_date)
        except asyncio.CancelledError:
            return
        except Exception as exc:
            print(f"❌ [scheduler] Google Ads sync exception: {exc}")
            await asyncio.sleep(60)


async def _facebook_ads_daily_sync_loop() -> None:
    while True:
        now = datetime.now()
        next_run = _next_midnight(now)
        sleep_secs = (next_run - now).total_seconds()
        if sleep_secs > 0:
            print(f"🕛 [scheduler] Next Facebook Ads sync at {next_run:%Y-%m-%d %H:%M:%S}")
            try:
                await asyncio.sleep(sleep_secs)
            except asyncio.CancelledError:
                return

        try:
            start_date, end_date = _compute_date_range(
                settings.FACEBOOK_DAILY_SYNC_DAYS,
                settings.FACEBOOK_DAILY_SYNC_INCLUDE_TODAY,
            )
        except Exception as exc:
            print(f"❌ [scheduler] Invalid Facebook sync range: {exc}")
            await asyncio.sleep(60)
            continue

        try:
            await asyncio.to_thread(_run_facebook_ads_sync, start_date, end_date)
        except asyncio.CancelledError:
            return
        except Exception as exc:
            print(f"❌ [scheduler] Facebook Ads sync exception: {exc}")
            await asyncio.sleep(60)


def start_google_ads_daily_sync_task() -> asyncio.Task:
    return asyncio.create_task(_google_ads_daily_sync_loop())


def start_facebook_ads_daily_sync_task() -> asyncio.Task:
    return asyncio.create_task(_facebook_ads_daily_sync_loop())
