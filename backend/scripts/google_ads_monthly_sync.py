#!/usr/bin/env python
"""
Daily Google Ads sync script.

Default behavior:
- Runs a rolling window of the last 30 days.
- Ends at yesterday (safe for midnight runs).

Example:
  python backend/scripts/google_ads_monthly_sync.py --days 30
  python backend/scripts/google_ads_monthly_sync.py --end-date 2026-01-15 --days 30
  python backend/scripts/google_ads_monthly_sync.py --include-today
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Tuple


def _bootstrap_backend() -> Path:
    """Add backend to sys.path and load .env if present."""
    backend_dir = Path(__file__).resolve().parents[1]
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    env_file = backend_dir / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_file)
            print(f"🔧 Loaded env from {env_file}")
        except Exception as exc:  # pragma: no cover
            print(f"⚠️  Failed to load .env ({exc})")
    return backend_dir


def _compute_date_range(days: int, end_date: Optional[str], include_today: bool) -> Tuple[str, str]:
    if days < 1:
        raise ValueError("--days must be >= 1")

    if end_date:
        end = date.fromisoformat(end_date)
    else:
        today = date.today()
        end = today if include_today else today - timedelta(days=1)

    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Daily Google Ads sync (rolling last month)")
    parser.add_argument("--days", type=int, default=30, help="Rolling window length (default 30)")
    parser.add_argument("--end-date", help="End date YYYY-MM-DD (default: yesterday)")
    parser.add_argument(
        "--include-today",
        action="store_true",
        help="Include today as end date (default is yesterday for midnight runs)",
    )
    parser.add_argument("--customer-id", help="Google Ads customer ID (dashes optional)")
    parser.add_argument("--proxy-url", help="Override proxy URL")
    parser.add_argument("--no-proxy", action="store_true", help="Do not set proxy even if configured")
    parser.add_argument("--max-workers", type=int, default=8, help="Workers for concurrent fetch")
    parser.add_argument("--serial", action="store_true", help="Use serial fetch instead of concurrent")
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Do not clear existing rows in the date range before insert",
    )
    return parser.parse_args()


def main() -> int:
    _bootstrap_backend()
    args = parse_args()

    from app.core.config import settings
    from app.core.database import SessionLocal
    from app.services.google_ads_sync_service import GoogleAdsDataSyncService

    customer_id = (args.customer_id or settings.GOOGLE_ADS_CUSTOMER_ID or "").replace("-", "")
    if not customer_id:
        print("❌ Missing customer_id. Set --customer-id or GOOGLE_ADS_CUSTOMER_ID in backend/.env")
        return 1

    try:
        start_date, end_date = _compute_date_range(
            args.days, args.end_date, args.include_today
        )
    except ValueError as exc:
        print(f"❌ {exc}")
        return 1

    proxy_url = None if args.no_proxy else (args.proxy_url or settings.GOOGLE_ADS_PROXY_URL_EFFECTIVE)

    print(f"\nDate range: {start_date} -> {end_date}")
    print(f"Mode: {'serial' if args.serial else 'concurrent'} (workers={args.max_workers})")
    print(f"Customer ID: {customer_id}")
    print(f"Proxy: {'disabled' if args.no_proxy else (proxy_url or 'none')}")
    print(f"Clear existing rows: {not args.keep_existing}\n")

    db = SessionLocal()
    try:
        service = GoogleAdsDataSyncService(db)
        result = service.sync_campaigns(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            proxy_url=proxy_url,
            clear_existing=not args.keep_existing,
            use_concurrent=not args.serial,
            max_workers=args.max_workers,
        )
    finally:
        db.close()

    if result.get("success"):
        print(f"✅ Sync complete: {result.get('message')}")
        return 0

    print(f"❌ Sync failed: {result.get('message')}")
    if result.get("errors"):
        for err in result["errors"]:
            print(f"   - {err}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
