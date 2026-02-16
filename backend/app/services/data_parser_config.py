"""
数据解析器配置 - 通过配置减少重复代码
"""

# ==================== Facebook解析配置 ====================

FACEBOOK_PARSE_CONFIGS = {
    "impression": {
        "date": ("createtime", "str"),
        "impressions": ("impressions", "int"),
        "reach": ("reach", "int"),
        "clicks": ("clicks", "int"),
        "unique_link_clicks": ("unique_link_clicks", "int"),
        "ctr": ("ctr", "float", 2),
        "cpm": ("cpm", "float", 2)
    },
    "purchase": {
        "date": ("createtime", "str"),
        "purchases_value": ("purchases_value", "float", 2),
        "spend": ("spend", "float", 2),
        "purchases": ("purchases", "int"),
        "adds_to_cart": ("adds_to_cart", "int"),
        "adds_payment_info": ("adds_payment_info", "int"),
        "roas": ("roas", "float", 2)
    },
    "performance_comparison": {
        "createtime": ("createtime", "str"),
        "impression": ("impression", "int"),
        "compare_impression": ("compare_impression", "int"),
        "reach": ("reach", "int"),
        "compare_reach": ("compare_reach", "int"),
        "clicks": ("clicks", "int"),
        "compare_clicks": ("compare_clicks", "int"),
        "unique_link_clicks": ("unique_link_clicks", "int"),
        "compare_unique_link_clicks": ("compare_unique_link_clicks", "int"),
        "purchases": ("purchases", "int"),
        "compare_purchases": ("compare_purchases", "int"),
        "purchases_value": ("purchases_value", "float"),
        "compare_purchases_value": ("compare_purchases_value", "float"),
        "spend": ("spend", "float"),
        "compare_spend": ("compare_spend", "float"),
        "adds_to_cart": ("adds_to_cart", "int"),
        "compare_adds_to_cart": ("compare_adds_to_cart", "int"),
        "adds_payment_info": ("adds_payment_info", "int"),
        "compare_adds_payment_info": ("compare_adds_payment_info", "int")
    },
    "campaign_performance": {
        "campaign_id": ("campaign_id", "str"),
        "campaign": ("campaign_name", "str"),
        "impression": ("impression", "int"),
        "spend": ("spend", "float", 2),
        "clicks": ("clicks", "int"),
        "purchases": ("purchases", "int"),
        "purchases_value": ("purchases_value", "float", 2),
        "roas": ("roas", "float", 2),
        "ctr": ("ctr", "float", 4),
        "cpm": ("cpm", "float", 2)
    },
    "ads_performance": {
        "campaign_name": ("campaign_name", "str"),
        "last_purchases": ("last_purchases", "int"),
        "last_purchases_value": ("last_purchases_value", "float", 2),
        "last_spend": ("last_spend", "float", 2),
        "last_roas": ("last_roas", "float", 2),
        "current_purchases": ("current_purchases", "int"),
        "current_purchases_value": ("current_purchases_value", "float", 2),
        "current_spend": ("current_spend", "float", 2),
        "current_roas": ("current_roas", "float", 2)
    },
    "adset_performance": {
        "campaign_id": ("adset_id", "str"),
        "name": ("name", "str"),
        "spend": ("spend", "float", 2),
        "spendPrevious": ("spend_previous", "float", 2),
        "purchases": ("purchases", "int"),
        "purchasesPrevious": ("purchases_previous", "int"),
        "purchasesValue": ("purchases_value", "float", 2),
        "purchasesValuePrevious": ("purchases_value_previous", "float", 2),
        "purchaseRoas": ("purchase_roas", "float", 2),
        "purchaseRoasPrevious": ("purchase_roas_previous", "float", 2),
        "ctr": ("ctr", "float", 4),
        "ctrPrevious": ("ctr_previous", "float", 4),
        "cpm": ("cpm", "float", 2),
        "cpmPrevious": ("cpm_previous", "float", 2)
    },
    "ad_detail_performance": {
        "ad_id": ("ad_id", "str"),
        "name": ("name", "str"),
        "spend": ("spend", "float", 2),
        "spendPrevious": ("spend_previous", "float", 2),
        "purchases": ("purchases", "int"),
        "purchasesPrevious": ("purchases_previous", "int"),
        "purchasesValue": ("purchases_value", "float", 2),
        "purchasesValuePrevious": ("purchases_value_previous", "float", 2),
        "purchaseRoas": ("purchase_roas", "float", 2),
        "purchaseRoasPrevious": ("purchase_roas_previous", "float", 2),
        "addsPaymentInfo": ("adds_payment_info", "int"),
        "addsPaymentInfoPrevious": ("adds_payment_info_previous", "int"),
        "addsToCart": ("adds_to_cart", "int"),
        "addsToCartPrevious": ("adds_to_cart_previous", "int"),
        "ctr": ("ctr", "float", 4),
        "ctrPrevious": ("ctr_previous", "float", 4),
        "cpm": ("cpm", "float", 2),
        "cpmPrevious": ("cpm_previous", "float", 2)
    }
}


# ==================== Google解析配置 ====================

GOOGLE_PARSE_CONFIGS = {
    "impression": {
        "date": ("createtime", "str"),
        "impressions": ("impressions", "int"),
        "clicks": ("clicks", "int"),
        "ctr": ("ctr", "float", 2),
        "cpm": ("cpm", "float", 2)
    },
    "conversion": {
        "date": ("createtime", "str"),
        "conversion_value": ("conversion_value", "float", 2),
        "cost": ("cost", "float", 2),
        "conversions": ("conversions", "float", 2),
        "roas": ("roas", "float", 2)
    },
    "performance_comparison": {
        "createtime": ("createtime", "str"),
        "impression": ("impression", "int"),
        "compare_impression": ("compare_impression", "int"),
        "clicks": ("clicks", "int"),
        "compare_clicks": ("compare_clicks", "int"),
        "conversions": ("conversions", "float"),
        "compare_conversions": ("compare_conversions", "float"),
        "conversion_value": ("conversion_value", "float"),
        "compare_conversion_value": ("compare_conversion_value", "float"),
        "cost": ("cost", "float"),
        "compare_cost": ("compare_cost", "float")
    },
    "campaign_performance": {
        "campaign_id": ("campaign_id", "str"),
        "campaign": ("campaign", "str"),
        "impression": ("impression", "int"),
        "cost": ("cost", "float", 2),
        "clicks": ("clicks", "int"),
        "conversions": ("conversions", "float", 2),
        "conversion_value": ("conversion_value", "float", 2),
        "roas": ("roas", "float", 2),
        "ctr": ("ctr", "float", 4),
        "cpc": ("cpc", "float", 2)
    },
    "ads_performance": {
        "campaign_name": ("campaign_name", "str"),
        "last_conversions": ("last_conversions", "float", 2),
        "last_conversion_value": ("last_conversion_value", "float", 2),
        "last_cost": ("last_cost", "float", 2),
        "last_roas": ("last_roas", "float", 2),
        "current_conversions": ("current_conversions", "float", 2),
        "current_conversion_value": ("current_conversion_value", "float", 2),
        "current_cost": ("current_cost", "float", 2),
        "current_roas": ("current_roas", "float", 2)
    }
}


def get_parse_config(platform: str, config_name: str):
    """
    获取解析配置
    
    Args:
        platform: 平台名称 ('facebook' 或 'google')
        config_name: 配置名称
        
    Returns:
        解析配置字典
    """
    configs = FACEBOOK_PARSE_CONFIGS if platform == 'facebook' else GOOGLE_PARSE_CONFIGS
    return configs.get(config_name, {})
