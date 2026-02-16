"""
数据模式（Pydantic schemas）
"""
from .dashboard import (
    FacebookPerformanceComparisonRequest,
    FacebookAdsetsPerformanceOverviewRequest,
    FacebookAdsDetailPerformanceOverviewRequest,
    FacebookAdsPerformanceOverviewRequest,
    PerformanceComparisonRequest,
    CampaignPerformanceRequest,
    AdsPerformanceOverviewRequest
)

__all__ = [
    "FacebookPerformanceComparisonRequest",
    "FacebookAdsetsPerformanceOverviewRequest",
    "FacebookAdsDetailPerformanceOverviewRequest",
    "FacebookAdsPerformanceOverviewRequest",
    "PerformanceComparisonRequest",
    "CampaignPerformanceRequest",
    "AdsPerformanceOverviewRequest"
]

