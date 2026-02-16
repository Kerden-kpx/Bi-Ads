"""
数据库配置和连接
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# 创建数据库引擎（优化连接池配置以提升性能）
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,              # 连接前检查连接是否有效
    pool_recycle=3600,                # 1小时后回收连接
    pool_size=20,                     # 连接池大小增加到20（默认5）
    max_overflow=40,                  # 最大溢出连接数增加到40（默认10）
    pool_timeout=30,                  # 连接超时30秒
    echo=settings.DEBUG,
    execution_options={
        "isolation_level": "READ COMMITTED"  # 设置事务隔离级别
    }
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话
    用于FastAPI依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)

