"""
Redis缓存管理器
提供两级缓存策略：L1内存缓存 + L2 Redis缓存
"""
import json
import hashlib
import logging
from typing import Any, Optional, Callable
from collections.abc import Mapping, Sequence
from functools import wraps
from datetime import timedelta
import redis
from cachetools import TTLCache
from .config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器 - 支持两级缓存"""
    
    def __init__(self):
        """初始化缓存管理器"""
        self.redis_client: Optional[redis.Redis] = None
        self.l1_cache = TTLCache(maxsize=100, ttl=300)  # L1: 内存缓存，5分钟TTL
        self._connect_redis()
    
    def _connect_redis(self):
        """连接到Redis服务器"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # 测试连接
            self.redis_client.ping()
            logger.info(f"✅ Redis连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.warning(f"⚠️ Redis连接失败，将仅使用内存缓存: {str(e)}")
            self.redis_client = None
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            prefix: 键前缀（如 'facebook:ads'）
            *args, **kwargs: 用于生成键的参数
            
        Returns:
            缓存键字符串
        """
        def normalize(value: Any) -> str:
            """将参数转换为稳定的字符串表示，避免包含内存地址。"""
            if value is None or isinstance(value, (str, int, float, bool)):
                return repr(value)
            if isinstance(value, Mapping):
                items = [
                    f"{normalize(k)}:{normalize(v)}"
                    for k, v in sorted(value.items(), key=lambda item: str(item[0]))
                ]
                return "{" + ",".join(items) + "}"
            if isinstance(value, set):
                items = sorted(normalize(v) for v in value)
                return "{" + ",".join(items) + "}"
            if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
                return "[" + ",".join(normalize(v) for v in value) + "]"
            module = getattr(value.__class__, "__module__", "")
            name = getattr(value.__class__, "__name__", value.__class__.__qualname__)
            return f"<{module}.{name}>"
        
        # 将参数序列化为字符串
        key_parts = [normalize(arg) for arg in args]
        key_parts.extend([f"{k}={normalize(v)}" for k, v in sorted(kwargs.items())])
        key_str = ":".join(key_parts)
        if not key_str:
            key_str = "default"
        
        # 对于长键，使用哈希
        if len(key_str) > 100:
            key_hash = hashlib.md5(key_str.encode()).hexdigest()[:16]
            return f"{prefix}:{key_hash}"
        
        return f"{prefix}:{key_str}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据（先L1后L2）
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的数据，如果不存在返回None
        """
        # 先查L1缓存
        if key in self.l1_cache:
            logger.debug(f"🎯 L1缓存命中: {key}")
            return self.l1_cache[key]
        
        # 再查L2缓存（Redis）
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    logger.debug(f"🎯 L2缓存命中: {key}")
                    # 反序列化
                    data = json.loads(value)
                    # 写入L1缓存
                    self.l1_cache[key] = data
                    return data
            except Exception as e:
                logger.error(f"Redis获取失败: {key}, {str(e)}")
        
        logger.debug(f"❌ 缓存未命中: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        设置缓存数据（同时写入L1和L2）
        
        Args:
            key: 缓存键
            value: 要缓存的数据
            ttl: 过期时间（秒），默认1小时
        """
        # 写入L1缓存
        self.l1_cache[key] = value
        
        # 写入L2缓存（Redis）
        if self.redis_client:
            try:
                serialized = json.dumps(value, ensure_ascii=False)
                self.redis_client.setex(key, ttl, serialized)
                logger.debug(f"✅ 缓存已设置: {key} (TTL: {ttl}s)")
            except Exception as e:
                logger.error(f"Redis设置失败: {key}, {str(e)}")
    
    def delete(self, key: str):
        """删除缓存数据"""
        # 删除L1缓存
        self.l1_cache.pop(key, None)
        
        # 删除L2缓存
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                logger.debug(f"🗑️ 缓存已删除: {key}")
            except Exception as e:
                logger.error(f"Redis删除失败: {key}, {str(e)}")
    
    def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的所有缓存
        
        Args:
            pattern: 匹配模式（如 'facebook:*'）
            
        Returns:
            删除的键数量
        """
        deleted_count = 0
        
        # 清除L1缓存中匹配的键
        keys_to_delete = [k for k in self.l1_cache.keys() if self._match_pattern(k, pattern)]
        for key in keys_to_delete:
            self.l1_cache.pop(key, None)
            deleted_count += 1
        
        # 清除L2缓存中匹配的键
        if self.redis_client:
            try:
                cursor = 0
                while True:
                    cursor, keys = self.redis_client.scan(cursor, match=pattern, count=100)
                    if keys:
                        self.redis_client.delete(*keys)
                        deleted_count += len(keys)
                    if cursor == 0:
                        break
                logger.info(f"🗑️ 清除缓存模式 '{pattern}': {deleted_count} 个键")
            except Exception as e:
                logger.error(f"Redis批量删除失败: {pattern}, {str(e)}")
        
        return deleted_count
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """简单的模式匹配（支持*通配符）"""
        import re
        regex_pattern = pattern.replace('*', '.*')
        return re.match(f'^{regex_pattern}$', key) is not None
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        stats = {
            "l1_cache": {
                "size": len(self.l1_cache),
                "maxsize": self.l1_cache.maxsize,
                "ttl": self.l1_cache.ttl
            },
            "redis": {
                "connected": self.redis_client is not None
            }
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats["redis"].update({
                    "used_memory_human": info.get("used_memory_human", "N/A"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                })
                
                # 计算命中率
                hits = info.get("keyspace_hits", 0)
                misses = info.get("keyspace_misses", 0)
                if hits + misses > 0:
                    stats["redis"]["hit_rate"] = f"{hits / (hits + misses) * 100:.2f}%"
            except Exception as e:
                logger.error(f"获取Redis统计信息失败: {str(e)}")
        
        return stats
    
    def flush_all(self):
        """清空所有缓存（谨慎使用）"""
        # 清空L1
        self.l1_cache.clear()
        
        # 清空L2
        if self.redis_client:
            try:
                self.redis_client.flushdb()
                logger.warning("⚠️ 已清空所有Redis缓存")
            except Exception as e:
                logger.error(f"Redis清空失败: {str(e)}")


# 全局缓存管理器实例
cache_manager = CacheManager()


def cached(prefix: str, ttl: int = 3600, key_builder: Optional[Callable] = None):
    """
    缓存装饰器 - 用于缓存函数返回值
    
    Args:
        prefix: 缓存键前缀
        ttl: 过期时间（秒）
        key_builder: 自定义键生成函数
    
    Example:
        @cached(prefix="facebook:impressions", ttl=1800)
        async def get_impressions_data(start_date, end_date):
            # 调用API获取数据
            return data
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_cache_key(prefix, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_data = cache_manager.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            # 缓存未命中，执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            if result is not None:
                cache_manager.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 生成缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_cache_key(prefix, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_data = cache_manager.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            # 缓存未命中，执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            if result is not None:
                cache_manager.set(cache_key, result, ttl)
            
            return result
        
        # 根据函数类型返回对应的wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def invalidate_cache(pattern: str):
    """
    清除缓存的辅助函数
    
    Args:
        pattern: 缓存键模式（支持*通配符）
    
    Example:
        invalidate_cache("facebook:*")  # 清除所有Facebook缓存
    """
    return cache_manager.clear_pattern(pattern)

