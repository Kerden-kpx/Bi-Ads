"""
基础Dashboard服务类
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi.concurrency import run_in_threadpool

from app.utils.helpers import calc_change, aggregate_data, calculate_averages
from app.utils.chart_helpers import generate_chart_data


class BaseDashboardService:
    """Dashboard服务基类 - 提供通用数据处理方法"""
    
    def __init__(self, db: Session, platform: str):
        self.db = db
        self.PLATFORM = platform
    
    async def execute_query(self, query: text, params: Dict[str, Any]) -> List[Any]:
        """
        执行SQL查询并返回结果
        
        Args:
            query: SQL查询对象
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        def _run():
            result = self.db.execute(query, params)
            return result.fetchall()
        
        return await run_in_threadpool(_run)
    
    def process_comparison_data(
        self,
        current_data: List[Dict[str, Any]],
        compare_data: Optional[List[Dict[str, Any]]],
        aggregate_fields: List[str],
        average_fields: List[str],
        change_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        处理对比数据的通用方法
        
        Args:
            current_data: 当前期间数据
            compare_data: 对比期间数据
            aggregate_fields: 需要聚合的字段
            average_fields: 需要计算平均值的字段
            change_mapping: 变化字段映射
            
        Returns:
            包含当前数据和对比数据的字典
        """
        # 聚合当前数据
        current_totals = aggregate_data(current_data, aggregate_fields)
        current_averages = calculate_averages(current_data, average_fields)
        current_result = {**current_totals, **current_averages}
        
        result = {"current": current_result}
        
        # 处理对比数据
        if compare_data:
            compare_totals = aggregate_data(compare_data, aggregate_fields)
            compare_averages = calculate_averages(compare_data, average_fields)
            compare_result = {**compare_totals, **compare_averages}
            
            result["compare"] = compare_result
            
            # 计算变化
            for field, change_field in change_mapping.items():
                current_val = current_result.get(field, 0)
                compare_val = compare_result.get(field, 0)
                result["current"][change_field] = calc_change(current_val, compare_val)
        else:
            # 没有对比数据，设置变化为0
            for change_field in change_mapping.values():
                result["current"][change_field] = 0
        
        return result
    
    def convert_row_to_dict(self, row: Any, field_mapping: Dict[str, tuple]) -> Dict[str, Any]:
        """
        将数据库行转换为字典
        
        Args:
            row: 数据库行对象
            field_mapping: 字段映射 {输出字段名: (数据库字段名, 类型转换函数)}
            
        Returns:
            转换后的字典
        """
        result = {}
        for output_field, (db_field, converter) in field_mapping.items():
            value = getattr(row, db_field, None)
            result[output_field] = converter(value) if value is not None else (0 if converter in [int, float] else "")
        return result
    
    def parse_row_with_mapping(
        self, 
        row: Any, 
        field_configs: Dict[str, tuple]
    ) -> Dict[str, Any]:
        """
        通用的行解析方法
        
        Args:
            row: 数据库行对象
            field_configs: 字段配置 {输出字段名: (数据库字段名, 类型, 精度, 默认值)}
                          类型: 'int', 'float', 'str'
                          精度: 小数位数 (仅对float有效)
                          默认值: 可选，默认int/float为0，str为""
        
        Returns:
            解析后的字典
        
        Example:
            field_configs = {
                "date": ("createtime", "str", None, ""),
                "impressions": ("impressions", "int", None, 0),
                "ctr": ("ctr", "float", 2, 0.0)
            }
        """
        result = {}
        for output_field, config in field_configs.items():
            db_field = config[0]
            field_type = config[1]
            precision = config[2] if len(config) > 2 else None
            default = config[3] if len(config) > 3 else (0 if field_type in ['int', 'float'] else "")
            
            value = getattr(row, db_field, None)
            
            if value is None:
                result[output_field] = default
            elif field_type == 'int':
                result[output_field] = int(value or 0)
            elif field_type == 'float':
                float_val = float(value or 0)
                result[output_field] = round(float_val, precision) if precision is not None else float_val
            else:  # str
                result[output_field] = str(value or "")
        
        return result
    
    def merge_comparison_data_generic(
        self,
        current_data: List[Dict[str, Any]],
        compare_data: List[Dict[str, Any]],
        field_mapping: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        通用的对比数据合并方法
        
        Args:
            current_data: 当前期间数据列表
            compare_data: 对比期间数据列表
            field_mapping: 字段映射 {原字段名: 对比字段前缀}
                          例如: {"impressions": "compare_", "clicks": "compare_"}
                          会生成: compare_impressions, compare_clicks
        
        Returns:
            合并后的数据列表
        """
        merged = []
        
        for i, current in enumerate(current_data):
            compare = compare_data[i] if i < len(compare_data) else {}
            
            # 复制当前数据
            merged_item = current.copy()
            
            # 添加对比数据
            for field, prefix in field_mapping.items():
                compare_field = f"{prefix}{field}"
                merged_item[compare_field] = compare.get(field, 0)
            
            merged.append(merged_item)
        
        return merged
    
    async def refresh_all_data(self) -> Dict[str, Any]:
        """刷新所有数据（从API拉取）- 子类可以重写此方法"""
        return {
            "refreshTime": datetime.now().isoformat(),
            "updatedRecords": 0,
            "message": f"此功能需要配置{self.PLATFORM.title()} API密钥"
        }
