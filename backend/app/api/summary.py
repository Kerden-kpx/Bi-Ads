"""
Summary Dashboard API路由 - 批量获取汇总数据
"""
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Optional, List
import asyncio

from app.core.database import get_db
from app.services.facebook_service import FacebookDashboardService
from app.services.google_ads_sync_service import GoogleAdsDataSyncService
from app.core.config import settings
from app.utils.api_helpers import api_success, api_error
from app.core.cache import cached

router = APIRouter()


@cached(prefix="summary:facebook_multi_account", ttl=settings.CACHE_TTL_SHORT)
async def _get_facebook_multi_account_summary(
    account_ids: List[str],
    this_week_start: str,
    this_week_end: str,
    last_week_start: str,
    last_week_end: str,
    db: Session
):
    """
    批量获取多个Facebook账户的两周汇总数据
    
    返回格式:
    {
        "account1": {"this_week": {...}, "last_week": {...}},
        "account2": {"this_week": {...}, "last_week": {...}}
    }
    """
    service = FacebookDashboardService(db)
    results = {}
    
    # 为每个账户并行获取本周和上周数据
    tasks = []
    task_keys = []
    
    for account_id in account_ids:
        # 本周任务
        task_keys.append((account_id, 'this_week'))
        tasks.append(
            service.get_overview_data_from_api(
                start_date=this_week_start,
                end_date=this_week_end,
                access_token=None,
                account_id=account_id
            )
        )
        
        # 上周任务
        task_keys.append((account_id, 'last_week'))
        tasks.append(
            service.get_overview_data_from_api(
                start_date=last_week_start,
                end_date=last_week_end,
                access_token=None,
                account_id=account_id
            )
        )
    
    # 并行执行所有请求
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 组织结果
    for i, (account_id, week_type) in enumerate(task_keys):
        if account_id not in results:
            results[account_id] = {}
        
        response = responses[i]
        if isinstance(response, Exception):
            results[account_id][week_type] = {"error": str(response)}
        else:
            # 提取purchases数据
            results[account_id][week_type] = response.get('purchases', {}) if isinstance(response, dict) else {}
    
    return results


@router.post("/facebook-multi-account")
async def get_facebook_multi_account_summary(
    account_ids: List[str] = Body(..., description="Facebook账户ID列表"),
    this_week_start: str = Body(..., description="本周开始日期"),
    this_week_end: str = Body(..., description="本周结束日期"),
    last_week_start: str = Body(..., description="上周开始日期"),
    last_week_end: str = Body(..., description="上周结束日期"),
    db: Session = Depends(get_db)
):
    """
    批量获取多个Facebook账户的两周汇总数据
    
    一次请求替代 N*2 次请求（N个账户 × 2周）
    
    示例请求:
    ```json
    {
        "account_ids": ["2613027225660900", "1069516980635624"],
        "this_week_start": "2025-01-20",
        "this_week_end": "2025-01-26",
        "last_week_start": "2025-01-13",
        "last_week_end": "2025-01-19"
    }
    ```
    """
    try:
        results = await _get_facebook_multi_account_summary(
            account_ids=account_ids,
            this_week_start=this_week_start,
            this_week_end=this_week_end,
            last_week_start=last_week_start,
            last_week_end=last_week_end,
            db=db
        )
        
        return api_success(results, "成功获取Facebook多账户汇总数据")
    except Exception as e:
        return api_error(f"获取Facebook汇总数据失败: {str(e)}", code=500)


@cached(prefix="summary:google_two_weeks", ttl=settings.CACHE_TTL_SHORT)
async def _get_google_two_weeks_summary(
    this_week_start: str,
    this_week_end: str,
    last_week_start: str,
    last_week_end: str,
    customer_id: str,
    proxy_url: Optional[str],
    db: Session
):
    """
    批量获取Google Ads的两周汇总数据
    
    返回格式:
    {
        "this_week": {...},
        "last_week": {...}
    }
    """
    sync_service = GoogleAdsDataSyncService(db)
    
    # 设置代理
    if proxy_url:
        sync_service.setup_proxy(proxy_url)
    
    # 初始化客户端
    if not sync_service.initialize_client():
        raise Exception("初始化 Google Ads 客户端失败")
    
    # 并行获取本周和上周数据
    tasks = [
        asyncio.to_thread(
            sync_service.fetch_overview_summary,
            customer_id=customer_id.replace("-", ""),
            start_date=this_week_start,
            end_date=this_week_end
        ),
        asyncio.to_thread(
            sync_service.fetch_overview_summary,
            customer_id=customer_id.replace("-", ""),
            start_date=last_week_start,
            end_date=last_week_end
        )
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    this_week_result = results[0]
    last_week_result = results[1]
    
    response = {}
    
    if isinstance(this_week_result, tuple) and this_week_result[0]:
        response['this_week'] = this_week_result[1]
    else:
        response['this_week'] = {"error": str(this_week_result) if isinstance(this_week_result, Exception) else "获取失败"}
    
    if isinstance(last_week_result, tuple) and last_week_result[0]:
        response['last_week'] = last_week_result[1]
    else:
        response['last_week'] = {"error": str(last_week_result) if isinstance(last_week_result, Exception) else "获取失败"}
    
    return response


@router.post("/google-two-weeks")
async def get_google_two_weeks_summary(
    this_week_start: str = Body(..., description="本周开始日期"),
    this_week_end: str = Body(..., description="本周结束日期"),
    last_week_start: str = Body(..., description="上周开始日期"),
    last_week_end: str = Body(..., description="上周结束日期"),
    customer_id: Optional[str] = Body(None, description="Google Ads客户ID"),
    proxy_url: Optional[str] = Body(None, description="代理URL"),
    db: Session = Depends(get_db)
):
    """
    批量获取Google Ads的两周汇总数据
    
    一次请求替代 2 次请求（本周+上周）
    
    示例请求:
    ```json
    {
        "this_week_start": "2025-01-20",
        "this_week_end": "2025-01-26",
        "last_week_start": "2025-01-13",
        "last_week_end": "2025-01-19"
    }
    ```
    """
    try:
        # 使用配置中的默认值
        final_customer_id = customer_id or settings.GOOGLE_ADS_CUSTOMER_ID
        final_proxy_url = proxy_url or settings.GOOGLE_ADS_PROXY_URL_EFFECTIVE
        
        if not final_customer_id:
            return api_error("缺少Google Ads客户ID", code=400)
        
        results = await _get_google_two_weeks_summary(
            this_week_start=this_week_start,
            this_week_end=this_week_end,
            last_week_start=last_week_start,
            last_week_end=last_week_end,
            customer_id=final_customer_id,
            proxy_url=final_proxy_url,
            db=db
        )
        
        return api_success(results, "成功获取Google两周汇总数据")
    except Exception as e:
        return api_error(f"获取Google汇总数据失败: {str(e)}", code=500)


@router.post("/all-summary")
async def get_all_summary_data(
    account_ids: List[str] = Body(..., description="Facebook账户ID列表"),
    this_week_start: str = Body(..., description="本周开始日期"),
    this_week_end: str = Body(..., description="本周结束日期"),
    last_week_start: str = Body(..., description="上周开始日期"),
    last_week_end: str = Body(..., description="上周结束日期"),
    customer_id: Optional[str] = Body(None, description="Google Ads客户ID"),
    proxy_url: Optional[str] = Body(None, description="代理URL"),
    db: Session = Depends(get_db)
):
    """
    一次性获取所有Summary数据（Facebook + Google）
    
    将 6+ 次请求合并为 1 次！
    """
    try:
        # 并行获取Facebook和Google数据
        facebook_task = _get_facebook_multi_account_summary(
            account_ids=account_ids,
            this_week_start=this_week_start,
            this_week_end=this_week_end,
            last_week_start=last_week_start,
            last_week_end=last_week_end,
            db=db
        )
        
        final_customer_id = customer_id or settings.GOOGLE_ADS_CUSTOMER_ID
        final_proxy_url = proxy_url or settings.GOOGLE_ADS_PROXY_URL_EFFECTIVE
        
        google_task = _get_google_two_weeks_summary(
            this_week_start=this_week_start,
            this_week_end=this_week_end,
            last_week_start=last_week_start,
            last_week_end=last_week_end,
            customer_id=final_customer_id,
            proxy_url=final_proxy_url,
            db=db
        ) if final_customer_id else None
        
        tasks = [facebook_task]
        if google_task:
            tasks.append(google_task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        response = {
            "facebook": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "google": results[1] if len(results) > 1 and not isinstance(results[1], Exception) else {"error": "未配置或获取失败"}
        }
        
        return api_success(response, "成功获取所有汇总数据")
    except Exception as e:
        return api_error(f"获取汇总数据失败: {str(e)}", code=500)
