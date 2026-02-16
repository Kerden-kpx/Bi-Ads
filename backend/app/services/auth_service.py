"""
钉钉认证服务
"""
import hashlib
import os
import time
from typing import Any, Dict

import requests
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.auth import create_access_token
from app.core.config import settings


_TOKEN_CACHE: Dict[str, Any] = {"token": None, "expires_at": 0}
_TICKET_CACHE: Dict[str, Any] = {"ticket": None, "expires_at": 0}

_USER_SELECT_SQL = text(
    """
    SELECT dingtalk_userid, dingtalk_username, created_at
    FROM dim_bi_ads_user
    WHERE dingtalk_userid = :userid
    LIMIT 1
    """
)


def _ensure_config(value: str, field_name: str) -> str:
    if not value:
        raise HTTPException(status_code=500, detail=f"缺少配置: {field_name}")
    return value


def _http_get_json(url: str, params: Dict[str, str]) -> Dict[str, Any]:
    try:
        response = requests.get(url, params=params, timeout=settings.DINGTALK_HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"调用钉钉接口失败: {url}") from exc


def _http_post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        response = requests.post(url, json=payload, timeout=settings.DINGTALK_HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"调用钉钉接口失败: {url}") from exc


def _ensure_ok(resp: Dict[str, Any], context: str) -> None:
    errcode = resp.get("errcode")
    if errcode not in (0, None):
        errmsg = resp.get("errmsg") or resp.get("message") or "unknown error"
        raise HTTPException(
            status_code=502,
            detail=f"{context} 失败: errcode={errcode}, errmsg={errmsg}",
        )


def _get_access_token() -> str:
    now = int(time.time())
    cached = _TOKEN_CACHE.get("token")
    if cached and now < int(_TOKEN_CACHE.get("expires_at", 0)) - 60:
        return str(cached)

    app_key = _ensure_config(settings.DINGTALK_APP_KEY, "DINGTALK_APP_KEY")
    app_secret = _ensure_config(settings.DINGTALK_APP_SECRET, "DINGTALK_APP_SECRET")
    resp = _http_get_json(
        settings.DINGTALK_TOKEN_URL,
        {"appkey": app_key, "appsecret": app_secret},
    )
    _ensure_ok(resp, "获取access_token")
    token = resp.get("access_token")
    expires_in = int(resp.get("expires_in") or 7200)
    if not token:
        raise HTTPException(status_code=502, detail="钉钉返回缺少 access_token")
    _TOKEN_CACHE["token"] = token
    _TOKEN_CACHE["expires_at"] = now + expires_in
    return str(token)


def _get_jsapi_ticket(token: str) -> str:
    now = int(time.time())
    cached = _TICKET_CACHE.get("ticket")
    if cached and now < int(_TICKET_CACHE.get("expires_at", 0)) - 60:
        return str(cached)

    resp = _http_get_json(
        settings.DINGTALK_JSAPI_TICKET_URL,
        {"access_token": token},
    )
    _ensure_ok(resp, "获取jsapi_ticket")
    ticket = resp.get("ticket")
    expires_in = int(resp.get("expires_in") or 7200)
    if not ticket:
        raise HTTPException(status_code=502, detail="钉钉返回缺少 jsapi_ticket")
    _TICKET_CACHE["ticket"] = ticket
    _TICKET_CACHE["expires_at"] = now + expires_in
    return str(ticket)


def sign_jsapi(url: str) -> Dict[str, Any]:
    raw_url = (url or "").strip()
    if not raw_url:
        raise HTTPException(status_code=400, detail="缺少 url")

    corp_id = _ensure_config(settings.DINGTALK_CORP_ID, "DINGTALK_CORP_ID")
    token = _get_access_token()
    ticket = _get_jsapi_ticket(token)

    nonce_str = hashlib.md5(os.urandom(16)).hexdigest()[:16]
    timestamp = str(int(time.time()))
    raw = f"jsapi_ticket={ticket}&noncestr={nonce_str}&timestamp={timestamp}&url={raw_url}"
    signature = hashlib.sha1(raw.encode("utf-8")).hexdigest()

    return {
        "corpId": corp_id,
        "agentId": settings.DINGTALK_AGENT_ID or "",
        "timeStamp": timestamp,
        "nonceStr": nonce_str,
        "signature": signature,
    }


def _get_userid_from_auth_code(auth_code: str) -> str:
    token = _get_access_token()
    url = f"{settings.DINGTALK_USERID_URL}?access_token={token}"
    resp = _http_post_json(url, {"code": auth_code})
    _ensure_ok(resp, "获取userid")
    result = resp.get("result") or {}
    userid = result.get("userid")
    if not userid:
        raise HTTPException(status_code=502, detail="钉钉返回缺少 userid")
    return str(userid)


def _fetch_user(db: Session, userid: str) -> Dict[str, Any] | None:
    row = db.execute(_USER_SELECT_SQL, {"userid": userid}).mappings().first()
    return dict(row) if row else None


def login_with_auth_code(db: Session, auth_code: str) -> Dict[str, Any]:
    code = (auth_code or "").strip()
    if not code:
        raise HTTPException(status_code=400, detail="缺少 auth_code")

    userid = _get_userid_from_auth_code(code)
    user = _fetch_user(db, userid)
    if not user:
        raise HTTPException(status_code=403, detail="用户不存在或无权限")
    token = create_access_token(
        userid=str(user.get("dingtalk_userid") or userid),
        username=str(user.get("dingtalk_username") or userid),
    )
    return {"user": user, "token": token}


def refresh_user_profile(db: Session, userid: str) -> Dict[str, Any]:
    if not userid:
        raise HTTPException(status_code=400, detail="缺少 userid")

    user = _fetch_user(db, userid)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


def get_user_profile(db: Session, userid: str) -> Dict[str, Any]:
    user = _fetch_user(db, userid)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
