"""
Dashboard数据模型

注意：
- ImpressionData 已移除，现在直接从原始数据表（fact_bi_ads_facebook_campaign, fact_bi_ads_google_campaign）获取印象数据
- PurchaseData 已移除，现在直接从原始数据表（fact_bi_ads_facebook_campaign, fact_bi_ads_google_campaign）获取购买/转化数据
- AdSetData 已移除，现在使用 get_adsets_performance_overview 直接查询
- AdsPerformanceData 已移除，现在使用 get_ads_performance_overview 直接查询

只保留原始数据表模型：FacebookAdsRaw 和 GoogleAdsCampaignRaw
"""
from sqlalchemy import Column, Integer, String, DECIMAL
from app.core.database import Base
from sqlalchemy import Date


class FacebookAdsRaw(Base):
    """
    Facebook Ads 原始数据表（广告级别）
    映射到数据库表：fact_bi_ads_facebook_campaign
    
    主键：(campaign_id, adset_id, ad_id, createtime)
    编码：utf8mb4
    引擎：InnoDB
    """
    __tablename__ = "fact_bi_ads_facebook_campaign"
    
    # 主键（复合主键）
    campaign_id = Column(String(255), primary_key=True, comment='广告系列ID')
    adset_id = Column(String(255), primary_key=True, comment='广告组ID')
    ad_id = Column(String(255), primary_key=True, comment='广告ID')
    createtime = Column(Date, primary_key=True, comment='日期')
    
    # 账户信息
    account_id = Column(String(255), comment='广告账户ID')
    
    # 广告系列信息
    campaign_name = Column(String(255), comment='广告系列')
    adset_name = Column(String(255), comment='广告组')
    ad_name = Column(String(255), comment='广告')
    
    # 性能指标
    impression = Column(Integer, comment='展示次数')
    spend = Column(DECIMAL(10, 2), comment='费用')
    clicks = Column(Integer, comment='点击次数')
    purchases_roas = Column(DECIMAL(10, 2), comment='购物转化ROAS')
    reach = Column(Integer, comment='覆盖人数')
    unique_link_clicks = Column(Integer, comment='链接点击量 - 独立用户')
    adds_to_cart = Column(Integer, comment='加入购物车')
    adds_payment_info = Column(Integer, comment='添加支付信息')
    purchases = Column(Integer, comment='购物次数')
    
    # 创意信息（新增）
    image_url = Column(String(500), comment='广告图片URL')
    preview_url = Column(String(65535), comment='广告预览HTML')
    
    def __repr__(self):
        return f"<FacebookAds(campaign_id={self.campaign_id}, adset_id={self.adset_id}, ad_id={self.ad_id}, date={self.createtime})>"
    
    def to_dict(self):
        """转换为字典"""
        spend_value = float(self.spend or 0)
        purchases_roas_value = float(self.purchases_roas or 0)
        purchases_value = purchases_roas_value * spend_value
        
        return {
            'account_id': self.account_id,
            'campaign_id': self.campaign_id,
            'adset_id': self.adset_id,
            'ad_id': self.ad_id,
            'campaign_name': self.campaign_name,
            'adset_name': self.adset_name,
            'ad_name': self.ad_name,
            'date': self.createtime.isoformat() if self.createtime else "",
            'impressions': self.impression or 0,
            'spend': spend_value,
            'clicks': self.clicks or 0,
            'purchases_value': round(purchases_value, 2),
            'reach': self.reach or 0,
            'unique_link_clicks': self.unique_link_clicks or 0,
            'adds_to_cart': self.adds_to_cart or 0,
            'adds_payment_info': self.adds_payment_info or 0,
            'purchases': self.purchases or 0,
            'ctr': round(float(self.clicks or 0) / float(self.impression or 1) * 100, 2) if self.impression else 0,
            'cpm': round(float(self.spend or 0) / float(self.impression or 1) * 1000, 2) if self.impression else 0,
            'roas': round(purchases_roas_value, 2),
            'image_url': self.image_url,
            'preview_url': self.preview_url
        }


class GoogleAdsCampaignRaw(Base):
    """
    Google Ads Campaign 原始数据表
    映射到数据库表：fact_bi_ads_google_campaign
    
    主键：(campaign_id, createtime)
    编码：utf8mb4
    引擎：InnoDB
    """
    __tablename__ = "fact_bi_ads_google_campaign"
    
    # 主键（复合主键）
    campaign_id = Column(String(255), primary_key=True, comment='广告系列ID')
    createtime = Column(Date, primary_key=True, comment='日期')
    
    # 广告系列信息
    campaign = Column(String(255), comment='广告系列')
    
    # 性能指标
    impression = Column(Integer, comment='展示次数')
    clicks = Column(Integer, comment='点击次数')
    
    # 成本和转化
    cost = Column(DECIMAL(10, 2), comment='费用')
    conversions = Column(DECIMAL(10, 2), comment='转化次数')
    conversion_value = Column(DECIMAL(10, 2), comment='转化价值')
    
    def __repr__(self):
        return f"<GoogleAdsCampaign(campaign_id={self.campaign_id}, campaign={self.campaign}, date={self.createtime})>"
    
    def to_dict(self):
        """转换为字典"""
        impressions = self.impression or 0
        clicks = self.clicks or 0
        cost = float(self.cost or 0)
        conversion_value = float(self.conversion_value or 0)
        
        # 计算派生指标
        ctr = (clicks / impressions) if impressions > 0 else 0
        roas = (conversion_value / cost) if cost > 0 else 0
        avg_cpc = (cost / clicks) if clicks > 0 else 0
        
        return {
            'campaign_id': self.campaign_id,
            'campaign': self.campaign,
            'date': self.createtime.isoformat() if self.createtime else "",
            'impressions': impressions,
            'clicks': clicks,
            'ctr': round(ctr, 5),
            'cost': cost,
            'conversions': float(self.conversions or 0),
            'conversion_value': conversion_value,
            'roas': round(roas, 2),
            'avg_cpc': round(avg_cpc, 2)
        }
