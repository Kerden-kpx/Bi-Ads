"""
AI分析通用路由工厂 - 减少重复代码
"""
from fastapi import Body
from typing import Optional, Callable
from app.services.gemini_ai_service import get_gemini_service
from app.utils.api_helpers import api_endpoint, handle_ai_analysis


def create_ai_analysis_endpoint(analysis_method_name: str, error_message: str):
    """
    创建AI分析端点的工厂函数
    
    Args:
        analysis_method_name: Gemini服务的分析方法名
        error_message: 错误消息
        
    Returns:
        分析端点函数
    """
    @api_endpoint(error_message=error_message)
    async def analyze(
        startDate: str = Body(..., description="开始日期 YYYY-MM-DD"),
        endDate: str = Body(..., description="结束日期 YYYY-MM-DD"),
        compareStartDate: Optional[str] = Body(None, description="对比开始日期"),
        compareEndDate: Optional[str] = Body(None, description="对比结束日期"),
        accountId: Optional[str] = Body(None, description="账户ID（可选）"),
        metricsData: Optional[dict] = Body(None, description="指标卡数据")
    ):
        """AI数据分析"""
        gemini_service = get_gemini_service()
        analysis_func = getattr(gemini_service, analysis_method_name)
        return await handle_ai_analysis(
            analysis_func,
            metricsData,
            {"startDate": startDate, "endDate": endDate}
        )
    
    return analyze

