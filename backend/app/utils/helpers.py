"""
通用工具函数
"""
import re
from datetime import datetime
from typing import List, Dict, Any, Optional


def calc_change(current_val: float, compare_val: float) -> float:
    """
    计算变化百分比
    
    Args:
        current_val: 当前值
        compare_val: 对比值
        
    Returns:
        变化百分比
    """
    if compare_val == 0:
        return 0
    return round(((current_val - compare_val) / compare_val) * 100, 2)


def format_date_label(date_str: str, date_format: str = "%Y-%m-%d") -> str:
    """
    格式化日期标签
    
    Args:
        date_str: 日期字符串
        date_format: 输入日期格式
        
    Returns:
        格式化后的日期标签 (如 "01 Jan")
    """
    try:
        date_obj = datetime.strptime(date_str, date_format)
        return date_obj.strftime("%d %b")
    except:
        return date_str


def aggregate_data(data_list: List[Dict[str, Any]], fields: List[str]) -> Dict[str, Any]:
    """
    聚合数据列表中的指定字段
    
    Args:
        data_list: 数据列表
        fields: 需要聚合的字段列表
        
    Returns:
        聚合后的数据字典
    """
    result = {}
    for field in fields:
        result[field] = sum(d.get(field, 0) for d in data_list)
    return result


def calculate_averages(data_list: List[Dict[str, Any]], fields: List[str]) -> Dict[str, float]:
    """
    计算平均值
    
    Args:
        data_list: 数据列表
        fields: 需要计算平均值的字段列表
        
    Returns:
        平均值字典
    """
    result = {}
    count = len(data_list) if data_list else 1
    for field in fields:
        total = sum(d.get(field, 0) for d in data_list)
        result[field] = round(total / count, 2) if count > 0 else 0
    return result


def safe_divide(numerator: float, denominator: float, default: float = 0, precision: int = 2) -> float:
    """
    安全除法，避免除零错误
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 默认值（当分母为0时）
        precision: 精度
        
    Returns:
        计算结果
    """
    if denominator == 0:
        return default
    return round(numerator / denominator, precision)


def normalize_account_id(account_id: Optional[str], prefix: str = "act_") -> Optional[str]:
    """
    规范化账户ID，确保以指定前缀开头
    
    Args:
        account_id: 账户ID（可能带或不带前缀）
        prefix: 需要的前缀，默认为 act_
        
    Returns:
        带前缀的账户ID，如果输入为None则返回None
    """
    if not account_id:
        return None
    return f'{prefix}{account_id}' if not account_id.startswith(prefix) else account_id


def escape_mysql_regex_literal(value: str) -> str:
    """
    将字符串转义为 MySQL REGEXP 可安全使用的字面量模式
    """
    return re.escape(str(value or ""))


def build_mysql_regex_union(values: List[str]) -> str:
    """
    构建由多个字面量组成的正则 OR 模式
    """
    escaped = [escape_mysql_regex_literal(v.strip()) for v in values if isinstance(v, str) and v.strip()]
    return "|".join(escaped)
