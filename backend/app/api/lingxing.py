"""
Lingxing Data API
提供独立站全站数据
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
import calendar
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.facebook_service import FacebookDashboardService
from app.services.google_ads_sync_service import GoogleAdsDataSyncService
from app.core.config import settings

router = APIRouter()

# 获取数据文件路径
DATA_FILE = Path(__file__).parent.parent.parent / "data" / "lingxing_month_data.json"
SALES_TARGET_FILE = Path(__file__).parent.parent.parent / "data" / "independent_station_month_data.json"


def load_lingxing_data() -> list:
    """加载lingxing月度数据"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载lingxing数据失败: {e}")
        return []


def load_sales_target_data() -> list:
    """加载独立站销售目标数据"""
    try:
        with open(SALES_TARGET_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载独立站销售目标数据失败: {e}")
        return []


def get_month_data_by_date(target_date: str) -> Dict[str, Any]:
    """
    根据日期获取本月和上月的数据（带推算）
    
    Args:
        target_date: 目标日期字符串 (YYYY-MM-DD)
        
    Returns:
        包含本月和上月数据的字典（本月数据已推算）
    """
    try:
        target = datetime.strptime(target_date, '%Y-%m-%d')
        current_month, current_year = target.month, target.year
        
        # 计算上个月
        last_month = 12 if current_month == 1 else current_month - 1
        last_year = current_year - 1 if current_month == 1 else current_year
        
        # 加载并查找匹配的月度数据
        all_data = load_lingxing_data()
        current_month_data = None
        last_month_data = None
        
        for month_data in all_data:
            month_num = month_data['month']
            start_date = datetime.strptime(month_data['start_date'], '%Y-%m-%d')
            
            if month_num == current_month and start_date.year == current_year:
                current_month_data = month_data
            elif month_num == last_month and start_date.year == last_year:
                last_month_data = month_data
        
        # 默认值
        default_data = {"conversion": 0, "conversion_value": 0, "end_date": target_date}
        
        return {
            "current_month": current_month_data or default_data,
            "last_month": last_month_data or default_data,
            "current_month_num": current_month,
            "last_month_num": last_month
        }
    except Exception as e:
        print(f"获取月度数据失败: {e}")
        return {
            "current_month": {"conversion": 0, "conversion_value": 0},
            "last_month": {"conversion": 0, "conversion_value": 0}
        }


def project_to_month_total(value: float, target_date: str, data_end_date: str) -> float:
    """
    将部分月度数据推算到整月
    
    Args:
        value: 原始值
        target_date: 目标日期
        data_end_date: 数据截止日期
        
    Returns:
        推算后的值
    """
    try:
        target = datetime.strptime(target_date, '%Y-%m-%d')
        end_date = datetime.strptime(data_end_date, '%Y-%m-%d')
        
        # 只有当月数据才需要推算
        if target.year == end_date.year and target.month == end_date.month:
            days_in_data = end_date.day
            total_days = calendar.monthrange(target.year, target.month)[1]
            
            if days_in_data > 0:
                projected = (value / days_in_data) * total_days
                print(f"月度推算: {value} / {days_in_data} * {total_days} = {projected}")
                return projected
        
        return value
    except Exception as e:
        print(f"推算失败: {e}")
        return value


@router.get("/website-monthly-simulation")
async def get_website_monthly_simulation(date: Optional[str] = None):
    """获取独立站全站月度模拟数据（带推算）"""
    try:
        date = date or datetime.now().strftime('%Y-%m-%d')
        month_data = get_month_data_by_date(date)
        
        current = month_data['current_month']
        last = month_data['last_month']
        
        # 对当月数据进行推算
        current_conversion = project_to_month_total(
            current.get('conversion', 0), date, current.get('end_date', date)
        )
        current_conversion_value = project_to_month_total(
            current.get('conversion_value', 0), date, current.get('end_date', date)
        )
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "conversions": {
                    "thisWeek": current_conversion,
                    "lastWeek": last.get('conversion', 0)
                },
                "conversionValue": {
                    "thisWeek": current_conversion_value,
                    "lastWeek": last.get('conversion_value', 0)
                },
                "monthInfo": {
                    "currentMonth": month_data['current_month_num'],
                    "lastMonth": month_data['last_month_num']
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取独立站数据失败: {str(e)}")


@router.get("/all-months")
async def get_all_months():
    """
    获取所有月的数据（用于调试或数据展示）
    
    Returns:
        所有月的数据列表
    """
    try:
        data = load_lingxing_data()
        return {
            "code": 200,
            "message": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取数据失败: {str(e)}"
        )


def get_month_range(target_date: str) -> Dict[str, str]:
    """根据日期计算本月和上月的起止日期"""
    target = datetime.strptime(target_date, '%Y-%m-%d')
    
    # 本月范围
    current_month_start = target.replace(day=1)
    _, last_day = calendar.monthrange(target.year, target.month)
    current_month_end = target.replace(day=last_day)
    
    # 上月范围
    last_month = 12 if target.month == 1 else target.month - 1
    last_year = target.year - 1 if target.month == 1 else target.year
    last_month_start = datetime(last_year, last_month, 1)
    _, last_month_last_day = calendar.monthrange(last_year, last_month)
    last_month_end = datetime(last_year, last_month, last_month_last_day)
    
    return {
        "current_month_start": current_month_start.strftime('%Y-%m-%d'),
        "current_month_end": current_month_end.strftime('%Y-%m-%d'),
        "last_month_start": last_month_start.strftime('%Y-%m-%d'),
        "last_month_end": last_month_end.strftime('%Y-%m-%d')
    }


@router.get("/monthly-cost")
async def get_monthly_cost(date: Optional[str] = None, db: Session = Depends(get_db)):
    """
    获取独立站全站月度模拟的花费数据（带推算）
    从Facebook和Google Ads获取本月和上月的广告花费
    """
    try:
        date = date or datetime.now().strftime('%Y-%m-%d')
        month_range = get_month_range(date)
        
        # Facebook账户ID
        FB_ACCOUNTS = ['2613027225660900', '1069516980635624']
        
        # 初始化服务
        fb_service = FacebookDashboardService(db)
        google_service = GoogleAdsDataSyncService(db)
        google_service.initialize_client()
        
        current_month_cost = 0.0
        last_month_cost = 0.0
        
        # 获取Facebook数据（两个账户）
        for account_id in FB_ACCOUNTS:
            try:
                fb_current = await fb_service.get_overview_data_from_api(
                    start_date=month_range["current_month_start"],
                    end_date=month_range["current_month_end"],
                    account_id=account_id
                )
                current_month_cost += fb_current.get('purchases', {}).get('spend', 0) or 0
                
                fb_last = await fb_service.get_overview_data_from_api(
                    start_date=month_range["last_month_start"],
                    end_date=month_range["last_month_end"],
                    account_id=account_id
                )
                last_month_cost += fb_last.get('purchases', {}).get('spend', 0) or 0
            except Exception as e:
                print(f"获取Facebook账户{account_id}花费失败: {e}")
        
        # 获取Google数据
        try:
            customer_id = settings.GOOGLE_ADS_CUSTOMER_ID.replace("-", "")
            
            success, google_current, _ = google_service.fetch_overview_summary(
                customer_id=customer_id,
                start_date=month_range["current_month_start"],
                end_date=month_range["current_month_end"]
            )
            if success:
                current_month_cost += google_current.get('cost', 0) or 0
            
            success, google_last, _ = google_service.fetch_overview_summary(
                customer_id=customer_id,
                start_date=month_range["last_month_start"],
                end_date=month_range["last_month_end"]
            )
            if success:
                last_month_cost += google_last.get('cost', 0) or 0
        except Exception as e:
            print(f"获取Google花费失败: {e}")
        
        # 对当月花费进行推算
        month_data = get_month_data_by_date(date)
        if 'end_date' in month_data.get('current_month', {}):
            current_month_cost = project_to_month_total(
                current_month_cost, date, month_data['current_month']['end_date']
            )
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "cost": {
                    "thisWeek": current_month_cost,
                    "lastWeek": last_month_cost
                },
                "monthRange": month_range
            }
        }
    except Exception as e:
        print(f"获取月度花费失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取月度花费失败: {str(e)}")


@router.get("/sales-target")
async def get_sales_target(date: Optional[str] = None):
    """获取独立站销售目标数据"""
    try:
        date = date or datetime.now().strftime('%Y-%m-%d')
        target = datetime.strptime(date, '%Y-%m-%d')
        current_month, current_year = target.month, target.year
        
        # 计算上个月
        last_month = 12 if current_month == 1 else current_month - 1
        last_year = current_year - 1 if current_month == 1 else current_year
        
        # 加载销售目标数据
        all_data = load_sales_target_data()
        current_month_data = None
        last_month_data = None
        
        for month_data in all_data:
            month_num = month_data['month']
            start_date = datetime.strptime(month_data['start_date'], '%Y-%m-%d')
            
            if month_num == current_month and start_date.year == current_year:
                current_month_data = month_data
            elif month_num == last_month and start_date.year == last_year:
                last_month_data = month_data
        
        # 默认值
        default_value = 0
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "conversionValue": {
                    "thisWeek": current_month_data.get('conversion_value', default_value) if current_month_data else default_value,
                    "lastWeek": last_month_data.get('conversion_value', default_value) if last_month_data else default_value
                },
                "monthInfo": {
                    "currentMonth": current_month,
                    "lastMonth": last_month
                }
            }
        }
    except Exception as e:
        print(f"获取销售目标数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取销售目标数据失败: {str(e)}")


@router.put("/sales-target")
async def update_sales_target(
    month: int,
    year: int,
    conversion_value: float
):
    """
    更新独立站销售目标数据
    
    Args:
        month: 月份 (1-12)
        year: 年份
        conversion_value: 转化价值
        
    Returns:
        更新结果
    """
    try:
        # 加载现有数据
        all_data = load_sales_target_data()
        
        # 查找并更新对应月份的数据
        updated = False
        for month_data in all_data:
            month_num = month_data['month']
            start_date = datetime.strptime(month_data['start_date'], '%Y-%m-%d')
            
            if month_num == month and start_date.year == year:
                month_data['conversion_value'] = conversion_value
                updated = True
                break
        
        # 如果没找到对应月份，创建新记录
        if not updated:
            # 计算该月的起止日期
            _, last_day = calendar.monthrange(year, month)
            new_record = {
                "month": month,
                "start_date": f"{year}-{month:02d}-01",
                "end_date": f"{year}-{month:02d}-{last_day:02d}",
                "conversion_value": conversion_value
            }
            all_data.append(new_record)
            # 按月份和年份排序
            all_data.sort(key=lambda x: (datetime.strptime(x['start_date'], '%Y-%m-%d')))
        
        # 保存到文件
        with open(SALES_TARGET_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        return {
            "code": 200,
            "message": "销售目标更新成功",
            "data": {
                "month": month,
                "year": year,
                "conversion_value": conversion_value,
                "updated": updated
            }
        }
    except Exception as e:
        print(f"更新销售目标数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新销售目标数据失败: {str(e)}")

