"""
缓存管理API路由
"""
from fastapi import APIRouter, Query
from typing import Optional

from app.core.cache import cache_manager, invalidate_cache
from app.utils.api_helpers import api_success, api_error

router = APIRouter()


@router.get("/stats")
async def get_cache_stats():
    """获取缓存统计信息"""
    try:
        stats = cache_manager.get_stats()
        return api_success(stats, "成功获取缓存统计信息")
    except Exception as e:
        return api_error(f"获取缓存统计失败: {str(e)}", code=500)


@router.post("/clear")
async def clear_cache(
    pattern: Optional[str] = Query(None, description="缓存键模式（支持*通配符），例如: facebook:*, google:*, 留空清除所有缓存")
):
    """
    清除缓存
    
    参数:
    - pattern: 缓存键模式，支持*通配符
      - facebook:* - 清除所有Facebook缓存
      - google:* - 清除所有Google缓存
      - facebook:impressions:* - 清除Facebook印象数据缓存
      - 留空 - 清除所有缓存（谨慎使用）
    
    示例:
    - POST /api/cache/clear?pattern=facebook:*
    - POST /api/cache/clear?pattern=google:impressions:*
    - POST /api/cache/clear （清除所有）
    """
    try:
        if pattern:
            deleted_count = invalidate_cache(pattern)
            return api_success(
                {"deleted_count": deleted_count, "pattern": pattern},
                f"成功清除匹配 '{pattern}' 的缓存，共 {deleted_count} 个键"
            )
        else:
            # 清除所有缓存
            cache_manager.flush_all()
            return api_success(
                {"deleted_count": "all"},
                "成功清除所有缓存"
            )
    except Exception as e:
        return api_error(f"清除缓存失败: {str(e)}", code=500)


@router.post("/clear/facebook")
async def clear_facebook_cache():
    """清除所有Facebook缓存"""
    try:
        deleted_count = invalidate_cache("facebook:*")
        return api_success(
            {"deleted_count": deleted_count, "platform": "facebook"},
            f"成功清除Facebook缓存，共 {deleted_count} 个键"
        )
    except Exception as e:
        return api_error(f"清除Facebook缓存失败: {str(e)}", code=500)


@router.post("/clear/google")
async def clear_google_cache():
    """清除所有Google缓存"""
    try:
        deleted_count = invalidate_cache("google:*")
        return api_success(
            {"deleted_count": deleted_count, "platform": "google"},
            f"成功清除Google缓存，共 {deleted_count} 个键"
        )
    except Exception as e:
        return api_error(f"清除Google缓存失败: {str(e)}", code=500)


@router.get("/health")
async def cache_health():
    """检查缓存系统健康状态"""
    try:
        stats = cache_manager.get_stats()
        redis_connected = stats.get("redis", {}).get("connected", False)
        
        health_status = {
            "redis_connected": redis_connected,
            "l1_cache_enabled": True,
            "status": "healthy" if redis_connected else "degraded"
        }
        
        if not redis_connected:
            health_status["warning"] = "Redis未连接，仅使用内存缓存"
        
        return api_success(health_status, "缓存系统运行正常")
    except Exception as e:
        return api_error(f"缓存健康检查失败: {str(e)}", code=500)

