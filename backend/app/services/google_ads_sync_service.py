"""
Google Ads API 数据同步服务
用于从 Google Ads API 获取数据并同步到数据库
优化版本：支持并发处理、批量操作、自动重试、响应缓存
"""
import os
import time
import hashlib
import atexit
from threading import Lock
from typing import List, Tuple, Optional, Dict, Any
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from sqlalchemy.orm import Session
from sqlalchemy import text
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.services.base_sync_service import BaseSyncService
from app.core.config import settings

_executor_cache: Dict[int, ThreadPoolExecutor] = {}
_executor_lock = Lock()


def _get_thread_pool(requested_workers: int, limit: Optional[int] = None) -> ThreadPoolExecutor:
    """
    获取或创建指定大小的线程池（复用实例，避免频繁创建销毁）
    """
    max_allowed = limit or settings.GOOGLE_ADS_MAX_WORKERS
    worker_count = max(1, min(requested_workers, max_allowed))

    with _executor_lock:
        executor = _executor_cache.get(worker_count)
        if executor is None:
            executor = ThreadPoolExecutor(max_workers=worker_count)
            _executor_cache[worker_count] = executor
    return executor


def _shutdown_thread_pools():
    with _executor_lock:
        for executor in _executor_cache.values():
            executor.shutdown(wait=False)
        _executor_cache.clear()


atexit.register(_shutdown_thread_pools)


class GoogleAdsDataSyncService(BaseSyncService):
    """Google Ads 数据同步服务"""
    
    # 类级别的内存缓存
    _cache = {}
    _cache_ttl = {}  # 缓存过期时间
    CACHE_DURATION = 300  # 缓存5分钟
    
    def __init__(self, db: Session, config_path: str = None):
        """
        初始化服务
        
        Args:
            db: 数据库会话
            config_path: Google Ads 配置文件路径（默认从配置读取）
        """
        super().__init__(db, "fact_bi_ads_google_campaign")
        
        # 从配置读取路径，支持相对路径和绝对路径
        if config_path:
            self.config_path = config_path
        else:
            # 从环境变量读取配置路径
            config_path_from_env = settings.GOOGLE_ADS_CONFIG_PATH
            # 如果是相对路径，转换为绝对路径（相对于项目根目录）
            if not os.path.isabs(config_path_from_env):
                # 获取项目根目录（backend目录）
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                self.config_path = os.path.join(project_root, config_path_from_env)
            else:
                self.config_path = config_path_from_env
        
        self.client = None
        
    def setup_proxy(self, proxy_url: str = None):
        """设置代理环境变量"""
        # 从配置读取代理地址
        if proxy_url is None:
            proxy_url = settings.GOOGLE_ADS_PROXY_URL_EFFECTIVE
        
        if proxy_url:
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
            os.environ['http_proxy'] = proxy_url
            os.environ['https_proxy'] = proxy_url
            print(f"🔧 已设置代理: {proxy_url}")
        else:
            print("⚠️  未设置代理")
    
    def initialize_client(self):
        """
        初始化 Google Ads 客户端
        使用简单直接的加载方式（已验证可工作）
        """
        try:
            # 切换到配置文件所在目录（关键！）
            original_dir = os.getcwd()
            config_dir = os.path.dirname(os.path.abspath(self.config_path))
            config_filename = os.path.basename(self.config_path)
            
            print(f"📂 切换到配置目录: {config_dir}")
            os.chdir(config_dir)
            
            try:
                # 使用简单的文件名加载（与成功的脚本一致）
                self.client = GoogleAdsClient.load_from_storage(config_filename)
                print("✅ Google Ads 客户端初始化成功")
                return True
            finally:
                # 恢复原始工作目录
                os.chdir(original_dir)
                
        except Exception as e:
            print(f"❌ 初始化 Google Ads 客户端失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_date_list(self, start_date: str, end_date: str) -> List[str]:
        """生成日期范围内的所有日期列表"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        date_list = []
        current = start
        while current <= end:
            date_list.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        return date_list
    
    def _fetch_single_date_data(
        self,
        customer_id: str,
        date: str
    ) -> Tuple[bool, List[Tuple], str]:
        """
        获取单个日期的数据（用于并发处理）
        
        Args:
            customer_id: Google Ads 客户ID
            date: 日期
            
        Returns:
            (成功标志, 数据列表, 错误信息)
        """
        if not self.client:
            return False, [], "客户端未初始化"
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # SQL查询语句（单日）
            query = f"""
                SELECT campaign.id,
                       campaign.name,
                       metrics.impressions,
                       metrics.conversions,
                       metrics.cost_micros,
                       metrics.clicks,
                       metrics.conversions_value,
                       segments.date
                FROM campaign
                WHERE segments.date = '{date}'
            """
            
            # 执行查询
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            ads_data = []
            
            # 解析查询结果
            for batch in stream:
                for row in batch.results:
                    campaign = row.campaign
                    metrics = row.metrics
                    segments = row.segments
                    
                    # 转化次数保留两位小数
                    conversions = round(metrics.conversions, 2)
                    # 转化价值保留两位小数
                    conversions_value = round(metrics.conversions_value, 2)
                    # 费用除以10的六次方,保留两位小数
                    cost = round(float(metrics.cost_micros) / 1000000, 2)
                    
                    # 将数据存储到列表中
                    ads_data.append((
                        campaign.id,
                        campaign.name,
                        metrics.impressions,
                        conversions,
                        cost,
                        metrics.clicks,
                        conversions_value,
                        segments.date
                    ))
            
            return True, ads_data, ""
            
        except Exception as e:
            error_msg = f"获取 {date} 数据失败: {str(e)}"
            return False, [], error_msg
    
    def _generate_cache_key(self, customer_id: str, start_date: str, end_date: str, data_type: str = "summary") -> str:
        """生成缓存键"""
        key_string = f"{customer_id}:{start_date}:{end_date}:{data_type}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Tuple[Dict, List]]:
        """从缓存获取数据"""
        if cache_key in self._cache:
            # 检查缓存是否过期
            if time.time() < self._cache_ttl.get(cache_key, 0):
                print(f"🎯 从缓存获取数据: {cache_key[:8]}...")
                return self._cache[cache_key]
            else:
                # 清除过期缓存
                del self._cache[cache_key]
                if cache_key in self._cache_ttl:
                    del self._cache_ttl[cache_key]
        return None
    
    def _set_to_cache(self, cache_key: str, data: Tuple[Dict, List]):
        """设置缓存"""
        self._cache[cache_key] = data
        self._cache_ttl[cache_key] = time.time() + self.CACHE_DURATION
        print(f"💾 数据已缓存: {cache_key[:8]}... (TTL: {self.CACHE_DURATION}秒)")
    
    @retry(
        stop=stop_after_attempt(3),  # 最多重试3次
        wait=wait_exponential(multiplier=1, min=2, max=10),  # 指数退避：2s, 4s, 8s
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),  # 重试这些错误
        reraise=True  # 最终失败时抛出原始异常
    )
    def _fetch_summary_data(self, customer_id: str, start_date: str, end_date: str) -> Tuple[Dict, List]:
        """获取单个时间段的汇总和每日数据（线程安全，支持自动重试，带缓存）"""
        # 检查缓存
        cache_key = self._generate_cache_key(customer_id, start_date, end_date, "summary")
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # 每个线程获取自己的服务实例以保证线程安全
        ga_service = self.client.get_service("GoogleAdsService")
        
        # 汇总查询
        summary_query = f"""
            SELECT 
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.cost_micros,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion
            FROM customer
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        """
        
        # 每日数据查询
        daily_query = f"""
            SELECT 
                segments.date,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.cost_micros
            FROM customer
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY segments.date
        """
        
        summary_response = ga_service.search(customer_id=customer_id, query=summary_query)
        daily_response = ga_service.search(customer_id=customer_id, query=daily_query)
        
        # 解析汇总数据
        summary = {}
        for row in summary_response:
            metrics = row.metrics
            summary = {
                "impressions": metrics.impressions,
                "clicks": metrics.clicks,
                "conversions": metrics.conversions,
                "conversions_value": metrics.conversions_value,
                "cost": float(metrics.cost_micros) / 1000000,
                "ctr": metrics.ctr * 100,
                "average_cpc": float(metrics.average_cpc) / 1000000,
                "cost_per_conversion": float(metrics.cost_per_conversion) / 1000000 if metrics.cost_per_conversion > 0 else 0
            }
        
        # 解析每日数据
        daily_data = []
        for row in daily_response:
            segments = row.segments
            metrics = row.metrics
            daily_data.append({
                "date": segments.date,
                "impressions": metrics.impressions,
                "clicks": metrics.clicks,
                "conversions": metrics.conversions,
                "conversions_value": metrics.conversions_value,
                "cost": float(metrics.cost_micros) / 1000000
            })
        
        # 缓存结果
        result = (summary, daily_data)
        self._set_to_cache(cache_key, result)
        
        return result
    
    def fetch_overview_summary(
        self, 
        customer_id: str, 
        start_date: str,
        end_date: str,
        compare_start_date: Optional[str] = None,
        compare_end_date: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        从 Google Ads API 获取概览汇总数据（并发执行，提升速度）
        用于 Top Funnel Overview 和 Conversion Value & Cost Overview
        
        Args:
            customer_id: Google Ads 客户ID
            start_date: 开始日期
            end_date: 结束日期
            compare_start_date: 对比开始日期（可选）
            compare_end_date: 对比结束日期（可选）
            
        Returns:
            (成功标志, 汇总数据字典, 错误信息)
        """
        if not self.client:
            return False, {}, "客户端未初始化"
        
        try:
            import time
            start_time = time.time()
            
            # 检查完整请求的缓存（包含对比期）
            full_cache_key = self._generate_cache_key(
                customer_id, 
                f"{start_date}:{end_date}:{compare_start_date}:{compare_end_date}",
                "",
                "overview"
            )
            cached_full_data = self._get_from_cache(full_cache_key)
            if cached_full_data:
                elapsed = time.time() - start_time
                print(f"⚡ 从缓存获取完整概览数据，耗时: {elapsed:.2f}秒")
                return True, cached_full_data[0], ""
            
            # 使用并发执行提升速度（受配置限制的线程池）
            
            # 初始化汇总数据
            summary_data = {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0.0,
                "conversions_value": 0.0,
                "cost": 0.0,
                "ctr": 0.0,
                "average_cpc": 0.0,
                "cost_per_conversion": 0.0,
                "daily_data": [],
                # 对比期数据
                "compare_impressions": 0,
                "compare_clicks": 0,
                "compare_conversions": 0.0,
                "compare_conversions_value": 0.0,
                "compare_cost": 0.0,
                "compare_ctr": 0.0,
                "compare_average_cpc": 0.0,
                "compare_cost_per_conversion": 0.0,
                "compare_daily_data": []
            }
            
            # 并发执行查询（线程安全，复用线程池以减少开销）
            executor = _get_thread_pool(4, settings.GOOGLE_ADS_SUMMARY_MAX_WORKERS)
            
            # 提交当前期数据获取任务
            future_current = executor.submit(
                self._fetch_summary_data,
                customer_id,
                start_date,
                end_date
            )
            
            # 如果有对比期，提交对比期数据获取任务
            future_compare = None
            if compare_start_date and compare_end_date:
                future_compare = executor.submit(
                    self._fetch_summary_data,
                    customer_id,
                    compare_start_date,
                    compare_end_date
                )
            
            # 获取当前期数据
            current_summary, current_daily = future_current.result()
            summary_data.update(current_summary)
            summary_data["daily_data"] = current_daily
            
            # 获取对比期数据
            if future_compare:
                compare_summary, compare_daily = future_compare.result()
                summary_data["compare_impressions"] = compare_summary.get("impressions", 0)
                summary_data["compare_clicks"] = compare_summary.get("clicks", 0)
                summary_data["compare_conversions"] = compare_summary.get("conversions", 0)
                summary_data["compare_conversions_value"] = compare_summary.get("conversions_value", 0)
                summary_data["compare_cost"] = compare_summary.get("cost", 0)
                summary_data["compare_ctr"] = compare_summary.get("ctr", 0)
                summary_data["compare_average_cpc"] = compare_summary.get("average_cpc", 0)
                summary_data["compare_cost_per_conversion"] = compare_summary.get("cost_per_conversion", 0)
                summary_data["compare_daily_data"] = compare_daily
            
            elapsed = time.time() - start_time
            
            print(f"\n📊 概览汇总数据 ({start_date} 至 {end_date}):")
            print(f"   展示次数: {summary_data['impressions']:,}")
            print(f"   点击次数: {summary_data['clicks']:,}")
            print(f"   点击率: {summary_data['ctr']:.2f}%")
            print(f"   转化次数: {summary_data['conversions']:,}")
            print(f"   转化价值: ${summary_data['conversions_value']:,.2f}")
            print(f"   总成本: ${summary_data['cost']:,.2f}")
            print(f"   平均CPC: ${summary_data['average_cpc']:.2f}")
            print(f"   每日数据点: {len(summary_data['daily_data'])} 天")
            print(f"   ⚡ API请求耗时: {elapsed:.2f}秒")
            
            if compare_start_date and compare_end_date:
                print(f"\n📊 对比期数据 ({compare_start_date} 至 {compare_end_date}):")
                print(f"   展示次数: {summary_data['compare_impressions']:,}")
                print(f"   点击次数: {summary_data['compare_clicks']:,}")
                print(f"   对比期数据点: {len(summary_data['compare_daily_data'])} 天")
            
            # 缓存完整结果
            self._set_to_cache(full_cache_key, (summary_data, []))
            
            return True, summary_data, ""
            
        except GoogleAdsException as ex:
            print(f"❌ Google Ads API 错误:")
            error_msg = ""
            for error in ex.failure.errors:
                print(f"   错误代码: {error.error_code.name}")
                print(f"   错误信息: {error.message}")
                error_msg += f"错误代码: {error.error_code.name}, 错误信息: {error.message}\n"
            return False, {}, error_msg
            
        except Exception as e:
            error_msg = f"获取概览汇总数据时出错: {str(e)}"
            print(f"❌ {error_msg}")
            return False, {}, error_msg
    
    def fetch_campaigns_data(
        self, 
        customer_id: str, 
        start_date: str,
        end_date: str
    ) -> Tuple[bool, List[Tuple], str]:
        """
        从 Google Ads API 获取广告系列数据（串行版本，保留用于兼容）
        
        Args:
            customer_id: Google Ads 客户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            (成功标志, 数据列表, 错误信息)
        """
        if not self.client:
            return False, [], "客户端未初始化"
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # SQL查询语句
            query = f"""
                SELECT campaign.id,              --广告系列ID
                       campaign.name,            --广告系列名称
                       metrics.impressions,      --展示次数
                       metrics.conversions,      --转化次数
                       metrics.cost_micros,      --费用
                       metrics.clicks,           --点击次数
                       metrics.conversions_value,--转化价值 
                       segments.date             -- 日期
                FROM campaign
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            # 执行查询
            stream = ga_service.search_stream(customer_id=customer_id, query=query)
            
            campaigns_found = 0
            ads_data = []
            
            # 解析查询结果
            for batch in stream:
                for row in batch.results:
                    campaign = row.campaign
                    metrics = row.metrics
                    segments = row.segments
                    campaigns_found += 1
                    
                    # 转化次数保留两位小数
                    conversions = round(metrics.conversions, 2)
                    # 转化价值保留两位小数
                    conversions_value = round(metrics.conversions_value, 2)
                    # 费用除以10的六次方,保留两位小数
                    cost = round(float(metrics.cost_micros) / 1000000, 2)
                    
                    # 将数据存储到列表中
                    ads_data.append((
                        campaign.id,
                        campaign.name,
                        metrics.impressions,
                        conversions,
                        cost,
                        metrics.clicks,
                        conversions_value,
                        segments.date
                    ))
                    
                    print(f"{campaign.id:<12} {campaign.name:<30} {metrics.impressions:<12} {conversions:<20} {metrics.cost_micros:<20.2f} {metrics.clicks:<20} {conversions_value:<20} {segments.date:<20}")
            
            print(f"总共找到 {campaigns_found} 个广告系列")
            return True, ads_data, ""
            
        except GoogleAdsException as ex:
            print(f"❌ Google Ads API 错误:")
            error_msg = ""
            for error in ex.failure.errors:
                print(f"   错误代码: {error.error_code.name}")
                print(f"   错误信息: {error.message}")
                error_msg += f"错误代码: {error.error_code.name}, 错误信息: {error.message}\n"
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        print(f"   字段: {field_path_element.field_name}")
            return False, [], error_msg
            
        except Exception as e:
            error_msg = f"获取广告系列时出错: {str(e)}"
            print(f"❌ {error_msg}")
            return False, [], error_msg
    
    def fetch_campaigns_data_concurrent(
        self, 
        customer_id: str, 
        start_date: str,
        end_date: str,
        max_workers: int = 5
    ) -> Tuple[bool, List[Tuple], str]:
        """
        从 Google Ads API 并发获取广告系列数据（优化版本）
        
        Args:
            customer_id: Google Ads 客户ID
            start_date: 开始日期
            end_date: 结束日期
            max_workers: 最大并发线程数（Google Ads API 建议较少并发）
            
        Returns:
            (成功标志, 数据列表, 错误信息)
        """
        if not self.client:
            return False, [], "客户端未初始化"
        
        try:
            # 生成日期列表
            date_list = self._generate_date_list(start_date, end_date)
            print(f"📅 将并发获取 {len(date_list)} 天的数据: {start_date} 到 {end_date}")
            effective_workers = min(max_workers, settings.GOOGLE_ADS_MAX_WORKERS)
            if effective_workers != max_workers:
                print(f"🚀 请求 {max_workers} 个并发线程，已根据配置限制为 {effective_workers} 个")
            else:
                print(f"🚀 使用 {effective_workers} 个并发线程")
            
            all_ads_data = []
            completed_dates = 0
            total_dates = len(date_list)
            
            # 使用线程池并发获取数据（复用线程池，减少创建销毁开销）
            executor = _get_thread_pool(effective_workers)
            # 提交所有任务
            future_to_date = {
                executor.submit(self._fetch_single_date_data, customer_id, date): date
                for date in date_list
            }
            
            # 收集结果
            for future in as_completed(future_to_date):
                date = future_to_date[future]
                completed_dates += 1
                
                try:
                    success, date_data, error_msg = future.result()
                    if success and date_data:
                        all_ads_data.extend(date_data)
                    elif not success:
                        print(f"   ⚠️  {date} 获取失败: {error_msg}")
                    
                    # 显示进度
                    progress = (completed_dates / total_dates) * 100
                    print(f"⏳ 进度: {completed_dates}/{total_dates} ({progress:.1f}%) - 已获取 {len(all_ads_data)} 条数据")
                except Exception as e:
                    print(f"   ⚠️  {date} 处理失败: {e}")
            
            print(f"\n🎉 并发获取完成！总共找到 {len(all_ads_data)} 条广告数据")
            return True, all_ads_data, ""
            
        except Exception as e:
            error_msg = f"并发获取数据失败: {str(e)}"
            print(f"❌ {error_msg}")
            return False, [], error_msg
    
    def sync_to_database(
        self, 
        data_list: List[Tuple],
        start_date: str,
        end_date: str,
        clear_existing: bool = True
    ) -> Tuple[bool, str]:
        """
        同步数据到数据库
        
        Args:
            data_list: 要插入的数据列表
            start_date: 开始日期
            end_date: 结束日期
            clear_existing: 是否清空日期范围内的现有数据
            
        Returns:
            (成功标志, 消息)
        """
        if not data_list:
            return False, "没有数据需要同步"
        
        try:
            # 清空指定日期范围内的数据（如果需要）
            if clear_existing:
                self.delete_data_in_range(start_date, end_date)
            
            # 准备SQL语句
            insert_query = text("""
                INSERT INTO fact_bi_ads_google_campaign (
                    campaign_id, campaign, impression, 
                    conversions, cost, clicks, conversion_value, createtime
                )
                VALUES (
                    :campaign_id, :campaign, :impression,
                    :conversions, :cost, :clicks, :conversion_value, :createtime
                )
            """)
            
            # 转换数据为字典格式
            data_dicts = [
                {
                    "campaign_id": data[0],
                    "campaign": data[1],
                    "impression": data[2],
                    "conversions": data[3],
                    "cost": data[4],
                    "clicks": data[5],
                    "conversion_value": data[6],
                    "createtime": data[7]
                }
                for data in data_list
            ]
            
            # 批量插入
            count = self.batch_insert(insert_query, data_dicts)
            message = f"成功插入 {count} 条数据"
            return True, message
            
        except Exception as e:
            self.db.rollback()
            error_msg = f"数据库错误: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def sync_campaigns(
        self,
        customer_id: str,
        start_date: str,
        end_date: str,
        proxy_url: Optional[str] = None,
        clear_existing: bool = True,
        use_concurrent: bool = True,
        max_workers: int = 10  # 提升并发数：5 -> 10
    ) -> Dict[str, Any]:
        """
        完整的同步流程：获取数据并同步到数据库（优化版本）
        
        Args:
            customer_id: Google Ads 客户ID
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            proxy_url: 代理URL（可选）
            clear_existing: 是否清空现有数据
            use_concurrent: 是否使用并发模式（默认True，性能更好）
            max_workers: 并发线程数（默认5，Google Ads API建议较少并发）
            
        Returns:
            包含执行结果的字典
        """
        start_time = time.time()
        
        try:
            print(f"\n{'='*60}")
            print(f"🚀 开始同步 Google Ads 数据（{'并发' if use_concurrent else '串行'}模式）")
            print(f"📅 日期范围: {start_date} 到 {end_date}")
            print(f"{'='*60}\n")
            
            # 设置代理（如果提供）
            if proxy_url:
                self.setup_proxy(proxy_url)
            
            # 初始化客户端
            if not self.initialize_client():
                return self.create_sync_result(False, "初始化 Google Ads 客户端失败", 0, ["初始化失败"])
            
            # 获取数据（选择并发或串行模式）
            print("\n📡 从 Google Ads API 获取数据...")
            if use_concurrent:
                success, data_list, error_msg = self.fetch_campaigns_data_concurrent(
                    customer_id, start_date, end_date, max_workers
                )
            else:
                success, data_list, error_msg = self.fetch_campaigns_data(
                    customer_id, start_date, end_date
                )
            
            if not success:
                return self.create_sync_result(False, error_msg, 0, [error_msg])
            
            print(f"✅ 成功获取 {len(data_list)} 条广告数据")
            
            # 同步到数据库
            print("\n💾 写入数据库...")
            success, message = self.sync_to_database(data_list, start_date, end_date, clear_existing)
            if not success:
                return self.create_sync_result(False, message, 0, [message])
            
            elapsed_time = time.time() - start_time
            
            print(f"\n{'='*60}")
            print(f"✅ Google Ads 数据同步完成！")
            print(f"📊 共同步 {len(data_list)} 条记录")
            print(f"⏱️  总耗时: {elapsed_time:.2f} 秒")
            print(f"⚡ 平均速度: {len(data_list)/elapsed_time:.2f} 条/秒")
            print(f"{'='*60}\n")
            
            # 成功
            return self.create_sync_result(True, f"{message}（耗时 {elapsed_time:.2f}秒）", len(data_list))
            
        except Exception as e:
            error_msg = f"同步过程出错: {str(e)}"
            return self.create_sync_result(False, error_msg, 0, [error_msg])
