"""
日志与请求追踪工具
"""
from __future__ import annotations

import logging
import sys
import uuid
from contextvars import ContextVar, Token

_REQUEST_ID_CTX: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """将 request_id 注入日志记录"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _REQUEST_ID_CTX.get("-")
        return True


def setup_logging(debug: bool = False) -> None:
    """初始化全局日志格式与级别"""
    level = logging.DEBUG if debug else logging.INFO
    root_logger = logging.getLogger()

    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        root_logger.addHandler(handler)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(name)s] [rid=%(request_id)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    for handler in root_logger.handlers:
        handler.setFormatter(formatter)
        if not any(isinstance(f, RequestIdFilter) for f in handler.filters):
            handler.addFilter(RequestIdFilter())

    root_logger.setLevel(level)


def build_request_id(candidate: str | None = None) -> str:
    """构建规范 request_id（优先复用请求头）"""
    value = (candidate or "").strip()
    if value and len(value) <= 64 and value.replace("-", "").isalnum():
        return value
    return uuid.uuid4().hex[:16]


def set_request_id(request_id: str) -> Token:
    """写入上下文 request_id，并返回上下文 token"""
    return _REQUEST_ID_CTX.set(request_id)


def reset_request_id(token: Token) -> None:
    """恢复上下文 request_id"""
    _REQUEST_ID_CTX.reset(token)
