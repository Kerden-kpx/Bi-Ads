"""
Facebook Ads BI Dashboard - FastAPI Backend
主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

from app.api import facebook, google, lingxing, cache, summary, settings as settings_api
from app.core.config import settings
from app.core.scheduler import (
    start_facebook_ads_daily_sync_task,
    start_google_ads_daily_sync_task,
)

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="广告数据BI仪表板后端API - 支持Facebook和Google Ads",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Gzip压缩中间件（优先级最高，最先添加）
# 自动压缩大于500字节的响应，压缩率通常达到70-90%
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials="*" not in settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(facebook.router, prefix="/api/dashboard/facebook", tags=["Facebook Ads"])
app.include_router(google.router, prefix="/api/dashboard/google", tags=["Google Ads"])
app.include_router(lingxing.router, prefix="/api/dashboard/lingxing", tags=["Lingxing Data"])
app.include_router(summary.router, prefix="/api/dashboard/summary", tags=["Summary Dashboard"])
app.include_router(cache.router, prefix="/api/cache", tags=["Cache Management"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])


@app.on_event("startup")
async def start_scheduler():
    app.state.scheduler_tasks = []
    if settings.GOOGLE_ADS_DAILY_SYNC_ENABLED:
        app.state.scheduler_tasks.append(start_google_ads_daily_sync_task())
        print("✅ [scheduler] Google Ads daily sync enabled")
    if settings.FACEBOOK_DAILY_SYNC_ENABLED:
        app.state.scheduler_tasks.append(start_facebook_ads_daily_sync_task())
        print("✅ [scheduler] Facebook Ads daily sync enabled")


@app.on_event("shutdown")
async def stop_scheduler():
    tasks = getattr(app.state, "scheduler_tasks", [])
    for task in tasks:
        task.cancel()

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "OK",
        "message": "Server is running",
        "version": settings.APP_VERSION
    }

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "广告数据BI仪表板API - 支持Facebook和Google Ads",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "platforms": ["facebook", "google"]
    }

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": str(exc) if settings.DEBUG else "服务器内部错误",
            "data": None
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
