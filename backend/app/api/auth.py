"""
钉钉认证 API
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.services.auth_service import get_user_profile, login_with_auth_code, refresh_user_profile, sign_jsapi
from app.utils.api_helpers import api_success

router = APIRouter()


class DingTalkSignRequest(BaseModel):
    url: str


class DingTalkLoginRequest(BaseModel):
    auth_code: str


@router.post("/api/auth/dingtalk/jsapi-sign")
async def dingtalk_jsapi_sign(payload: DingTalkSignRequest):
    return api_success(sign_jsapi(payload.url))


@router.post("/api/auth/dingtalk/login")
async def dingtalk_login(payload: DingTalkLoginRequest, db: Session = Depends(get_db)):
    result = login_with_auth_code(db, payload.auth_code)
    return api_success(result)


@router.post("/api/auth/dingtalk/refresh-user")
async def dingtalk_refresh_user(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = refresh_user_profile(db, current_user.userid)
    return api_success({"user": user})


@router.get("/api/auth/me")
async def auth_me(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_user_profile(db, current_user.userid)
    return api_success({"user": user})
