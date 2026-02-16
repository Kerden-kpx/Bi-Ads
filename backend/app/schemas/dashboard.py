"""
Dashboard API请求模式 - 优化版
"""
from pydantic import BaseModel, Field
from typing import Optional


# ==================== 基础Schema ====================

class DateRangeComparisonRequest(BaseModel):
    """日期范围对比请求基类"""
    startDate1: str = Field(..., description="当前时间段开始日期 YYYY-MM-DD")
    endDate1: str = Field(..., description="当前时间段结束日期 YYYY-MM-DD")
    startDate2: str = Field(..., description="对比时间段开始日期 YYYY-MM-DD")
    endDate2: str = Field(..., description="对比时间段结束日期 YYYY-MM-DD")


class SingleDateRequest(BaseModel):
    """单日期请求基类"""
    date: str = Field(..., description="基准日期 YYYY-MM-DD，用于计算本周和上周")


# ==================== Google Ads Schema ====================

class PerformanceComparisonRequest(DateRangeComparisonRequest):
    """Google性能对比数据请求"""
    pass


class CampaignPerformanceRequest(DateRangeComparisonRequest):
    """Campaign Performance Overview 请求"""
    pass


class AdsPerformanceOverviewRequest(SingleDateRequest):
    """Ads Performance Overview 请求"""
    pass


# ==================== Facebook Schema ====================

class FacebookDateRangeWithAccountRequest(DateRangeComparisonRequest):
    """Facebook日期范围对比请求（带账户ID）"""
    accountId: Optional[str] = Field(None, description="账户ID")


class FacebookPerformanceComparisonRequest(FacebookDateRangeWithAccountRequest):
    """Facebook性能对比数据请求"""
    pass


class FacebookAdsetsPerformanceOverviewRequest(FacebookDateRangeWithAccountRequest):
    """Facebook Ad Sets Performance Overview 请求"""
    pass


class FacebookAdsDetailPerformanceOverviewRequest(FacebookDateRangeWithAccountRequest):
    """Facebook Ads Detail Performance Overview 请求"""
    pass


class FacebookAdsPerformanceOverviewRequest(SingleDateRequest):
    """Facebook Ads Performance Overview 请求"""
    accountId: Optional[str] = Field(None, description="账户ID")

