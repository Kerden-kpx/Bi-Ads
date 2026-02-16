"""
Facebook Dashboard API路由
"""
import logging
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.core.cache import invalidate_cache
from app.services.facebook_service import FacebookDashboardService
from app.services.facebook_ads_sync_service import FacebookAdsDataSyncService
from app.schemas.dashboard import (
    FacebookPerformanceComparisonRequest,
    FacebookAdsPerformanceOverviewRequest,
    FacebookAdsetsPerformanceOverviewRequest,
    FacebookAdsDetailPerformanceOverviewRequest
)
from app.utils.api_helpers import api_success, api_error, handle_error, api_endpoint, validate_required_config, handle_ai_analysis
from app.utils.helpers import normalize_account_id


logger = logging.getLogger(__name__)
router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> FacebookDashboardService:
    """获取Facebook服务实例"""
    return FacebookDashboardService(db)


@router.get("/impressions")
@api_endpoint(error_message="获取印象数据失败")
async def get_impressions(
    startDate: str = Query(..., description="开始日期 YYYY-MM-DD"),
    endDate: str = Query(..., description="结束日期 YYYY-MM-DD"),
    compareStartDate: Optional[str] = Query(None, description="对比开始日期"),
    compareEndDate: Optional[str] = Query(None, description="对比结束日期"),
    accountId: Optional[str] = Query(None, description="账户ID"),
    service: FacebookDashboardService = Depends(get_service)
):
    """获取Facebook印象和触达数据（从数据库）"""
    return await service.get_impressions_data(startDate, endDate, compareStartDate, compareEndDate, accountId)


@router.get("/impressions/api")
@api_endpoint(error_message="从API获取印象数据失败")
async def get_impressions_from_api(
    startDate: str = Query(..., description="开始日期 YYYY-MM-DD"),
    endDate: str = Query(..., description="结束日期 YYYY-MM-DD"),
    compareStartDate: Optional[str] = Query(None, description="对比开始日期"),
    compareEndDate: Optional[str] = Query(None, description="对比结束日期"),
    accessToken: Optional[str] = Query(None, description="Facebook访问令牌"),
    accountId: Optional[str] = Query(None, description="账户ID"),
    service: FacebookDashboardService = Depends(get_service)
):
    """获取Facebook印象和触达数据（直接从API，支持对比）"""
    return await service.get_impressions_data_from_api(startDate, endDate, compareStartDate, compareEndDate, accessToken, accountId)


@router.get("/purchases")
@api_endpoint(error_message="获取购买数据失败")
async def get_purchases(
    startDate: str = Query(..., description="开始日期 YYYY-MM-DD"),
    endDate: str = Query(..., description="结束日期 YYYY-MM-DD"),
    compareStartDate: Optional[str] = Query(None, description="对比开始日期"),
    compareEndDate: Optional[str] = Query(None, description="对比结束日期"),
    accountId: Optional[str] = Query(None, description="账户ID"),
    service: FacebookDashboardService = Depends(get_service)
):
    """获取Facebook购买和花费数据（从数据库）"""
    return await service.get_purchases_data(startDate, endDate, compareStartDate, compareEndDate, accountId)


@router.get("/purchases/api")
@api_endpoint(error_message="从API获取购买数据失败")
async def get_purchases_from_api(
    startDate: str = Query(..., description="开始日期 YYYY-MM-DD"),
    endDate: str = Query(..., description="结束日期 YYYY-MM-DD"),
    compareStartDate: Optional[str] = Query(None, description="对比开始日期"),
    compareEndDate: Optional[str] = Query(None, description="对比结束日期"),
    accessToken: Optional[str] = Query(None, description="Facebook访问令牌"),
    accountId: Optional[str] = Query(None, description="账户ID"),
    service: FacebookDashboardService = Depends(get_service)
):
    """获取Facebook购买和花费数据（直接从API，支持对比）"""
    return await service.get_purchases_data_from_api(startDate, endDate, compareStartDate, compareEndDate, accessToken, accountId)


@router.get("/overview/api")
@api_endpoint(error_message="从API获取总览数据失败")
async def get_overview_from_api(
    startDate: str = Query(..., description="开始日期 YYYY-MM-DD"),
    endDate: str = Query(..., description="结束日期 YYYY-MM-DD"),
    compareStartDate: Optional[str] = Query(None, description="对比开始日期"),
    compareEndDate: Optional[str] = Query(None, description="对比结束日期"),
    accessToken: Optional[str] = Query(None, description="Facebook访问令牌"),
    accountId: Optional[str] = Query(None, description="账户ID"),
    service: FacebookDashboardService = Depends(get_service)
):
    """获取Facebook总览数据（包含impressions和purchases，直接从API，支持对比）"""
    return await service.get_overview_data_from_api(startDate, endDate, compareStartDate, compareEndDate, accessToken, accountId)


@router.post("/performance-comparison")
@api_endpoint(error_message="获取性能对比数据失败")
async def get_performance_comparison(
    request: FacebookPerformanceComparisonRequest,
    service: FacebookDashboardService = Depends(get_service)
):
    """获取Facebook Ads性能对比数据"""
    return await service.get_performance_comparison(
        request.startDate1, request.endDate1, request.startDate2, request.endDate2, request.accountId
    )


@router.post("/ads-performance-overview")
@api_endpoint(error_message="获取广告数据失败")
async def get_ads_performance_overview(
    request: FacebookAdsPerformanceOverviewRequest,
    service: FacebookDashboardService = Depends(get_service)
):
    """获取Facebook Ads Performance Overview数据"""
    return await service.get_ads_performance_overview(request.date, request.accountId)


@router.post("/adsets-performance-overview")
@api_endpoint(error_message="获取广告组数据失败")
async def get_adsets_performance_overview(
    request: FacebookAdsetsPerformanceOverviewRequest,
    service: FacebookDashboardService = Depends(get_service)
):
    """获取Facebook Ad Sets Performance Overview数据"""
    return await service.get_adsets_performance_overview(
        request.startDate1, request.endDate1, request.startDate2, request.endDate2, request.accountId
    )


@router.post("/ads-detail-performance-overview")
@api_endpoint(error_message="获取广告详情数据失败")
async def get_ads_detail_performance_overview(
    request: FacebookAdsDetailPerformanceOverviewRequest,
    service: FacebookDashboardService = Depends(get_service)
):
    """获取Facebook Ads Detail Performance Overview数据"""
    return await service.get_ads_detail_performance_overview(
        request.startDate1, request.endDate1, request.startDate2, request.endDate2, request.accountId
    )


from app.api.ai_analysis import create_ai_analysis_endpoint

# AI分析端点 - 使用工厂函数创建（减少重复代码）
analyze_impressions_reach_trend = create_ai_analysis_endpoint(
    "analyze_impressions_reach_trend",
    "AI分析失败"
)
router.post("/analyze-impressions-reach", summary="分析展示和触达趋势")(analyze_impressions_reach_trend)

analyze_purchases_spend_trend = create_ai_analysis_endpoint(
    "analyze_purchases_spend_trend",
    "AI分析失败"
)
router.post("/analyze-purchases-spend", summary="分析购买价值和花费趋势")(analyze_purchases_spend_trend)


@router.post("/sync-data")
async def sync_facebook_ads_data(
    start_date: str = Body(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Body(..., description="结束日期 YYYY-MM-DD"),
    access_token: Optional[str] = Body(None, description="Facebook访问令牌（可选，默认使用配置）"),
    ad_account_id: Optional[str] = Body(None, description="广告账户ID（可选，默认使用配置）"),
    proxy_url: Optional[str] = Body(None, description="代理URL（可选，默认使用配置）"),
    db: Session = Depends(get_db)
):
    """
    从 Facebook Ads API 同步广告级别数据到数据库
    
    此接口会：
    1. 连接到 Facebook Ads API
    2. 获取指定日期范围的所有广告（Ad）的详细数据
    3. 包含完整的层级信息：Campaign -> AdSet -> Ad
    4. 将数据同步到 fact_bi_ads_facebook_campaign 表
    
    参数:
    - access_token: Facebook访问令牌（必填）
    - ad_account_id: 广告账户ID，格式：act_xxxxxxxxxxxx（必填）
    - start_date: 开始日期（必填，格式：YYYY-MM-DD）
    - end_date: 结束日期（必填，格式：YYYY-MM-DD）
    
    返回:
    - success: 是否成功
    - message: 执行结果消息
    - records_synced: 同步的记录数
    - errors: 错误信息列表（如果有）
    """
    try:
        # 使用配置中的默认值（如果未提供）并验证
        final_access_token = validate_required_config(
            access_token or settings.FACEBOOK_ACCESS_TOKEN,
            "Facebook Access Token"
        )
        final_ad_account_id = validate_required_config(
            ad_account_id or settings.FACEBOOK_AD_ACCOUNT_ID,
            "Facebook Ad Account ID"
        )
        
        # 调用Facebook API时需要添加 act_ 前缀
        final_ad_account_id_with_prefix = normalize_account_id(final_ad_account_id)
        
        # 创建同步服务
        sync_service = FacebookAdsDataSyncService(db)
        
        # 执行同步（传递带前缀的ID给Facebook API，不带前缀的ID用于数据库保存）
        result = sync_service.sync_ads(
            access_token=final_access_token,
            ad_account_id=final_ad_account_id_with_prefix,
            start_date=start_date,
            end_date=end_date,
            account_id_for_db=final_ad_account_id,  # 传递不带前缀的ID用于数据库保存
            proxy_url=proxy_url or settings.FACEBOOK_PROXY_URL_EFFECTIVE
        )
        
        if result["success"]:
            cache_patterns = [
                "facebook:impressions*",
                "facebook:purchases*",
                "facebook:impressions:db*",
                "facebook:purchases:db*",
                "facebook:overview*",
                "facebook:performance_comparison*",
                "facebook:campaign_performance*",
                "facebook:ads_performance*",
                "facebook:adsets_performance*",
                "facebook:ads_detail_performance*"
            ]
            for pattern in cache_patterns:
                try:
                    invalidate_cache(pattern)
                except Exception as cache_error:
                    logger.warning("清除缓存失败，pattern=%s，error=%s", pattern, cache_error)

            return api_success({
                "records_synced": result["records_synced"],
                "ad_account_id": final_ad_account_id,
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
