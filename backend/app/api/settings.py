"""
设置管理 API
用于管理产品名称等配置
"""
from fastapi import APIRouter
from typing import Optional, List
from pydantic import BaseModel
from pathlib import Path
import json

from app.core.cache import invalidate_cache
from app.core.config import settings
from app.utils.api_helpers import api_success, api_error

router = APIRouter()


class ProductNamesResponse(BaseModel):
    """产品名称响应模型"""
    facebook_product_names: List[str]
    google_product_names: List[str]


class UpdateProductNamesRequest(BaseModel):
    """更新产品名称请求模型"""
    facebookProductNames: Optional[List[str]] = None
    googleProductNames: Optional[List[str]] = None


@router.get("/product-names")
async def get_product_names():
    """
    获取当前的产品名称配置
    """
    try:
        return api_success({
            "facebook_product_names": settings.FACEBOOK_PRODUCT_NAMES_LIST,
            "google_product_names": settings.GOOGLE_PRODUCT_NAMES_LIST
        })
    except Exception as e:
        return api_error(f"获取产品名称配置失败: {str(e)}", code=500)


@router.post("/reload")
async def reload_settings():
    """
    重新加载配置
    
    从 .env 文件重新读取所有配置并应用，无需重启后端服务
    """
    try:
        settings.reload()
        return api_success({
            "message": "配置已重新加载",
            "current_values": {
                "facebook_product_names": settings.FACEBOOK_PRODUCT_NAMES_LIST,
                "google_product_names": settings.GOOGLE_PRODUCT_NAMES_LIST
            }
        })
    except Exception as e:
        return api_error(f"重新加载配置失败: {str(e)}", code=500)


@router.post("/product-names")
async def update_product_names(
    request: UpdateProductNamesRequest
):
    """
    更新产品名称配置
    
    此接口会更新 data/product_names.json 并重新加载配置，无需重启后端服务即可生效
    """
    try:
        max_items = 200
        max_name_len = 100

        def clean_names(names: Optional[List[str]]) -> List[str]:
            if not names:
                return []
            cleaned: List[str] = []
            seen = set()
            for name in names:
                if not isinstance(name, str):
                    continue
                value = " ".join(name.split()).strip()
                if not value:
                    continue
                if len(value) > max_name_len:
                    value = value[:max_name_len]
                if value in seen:
                    continue
                cleaned.append(value)
                seen.add(value)
                if len(cleaned) >= max_items:
                    break
            return cleaned

        # 计算产品名称配置文件路径（支持相对 backend 根目录）
        backend_dir = Path(__file__).resolve().parents[2]
        product_names_path = Path(settings.PRODUCT_NAMES_FILE_PATH)
        if not product_names_path.is_absolute():
            product_names_path = backend_dir / product_names_path
        product_names_path.parent.mkdir(parents=True, exist_ok=True)

        # 读取现有配置，读取失败时使用当前内存值兜底
        config_data = {
            "facebook_product_names": settings.FACEBOOK_PRODUCT_NAMES_LIST,
            "google_product_names": settings.GOOGLE_PRODUCT_NAMES_LIST
        }
        if product_names_path.exists():
            try:
                with open(product_names_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                if isinstance(existing, dict):
                    config_data["facebook_product_names"] = clean_names(existing.get("facebook_product_names")) or config_data["facebook_product_names"]
                    config_data["google_product_names"] = clean_names(existing.get("google_product_names")) or config_data["google_product_names"]
            except Exception:
                pass

        # 应用本次更新
        if request.facebookProductNames is not None:
            config_data["facebook_product_names"] = clean_names(request.facebookProductNames)
        if request.googleProductNames is not None:
            config_data["google_product_names"] = clean_names(request.googleProductNames)

        # 写回产品名称配置文件
        with open(product_names_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        
        # 重新加载配置
        settings.reload()

        # 自动清理受产品名称影响的缓存，确保下次查询立即生效
        cache_cleared = {}
        for pattern in ("facebook:ads_performance*", "google:ads_performance*"):
            try:
                cache_cleared[pattern] = invalidate_cache(pattern)
            except Exception:
                cache_cleared[pattern] = 0
        
        return api_success({
            "message": "产品名称配置已更新并生效",
            "updated": {
                "facebook": request.facebookProductNames is not None,
                "google": request.googleProductNames is not None
            },
            "cache_cleared": cache_cleared,
            "current_values": {
                "facebook_product_names": settings.FACEBOOK_PRODUCT_NAMES_LIST,
                "google_product_names": settings.GOOGLE_PRODUCT_NAMES_LIST
            }
        })
    except Exception as e:
        return api_error(f"更新产品名称配置失败: {str(e)}", code=500)
