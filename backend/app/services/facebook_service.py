"""
Facebook Ads Dashboard业务逻辑服务（优化版，支持自动重试和缓存）
"""
from typing import Dict, Any, List
import os
from sqlalchemy import text
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from concurrent.futures import ThreadPoolExecutor
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.services.base_service import BaseDashboardService
from app.services.data_parser_config import get_parse_config
from app.utils.chart_helpers import generate_chart_data, FACEBOOK_IMPRESSION_CHART_CONFIG, FACEBOOK_PURCHASE_CHART_CONFIG
from app.utils.helpers import build_mysql_regex_union, escape_mysql_regex_literal, safe_divide
from app.core.config import settings
from app.core.cache import cached

FACEBOOK_API_EXECUTOR = ThreadPoolExecutor(max_workers=max(1, settings.FACEBOOK_API_MAX_WORKERS))


class FacebookDashboardService(BaseDashboardService):
    """Facebook Dashboard服务类 - 继承基础服务"""
    
    def __init__(self, db):
        super().__init__(db, platform="facebook")

    def setup_proxy(self, proxy_url: str = None):
        """为 Facebook API 设置代理（可选）"""
        if proxy_url is None:
            proxy_url = settings.FACEBOOK_PROXY_URL_EFFECTIVE

        if proxy_url:
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
            os.environ['http_proxy'] = proxy_url
            os.environ['https_proxy'] = proxy_url
            print(f"🔧 Facebook 代理已设置: {proxy_url}")
        else:
            print("ℹ️ 未设置 Facebook 代理，使用直连")
    
    @cached(prefix="facebook:impressions:db", ttl=settings.CACHE_TTL_MEDIUM)
    async def get_impressions_data(
        self,
        start_date: str,
        end_date: str,
        compare_start_date: str = None,
        compare_end_date: str = None,
        account_id: str = None
    ) -> Dict[str, Any]:
        """获取印象和触达数据（从数据库）- 已启用缓存"""
        
        # 构建WHERE条件
        where_conditions = "createtime BETWEEN :start_date AND :end_date"
        if account_id:
            where_conditions += " AND account_id = :account_id"
        
        query = text(f"""
            SELECT
                createtime,
                SUM(impression) AS impressions,
                SUM(reach) AS reach,
                SUM(clicks) AS clicks,
                SUM(unique_link_clicks) AS unique_link_clicks,
                AVG(CASE WHEN impression > 0 THEN (clicks / impression * 100) ELSE 0 END) AS ctr,
                AVG(CASE WHEN impression > 0 THEN (spend / impression * 1000) ELSE 0 END) AS cpm
            FROM fact_bi_ads_facebook_campaign
            WHERE {where_conditions}
            GROUP BY createtime
            ORDER BY createtime
        """)
        
        # 执行查询
        params = {"start_date": start_date, "end_date": end_date}
        if account_id:
            params["account_id"] = account_id
        current_rows = await self.execute_query(query, params)
        current_data = [self._parse_impression_row(row) for row in current_rows]
        
        # 生成图表数据
        chart_data = generate_chart_data(current_data, "date", FACEBOOK_IMPRESSION_CHART_CONFIG)
        
        # 聚合数据
        result = self.process_comparison_data(
            current_data=current_data,
            compare_data=None,
            aggregate_fields=["impressions", "reach", "clicks", "unique_link_clicks"],
            average_fields=["ctr", "cpm"],
            change_mapping={
                "impressions": "impressionsChange",
                "reach": "reachChange",
                "clicks": "clicksChange",
                "unique_link_clicks": "uniqueLinkClicksChange",
                "ctr": "ctrChange",
                "cpm": "cpmChange"
            }
        )
        
        # 处理对比数据
        if compare_start_date and compare_end_date:
            compare_params = {"start_date": compare_start_date, "end_date": compare_end_date}
            if account_id:
                compare_params["account_id"] = account_id
            compare_rows = await self.execute_query(query, compare_params)
            compare_data = [self._parse_impression_row(row) for row in compare_rows]
            
            result = self.process_comparison_data(
                current_data=current_data,
                compare_data=compare_data,
                aggregate_fields=["impressions", "reach", "clicks", "unique_link_clicks"],
                average_fields=["ctr", "cpm"],
                change_mapping={
                    "impressions": "impressionsChange",
                    "reach": "reachChange",
                    "clicks": "clicksChange",
                    "unique_link_clicks": "uniqueLinkClicksChange",
                    "ctr": "ctrChange",
                    "cpm": "cpmChange"
                }
            )
        
        # 添加图表数据
        result["current"]["chartData"] = chart_data
        return result
    
    @cached(prefix="facebook:purchases:db", ttl=settings.CACHE_TTL_MEDIUM)
    async def get_purchases_data(
        self,
        start_date: str,
        end_date: str,
        compare_start_date: str = None,
        compare_end_date: str = None,
        account_id: str = None
    ) -> Dict[str, Any]:
        """获取购买和花费数据（从数据库）- 已启用缓存"""
        
        # 构建WHERE条件
        where_conditions = "createtime BETWEEN :start_date AND :end_date"
        if account_id:
            where_conditions += " AND account_id = :account_id"
        
        query = text(f"""
            SELECT
                createtime,
                SUM(purchases_roas * spend) AS purchases_value,
                SUM(spend) AS spend,
                SUM(purchases) AS purchases,
                SUM(adds_to_cart) AS adds_to_cart,
                SUM(adds_payment_info) AS adds_payment_info,
                IFNULL(SUM(purchases_roas * spend) / NULLIF(SUM(spend), 0), 0) AS roas
            FROM fact_bi_ads_facebook_campaign
            WHERE {where_conditions}
            GROUP BY createtime
            ORDER BY createtime
        """)
        
        # 执行查询
        params = {"start_date": start_date, "end_date": end_date}
        if account_id:
            params["account_id"] = account_id
        current_rows = await self.execute_query(query, params)
        current_data = [self._parse_purchase_row(row) for row in current_rows]
        
        # 生成图表数据
        chart_data = generate_chart_data(current_data, "date", FACEBOOK_PURCHASE_CHART_CONFIG)
        
        # 处理数据
        result = self.process_comparison_data(
            current_data=current_data,
            compare_data=None,
            aggregate_fields=["purchases_value", "spend", "purchases", "adds_to_cart", "adds_payment_info"],
            average_fields=["roas"],
            change_mapping={
                "purchases_value": "purchasesValueChange",
                "spend": "spendChange",
                "purchases": "purchasesChange",
                "adds_to_cart": "addsToCartChange",
                "adds_payment_info": "addsPaymentInfoChange",
                "roas": "roasChange"
            }
        )
        
        # 重新计算总ROAS
        total_value = result["current"]["purchases_value"]
        total_spend = result["current"]["spend"]
        result["current"]["roas"] = safe_divide(total_value, total_spend, 0, 2)
        
        # 处理对比数据
        if compare_start_date and compare_end_date:
            compare_params = {"start_date": compare_start_date, "end_date": compare_end_date}
            if account_id:
                compare_params["account_id"] = account_id
            compare_rows = await self.execute_query(query, compare_params)
            compare_data = [self._parse_purchase_row(row) for row in compare_rows]
            
            result = self.process_comparison_data(
                current_data=current_data,
                compare_data=compare_data,
                aggregate_fields=["purchases_value", "spend", "purchases", "adds_to_cart", "adds_payment_info"],
                average_fields=[],
                change_mapping={
                    "purchases_value": "purchasesValueChange",
                    "spend": "spendChange",
                    "purchases": "purchasesChange",
                    "adds_to_cart": "addsToCartChange",
                    "adds_payment_info": "addsPaymentInfoChange",
                    "roas": "roasChange"
                }
            )
            
            # 重新计算ROAS
            result["current"]["roas"] = safe_divide(result["current"]["purchases_value"], result["current"]["spend"], 0, 2)
            if "compare" in result:
                result["compare"]["roas"] = safe_divide(result["compare"]["purchases_value"], result["compare"]["spend"], 0, 2)
        
        # 添加图表数据
        result["current"]["chartData"] = chart_data
        
        # 转换字段名以匹配前端
        result["current"]["purchasesValue"] = result["current"].pop("purchases_value", 0)
        result["current"]["addsToCart"] = result["current"].pop("adds_to_cart", 0)
        result["current"]["addsPaymentInfo"] = result["current"].pop("adds_payment_info", 0)
        
        if "compare" in result:
            result["compare"]["purchasesValue"] = result["compare"].pop("purchases_value", 0)
            result["compare"]["addsToCart"] = result["compare"].pop("adds_to_cart", 0)
            result["compare"]["addsPaymentInfo"] = result["compare"].pop("adds_payment_info", 0)
        
        return result
    
    @cached(prefix="facebook:performance_comparison", ttl=settings.CACHE_TTL_LONG)
    async def get_performance_comparison(
        self,
        start_time1: str,
        end_time1: str,
        start_time2: str,
        end_time2: str,
        account_id: str = None
    ) -> List[Dict[str, Any]]:
        """获取性能对比数据（用于面积图）- 已启用缓存"""
        
        # 构建WHERE条件
        where_cond1 = "createtime BETWEEN :start_time1 AND :end_time1"
        where_cond2 = "createtime BETWEEN :start_time2 AND :end_time2"
        if account_id:
            where_cond1 += " AND account_id = :account_id"
            where_cond2 += " AND account_id = :account_id"
        
        query = text(f"""
            WITH date_current AS (
                SELECT
                    createtime,
                    ROW_NUMBER() OVER (ORDER BY createtime) AS current_seq,
                    SUM(impression) AS impression,
                    SUM(reach) AS reach,
                    SUM(clicks) AS clicks,
                    SUM(unique_link_clicks) AS unique_link_clicks,
                    SUM(purchases) AS purchases,
                    SUM(purchases_roas * spend) AS purchases_value,
                    SUM(spend) AS spend,
                    SUM(adds_to_cart) AS adds_to_cart,
                    SUM(adds_payment_info) AS adds_payment_info
                FROM fact_bi_ads_facebook_campaign
                WHERE {where_cond1}
                GROUP BY createtime
            ),
            data_compare AS (
                SELECT
                    createtime,
                    ROW_NUMBER() OVER (ORDER BY createtime) AS compare_seq,
                    SUM(impression) AS compare_impression,
                    SUM(reach) AS compare_reach,
                    SUM(clicks) AS compare_clicks,
                    SUM(unique_link_clicks) AS compare_unique_link_clicks,
                    SUM(purchases) AS compare_purchases,
                    SUM(purchases_roas * spend) AS compare_purchases_value,
                    SUM(spend) AS compare_spend,
                    SUM(adds_to_cart) AS compare_adds_to_cart,
                    SUM(adds_payment_info) AS compare_adds_payment_info
                FROM fact_bi_ads_facebook_campaign
                WHERE {where_cond2}
                GROUP BY createtime
            )
            SELECT
                A.createtime AS createtime,
                A.impression,
                IFNULL(B.compare_impression, 0) AS compare_impression,
                A.reach,
                IFNULL(B.compare_reach, 0) AS compare_reach,
                A.clicks,
                IFNULL(B.compare_clicks, 0) AS compare_clicks,
                A.unique_link_clicks,
                IFNULL(B.compare_unique_link_clicks, 0) AS compare_unique_link_clicks,
                A.purchases,
                IFNULL(B.compare_purchases, 0) AS compare_purchases,
                A.purchases_value,
                IFNULL(B.compare_purchases_value, 0) AS compare_purchases_value,
                A.spend,
                IFNULL(B.compare_spend, 0) AS compare_spend,
                A.adds_to_cart,
                IFNULL(B.compare_adds_to_cart, 0) AS compare_adds_to_cart,
                A.adds_payment_info,
                IFNULL(B.compare_adds_payment_info, 0) AS compare_adds_payment_info
            FROM date_current A
                LEFT JOIN data_compare B ON A.current_seq = B.compare_seq
        """)
        
        params = {
            "start_time1": start_time1,
            "end_time1": end_time1,
            "start_time2": start_time2,
            "end_time2": end_time2
        }
        if account_id:
            params["account_id"] = account_id
        
        rows = await self.execute_query(query, params)
        
        return [self._parse_performance_comparison_row(row) for row in rows]
    
    @cached(prefix="facebook:campaign_performance", ttl=settings.CACHE_TTL_LONG)
    async def get_campaign_performance_overview(
        self,
        start_time1: str,
        end_time1: str,
        start_time2: str,
        end_time2: str
    ) -> List[Dict[str, Any]]:
        """获取Campaign Performance Overview数据 - 已启用缓存"""
        
        query = text("""
            WITH date_current AS (
                SELECT
                    campaign_id,
                    campaign_name,
                    SUM(impression) AS impression,
                    SUM(spend) AS spend,
                    SUM(clicks) AS clicks,
                    SUM(purchases) AS purchases,
                    SUM(purchases_roas * spend) AS purchases_value,
                    IFNULL(SUM(purchases_roas * spend) / NULLIF(SUM(spend), 0), 0) AS roas
                FROM fact_bi_ads_facebook_campaign
                WHERE createtime BETWEEN :start_time1 AND :end_time1
                GROUP BY campaign_id, campaign_name
                HAVING SUM(spend) > 0
            ),
            date_compare AS (
                SELECT
                    campaign_id,
                    SUM(impression) AS impression,
                    SUM(spend) AS spend,
                    SUM(clicks) AS clicks,
                    SUM(purchases) AS purchases,
                    SUM(purchases_roas * spend) AS purchases_value,
                    IFNULL(SUM(purchases_roas * spend) / NULLIF(SUM(spend), 0), 0) AS roas
                FROM fact_bi_ads_facebook_campaign
                WHERE createtime BETWEEN :start_time2 AND :end_time2
                GROUP BY campaign_id
            )
                SELECT
                    A.campaign_id,
                    A.campaign_name,
                    A.impression,
                    A.spend,
                    A.clicks,
                    A.purchases,
                    A.purchases_value,
                    A.roas,
                    A.clicks / A.impression AS ctr,
                A.spend / A.impression * 1000 AS cpm,
                    B.impression AS compare_impression,
                    B.spend AS compare_spend,
                    B.clicks AS compare_clicks,
                    B.purchases AS compare_purchases,
                    B.purchases_value AS compare_purchases_value,
                    B.roas AS compare_roas,
                    B.clicks / B.impression AS compare_ctr,
                    B.spend / B.impression * 1000 AS compare_cpm
            FROM date_current A
                    LEFT JOIN date_compare B ON A.campaign_id = B.campaign_id
            WHERE B.campaign_id IS NOT NULL
        """)
        
        rows = await self.execute_query(query, {
                "start_time1": start_time1,
                "end_time1": end_time1,
                "start_time2": start_time2,
                "end_time2": end_time2
        })
        
        return [self._parse_campaign_performance_row(row) for row in rows]
    
    @cached(prefix="facebook:ads_performance", ttl=settings.CACHE_TTL_LONG)
    async def get_ads_performance_overview(self, variable_date: str, account_id: str = None) -> List[Dict[str, Any]]:
        """获取Ads Performance Overview数据（产品表现）- 已启用缓存"""
        product_list = [name.strip() for name in settings.FACEBOOK_PRODUCT_NAMES_LIST if name and name.strip()]
        if not product_list:
            return []

        params = {
            "variable_time": variable_date,
            "product_pattern": build_mysql_regex_union(product_list),
        }

        # 构建WHERE条件
        where_condition = "campaign_name REGEXP :product_pattern"
        if account_id:
            where_condition += " AND account_id = :account_id"
            params["account_id"] = account_id

        # 动态构建CASE WHEN语句（使用参数绑定，避免字符串拼接注入）
        case_statements = []
        for idx, product in enumerate(product_list):
            regex_key = f"campaign_regex_{idx}"
            label_key = f"campaign_label_{idx}"
            if product == "黑曜石OMT":
                params[regex_key] = build_mysql_regex_union(["黑曜石OMT", "黑曜石"])
            else:
                params[regex_key] = escape_mysql_regex_literal(product)
            params[label_key] = product
            case_statements.append(f"WHEN campaign_name REGEXP :{regex_key} THEN :{label_key}")
        case_when_clause = "\n                  ".join(case_statements)

        query = text(f"""
            WITH date_range AS (
              SELECT
                DATE_FORMAT(monday_current, '%Y-%m-%d') AS current_week_start,
                DATE_FORMAT(sunday_current, '%Y-%m-%d') AS current_week_end,
                DATE_FORMAT(monday_last, '%Y-%m-%d') AS last_week_start,
                DATE_FORMAT(sunday_last, '%Y-%m-%d') AS last_week_end
              FROM
                (SELECT
                    DATE_SUB(:variable_time, INTERVAL WEEKDAY(:variable_time) DAY) AS monday_current,
                    DATE_SUB(:variable_time, INTERVAL WEEKDAY(:variable_time) + 7 DAY) AS monday_last
                ) AS dates,
                LATERAL (SELECT
                    DATE_ADD(monday_current, INTERVAL 6 DAY) AS sunday_current,
                    DATE_ADD(monday_last, INTERVAL 6 DAY) AS sunday_last
                ) AS sundays
            ),
            data_detail AS (
              SELECT
                campaign_id,
                CASE
                  {case_when_clause}
                  ELSE campaign_name
                END AS campaign_name,
                purchases, spend, purchases_roas, createtime
              FROM fact_bi_ads_facebook_campaign, date_range
              WHERE {where_condition}
            ),
            current_week_data AS (
              SELECT
                campaign_id, campaign_name,
                SUM(purchases) AS purchases,
                SUM(purchases_roas * spend) AS purchases_value,
                SUM(spend) AS spend,
                IFNULL(SUM(purchases_roas * spend) / NULLIF(SUM(spend), 0), 0) AS roas
              FROM data_detail, date_range
              WHERE createtime BETWEEN current_week_start AND current_week_end
              GROUP BY campaign_id, campaign_name
            ),
            last_week_data AS (
              SELECT
                campaign_id, campaign_name,
                SUM(purchases) AS purchases,
                SUM(purchases_roas * spend) AS purchases_value,
                SUM(spend) AS spend,
                IFNULL(SUM(purchases_roas * spend) / NULLIF(SUM(spend), 0), 0) AS roas
              FROM data_detail, date_range
              WHERE createtime BETWEEN last_week_start AND last_week_end
              GROUP BY campaign_id, campaign_name
            )
              SELECT
                temp.campaign_name,
                SUM(last_purchases) AS last_purchases,
                SUM(last_purchases_value) AS last_purchases_value,
                SUM(last_spend) AS last_spend,
                SUM(last_purchases_value) / SUM(last_spend) AS last_roas,
                SUM(current_purchases) AS current_purchases,
                SUM(current_purchases_value) AS current_purchases_value,
                SUM(current_spend) AS current_spend,
                SUM(current_purchases_value) / SUM(current_spend) AS current_roas
            FROM (
                  SELECT
                    L.campaign_name,
                    L.purchases AS last_purchases,
                    L.purchases_value AS last_purchases_value,
                    L.spend AS last_spend,
                    C.purchases AS current_purchases,
                    C.purchases_value AS current_purchases_value,
                    C.spend AS current_spend
                FROM last_week_data L
                    LEFT JOIN current_week_data C ON L.campaign_id = C.campaign_id
                ) temp
            GROUP BY temp.campaign_name
        """)

        rows = await self.execute_query(query, params)
        return [self._parse_ads_performance_row(row) for row in rows]
    
    @cached(prefix="facebook:adsets_performance", ttl=settings.CACHE_TTL_LONG)
    async def get_adsets_performance_overview(
        self,
        start_time1: str,
        end_time1: str,
        start_time2: str,
        end_time2: str,
        account_id: str = None
    ) -> List[Dict[str, Any]]:
        """获取Ad Sets Performance Overview数据 - 已启用缓存"""
        
        # 构建WHERE条件
        where_cond1 = "createtime BETWEEN :start_time1 AND :end_time1"
        where_cond2 = "createtime BETWEEN :start_time2 AND :end_time2"
        if account_id:
            where_cond1 += " AND account_id = :account_id"
            where_cond2 += " AND account_id = :account_id"
        
        query = text(f"""
            WITH date_current AS (
                SELECT
                    adset_id, adset_name,
                    SUM(impression) AS impression,
                    SUM(spend) AS spend,
                    SUM(clicks) AS clicks,
                    SUM(purchases) AS purchases,
                    SUM(purchases_roas * spend) AS purchases_value,
                    IFNULL(SUM(purchases_roas * spend) / NULLIF(SUM(spend), 0), 0) AS purchase_roas,
                    SUM(unique_link_clicks) AS unique_link_clicks
                FROM fact_bi_ads_facebook_campaign
                WHERE {where_cond1}
                GROUP BY adset_id, adset_name
            ),
            date_compare AS (
                SELECT
                    adset_id,
                    SUM(impression) AS impression,
                    SUM(spend) AS spend,
                    SUM(purchases) AS purchases,
                    SUM(purchases_roas * spend) AS purchases_value,
                    IFNULL(SUM(purchases_roas * spend) / NULLIF(SUM(spend), 0), 0) AS purchase_roas,
                    SUM(unique_link_clicks) AS unique_link_clicks
                FROM fact_bi_ads_facebook_campaign
                WHERE {where_cond2}
                GROUP BY adset_id
            )
            SELECT
                A.adset_id, A.adset_name AS name,
                A.spend, IFNULL(B.spend, 0) AS spend_previous,
                A.purchases, IFNULL(B.purchases, 0) AS purchases_previous,
                A.purchases_value, IFNULL(B.purchases_value, 0) AS purchases_value_previous,
                A.purchase_roas, IFNULL(B.purchase_roas, 0) AS purchase_roas_previous,
                CASE WHEN A.impression > 0 THEN (A.unique_link_clicks / A.impression * 100) ELSE 0 END AS ctr,
                CASE WHEN B.impression > 0 THEN (B.unique_link_clicks / B.impression * 100) ELSE 0 END AS ctr_previous,
                CASE WHEN A.impression > 0 THEN (A.spend / A.impression * 1000) ELSE 0 END AS cpm,
                CASE WHEN B.impression > 0 THEN (B.spend / B.impression * 1000) ELSE 0 END AS cpm_previous
            FROM date_current A
                LEFT JOIN date_compare B ON A.adset_id = B.adset_id
        """)
        
        params = {
            "start_time1": start_time1,
            "end_time1": end_time1,
            "start_time2": start_time2,
            "end_time2": end_time2
        }
        if account_id:
            params["account_id"] = account_id
        
        rows = await self.execute_query(query, params)
        
        return [self._parse_adset_performance_row(row) for row in rows]
    
    @cached(prefix="facebook:ads_detail_performance", ttl=settings.CACHE_TTL_LONG)
    async def get_ads_detail_performance_overview(
        self,
        start_time1: str,
        end_time1: str,
        start_time2: str,
        end_time2: str,
        account_id: str = None
    ) -> List[Dict[str, Any]]:
        """获取Ads Detail Performance Overview数据 - 已启用缓存"""
        
        # 构建WHERE条件
        where_cond1 = "createtime BETWEEN :start_time1 AND :end_time1"
        where_cond2 = "createtime BETWEEN :start_time2 AND :end_time2"
        if account_id:
            where_cond1 += " AND account_id = :account_id"
            where_cond2 += " AND account_id = :account_id"
        
        query = text(f"""
            WITH date_current AS (
                SELECT
                    ad_id, ad_name,
                    SUM(impression) AS impression,
                    SUM(spend) AS spend,
                    SUM(purchases) AS purchases,
                    SUM(purchases_roas * spend) AS purchases_value,
                    IFNULL(SUM(purchases_roas * spend) / NULLIF(SUM(spend), 0), 0) AS purchase_roas,
                    SUM(unique_link_clicks) AS unique_link_clicks,
                    SUM(adds_payment_info) AS adds_payment_info,
                    SUM(adds_to_cart) AS adds_to_cart,
                    MAX(image_url) AS image_url,
                    MAX(preview_url) AS preview_url
                FROM fact_bi_ads_facebook_campaign
                WHERE {where_cond1}
                GROUP BY ad_id, ad_name
            ),
            date_compare AS (
                SELECT
                    ad_id,
                    SUM(impression) AS impression,
                    SUM(spend) AS spend,
                    SUM(purchases) AS purchases,
                    SUM(purchases_roas * spend) AS purchases_value,
                    IFNULL(SUM(purchases_roas * spend) / NULLIF(SUM(spend), 0), 0) AS purchase_roas,
                    SUM(unique_link_clicks) AS unique_link_clicks,
                    SUM(adds_payment_info) AS adds_payment_info,
                    SUM(adds_to_cart) AS adds_to_cart
                FROM fact_bi_ads_facebook_campaign
                WHERE {where_cond2}
                GROUP BY ad_id
            )
            SELECT
                A.ad_id, A.ad_name AS name,
                A.spend, IFNULL(B.spend, 0) AS spend_previous,
                A.purchases, IFNULL(B.purchases, 0) AS purchases_previous,
                A.purchases_value, IFNULL(B.purchases_value, 0) AS purchases_value_previous,
                A.purchase_roas, IFNULL(B.purchase_roas, 0) AS purchase_roas_previous,
                A.adds_payment_info, IFNULL(B.adds_payment_info, 0) AS adds_payment_info_previous,
                A.adds_to_cart, IFNULL(B.adds_to_cart, 0) AS adds_to_cart_previous,
                CASE WHEN A.impression > 0 THEN (A.unique_link_clicks / A.impression * 100) ELSE 0 END AS ctr,
                CASE WHEN B.impression > 0 THEN (B.unique_link_clicks / B.impression * 100) ELSE 0 END AS ctr_previous,
                CASE WHEN A.impression > 0 THEN (A.spend / A.impression * 1000) ELSE 0 END AS cpm,
                CASE WHEN B.impression > 0 THEN (B.spend / B.impression * 1000) ELSE 0 END AS cpm_previous,
                A.image_url,
                A.preview_url
            FROM date_current A
                LEFT JOIN date_compare B ON A.ad_id = B.ad_id
        """)
        
        params = {
            "start_time1": start_time1,
            "end_time1": end_time1,
            "start_time2": start_time2,
            "end_time2": end_time2
        }
        if account_id:
            params["account_id"] = account_id
        
        rows = await self.execute_query(query, params)
        
        return [self._parse_ad_detail_performance_row(row) for row in rows]
    
    # ==================== 辅助方法 - 使用配置驱动解析 ====================
    
    def _parse_impression_row(self, row) -> Dict[str, Any]:
        """解析印象数据行"""
        return self.parse_row_with_mapping(row, get_parse_config('facebook', 'impression'))
    
    def _parse_purchase_row(self, row) -> Dict[str, Any]:
        """解析购买数据行"""
        return self.parse_row_with_mapping(row, get_parse_config('facebook', 'purchase'))
    
    def _parse_performance_comparison_row(self, row) -> Dict[str, Any]:
        """解析性能对比数据行"""
        return self.parse_row_with_mapping(row, get_parse_config('facebook', 'performance_comparison'))
    
    def _parse_campaign_performance_row(self, row) -> Dict[str, Any]:
        """解析Campaign性能数据行"""
        result = self.parse_row_with_mapping(row, get_parse_config('facebook', 'campaign_performance'))
        
        # 解析对比字段（动态处理）
        compare_fields = {
            'compare_impression': 'int', 'compare_clicks': 'int', 'compare_purchases': 'int',
            'compare_spend': 'float', 'compare_purchases_value': 'float', 
            'compare_roas': 'float', 'compare_cpm': 'float', 'compare_ctr': 'float'
        }
        
        for field, field_type in compare_fields.items():
            val = getattr(row, field, None)
            if val is not None:
                if field_type == 'int':
                    result[field] = int(val or 0)
                else:
                    precision = 4 if field == 'compare_ctr' else 2
                    result[field] = round(float(val or 0), precision)
            else:
                result[field] = None
        
        return result
    
    def _parse_ads_performance_row(self, row) -> Dict[str, Any]:
        """解析广告性能数据行"""
        return self.parse_row_with_mapping(row, get_parse_config('facebook', 'ads_performance'))
    
    def _parse_adset_performance_row(self, row) -> Dict[str, Any]:
        """解析广告组性能数据行"""
        return self.parse_row_with_mapping(row, get_parse_config('facebook', 'adset_performance'))
    
    def _parse_ad_detail_performance_row(self, row) -> Dict[str, Any]:
        """解析广告详情性能数据行"""
        result = self.parse_row_with_mapping(row, get_parse_config('facebook', 'ad_detail_performance'))
        result["imageUrl"] = str(row.image_url or "") if hasattr(row, 'image_url') else None
        result["previewUrl"] = str(row.preview_url or "") if hasattr(row, 'preview_url') else None
        return result
    
    # ==================== Facebook API 直接获取数据 ====================
    
    def _merge_comparison_data(
        self,
        current_data: List[Dict[str, Any]],
        compare_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """合并当前和对比期间的展示数据用于图表展示"""
        # 使用基类的通用合并方法
        merged = self.merge_comparison_data_generic(
            current_data, 
            compare_data,
            {
                "impressions": "compare_",
                "reach": "compare_",
                "clicks": "compare_",
                "unique_link_clicks": "compare_"
            }
        )
        # 调整字段名: date -> createtime, impressions -> impression
        for item in merged:
            if 'date' in item:
                item['createtime'] = item.pop('date')
            if 'impressions' in item:
                item['impression'] = item.pop('impressions')
            if 'compare_impressions' in item:
                item['compare_impression'] = item.pop('compare_impressions')
        return merged
    
    def _merge_purchases_comparison_data(
        self,
        current_data: List[Dict[str, Any]],
        compare_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """合并当前和对比期间的购买数据用于图表展示"""
        # 使用基类的通用合并方法
        merged = self.merge_comparison_data_generic(
            current_data,
            compare_data,
            {
                "purchases_value": "compare_",
                "spend": "compare_",
                "purchases": "compare_",
                "adds_to_cart": "compare_",
                "adds_payment_info": "compare_"
            }
        )
        # 调整字段名: date -> createtime
        for item in merged:
            if 'date' in item:
                item['createtime'] = item.pop('date')
        return merged
    
    @retry(
        stop=stop_after_attempt(3),  # 最多重试3次
        wait=wait_exponential(multiplier=1, min=2, max=10),  # 指数退避
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
        reraise=True
    )
    def _fetch_impressions_daily_insights(
        self,
        ad_account: AdAccount,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """获取每日展示数据（用于图表，支持自动重试）"""
        daily_insights = ad_account.get_insights(
            fields=[
                'impressions',
                'reach',
                'clicks',
                'unique_actions',
                'date_start'
            ],
            params={
                'level': 'account',
                'time_range': {
                    'since': start_date,
                    'until': end_date
                },
                'time_increment': 1  # 按天返回
            }
        )
        
        daily_data = []
        for insight in daily_insights:
            # 提取unique_actions（独立链接点击）
            unique_link_clicks = 0
            if insight.get('unique_actions'):
                for action in insight['unique_actions']:
                    if action.get('action_type') == 'link_click':
                        unique_link_clicks = int(action.get('value', 0))
                        break
            
            daily_data.append({
                'date': insight.get('date_start'),
                'impressions': int(insight.get('impressions', 0)),
                'reach': int(insight.get('reach', 0)),
                'clicks': int(insight.get('clicks', 0)),
                'unique_link_clicks': unique_link_clicks
            })
        
        return daily_data
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
        reraise=True
    )
    def _fetch_impressions_total_insights(
        self,
        ad_account: AdAccount,
        start_date: str,
        end_date: str
    ) -> tuple:
        """获取总汇总展示数据（用于指标卡，支持自动重试）"""
        total_insights = ad_account.get_insights(
            fields=[
                'impressions',
                'spend',  # 添加spend字段，确保CPM能正确返回
                'reach',
                'clicks',
                'unique_actions',
                'cpm',
                'ctr'
            ],
            params={
                'level': 'account',
                'time_range': {
                    'since': start_date,
                    'until': end_date
                }
                # 不使用time_increment，获取整个期间的总汇总
            }
        )
        
        # 获取第一条（唯一一条）总汇总数据
        summary_data = None
        for item in total_insights:
            summary_data = item
            break
        
        if not summary_data:
            return (0, 0, 0, 0, 0, 0)
        
        # 提取unique_actions
        unique_link_clicks = 0
        if summary_data.get('unique_actions'):
            for action in summary_data['unique_actions']:
                if action.get('action_type') == 'link_click':
                    unique_link_clicks = int(action.get('value', 0))
                    break
        
        # 返回原始数据，不进行四舍五入（用于环比计算）
        return (
            int(summary_data.get('impressions', 0)),
            int(summary_data.get('reach', 0)),
            int(summary_data.get('clicks', 0)),
            unique_link_clicks,
            float(summary_data.get('ctr', 0)),  # 原始CTR
            float(summary_data.get('cpm', 0))   # 原始CPM
        )
    
    @cached(prefix="facebook:impressions", ttl=settings.CACHE_TTL_MEDIUM)
    async def get_impressions_data_from_api(
        self,
        start_date: str,
        end_date: str,
        compare_start_date: str = None,
        compare_end_date: str = None,
        access_token: str = None,
        account_id: str = None
    ) -> Dict[str, Any]:
        """从Facebook API直接获取展示和触达数据（按天汇总，支持对比）- 已启用缓存"""
        try:
            # 设置代理（如果提供）
            self.setup_proxy()

            # 使用配置中的默认值
            final_access_token = access_token or settings.FACEBOOK_ACCESS_TOKEN
            final_account_id = account_id or settings.FACEBOOK_AD_ACCOUNT_ID
            
            # 确保account_id有act_前缀
            if not final_account_id.startswith('act_'):
                final_account_id = f'act_{final_account_id}'
            
            # 初始化Facebook API
            FacebookAdsApi.init(access_token=final_access_token)
            ad_account = AdAccount(final_account_id)
            
            # 获取当前日期范围的每日数据（用于图表）
            daily_data = self._fetch_impressions_daily_insights(ad_account, start_date, end_date)
            
            # 获取当前日期范围的总汇总数据（用于指标卡）
            (
                total_impressions,
                total_reach,
                total_clicks,
                total_unique_link_clicks,
                avg_ctr,
                avg_cpm
            ) = self._fetch_impressions_total_insights(ad_account, start_date, end_date)
            
            # 生成图表数据
            chart_data = generate_chart_data(daily_data, "date", FACEBOOK_IMPRESSION_CHART_CONFIG)
            
            result = {
                "current": {
                    "impressions": total_impressions,
                    "reach": total_reach,
                    "clicks": total_clicks,
                    "uniqueLinkClicks": total_unique_link_clicks,
                    "ctr": round(avg_ctr, 2),  # 显示时才四舍五入
                    "cpm": round(avg_cpm, 2),  # 显示时才四舍五入
                    "chartData": chart_data
                }
            }
            
            # 如果有对比日期范围，获取对比数据
            if compare_start_date and compare_end_date:
                # 获取对比期间的每日数据
                compare_daily_data = self._fetch_impressions_daily_insights(ad_account, compare_start_date, compare_end_date)
                
                # 获取对比期间的总汇总数据
                (
                    compare_impressions,
                    compare_reach,
                    compare_clicks,
                    compare_unique_link_clicks,
                    compare_ctr,
                    compare_cpm
                ) = self._fetch_impressions_total_insights(ad_account, compare_start_date, compare_end_date)
                
                result["compare"] = {
                    "impressions": compare_impressions,
                    "reach": compare_reach,
                    "clicks": compare_clicks,
                    "uniqueLinkClicks": compare_unique_link_clicks,
                    "ctr": compare_ctr,
                    "cpm": compare_cpm
                }
                
                # 计算变化百分比
                result["current"]["impressionsChange"] = round(safe_divide((total_impressions - compare_impressions) * 100, compare_impressions, 0, 4), 2)
                result["current"]["reachChange"] = round(safe_divide((total_reach - compare_reach) * 100, compare_reach, 0, 4), 2)
                result["current"]["clicksChange"] = round(safe_divide((total_clicks - compare_clicks) * 100, compare_clicks, 0, 4), 2)
                result["current"]["uniqueLinkClicksChange"] = round(safe_divide((total_unique_link_clicks - compare_unique_link_clicks) * 100, compare_unique_link_clicks, 0, 4), 2)
                result["current"]["ctrChange"] = round(safe_divide((avg_ctr - compare_ctr) * 100, compare_ctr, 0, 4), 2)
                result["current"]["cpmChange"] = round(safe_divide((avg_cpm - compare_cpm) * 100, compare_cpm, 0, 4), 2)
                
                # 合并当前和对比的每日数据用于图表展示
                merged_daily_data = self._merge_comparison_data(daily_data, compare_daily_data)
                result["performanceComparisonData"] = merged_daily_data
            
            return result
            
        except Exception as e:
            raise Exception(f"从Facebook API获取展示数据失败: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
        reraise=True
    )
    def _fetch_purchases_daily_insights(
        self,
        ad_account: AdAccount,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """获取每日购买数据（用于图表，支持自动重试）"""
        daily_insights = ad_account.get_insights(
            fields=[
                'spend',
                'actions',
                'action_values',
                'date_start'
            ],
            params={
                'level': 'account',
                'time_range': {
                    'since': start_date,
                    'until': end_date
                },
                'time_increment': 1  # 按天返回
            }
        )
        
        daily_data = []
        for insight in daily_insights:
            # 提取actions数据
            purchases = 0
            adds_to_cart = 0
            adds_payment_info = 0
            if insight.get('actions'):
                for action in insight['actions']:
                    action_type = action.get('action_type')
                    if action_type == 'purchase':
                        purchases = int(action.get('value', 0))
                    elif action_type == 'add_to_cart':
                        adds_to_cart = int(action.get('value', 0))
                    elif action_type == 'add_payment_info':
                        adds_payment_info = int(action.get('value', 0))
            
            # 提取购买价值
            purchases_value = 0
            if insight.get('action_values'):
                for action in insight['action_values']:
                    if action.get('action_type') == 'purchase':
                        purchases_value = float(action.get('value', 0))
                        break
            
            daily_data.append({
                'date': insight.get('date_start'),
                'spend': float(insight.get('spend', 0)),
                'purchases': purchases,
                'purchases_value': purchases_value,
                'adds_to_cart': adds_to_cart,
                'adds_payment_info': adds_payment_info
            })
        
        return daily_data
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
        reraise=True
    )
    def _fetch_purchases_total_insights(
        self,
        ad_account: AdAccount,
        start_date: str,
        end_date: str
    ) -> tuple:
        """获取总汇总购买数据（用于指标卡，支持自动重试）"""
        total_insights = ad_account.get_insights(
            fields=[
                'spend',
                'actions',
                'action_values',
                'purchase_roas'
            ],
            params={
                'level': 'account',
                'time_range': {
                    'since': start_date,
                    'until': end_date
                }
                # 不使用time_increment，获取整个期间的总汇总
            }
        )
        
        # 获取第一条（唯一一条）总汇总数据
        summary_data = None
        for item in total_insights:
            summary_data = item
            break
        
        if not summary_data:
            return (0, 0, 0, 0, 0, 0)
        
        # 提取actions数据
        purchases = 0
        adds_to_cart = 0
        adds_payment_info = 0
        if summary_data.get('actions'):
            for action in summary_data['actions']:
                action_type = action.get('action_type')
                if action_type == 'purchase':
                    purchases = int(action.get('value', 0))
                elif action_type == 'add_to_cart':
                    adds_to_cart = int(action.get('value', 0))
                elif action_type == 'add_payment_info':
                    adds_payment_info = int(action.get('value', 0))
        
        # 提取购买价值
        purchases_value = 0
        if summary_data.get('action_values'):
            for action in summary_data['action_values']:
                if action.get('action_type') == 'purchase':
                    purchases_value = float(action.get('value', 0))
                    break
        
        # 提取purchase_roas
        roas = 0
        if summary_data.get('purchase_roas'):
            for item in summary_data['purchase_roas']:
                if item.get('action_type') == 'omni_purchase':
                    roas = float(item.get('value', 0))
                    break
        
        # 返回原始数据，不进行四舍五入（用于环比计算）
        return (
            float(summary_data.get('spend', 0)),  # 原始spend
            purchases,
            purchases_value,  # 原始purchases_value
            adds_to_cart,
            adds_payment_info,
            roas  # 原始ROAS
        )
    
    @cached(prefix="facebook:purchases", ttl=settings.CACHE_TTL_MEDIUM)
    async def get_purchases_data_from_api(
        self,
        start_date: str,
        end_date: str,
        compare_start_date: str = None,
        compare_end_date: str = None,
        access_token: str = None,
        account_id: str = None
    ) -> Dict[str, Any]:
        """从Facebook API直接获取购买和花费数据（按天汇总，支持对比）- 已启用缓存"""
        try:
            # 设置代理（如果提供）
            self.setup_proxy()

            # 使用配置中的默认值
            final_access_token = access_token or settings.FACEBOOK_ACCESS_TOKEN
            final_account_id = account_id or settings.FACEBOOK_AD_ACCOUNT_ID
            
            # 确保account_id有act_前缀
            if not final_account_id.startswith('act_'):
                final_account_id = f'act_{final_account_id}'
            
            # 初始化Facebook API
            FacebookAdsApi.init(access_token=final_access_token)
            ad_account = AdAccount(final_account_id)
            
            # 获取当前日期范围的每日数据（用于图表）
            daily_data = self._fetch_purchases_daily_insights(ad_account, start_date, end_date)
            
            # 获取当前日期范围的总汇总数据（用于指标卡）
            (
                total_spend,
                total_purchases,
                total_purchases_value,
                total_adds_to_cart,
                total_adds_payment_info,
                total_roas
            ) = self._fetch_purchases_total_insights(ad_account, start_date, end_date)
            
            # 生成图表数据
            chart_data = generate_chart_data(daily_data, "date", FACEBOOK_PURCHASE_CHART_CONFIG)
            
            result = {
                "current": {
                    "spend": round(total_spend, 2),
                    "purchases": total_purchases,
                    "purchasesValue": round(total_purchases_value, 2),
                    "addsToCart": total_adds_to_cart,
                    "addsPaymentInfo": total_adds_payment_info,
                    "roas": round(total_roas, 2),  # 显示时才四舍五入
                    "chartData": chart_data
                }
            }
            
            # 如果有对比日期范围，获取对比数据
            if compare_start_date and compare_end_date:
                # 获取对比期间的每日数据
                compare_daily_data = self._fetch_purchases_daily_insights(ad_account, compare_start_date, compare_end_date)
                
                # 获取对比期间的总汇总数据
                (
                    compare_spend,
                    compare_purchases,
                    compare_purchases_value,
                    compare_adds_to_cart,
                    compare_adds_payment_info,
                    compare_roas
                ) = self._fetch_purchases_total_insights(ad_account, compare_start_date, compare_end_date)
                
                result["compare"] = {
                    "spend": round(compare_spend, 2),
                    "purchases": compare_purchases,
                    "purchasesValue": round(compare_purchases_value, 2),
                    "addsToCart": compare_adds_to_cart,
                    "addsPaymentInfo": compare_adds_payment_info,
                    "roas": compare_roas
                }
                
                # 计算变化百分比
                result["current"]["spendChange"] = round(safe_divide((total_spend - compare_spend) * 100, compare_spend, 0, 4), 2)
                result["current"]["purchasesChange"] = round(safe_divide((total_purchases - compare_purchases) * 100, compare_purchases, 0, 4), 2)
                result["current"]["purchasesValueChange"] = round(safe_divide((total_purchases_value - compare_purchases_value) * 100, compare_purchases_value, 0, 4), 2)
                result["current"]["addsToCartChange"] = round(safe_divide((total_adds_to_cart - compare_adds_to_cart) * 100, compare_adds_to_cart, 0, 4), 2)
                result["current"]["addsPaymentInfoChange"] = round(safe_divide((total_adds_payment_info - compare_adds_payment_info) * 100, compare_adds_payment_info, 0, 4), 2)
                result["current"]["roasChange"] = round(safe_divide((total_roas - compare_roas) * 100, compare_roas, 0, 4), 2)
                
                # 合并当前和对比的每日数据用于图表展示
                merged_daily_data = self._merge_purchases_comparison_data(daily_data, compare_daily_data)
                result["performanceComparisonData"] = merged_daily_data
            
            return result
            
        except Exception as e:
            raise Exception(f"从Facebook API获取购买数据失败: {str(e)}")
    
    @cached(prefix="facebook:overview", ttl=settings.CACHE_TTL_SHORT)
    async def get_overview_data_from_api(
        self,
        start_date: str,
        end_date: str,
        compare_start_date: str = None,
        compare_end_date: str = None,
        access_token: str = None,
        account_id: str = None
    ) -> Dict[str, Any]:
        """从Facebook API直接获取总览数据（包含impressions和purchases，支持对比）- 并行优化版 + 已启用缓存"""
        try:
            # 设置代理（如果提供）
            self.setup_proxy()

            # 使用配置中的默认值
            final_access_token = access_token or settings.FACEBOOK_ACCESS_TOKEN
            final_account_id = account_id or settings.FACEBOOK_AD_ACCOUNT_ID
            
            # 确保account_id有act_前缀
            if not final_account_id.startswith('act_'):
                final_account_id = f'act_{final_account_id}'
            
            # 初始化Facebook API
            FacebookAdsApi.init(access_token=final_access_token)
            ad_account = AdAccount(final_account_id)
            
            # ========== 使用线程池并行获取所有数据 ==========
            loop = asyncio.get_running_loop()
            executor = FACEBOOK_API_EXECUTOR

            # 提交所有当前期间的API请求
            futures = {
                'impressions_daily': loop.run_in_executor(executor, self._fetch_impressions_daily_insights, ad_account, start_date, end_date),
                'impressions_total': loop.run_in_executor(executor, self._fetch_impressions_total_insights, ad_account, start_date, end_date),
                'purchases_daily': loop.run_in_executor(executor, self._fetch_purchases_daily_insights, ad_account, start_date, end_date),
                'purchases_total': loop.run_in_executor(executor, self._fetch_purchases_total_insights, ad_account, start_date, end_date)
            }

            # 如果有对比日期，同时提交对比期间的请求
            if compare_start_date and compare_end_date:
                futures['compare_impressions_daily'] = loop.run_in_executor(
                    executor, self._fetch_impressions_daily_insights, ad_account, compare_start_date, compare_end_date
                )
                futures['compare_impressions_total'] = loop.run_in_executor(
                    executor, self._fetch_impressions_total_insights, ad_account, compare_start_date, compare_end_date
                )
                futures['compare_purchases_daily'] = loop.run_in_executor(
                    executor, self._fetch_purchases_daily_insights, ad_account, compare_start_date, compare_end_date
                )
                futures['compare_purchases_total'] = loop.run_in_executor(
                    executor, self._fetch_purchases_total_insights, ad_account, compare_start_date, compare_end_date
                )

            # 等待所有请求完成并获取结果
            future_keys = list(futures.keys())
            future_results = await asyncio.gather(*futures.values())
            results = dict(zip(future_keys, future_results))
            
            # 解包当前期间的结果
            impressions_daily_data = results['impressions_daily']
            (
                total_impressions,
                total_reach,
                total_clicks,
                total_unique_link_clicks,
                total_ctr,
                total_cpm
            ) = results['impressions_total']
            
            purchases_daily_data = results['purchases_daily']
            (
                total_spend,
                total_purchases,
                total_purchases_value,
                total_adds_to_cart,
                total_adds_payment_info,
                total_roas
            ) = results['purchases_total']
            
            # 生成图表数据
            impressions_chart_data = generate_chart_data(impressions_daily_data, "date", FACEBOOK_IMPRESSION_CHART_CONFIG)
            purchases_chart_data = generate_chart_data(purchases_daily_data, "date", FACEBOOK_PURCHASE_CHART_CONFIG)
            
            result = {
                "impressions": {
                    "impressions": total_impressions,
                    "reach": total_reach,
                    "clicks": total_clicks,
                    "uniqueLinkClicks": total_unique_link_clicks,
                    "ctr": round(total_ctr, 2),  # 显示时才四舍五入
                    "cpm": round(total_cpm, 2),  # 显示时才四舍五入
                    "chartData": impressions_chart_data
                },
                "purchases": {
                    "spend": round(total_spend, 2),  # 显示时才四舍五入
                    "purchases": total_purchases,
                    "purchasesValue": round(total_purchases_value, 2),  # 显示时才四舍五入
                    "addsToCart": total_adds_to_cart,
                    "addsPaymentInfo": total_adds_payment_info,
                    "roas": round(total_roas, 2),  # 显示时才四舍五入
                    "chartData": purchases_chart_data
                }
            }
            
            # 如果有对比日期范围，处理对比数据（已在线程池中并行获取）
            if compare_start_date and compare_end_date:
                # ========== Impressions对比数据 ==========
                # 从并行请求结果中获取数据
                compare_impressions_daily_data = results['compare_impressions_daily']
                (
                    compare_impressions,
                    compare_reach,
                    compare_clicks,
                    compare_unique_link_clicks,
                    compare_ctr,
                    compare_cpm
                ) = results['compare_impressions_total']
                
                # 计算变化百分比
                result["impressions"]["impressionsChange"] = round(safe_divide((total_impressions - compare_impressions) * 100, compare_impressions, 0, 4), 2)
                result["impressions"]["reachChange"] = round(safe_divide((total_reach - compare_reach) * 100, compare_reach, 0, 4), 2)
                result["impressions"]["clicksChange"] = round(safe_divide((total_clicks - compare_clicks) * 100, compare_clicks, 0, 4), 2)
                result["impressions"]["uniqueLinkClicksChange"] = round(safe_divide((total_unique_link_clicks - compare_unique_link_clicks) * 100, compare_unique_link_clicks, 0, 4), 2)
                result["impressions"]["ctrChange"] = round(safe_divide((total_ctr - compare_ctr) * 100, compare_ctr, 0, 4), 2)
                result["impressions"]["cpmChange"] = round(safe_divide((total_cpm - compare_cpm) * 100, compare_cpm, 0, 4), 2)
                
                # 合并impressions每日数据
                merged_impressions_daily = self._merge_comparison_data(impressions_daily_data, compare_impressions_daily_data)
                result["impressions"]["performanceComparisonData"] = merged_impressions_daily
                
                # ========== Purchases对比数据 ==========
                # 从并行请求结果中获取数据
                compare_purchases_daily_data = results['compare_purchases_daily']
                (
                    compare_spend,
                    compare_purchases,
                    compare_purchases_value,
                    compare_adds_to_cart,
                    compare_adds_payment_info,
                    compare_roas
                ) = results['compare_purchases_total']
                
                # 计算变化百分比
                result["purchases"]["spendChange"] = round(safe_divide((total_spend - compare_spend) * 100, compare_spend, 0, 4), 2)
                result["purchases"]["purchasesChange"] = round(safe_divide((total_purchases - compare_purchases) * 100, compare_purchases, 0, 4), 2)
                result["purchases"]["purchasesValueChange"] = round(safe_divide((total_purchases_value - compare_purchases_value) * 100, compare_purchases_value, 0, 4), 2)
                result["purchases"]["addsToCartChange"] = round(safe_divide((total_adds_to_cart - compare_adds_to_cart) * 100, compare_adds_to_cart, 0, 4), 2)
                result["purchases"]["addsPaymentInfoChange"] = round(safe_divide((total_adds_payment_info - compare_adds_payment_info) * 100, compare_adds_payment_info, 0, 4), 2)
                result["purchases"]["roasChange"] = round(safe_divide((total_roas - compare_roas) * 100, compare_roas, 0, 4), 2)
                
                # 合并purchases每日数据
                merged_purchases_daily = self._merge_purchases_comparison_data(purchases_daily_data, compare_purchases_daily_data)
                result["purchases"]["performanceComparisonData"] = merged_purchases_daily
            
            return result
            
        except Exception as e:
            raise Exception(f"从Facebook API获取总览数据失败: {str(e)}")
