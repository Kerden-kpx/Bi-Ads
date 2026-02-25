"""
钉钉告警通知服务（使用本项目自身配置）
"""
from __future__ import annotations

import importlib
import logging
import os
import sys

from app.core.config import settings

logger = logging.getLogger("app.services.dingtalk_notify")

_COMMON_SEND_USER_TEXT = None
_COMMON_LOAD_ATTEMPTED = False
_COMMON_LOAD_ERROR = ""
_MISSING_SENDER_WARNED = False


def _load_common_sender():
    """优先复用 Common/common 包中的 dingtalk_client.send_user_text"""
    global _COMMON_SEND_USER_TEXT, _COMMON_LOAD_ATTEMPTED, _COMMON_LOAD_ERROR
    if _COMMON_LOAD_ATTEMPTED:
        return _COMMON_SEND_USER_TEXT
    _COMMON_LOAD_ATTEMPTED = True

    # Common 目录的父目录应在 sys.path 中，才能 import Common/common.*
    candidate_roots = ["/yida", "/mnt/d/Yida_project"]
    env_root = os.getenv("YIDA_COMMON_PARENT")
    if env_root:
        candidate_roots.insert(0, env_root)

    # 兼容目录改名：默认尝试 Common，再尝试 common；可通过环境变量覆盖。
    candidate_pkg_names = ["Common", "common"]
    env_pkg_name = os.getenv("YIDA_COMMON_PACKAGE")
    if env_pkg_name:
        candidate_pkg_names.insert(0, env_pkg_name)

    for root in candidate_roots:
        if not os.path.isdir(root):
            continue
        for pkg_name in candidate_pkg_names:
            common_dir = os.path.join(root, pkg_name)
            if os.path.isdir(common_dir) and root not in sys.path:
                sys.path.insert(0, root)
                break

    for pkg_name in candidate_pkg_names:
        try:
            module = importlib.import_module(f"{pkg_name}.api.dingtalk_client")
            _COMMON_SEND_USER_TEXT = getattr(module, "send_user_text", None)
            if _COMMON_SEND_USER_TEXT:
                _COMMON_LOAD_ERROR = ""
                return _COMMON_SEND_USER_TEXT
        except Exception as exc:
            _COMMON_LOAD_ERROR = str(exc)
            continue

    _COMMON_SEND_USER_TEXT = None
    return _COMMON_SEND_USER_TEXT


def send_error_notification(text: str) -> None:
    """发送异常通知给技术人员（单聊）"""
    global _MISSING_SENDER_WARNED
    if not settings.DINGTALK_NOTIFY_ENABLED:
        return
    if not settings.DINGTALK_ROBOT_CODE:
        logger.warning("skip dingtalk notify: DINGTALK_ROBOT_CODE is empty")
        return
    user_ids = settings.DINGTALK_TECH_USER_ID_LIST
    if not user_ids:
        logger.warning("skip dingtalk notify: DINGTALK_TECH_USER_IDS is empty")
        return

    common_sender = _load_common_sender()
    if not common_sender:
        if not _MISSING_SENDER_WARNED:
            reason = f", reason={_COMMON_LOAD_ERROR}" if _COMMON_LOAD_ERROR else ""
            logger.warning(
                "skip dingtalk notify: Common/common.api.dingtalk_client.send_user_text not available%s",
                reason,
            )
            _MISSING_SENDER_WARNED = True
        return

    try:
        for user_id in user_ids:
            common_sender(
                user_id=user_id,
                text=text,
                app_key=settings.DINGTALK_APP_KEY,
                app_secret=settings.DINGTALK_APP_SECRET,
                robot_code=settings.DINGTALK_ROBOT_CODE,
            )
    except Exception as exc:
        logger.exception("send dingtalk notify failed: %s", exc)
