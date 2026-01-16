"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基础配置
    APP_NAME: str = "Ads BI Dashboard Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    PORT: int = 7800
    
    # CORS配置
    FRONTEND_URL: str = "http://localhost:5173"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """允许的CORS源"""
        if self.DEBUG:
            # 开发环境：允许所有源（包括局域网访问）
            return ["*"]
        else:
            # 生产环境：只允许特定源
            return [self.FRONTEND_URL, "http://localhost:5173"]
    
    # 数据库配置（敏感信息请在 .env 文件中配置）
    DB_HOST: str = "localhost"
    DB_PORT: int = 15388
    DB_NAME: str = "ads_data"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""  # 请在 .env 文件中设置
    
    @property
    def DATABASE_URL(self) -> str:
        """数据库连接URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    # Facebook API配置（请在 .env 文件中配置）
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    FACEBOOK_ACCESS_TOKEN: str = ""  # 请在 .env 文件中设置
    FACEBOOK_AD_ACCOUNT_ID: str = ""  # 账户ID（不含act_前缀）
    FACEBOOK_API_MAX_WORKERS: int = 8  # Facebook API线程池最大并发数
    FACEBOOK_PROXY_URL: str = ""  # Facebook API 代理地址（留空则直连）
    FACEBOOK_ADS_PROXY_URL: str = ""  # 兼容旧配置
    FACEBOOK_DAILY_SYNC_ENABLED: bool = False  # 启用每日自动同步
    FACEBOOK_DAILY_SYNC_DAYS: int = 30  # 同步最近多少天的数据
    FACEBOOK_DAILY_SYNC_INCLUDE_TODAY: bool = False  # 是否包含今天作为结束日期
    FACEBOOK_DAILY_SYNC_PROFILE: str = "default"  # 同步性能配置: default|conservative|aggressive
    FACEBOOK_DAILY_SYNC_ACCOUNT_IDS: str = ""  # 逗号分隔的账号列表，留空则使用 FACEBOOK_AD_ACCOUNT_ID
    
    # Google Ads API配置（请在 .env 文件中配置）
    GOOGLE_ADS_DEVELOPER_TOKEN: str = ""  # Google Ads开发者令牌
    GOOGLE_ADS_CUSTOMER_ID: str = ""  # 客户ID
    GOOGLE_ADS_CONFIG_PATH: str = "config/google-ads.yaml"  # 配置文件路径（相对于项目根目录）
    GOOGLE_ADS_JSON_KEY_FILE_PATH: str = "config/seismic-relic-466902-q4-c98779167f0b.json"  # 服务账号JSON密钥文件路径
    GOOGLE_ADS_PROXY_URL: str = "http://127.0.0.1:10808"  # 代理地址
    PROXY_URL: str = ""  # 通用代理地址（可用于Facebook/Google）
    GOOGLE_ADS_MAX_WORKERS: int = 8  # Google Ads API 并发线程池最大线程数
    GOOGLE_ADS_SUMMARY_MAX_WORKERS: int = 4  # 概览汇总线程池最大线程数
    GOOGLE_ADS_DAILY_SYNC_ENABLED: bool = False  # 启用每日自动同步
    GOOGLE_ADS_DAILY_SYNC_DAYS: int = 30  # 同步最近多少天的数据
    GOOGLE_ADS_DAILY_SYNC_INCLUDE_TODAY: bool = False  # 是否包含今天作为结束日期

    @property
    def FACEBOOK_PROXY_URL_EFFECTIVE(self) -> str:
        """Facebook 代理地址（优先专用配置，其次旧配置，再使用通用代理）"""
        return self.FACEBOOK_PROXY_URL or self.FACEBOOK_ADS_PROXY_URL or self.PROXY_URL

    @property
    def GOOGLE_ADS_PROXY_URL_EFFECTIVE(self) -> str:
        """Google Ads 代理地址（优先专用配置，再使用通用代理）"""
        return self.GOOGLE_ADS_PROXY_URL or self.PROXY_URL
    
    
    # Gemini AI配置（请在 .env 文件中配置）
    GEMINI_API_KEY: str = ""  # Google Gemini API密钥
    GEMINI_MODEL: str = "gemini-2.5-pro"  # 支持多个模型，用逗号分隔（例如：gemini-2.0-flash-exp,gemini-1.5-flash,gemini-1.5-pro）
    
    @property
    def GEMINI_MODELS(self) -> List[str]:
        """获取所有可用的Gemini模型列表（用于配额轮换）"""
        if not self.GEMINI_MODEL:
            return []
        # 支持用逗号分隔多个模型
        models = [model.strip() for model in self.GEMINI_MODEL.split(",") if model.strip()]
        return models
    
    # Facebook 产品名称配置（用于 Facebook Ads 数据筛选和分类）
    # 可在 .env 中通过 FACEBOOK_PRODUCT_NAMES 覆盖，使用逗号分隔
    FACEBOOK_PRODUCT_NAMES: str = "埋头钻,金刚石切割片,阶梯钻套装,超长镀钛OMT,陶瓷百叶轮,百叶轮,电动螺丝刀,批发装,切木锯条,黑曜石OMT,黑曜石,16pcs金属开孔器,超长弧形OMT"
    
    @property
    def FACEBOOK_PRODUCT_NAMES_LIST(self) -> List[str]:
        """获取 Facebook 产品名称列表"""
        return [name.strip() for name in self.FACEBOOK_PRODUCT_NAMES.split(",") if name.strip()]
    
    @property
    def FACEBOOK_PRODUCT_NAMES_PATTERN(self) -> str:
        """获取 Facebook 产品名称的正则表达式模式"""
        return "|".join(self.FACEBOOK_PRODUCT_NAMES_LIST)
    
    # Google Ads 产品名称配置（用于 Google Ads 数据筛选和分类）
    # 可在 .env 中通过 GOOGLE_PRODUCT_NAMES 覆盖，使用逗号分隔
    GOOGLE_PRODUCT_NAMES: str = "批发装,埋头钻,阶梯钻套装,切木锯条,百叶轮,陶瓷百叶轮,h"
    
    @property
    def GOOGLE_PRODUCT_NAMES_LIST(self) -> List[str]:
        """获取 Google Ads 产品名称列表"""
        return [name.strip() for name in self.GOOGLE_PRODUCT_NAMES.split(",") if name.strip()]
    
    @property
    def GOOGLE_PRODUCT_NAMES_PATTERN(self) -> str:
        """获取 Google Ads 产品名称的正则表达式模式"""
        return "|".join(self.GOOGLE_PRODUCT_NAMES_LIST)
    
    # 向后兼容：保留旧的 PRODUCT_NAMES（默认使用 Facebook 的配置）
    @property
    def PRODUCT_NAMES(self) -> str:
        """向后兼容的产品名称配置"""
        return self.FACEBOOK_PRODUCT_NAMES
    
    @property
    def PRODUCT_NAMES_LIST(self) -> List[str]:
        """向后兼容：获取产品名称列表"""
        return self.FACEBOOK_PRODUCT_NAMES_LIST
    
    @property
    def PRODUCT_NAMES_PATTERN(self) -> str:
        """向后兼容：获取产品名称的正则表达式模式"""
        return self.FACEBOOK_PRODUCT_NAMES_PATTERN
    
    # Redis缓存配置（请在 .env 文件中配置）
    REDIS_HOST: str = "localhost"  # Redis服务器地址
    REDIS_PORT: int = 6379  # Redis端口
    REDIS_DB: int = 0  # Redis数据库编号（0-15）
    REDIS_PASSWORD: str = ""  # Redis密码（如果设置了的话）
    REDIS_ENABLED: bool = True  # 是否启用Redis缓存
    
    # 缓存TTL配置（秒）
    CACHE_TTL_SHORT: int = 1800  # 短期缓存：30分钟（概览数据）
    CACHE_TTL_MEDIUM: int = 3600  # 中期缓存：1小时（广告数据）
    CACHE_TTL_LONG: int = 7200  # 长期缓存：2小时（性能分析、历史数据）
    
    # JWT配置（请在 .env 文件中设置生产环境密钥）
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略 .env 中未定义的额外字段
    
    def reload(self):
        """
        重新加载配置
        从 .env 文件重新读取配置并更新当前实例
        """
        # 重新加载环境变量
        if os.path.exists(self.Config.env_file):
            from dotenv import load_dotenv
            load_dotenv(self.Config.env_file, override=True)
        
        # 重新初始化所有字段
        new_settings = Settings()
        
        # 更新当前实例的所有字段
        for field_name in self.__fields__.keys():
            setattr(self, field_name, getattr(new_settings, field_name))


# 创建全局设置实例
settings = Settings()
