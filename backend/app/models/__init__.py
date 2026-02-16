"""
数据模型
注意：所有聚合表模型已移除，现在只保留原始数据表模型
"""
from .dashboard import (
    FacebookAdsRaw,
    GoogleAdsCampaignRaw
)

__all__ = [
    "FacebookAdsRaw",
    "GoogleAdsCampaignRaw"
]

