"""
API通用工具函数
提供统一的响应格式和错误处理
"""
from fastapi import HTTPException
from typing import Any, Callable
from functools import wraps
import asyncio


def api_success(data: Any, message: str = "success") -> dict:
    """
    统一成功响应格式
    
    Args:
        data: 返回的数据
        message: 成功消息
        
    Returns:
        统一格式的成功响应
    """
    return {"code": 200, "message": message, "data": data}


def api_error(message: str, code: int = 500, data: Any = None) -> dict:
    """
    统一错误响应格式
    
    Args:
        message: 错误消息
        code: 错误代码
        data: 附加数据
        
    Returns:
        统一格式的错误响应
    """
    return {"code": code, "message": message, "data": data or {}}


def handle_error(e: Exception, default_msg: str = "操作失败") -> None:
    """
    统一错误处理
    
    Args:
        e: 异常对象
        default_msg: 默认错误消息
        
    Raises:
        HTTPException: 返回格式化的HTTP异常
    """
    if isinstance(e, HTTPException):
        raise e
    raise HTTPException(status_code=500, detail=f"{default_msg}: {str(e)}")


def api_endpoint(error_message: str = "操作失败", success_message: str = "success"):
    """
    API端点装饰器，自动处理错误并返回统一格式
    
    Args:
        error_message: 错误消息前缀
        success_message: 成功消息
        
    Returns:
        装饰器函数
    
    Example:
        @api_endpoint(error_message="获取数据失败")
        async def get_data(...):
            return data  # 自动包装为 api_success(data)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                # 如果返回值已经是字典且包含code字段，说明已经格式化了，直接返回
                if isinstance(result, dict) and "code" in result:
                    return result
                # 否则自动包装为成功响应
                return api_success(result, success_message)
            except Exception as e:
                handle_error(e, error_message)
        return wrapper
    return decorator


def validate_required_config(config_value: Any, field_name: str, error_msg: str = None) -> Any:
    """
    验证必需的配置项
    
    Args:
        config_value: 配置值
        field_name: 字段名
        error_msg: 自定义错误消息
        
    Returns:
        配置值（如果验证通过）
        
    Raises:
        HTTPException: 如果配置值为空
    """
    if not config_value:
        msg = error_msg or f"{field_name} 未配置，请在环境变量或请求中提供"
        raise HTTPException(status_code=400, detail=msg)
    return config_value


def get_config_or_default(request_value: Any, default_value: Any, field_name: str = None) -> Any:
    """
    获取配置值，优先使用请求值，否则使用默认值
    
    Args:
        request_value: 请求中的值
        default_value: 默认值（通常来自settings）
        field_name: 字段名（用于验证）
        
    Returns:
        最终使用的配置值
        
    Raises:
        HTTPException: 如果两个值都为空
    """
    final_value = request_value or default_value
    if field_name and not final_value:
        raise HTTPException(
            status_code=400, 
            detail=f"{field_name} 未配置，请在环境变量或请求中提供"
        )
    return final_value


async def handle_ai_analysis(analyze_func: Callable, metrics_data: dict, date_range: dict) -> dict:
    """
    通用AI分析处理函数（异步版本，避免阻塞）
    
    Args:
        analyze_func: AI分析函数
        metrics_data: 指标数据
        date_range: 日期范围
        
    Returns:
        API响应字典
    """
    try:
        # 在线程池中执行同步的AI调用，避免阻塞主线程
        # 设置超时时间为90秒（考虑模型轮换）
        analysis_result = await asyncio.wait_for(
            asyncio.to_thread(
                analyze_func,
                metrics_data=metrics_data or {},
                date_range=date_range
            ),
            timeout=90.0
        )
        return api_success(analysis_result, "AI分析完成")
    except asyncio.TimeoutError:
        return api_error("AI分析超时，请稍后重试", code=504)
    except ValueError as e:
        return api_error(f"配置错误: {str(e)}", code=500)
    except Exception as e:
        handle_error(e, "AI分析失败")