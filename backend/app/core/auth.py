"""
认证核心工具
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import HTTPException, Request
from jose import JWTError, jwt
from sqlalchemy import text

from app.core.config import settings
from app.core.database import SessionLocal


@dataclass
class CurrentUser:
    """当前登录用户"""

    userid: str
    username: str


_USER_SELECT_SQL = text(
    """
    SELECT dingtalk_userid, dingtalk_username, created_at
    FROM dim_bi_ads_user
    WHERE dingtalk_userid = :userid
    LIMIT 1
    """
)


def _get_auth_secret() -> str:
    secret = (settings.AUTH_SECRET_EFFECTIVE or "").strip()
    if not secret:
        raise HTTPException(status_code=500, detail="认证密钥未配置")
    return secret


def create_access_token(userid: str, username: str) -> str:
    """签发访问令牌"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": userid,
        "name": username,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=settings.AUTH_TOKEN_TTL)).timestamp()),
    }
    return jwt.encode(payload, _get_auth_secret(), algorithm=settings.ALGORITHM)


def _decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, _get_auth_secret(), algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="无效或过期的令牌") from exc


def _fetch_user(userid: str) -> Dict[str, Any] | None:
    db = SessionLocal()
    try:
        row = db.execute(_USER_SELECT_SQL, {"userid": userid}).mappings().first()
        return dict(row) if row else None
    finally:
        db.close()


def authenticate_request(request: Request) -> CurrentUser:
    """从请求头认证并返回当前用户"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少认证令牌")

    token = auth_header.replace("Bearer ", "", 1).strip()
    if not token:
        raise HTTPException(status_code=401, detail="认证令牌为空")

    payload = _decode_access_token(token)
    userid = str(payload.get("sub") or "").strip()
    if not userid:
        raise HTTPException(status_code=401, detail="认证令牌缺少用户标识")

    user = _fetch_user(userid)
    if not user:
        raise HTTPException(status_code=403, detail="用户不存在或无权限")

    return CurrentUser(
        userid=str(user.get("dingtalk_userid") or userid),
        username=str(user.get("dingtalk_username") or userid),
    )


def get_current_user(request: Request) -> CurrentUser:
    """FastAPI 依赖：获取当前用户"""
    cached_user = getattr(request.state, "current_user", None)
    if isinstance(cached_user, CurrentUser):
        return cached_user
    return authenticate_request(request)
