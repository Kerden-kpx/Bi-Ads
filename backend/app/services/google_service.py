"""
Google Ads Dashboard业务逻辑服务（优化版，支持缓存）
"""
from typing import Dict, Any, List
from sqlalchemy import text

from app.services.base_service import BaseDashboardService
from app.services.data_parser_config import get_parse_config
from app.utils.chart_helpers import generate_chart_data, GOOGLE_IMPRESSION_CHART_CONFIG, GOOGLE_CONVERSION_CHART_CONFIG
from app.utils.helpers import build_mysql_regex_union, escape_mysql_regex_literal, safe_divide
from app.core.cache import cached
from app.core.config import settings


class GoogleDashboardService(BaseDashboardService):
    """Google Dashboard服务类 - 继承基础服务"""
    
    def __init__(self, db):
        super().__init__(db, platform="google")
    
    @cached(prefix="google:impressions", ttl=settings.CACHE_TTL_MEDIUM)
    async def get_impressions_data(
        self,
        start_date: str,
        end_date: str,
        compare_start_date: str = None,
        compare_end_date: str = None
    ) -> Dict[str, Any]:
        """获取印象和点击数据 - 已启用缓存"""
        
        query = text("""
            SELECT
                createtime,
                SUM(impression) AS impressions,
                SUM(clicks) AS clicks,
                SUM(clicks) / NULLIF(SUM(impression), 0) AS ctr,
                AVG(cost / NULLIF(impression, 0) * 1000) AS cpm
            FROM fact_bi_ads_google_campaign
            WHERE createtime BETWEEN :start_date AND :end_date
            GROUP BY createtime
            ORDER BY createtime
        """)
        
        # 执行查询
        current_rows = await self.execute_query(query, {"start_date": start_date, "end_date": end_date})
        current_data = [self._parse_impression_row(row) for row in current_rows]
        
        # 生成图表数据
        chart_data = generate_chart_data(current_data, "date", GOOGLE_IMPRESSION_CHART_CONFIG)
        
        # 处理数据
        result = self.process_comparison_data(
            current_data=current_data,
            compare_data=None,
            aggregate_fields=["impressions", "clicks"],
            average_fields=["ctr", "cpm"],
            change_mapping={
                "impressions": "impressionsChange",
                "clicks": "clicksChange",
                "ctr": "ctrChange",
                "cpm": "cpmChange"
            }
        )
        
        # 处理对比数据
        if compare_start_date and compare_end_date:
            compare_rows = await self.execute_query(query, {"start_date": compare_start_date, "end_date": compare_end_date})
            compare_data = [self._parse_impression_row(row) for row in compare_rows]
            
            result = self.process_comparison_data(
                current_data=current_data,
                compare_data=compare_data,
                aggregate_fields=["impressions", "clicks"],
                average_fields=["ctr", "cpm"],
                change_mapping={
                    "impressions": "impressionsChange",
                    "clicks": "clicksChange",
                    "ctr": "ctrChange",
                    "cpm": "cpmChange"
                }
            )
        
        # 添加Google特有字段和图表数据
        result["current"]["reach"] = 0
        result["current"]["uniqueLinkClicks"] = 0
        result["current"]["reachChange"] = 0
        result["current"]["uniqueLinkClicksChange"] = 0
        result["current"]["chartData"] = chart_data
        
        if "compare" in result:
            result["compare"]["reach"] = 0
            result["compare"]["uniqueLinkClicks"] = 0
        
        return result
    
    @cached(prefix="google:conversions", ttl=settings.CACHE_TTL_MEDIUM)
    async def get_purchases_data(
        self,
        start_date: str,
        end_date: str,
        compare_start_date: str = None,
        compare_end_date: str = None
    ) -> Dict[str, Any]:
        """获取转化和成本数据 - 已启用缓存"""
        
        query = text("""
            SELECT
                createtime,
                SUM(conversion_value) AS conversion_value,
                SUM(cost) AS cost,
                SUM(conversions) AS conversions,
                IFNULL(SUM(conversion_value) / NULLIF(SUM(cost), 0), 0) AS roas
            FROM fact_bi_ads_google_campaign
            WHERE createtime BETWEEN :start_date AND :end_date
            GROUP BY createtime
        """)
        
        # 执行查询
        current_rows = await self.execute_query(query, {"start_date": start_date, "end_date": end_date})
        current_data = [self._parse_conversion_row(row) for row in current_rows]
        
        # 生成图表数据
        chart_data = generate_chart_data(current_data, "date", GOOGLE_CONVERSION_CHART_CONFIG)
        
        # 处理数据
        result = self.process_comparison_data(
            current_data=current_data,
            compare_data=None,
            aggregate_fields=["conversion_value", "cost", "conversions"],
            average_fields=[],
            change_mapping={
                "conversion_value": "purchasesValueChange",
                "cost": "spendChange",
                "conversions": "purchasesChange",
                "roas": "roasChange"
            }
        )
        
        # 重新计算总ROAS
        total_value = result["current"]["conversion_value"]
        total_cost = result["current"]["cost"]
        result["current"]["roas"] = safe_divide(total_value, total_cost, 0, 2)
        
        # 处理对比数据
        if compare_start_date and compare_end_date:
            compare_rows = await self.execute_query(query, {"start_date": compare_start_date, "end_date": compare_end_date})
            compare_data = [self._parse_conversion_row(row) for row in compare_rows]
            
            result = self.process_comparison_data(
                current_data=current_data,
                compare_data=compare_data,
                aggregate_fields=["conversion_value", "cost", "conversions"],
                average_fields=[],
                change_mapping={
                    "conversion_value": "purchasesValueChange",
                    "cost": "spendChange",
                    "conversions": "purchasesChange",
                    "roas": "roasChange"
                }
            )
            
            # 重新计算ROAS
            result["current"]["roas"] = safe_divide(result["current"]["conversion_value"], result["current"]["cost"], 0, 2)
            result["compare"]["roas"] = safe_divide(result["compare"]["conversion_value"], result["compare"]["cost"], 0, 2)
        
        # 转换字段名以匹配前端
        result["current"]["purchasesValue"] = result["current"].pop("conversion_value")
        result["current"]["spend"] = result["current"].pop("cost")
        result["current"]["purchases"] = result["current"].pop("conversions")
        result["current"]["addsToCart"] = 0
        result["current"]["addsPaymentInfo"] = 0
        result["current"]["addsToCartChange"] = 0
        result["current"]["addsPaymentInfoChange"] = 0
        result["current"]["chartData"] = chart_data
        
        if "compare" in result:
            result["compare"]["purchasesValue"] = result["compare"].pop("conversion_value")
            result["compare"]["spend"] = result["compare"].pop("cost")
            result["compare"]["purchases"] = result["compare"].pop("conversions")
            result["compare"]["addsToCart"] = 0
            result["compare"]["addsPaymentInfo"] = 0
        
        return result
    
    
    @cached(prefix="google:performance", ttl=settings.CACHE_TTL_LONG)
    async def get_performance_comparison(
        self,
        start_time1: str,
        end_time1: str,
        start_time2: str,
        end_time2: str
    ) -> List[Dict[str, Any]]:
        """获取性能对比数据（用于面积图）- 已启用缓存"""
        
        query = text("""
            WITH date_current AS (
                SELECT
                    createtime,
                    ROW_NUMBER() OVER (ORDER BY createtime) AS current_seq,
                    SUM(impression) AS impression,
                    SUM(clicks) AS clicks,
                    SUM(conversions) AS conversions,
                    SUM(conversion_value) AS conversion_value,
                    SUM(cost) AS cost
                FROM fact_bi_ads_google_campaign
                WHERE createtime BETWEEN :start_time1 AND :end_time1
                GROUP BY createtime
            ),
            data_compare AS (
                SELECT
                    createtime,
                    ROW_NUMBER() OVER (ORDER BY createtime) AS compare_seq,
                    SUM(impression) AS compare_impression,
                    SUM(clicks) AS compare_clicks,
                    SUM(conversions) AS compare_conversions,
                    SUM(conversion_value) AS compare_conversion_value,
                    SUM(cost) AS compare_cost
                FROM fact_bi_ads_google_campaign
                WHERE createtime BETWEEN :start_time2 AND :end_time2
                GROUP BY createtime
            )
            SELECT
                A.createtime AS createtime,
                A.impression,
                IFNULL(B.compare_impression, 0) AS compare_impression,
                A.clicks,
                IFNULL(B.compare_clicks, 0) AS compare_clicks,
                A.conversions,
                IFNULL(B.compare_conversions, 0) AS compare_conversions,
                A.conversion_value,
                IFNULL(B.compare_conversion_value, 0) AS compare_conversion_value,
                A.cost,
                IFNULL(B.compare_cost, 0) AS compare_cost
            FROM date_current A
            LEFT JOIN data_compare B ON A.current_seq = B.compare_seq
        """)
        
        rows = await self.execute_query(query, {
            "start_time1": start_time1,
            "end_time1": end_time1,
            "start_time2": start_time2,
            "end_time2": end_time2
        })
        
        return [self._parse_performance_comparison_row(row) for row in rows]
    
    @cached(prefix="google:campaigns", ttl=settings.CACHE_TTL_LONG)
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
                    campaign_id, campaign,
                    SUM(impression) AS impression,
                    SUM(cost) AS cost,
                    SUM(clicks) AS clicks,
                    SUM(conversions) AS conversions,
                    SUM(conversion_value) AS conversion_value
                FROM fact_bi_ads_google_campaign
                WHERE createtime BETWEEN :start_time1 AND :end_time1
                GROUP BY campaign_id, campaign
            ),
            date_compare AS (
                SELECT
                    campaign_id,
                    SUM(impression) AS impression,
                    SUM(cost) AS cost,
                    SUM(clicks) AS clicks,
                    SUM(conversions) AS conversions,
                    SUM(conversion_value) AS conversion_value
                FROM fact_bi_ads_google_campaign
                WHERE createtime BETWEEN :start_time2 AND :end_time2
                GROUP BY campaign_id
            )
            SELECT
                A.campaign_id, A.campaign,
                A.impression, A.cost, A.clicks, A.conversions, A.conversion_value,
                A.conversion_value / A.cost AS roas,
                A.clicks / A.impression AS ctr,
                A.cost / A.clicks AS cpc,
                B.impression AS compare_impression,
                B.cost AS compare_cost,
                B.clicks AS compare_clicks,
                B.conversions AS compare_conversions,
                B.conversion_value AS compare_conversion_value,
                B.conversion_value / B.cost AS compare_roas,
                B.clicks / B.impression AS compare_ctr,
                B.cost / B.clicks AS compare_cpc
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
    
    @cached(prefix="google:ads_performance", ttl=settings.CACHE_TTL_LONG)
    async def get_ads_performance_overview(self, variable_date: str) -> List[Dict[str, Any]]:
        """获取Ads Performance Overview数据（产品表现）- 已启用缓存"""
        product_list = [name.strip() for name in settings.GOOGLE_PRODUCT_NAMES_LIST if name and name.strip()]
        if not product_list:
            return []

        params = {
            "variable_time": variable_date,
            "product_pattern": build_mysql_regex_union(product_list),
        }

        # 动态构建CASE WHEN语句（使用参数绑定，避免字符串拼接注入）
        case_statements = []
        for idx, product in enumerate(product_list):
            regex_key = f"campaign_regex_{idx}"
            label_key = f"campaign_label_{idx}"
            params[regex_key] = escape_mysql_regex_literal(product)
            params[label_key] = product
            case_statements.append(f"WHEN campaign REGEXP :{regex_key} THEN :{label_key}")

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
                  ELSE campaign
                END AS campaign_name,
                conversions, cost, conversion_value, createtime
              FROM fact_bi_ads_google_campaign, date_range
              WHERE campaign REGEXP :product_pattern
            ),
            current_week_data AS (
              SELECT
                campaign_id, campaign_name,
                SUM(conversions) AS conversions,
                SUM(conversion_value) AS conversion_value,
                SUM(cost) AS cost,
                IFNULL(SUM(conversion_value) / NULLIF(SUM(cost), 0), 0) AS roas
              FROM data_detail, date_range
              WHERE createtime BETWEEN current_week_start AND current_week_end
              GROUP BY campaign_id, campaign_name
            ),
            last_week_data AS (
              SELECT
                campaign_id, campaign_name,
                SUM(conversions) AS conversions,
                SUM(conversion_value) AS conversion_value,
                SUM(cost) AS cost,
                IFNULL(SUM(conversion_value) / NULLIF(SUM(cost), 0), 0) AS roas
              FROM data_detail, date_range
              WHERE createtime BETWEEN last_week_start AND last_week_end
              GROUP BY campaign_id, campaign_name
            )
            SELECT
                temp.campaign_name,
                SUM(last_conversions) AS last_conversions,
                SUM(last_conversion_value) AS last_conversion_value,
                SUM(last_cost) AS last_cost,
                SUM(last_conversion_value) / SUM(last_cost) AS last_roas,
                SUM(current_conversions) AS current_conversions,
                SUM(current_conversion_value) AS current_conversion_value,
                SUM(current_cost) AS current_cost,
                SUM(current_conversion_value) / SUM(current_cost) AS current_roas
            FROM (
                SELECT
                    L.campaign_name,
                    L.conversions AS last_conversions,
                    L.conversion_value AS last_conversion_value,
                    L.cost AS last_cost,
                    C.conversions AS current_conversions,
                    C.conversion_value AS current_conversion_value,
                    C.cost AS current_cost
                FROM last_week_data L
                LEFT JOIN current_week_data C ON L.campaign_id = C.campaign_id
            ) temp
            GROUP BY temp.campaign_name
        """)

        rows = await self.execute_query(query, params)
        return [self._parse_ads_performance_row(row) for row in rows]
    
    # ==================== 辅助方法 - 使用配置驱动解析 ====================
    
    def _parse_impression_row(self, row) -> Dict[str, Any]:
        """解析印象数据行"""
        result = self.parse_row_with_mapping(row, get_parse_config('google', 'impression'))
        # Google的CTR需要转换为百分比
        result["ctr"] = round(result["ctr"] * 100, 2)
        return result
    
    def _parse_conversion_row(self, row) -> Dict[str, Any]:
        """解析转化数据行"""
        return self.parse_row_with_mapping(row, get_parse_config('google', 'conversion'))
    
    def _parse_performance_comparison_row(self, row) -> Dict[str, Any]:
        """解析性能对比数据行"""
        return self.parse_row_with_mapping(row, get_parse_config('google', 'performance_comparison'))
    
    def _parse_campaign_performance_row(self, row) -> Dict[str, Any]:
        """解析Campaign性能数据行"""
        result = self.parse_row_with_mapping(row, get_parse_config('google', 'campaign_performance'))
        
        # 解析对比字段（动态处理）
        compare_fields = {
            'compare_impression': 'int', 'compare_clicks': 'int',
            'compare_cost': 'float', 'compare_conversions': 'float',
            'compare_conversion_value': 'float', 'compare_roas': 'float',
            'compare_cpc': 'float', 'compare_ctr': 'float'
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
        return self.parse_row_with_mapping(row, get_parse_config('google', 'ads_performance'))
