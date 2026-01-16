"""
Google Ads Dashboard API路由
"""
import logging
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.core.cache import invalidate_cache
from app.services.google_service import GoogleDashboardService
from app.services.google_ads_sync_service import GoogleAdsDataSyncService
from app.schemas.dashboard import (
    PerformanceComparisonRequest,
    CampaignPerformanceRequest,
    AdsPerformanceOverviewRequest
)
from app.utils.api_helpers import api_success, api_error, handle_error, api_endpoint, handle_ai_analysis


logger = logging.getLogger(__name__)
router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> GoogleDashboardService:
    """获取Google服务实例"""
    return GoogleDashboardService(db)


@router.get("/impressions")
@api_endpoint(error_message="获取印象数据失败")
async def get_impressions(
    startDate: str = Query(..., description="开始日期 YYYY-MM-DD"),
    endDate: str = Query(..., description="结束日期 YYYY-MM-DD"),
    compareStartDate: Optional[str] = Query(None, description="对比开始日期"),
    compareEndDate: Optional[str] = Query(None, description="对比结束日期"),
    service: GoogleDashboardService = Depends(get_service)
):
    """获取Google Ads印象和点击数据"""
    return await service.get_impressions_data(startDate, endDate, compareStartDate, compareEndDate)


@router.get("/conversions")
@api_endpoint(error_message="获取转化数据失败")
async def get_conversions(
    startDate: str = Query(..., description="开始日期 YYYY-MM-DD"),
    endDate: str = Query(..., description="结束日期 YYYY-MM-DD"),
    compareStartDate: Optional[str] = Query(None, description="对比开始日期"),
    compareEndDate: Optional[str] = Query(None, description="对比结束日期"),
    service: GoogleDashboardService = Depends(get_service)
):
    """获取Google Ads转化和成本数据"""
    return await service.get_purchases_data(startDate, endDate, compareStartDate, compareEndDate)


@router.post("/refresh")
@api_endpoint(error_message="刷新数据失败", success_message="数据刷新成功")
async def refresh_data(service: GoogleDashboardService = Depends(get_service)):
    """刷新Google Ads数据"""
    return await service.refresh_all_data()


@router.post("/performance-comparison")
@api_endpoint(error_message="获取性能对比数据失败")
async def get_performance_comparison(
    request: PerformanceComparisonRequest,
    service: GoogleDashboardService = Depends(get_service)
):
    """获取Google Ads性能对比数据"""
    return await service.get_performance_comparison(
        request.startDate1, request.endDate1, request.startDate2, request.endDate2
    )


@router.post("/campaign-performance-overview")
@api_endpoint(error_message="获取Campaign数据失败")
async def get_campaign_performance_overview(
    request: CampaignPerformanceRequest,
    service: GoogleDashboardService = Depends(get_service)
):
    """获取Campaign Performance Overview数据"""
    return await service.get_campaign_performance_overview(
        request.startDate1, request.endDate1, request.startDate2, request.endDate2
    )


@router.post("/ads-performance-overview")
@api_endpoint(error_message="获取广告数据失败")
async def get_ads_performance_overview(
    request: AdsPerformanceOverviewRequest,
    service: GoogleDashboardService = Depends(get_service)
):
    """获取Ads Performance Overview数据"""
    return await service.get_ads_performance_overview(request.date)


@router.get("/overview-summary")
async def get_overview_summary(
    startDate: str = Query(..., description="开始日期 YYYY-MM-DD"),
    endDate: str = Query(..., description="结束日期 YYYY-MM-DD"),
    compareStartDate: Optional[str] = Query(None, description="对比开始日期 YYYY-MM-DD"),
    compareEndDate: Optional[str] = Query(None, description="对比结束日期 YYYY-MM-DD"),
    customer_id: Optional[str] = Query(None, description="Google Ads 客户ID"),
    proxy_url: Optional[str] = Query(None, description="代理URL"),
    db: Session = Depends(get_db)
):
    """
    获取 Google Ads 概览汇总数据（包含对比数据）
    用于 Top Funnel Overview 和 Conversion Value & Cost Overview
    直接从API获取汇总数据，支持对比日期范围
    """
    try:
        # 使用配置中的默认值
        final_customer_id = customer_id or settings.GOOGLE_ADS_CUSTOMER_ID
        final_proxy_url = proxy_url or settings.GOOGLE_ADS_PROXY_URL_EFFECTIVE
        
        if not final_customer_id:
            return api_error("缺少Google Ads客户ID，请在环境变量中配置GOOGLE_ADS_CUSTOMER_ID或在请求中提供", code=400)
        
        sync_service = GoogleAdsDataSyncService(db)
        
        # 设置代理
        if final_proxy_url:
            sync_service.setup_proxy(final_proxy_url)
        
        # 初始化客户端
        if not sync_service.initialize_client():
            return api_error("初始化 Google Ads 客户端失败", code=500)
        
        # 获取概览汇总数据
        success, summary_data, error_msg = sync_service.fetch_overview_summary(
            customer_id=final_customer_id.replace("-", ""),
            start_date=startDate,
            end_date=endDate,
            compare_start_date=compareStartDate,
            compare_end_date=compareEndDate
        )
        
        if success:
            return api_success({
                "summary": summary_data,
                "date_range": {
                    "start_date": startDate,
                    "end_date": endDate,
                    "compare_start_date": compareStartDate,
                    "compare_end_date": compareEndDate
                }
            }, "成功获取概览汇总数据")
        else:
            return api_error(error_msg, code=500)
            
    except Exception as e:
        handle_error(e, "获取概览汇总数据失败")


@router.post("/sync-data")
async def sync_google_ads_data(
    start_date: str = Body(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Body(..., description="结束日期 YYYY-MM-DD"),
    customer_id: Optional[str] = Body(None, description="Google Ads客户ID"),
    proxy_url: Optional[str] = Body(None, description="代理URL"),
    clear_existing: bool = Body(True, description="是否清除现有数据"),
    db: Session = Depends(get_db)
):
    """从 Google Ads API 同步数据到数据库"""
    try:
        # 使用配置中的默认值
        final_customer_id = customer_id or settings.GOOGLE_ADS_CUSTOMER_ID
        final_proxy_url = proxy_url or settings.GOOGLE_ADS_PROXY_URL_EFFECTIVE
        
        if not final_customer_id:
            return api_error("缺少Google Ads客户ID，请在环境变量中配置GOOGLE_ADS_CUSTOMER_ID或在请求中提供", code=400)
        
        sync_service = GoogleAdsDataSyncService(db)
        result = sync_service.sync_campaigns(
            customer_id=final_customer_id.replace("-", ""),
            start_date=start_date,
            end_date=end_date,
            proxy_url=final_proxy_url,
            clear_existing=clear_existing
        )
        
        if result["success"]:
            # 清除所有 Google Ads 相关缓存
            cache_patterns = [
                "google:impressions*",
                "google:purchases*",
                "google:campaigns*",  # Campaign Performance Overview
                "google:ads_performance*",  # Ads Performance Overview
                "google:performance_comparison*",
                "google:overview*"
            ]
            for pattern in cache_patterns:
                try:
                    invalidate_cache(pattern)
                    logger.info(f"已清除缓存: {pattern}")
                except Exception as cache_error:
                    logger.warning(f"清除缓存失败，pattern={pattern}，error={cache_error}")
            
            return api_success({
                "records_synced": result["records_synced"],
                "customer_id": customer_id,
                "start_date": start_date,
                "end_date": end_date
            }, result["message"])
        else:
            return api_error(
                result["message"], 
                code=500, 
                data={"records_synced": 0, "errors": result["errors"]}
            )
    except Exception as e:
        handle_error(e, "同步数据失败")


from app.api.ai_analysis import create_ai_analysis_endpoint

# AI分析端点 - 使用工厂函数创建（减少重复代码）
analyze_top_funnel_overview = create_ai_analysis_endpoint(
    "analyze_google_top_funnel",
    "AI分析失败"
)
router.post("/analyze-top-funnel", summary="分析Top Funnel数据")(analyze_top_funnel_overview)

analyze_conversion_cost_overview = create_ai_analysis_endpoint(
    "analyze_google_conversion_cost",
    "AI分析失败"
)
router.post("/analyze-conversion-cost", summary="分析转化和成本数据")(analyze_conversion_cost_overview)
