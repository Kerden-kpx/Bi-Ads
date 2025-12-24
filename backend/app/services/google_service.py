"""
Google Ads Dashboard业务逻辑服务（优化版，支持缓存）
"""
from typing import Dict, Any, List
from sqlalchemy import text

from app.services.base_service import BaseDashboardService
from app.services.data_parser_config import get_parse_config
from app.utils.chart_helpers import generate_chart_data, GOOGLE_IMPRESSION_CHART_CONFIG, GOOGLE_CONVERSION_CHART_CONFIG
from app.utils.helpers import safe_divide
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
                SUM(Clicks) AS clicks,
                SUM(Clicks) / NULLIF(SUM(impression), 0) AS ctr,
                AVG(Cost / NULLIF(impression, 0) * 1000) AS cpm
            FROM google_ads
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
                SUM(Conversion_value) AS conversion_value,
                SUM(Cost) AS cost,
                SUM(Conversions) AS conversions,
                IFNULL(SUM(Conversion_value) / NULLIF(SUM(Cost), 0), 0) AS roas
            FROM google_ads
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
                    SUM(Clicks) AS clicks,
                    SUM(Conversions) AS conversions,
                    SUM(Conversion_value) AS conversion_value,
                    SUM(cost) AS cost
                FROM google_ads
                WHERE createtime BETWEEN :start_time1 AND :end_time1
                GROUP BY createtime
            ),
            data_compare AS (
                SELECT
                    createtime,
                    ROW_NUMBER() OVER (ORDER BY createtime) AS compare_seq,
                    SUM(impression) AS compare_impression,
                    SUM(Clicks) AS compare_clicks,
                    SUM(Conversions) AS compare_conversions,
                    SUM(Conversion_value) AS compare_conversion_value,
                    SUM(cost) AS compare_cost
                FROM google_ads
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
                FROM google_ads
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
                FROM google_ads
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
        from app.core.config import settings
        
        # 使用 Google Ads 专用的产品名称配置
        product_pattern = settings.GOOGLE_PRODUCT_NAMES_PATTERN
        product_list = settings.GOOGLE_PRODUCT_NAMES_LIST
        
        # 动态构建CASE WHEN语句
        case_statements = []
        for product in product_list:
            # 处理特殊情况（如黑曜石可能有多个变体）
            if product == "黑曜石OMT":
                case_statements.append(f"WHEN campaign REGEXP '黑曜石OMT' THEN '黑曜石OMT'")
            else:
                case_statements.append(f"WHEN campaign REGEXP '{product}' THEN '{product}'")
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
                Conversions, Cost, Conversion_value, createtime
              FROM google_ads, date_range
              WHERE campaign REGEXP '{product_pattern}'
            ),
            current_week_data AS (
              SELECT
                campaign_id, campaign_name,
                SUM(Conversions) AS Conversions,
                SUM(Conversion_value) AS Conversion_value,
                SUM(Cost) AS Cost,
                IFNULL(SUM(Conversion_value) / NULLIF(SUM(Cost), 0), 0) AS roas
              FROM data_detail, date_range
              WHERE createtime BETWEEN current_week_start AND current_week_end
              GROUP BY campaign_id, campaign_name
            ),
            last_week_data AS (
              SELECT
                campaign_id, campaign_name,
                SUM(Conversions) AS Conversions,
                SUM(Conversion_value) AS Conversion_value,
                SUM(Cost) AS Cost,
                IFNULL(SUM(Conversion_value) / NULLIF(SUM(Cost), 0), 0) AS roas
              FROM data_detail, date_range
              WHERE createtime BETWEEN last_week_start AND last_week_end
              GROUP BY campaign_id, campaign_name
            )
            SELECT
                temp.campaign_name,
                SUM(last_Conversions) AS last_Conversions,
                SUM(last_Conversion_value) AS last_Conversion_value,
                SUM(last_Cost) AS last_Cost,
                SUM(last_Conversion_value) / SUM(last_Cost) AS last_roas,
                SUM(current_Conversions) AS current_Conversions,
                SUM(current_Conversion_value) AS current_Conversion_value,
                SUM(current_Cost) AS current_Cost,
                SUM(current_conversion_value) / SUM(current_cost) AS current_roas
            FROM (
                SELECT
                    L.campaign_name,
                    L.Conversions AS last_Conversions,
                    L.Conversion_value AS last_Conversion_value,
                    L.Cost AS last_Cost,
                    C.Conversions AS current_Conversions,
                    C.Conversion_value AS current_Conversion_value,
                    C.Cost AS current_Cost
                FROM last_week_data L
                LEFT JOIN current_week_data C ON L.campaign_id = C.campaign_id
            ) temp
            GROUP BY temp.campaign_name
        """)
        
        rows = await self.execute_query(query, {"variable_time": variable_date})
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
