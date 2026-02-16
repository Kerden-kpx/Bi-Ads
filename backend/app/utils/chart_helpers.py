"""
图表数据生成工具
"""
from typing import List, Dict, Any
from .helpers import format_date_label


def generate_chart_data(
    data: List[Dict[str, Any]],
    date_field: str,
    datasets_config: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    生成图表数据的通用方法
    
    Args:
        data: 数据列表
        date_field: 日期字段名
        datasets_config: 数据集配置列表
            [{
                "label": "显示名称",
                "field": "数据字段名",
                "borderColor": "#颜色",
                "backgroundColor": "#颜色",
                "fill": True/False,
                "stack": "stack1" (可选),
                "borderWidth": 2 (可选)
            }]
    
    Returns:
        图表数据字典
    """
    if not data:
        return {"labels": [], "datasets": []}
    
    # 按日期排序
    sorted_data = sorted(data, key=lambda x: x.get(date_field, ""))
    
    # 格式化日期标签
    labels = [format_date_label(d.get(date_field, "")) for d in sorted_data]
    
    # 构建数据集
    datasets = []
    for config in datasets_config:
        dataset = {
            "label": config["label"],
            "data": [d.get(config["field"], 0) for d in sorted_data],
            "borderColor": config["borderColor"],
            "backgroundColor": config.get("backgroundColor", config["borderColor"]),
            "fill": config.get("fill", True),
            "tension": config.get("tension", 0.4),
            "pointRadius": config.get("pointRadius", 0),
            "pointHoverRadius": config.get("pointHoverRadius", 6),
        }
        
        # 可选字段
        if "stack" in config:
            dataset["stack"] = config["stack"]
        if "borderWidth" in config:
            dataset["borderWidth"] = config["borderWidth"]
        
        datasets.append(dataset)
    
    return {"labels": labels, "datasets": datasets}


# 预定义的图表配置
FACEBOOK_IMPRESSION_CHART_CONFIG = [
    {
        "label": "Impressions",
        "field": "impressions",
        "borderColor": "#5B8FF9",
        "backgroundColor": "#5B8FF9",
        "fill": True,
        "stack": "stack1"
    },
    {
        "label": "Total Reach",
        "field": "reach",
        "borderColor": "#5D7092",
        "backgroundColor": "#5D7092",
        "fill": True,
        "stack": "stack1"
    },
    {
        "label": "Clicks (All)",
        "field": "clicks",
        "borderColor": "#5B8FF9",
        "backgroundColor": "transparent",
        "fill": False,
        "borderWidth": 2
    },
    {
        "label": "Unique Link Clicks",
        "field": "unique_link_clicks",
        "borderColor": "#5B8FF9",
        "backgroundColor": "#5B8FF9",
        "fill": True,
        "stack": "stack1"
    }
]

FACEBOOK_PURCHASE_CHART_CONFIG = [
    {
        "label": "Purchases Value",
        "field": "purchases_value",
        "borderColor": "#6B9EF5",
        "backgroundColor": "#6B9EF5",
        "fill": True,
        "borderWidth": 0
    },
    {
        "label": "Spend",
        "field": "spend",
        "borderColor": "#3B5A8F",
        "backgroundColor": "#3B5A8F",
        "fill": True,
        "borderWidth": 0
    }
]

GOOGLE_IMPRESSION_CHART_CONFIG = [
    {
        "label": "Impressions",
        "field": "impressions",
        "borderColor": "#5676ff",
        "backgroundColor": "#5676ff",
        "fill": True,
        "stack": "stack1"
    },
    {
        "label": "Clicks",
        "field": "clicks",
        "borderColor": "#0a0b5c",
        "backgroundColor": "#0a0b5c",
        "fill": True,
        "stack": "stack1"
    }
]

GOOGLE_CONVERSION_CHART_CONFIG = [
    {
        "label": "Conversion Value",
        "field": "conversion_value",
        "borderColor": "#5676ff",
        "backgroundColor": "#5676ff",
        "fill": True,
        "borderWidth": 0
    },
    {
        "label": "Cost",
        "field": "cost",
        "borderColor": "#0a0b5c",
        "backgroundColor": "#0a0b5c",
        "fill": True,
        "borderWidth": 0
    }
]

