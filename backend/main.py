"""
Facebook Ads BI Dashboard - FastAPI Backend
主应用入口
"""
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

from app.api import auth, facebook, google, lingxing, cache, summary, settings as settings_api
from app.core.auth import authenticate_request
from app.core.config import settings
from app.core.logging import build_request_id, reset_request_id, set_request_id, setup_logging
from app.core.scheduler import (
    acquire_scheduler_lock,
    release_scheduler_lock,
    start_facebook_ads_daily_sync_task,
    start_google_ads_daily_sync_task,
)

# 加载环境变量
load_dotenv()
setup_logging(settings.DEBUG)
logger = logging.getLogger("app.main")

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


def _auth_error_response(status_code: int, detail):
    if isinstance(detail, dict):
        message = str(detail.get("message") or "认证失败")
    else:
        message = str(detail or "认证失败")
    return JSONResponse(
        status_code=status_code,
        content={"code": status_code, "message": message, "data": None},
    )


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = build_request_id(request.headers.get("X-Request-ID"))
    token = set_request_id(request_id)
    request.state.request_id = request_id
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        reset_request_id(token)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.method.upper() == "OPTIONS":
        return await call_next(request)

    path = request.url.path
    public_paths = {"/", "/health", "/openapi.json"}
    public_prefixes = ("/docs", "/redoc", "/api/auth")
    if path in public_paths or any(path.startswith(prefix) for prefix in public_prefixes):
        return await call_next(request)

    if path.startswith("/api"):
        try:
            request.state.current_user = authenticate_request(request)
        except HTTPException as exc:
            logger.warning("auth failed path=%s status=%s", path, exc.status_code)
            return _auth_error_response(exc.status_code, exc.detail)

    return await call_next(request)

# 注册路由
app.include_router(auth.router, tags=["Auth"])
app.include_router(facebook.router, prefix="/api/dashboard/facebook", tags=["Facebook Ads"])
app.include_router(google.router, prefix="/api/dashboard/google", tags=["Google Ads"])
app.include_router(lingxing.router, prefix="/api/dashboard/lingxing", tags=["Lingxing Data"])
app.include_router(summary.router, prefix="/api/dashboard/summary", tags=["Summary Dashboard"])
app.include_router(cache.router, prefix="/api/cache", tags=["Cache Management"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])


@app.on_event("startup")
async def start_scheduler():
    app.state.scheduler_tasks = []
    app.state.scheduler_lock_conn = None

    scheduler_enabled = settings.GOOGLE_ADS_DAILY_SYNC_ENABLED or settings.FACEBOOK_DAILY_SYNC_ENABLED
    if not scheduler_enabled:
        logger.info("scheduler disabled by config")
        return

    lock_conn = acquire_scheduler_lock()
    if lock_conn is None:
        logger.info("scheduler not started in this worker because lock is held by another worker")
        return

    app.state.scheduler_lock_conn = lock_conn

    if settings.GOOGLE_ADS_DAILY_SYNC_ENABLED:
        app.state.scheduler_tasks.append(start_google_ads_daily_sync_task())
        logger.info("Google Ads hourly sync enabled")
    if settings.FACEBOOK_DAILY_SYNC_ENABLED:
        app.state.scheduler_tasks.append(start_facebook_ads_daily_sync_task())
        logger.info("Facebook Ads hourly sync enabled")


@app.on_event("shutdown")
async def stop_scheduler():
    tasks = getattr(app.state, "scheduler_tasks", [])
    for task in tasks:
        task.cancel()
    release_scheduler_lock(getattr(app.state, "scheduler_lock_conn", None))

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
    logger.exception("unhandled exception path=%s", getattr(request, "url", "unknown"))
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
