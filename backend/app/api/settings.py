"""
设置管理 API
用于管理产品名称等配置
"""
from fastapi import APIRouter, Body
from typing import Optional, List
from pydantic import BaseModel

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
    
    此接口会更新 .env 文件并重新加载配置，无需重启后端服务即可生效
    """
    try:
        import os
        import re
        from pathlib import Path
        
        # 获取项目根目录（backend目录）
        backend_dir = Path(__file__).parent.parent.parent
        env_path = backend_dir / ".env"
        
        # 如果 .env 文件不存在，创建它
        if not env_path.exists():
            env_path.touch()
            env_content = ""
        else:
            # 读取现有 .env 文件内容
            with open(env_path, 'r', encoding='utf-8') as f:
                env_content = f.read()
        
        # 更新 Facebook 产品名称
        if request.facebookProductNames is not None:
            new_facebook_names = ",".join(request.facebookProductNames)
            pattern = r'^FACEBOOK_PRODUCT_NAMES=.*$'
            replacement = f'FACEBOOK_PRODUCT_NAMES={new_facebook_names}'
            
            if re.search(pattern, env_content, re.MULTILINE):
                # 如果存在，则替换
                env_content = re.sub(pattern, replacement, env_content, flags=re.MULTILINE)
            else:
                # 如果不存在，则添加
                if env_content and not env_content.endswith('\n'):
                    env_content += '\n'
                env_content += f'{replacement}\n'
        
        # 更新 Google 产品名称
        if request.googleProductNames is not None:
            new_google_names = ",".join(request.googleProductNames)
            pattern = r'^GOOGLE_PRODUCT_NAMES=.*$'
            replacement = f'GOOGLE_PRODUCT_NAMES={new_google_names}'
            
            if re.search(pattern, env_content, re.MULTILINE):
                # 如果存在，则替换
                env_content = re.sub(pattern, replacement, env_content, flags=re.MULTILINE)
            else:
                # 如果不存在，则添加
                if env_content and not env_content.endswith('\n'):
                    env_content += '\n'
                env_content += f'{replacement}\n'
        
        # 写回 .env 文件
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        # 重新加载配置
        settings.reload()
        
        return api_success({
            "message": "产品名称配置已更新并生效",
            "updated": {
                "facebook": request.facebookProductNames is not None,
                "google": request.googleProductNames is not None
            },
            "current_values": {
                "facebook_product_names": settings.FACEBOOK_PRODUCT_NAMES_LIST,
                "google_product_names": settings.GOOGLE_PRODUCT_NAMES_LIST
            }
        })
    except Exception as e:
        return api_error(f"更新产品名称配置失败: {str(e)}", code=500)


