"""
基础数据同步服务类
提供通用的数据同步逻辑
"""
import logging
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger("app.services.base_sync_service")
ALLOWED_SYNC_TABLES = frozenset(
    {
        "fact_bi_ads_google_campaign",
        "fact_bi_ads_facebook_campaign",
    }
)


def _log_print(*args, **kwargs) -> None:
    sep = kwargs.get("sep", " ")
    message = sep.join(str(arg) for arg in args).strip()
    if not message:
        return
    if "❌" in message:
        logger.error(message)
    elif "⚠️" in message or "警告" in message:
        logger.warning(message)
    elif "⏳" in message or "进度" in message:
        logger.debug(message)
    else:
        logger.info(message)


class BaseSyncService:
    """数据同步服务基类"""
    
    def __init__(self, db: Session, table_name: str):
        """
        初始化服务
        
        Args:
            db: 数据库会话
            table_name: 表名
        """
        if table_name not in ALLOWED_SYNC_TABLES:
            raise ValueError(f"不允许的同步表名: {table_name}")
        self.db = db
        self.table_name = table_name
    
    def delete_data_in_range(self, start_date: str, end_date: str) -> None:
        """
        删除指定日期范围内的数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        """
        delete_query = text(f"DELETE FROM {self.table_name} WHERE createtime BETWEEN :start_date AND :end_date")
        self.db.execute(delete_query, {"start_date": start_date, "end_date": end_date})
        _log_print(f"🗑️  已删除日期范围 {start_date} 到 {end_date} 的数据")
    
    def batch_insert(
        self, 
        insert_query: text, 
        data_dicts: List[Dict[str, Any]], 
        batch_size: int = 1000
    ) -> int:
        """
        批量插入数据（优化版本：支持分批提交）
        
        Args:
            insert_query: 插入SQL语句
            data_dicts: 数据字典列表
            batch_size: 每批插入的记录数（默认1000）
            
        Returns:
            插入的记录数
        """
        if not data_dicts:
            return 0
        
        total_count = len(data_dicts)
        inserted_count = 0
        
        # 分批插入以提高性能和内存使用效率
        for i in range(0, total_count, batch_size):
            batch = data_dicts[i:i + batch_size]
            self.db.execute(insert_query, batch)
            self.db.commit()
            inserted_count += len(batch)
            
            # 显示进度
            progress = (inserted_count / total_count) * 100
            _log_print(f"⏳ 插入进度: {inserted_count}/{total_count} ({progress:.1f}%)")
        
        _log_print(f"✅ 成功插入 {inserted_count} 条数据")
        return inserted_count
    
    def create_sync_result(
        self, 
        success: bool, 
        message: str, 
        records_synced: int = 0, 
        errors: List[str] = None
    ) -> Dict[str, Any]:
        """
        创建统一的同步结果
        
        Args:
            success: 是否成功
            message: 结果消息
            records_synced: 同步的记录数
            errors: 错误列表
            
        Returns:
            同步结果字典
        """
        return {
            "success": success,
            "message": message,
            "records_synced": records_synced,
            "errors": errors or []
        }
