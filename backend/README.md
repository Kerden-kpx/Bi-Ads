# Ads BI Dashboard Backend

广告数据 BI 仪表板后端 API - 支持 Facebook Ads 和 Google Ads 数据管理与分析

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [API 文档](#api-文档)
- [数据库](#数据库)
- [开发指南](#开发指南)
- [部署](#部署)
- [常见问题](#常见问题)

## 项目简介

这是一个基于 FastAPI 构建的广告数据 BI 仪表板后端系统，提供 Facebook Ads 和 Google Ads 的数据获取、存储、分析和可视化支持。系统集成了 Google Gemini AI，可对广告数据进行智能分析和洞察。

### 主要功能

- **多平台支持**：同时支持 Facebook Ads 和 Google Ads 平台
- **数据同步**：自动从广告平台同步数据到本地数据库
- **数据分析**：提供多维度的数据统计和对比分析
- **AI 分析**：集成 Google Gemini AI 进行智能数据分析
- **RESTful API**：提供完整的 REST API 接口
- **自动文档**：自动生成交互式 API 文档

## 功能特性

### Facebook Ads 功能
- ✅ 账户数据概览
- ✅ 广告系列性能分析
- ✅ 广告组性能分析
- ✅ 广告详情性能分析
- ✅ 印象与触达数据统计
- ✅ 购买与花费数据统计
- ✅ 双账户对比分析
- ✅ 时间段对比分析
- ✅ AI 智能分析与建议

### Google Ads 功能
- ✅ 账户数据概览
- ✅ 广告系列性能分析
- ✅ 印象与点击数据统计
- ✅ 购买与花费数据统计
- ✅ 时间段对比分析
- ✅ AI 智能分析与建议
- ✅ 自动数据同步

## 技术栈

### 核心框架
- **FastAPI** 0.104.1 - 高性能 Web 框架
- **Uvicorn** 0.24.0 - ASGI 服务器
- **Python** 3.8+ - 编程语言

### 数据库
- **MySQL** - 关系型数据库
- **SQLAlchemy** 2.0.23 - ORM 框架
- **PyMySQL** 1.1.0 - MySQL 驱动
- **Alembic** 1.12.1 - 数据库迁移工具

### 数据验证
- **Pydantic** 2.5.0 - 数据验证和设置管理
- **Pydantic-Settings** 2.1.0 - 配置管理

### 第三方 API
- **Facebook Business SDK** 21.0.0 - Facebook Ads API
- **Google Ads API** 27.0.0 - Google Ads API
- **Google Generative AI** - Google Gemini AI

### 工具库
- **Pandas** 2.1.4 - 数据处理
- **Python-dotenv** 1.0.0 - 环境变量管理
- **Tenacity** 8.2.3 - 重试机制
- **HTTPX** 0.25.2 - 异步 HTTP 客户端
- **OpenPyXL** 3.1.2 - Excel 处理

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── api/                      # API 路由
│   │   ├── facebook.py          # Facebook Ads 路由
│   │   └── google.py            # Google Ads 路由
│   ├── core/                    # 核心配置
│   │   ├── config.py            # 应用配置
│   │   └── database.py          # 数据库配置
│   ├── models/                  # 数据模型
│   │   └── dashboard.py         # 仪表板数据模型
│   ├── schemas/                 # Pydantic 模式
│   │   └── dashboard.py         # 仪表板数据模式
│   ├── services/                # 业务逻辑
│   │   ├── base_service.py                    # 基础服务
│   │   ├── base_sync_service.py               # 基础同步服务
│   │   ├── facebook_service.py                # Facebook 服务
│   │   ├── facebook_ads_sync_service.py       # Facebook 数据同步
│   │   ├── google_service.py                  # Google 服务
│   │   ├── google_ads_sync_service.py         # Google 数据同步
│   │   └── gemini_ai_service.py               # AI 分析服务
│   └── utils/                   # 工具函数
│       ├── api_helpers.py       # API 辅助函数
│       ├── chart_helpers.py     # 图表辅助函数
│       └── helpers.py           # 通用辅助函数
├── config/                      # 配置文件
│   ├── google-ads.yaml          # Google Ads 配置
│   └── seismic-relic-*.json     # Google 服务账号密钥
├── scripts/                     # 脚本文件
│   └── create_database.sql      # 数据库创建脚本
├── main.py                      # 应用入口
├── requirements.txt             # Python 依赖
├── .env.example                 # 环境变量示例
└── README.md                    # 项目文档
```

## 快速开始

### 前置要求

- Python 3.8 或更高版本
- MySQL 5.7 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆项目**
```bash
cd backend
```

2. **创建虚拟环境**（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置数据库**
```bash
# 登录 MySQL
mysql -u root -p

# 执行创建数据库脚本
source scripts/create_database.sql
```

5. **配置环境变量**

复制 `.env.example` 为 `.env` 并填写配置：
```bash
cp .env.example .env
```

编辑 `.env` 文件（参考 [配置说明](#配置说明)）

6. **启动服务**
```bash
# 开发模式（自动重载）
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 7800
```

7. **访问 API 文档**
- Swagger UI: http://localhost:7800/docs
- ReDoc: http://localhost:7800/redoc
- 健康检查: http://localhost:7800/health

## 配置说明

### 环境变量配置

创建 `.env` 文件并配置以下参数：

```env
# ========== 应用基础配置 ==========
APP_NAME=Ads BI Dashboard Backend
APP_VERSION=1.0.0
DEBUG=True
PORT=7800

# ========== 前端配置 ==========
FRONTEND_URL=http://localhost:5173

# ========== 数据库配置 ==========
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ads_data
DB_USER=root
DB_PASSWORD=your_password_here

# ========== Facebook API 配置 ==========
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_AD_ACCOUNT_ID=your_account_id

# ========== Google Ads API 配置 ==========
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CUSTOMER_ID=your_customer_id
GOOGLE_ADS_CONFIG_PATH=config/google-ads.yaml
GOOGLE_ADS_JSON_KEY_FILE_PATH=config/your-service-account-key.json
GOOGLE_ADS_PROXY_URL=http://127.0.0.1:10808
GOOGLE_ADS_SYNC_YEAR=2025

# OAuth2 配置（可选，用于替代 Service Account）
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token

# ========== Google Gemini AI 配置 ==========
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-pro

# ========== 产品名称配置 ==========
# 用于广告数据筛选和分类，使用逗号分隔
PRODUCT_NAMES=埋头钻,金刚石切割片,阶梯钻套装,超长镀钛OMT,陶瓷百叶轮

# ========== JWT 配置 ==========
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 获取 API 密钥

#### Facebook Ads API
1. 访问 [Facebook Developers](https://developers.facebook.com/)
2. 创建应用并获取 App ID 和 App Secret
3. 生成长期访问令牌（Access Token）
4. 获取广告账户 ID（在 Facebook Ads Manager 中）

#### Google Ads API
1. 访问 [Google Ads API](https://developers.google.com/google-ads/api)
2. 申请开发者令牌（Developer Token）
3. 创建 Google Cloud 项目并启用 Google Ads API
4. 创建服务账号并下载 JSON 密钥文件
5. 配置 OAuth2 凭证（可选）

#### Google Gemini AI
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建 API 密钥
3. 复制密钥到 `.env` 文件

## API 文档

### 接口概览

#### 健康检查
- `GET /health` - 健康检查接口
- `GET /` - 根路径，返回 API 信息

#### Facebook Ads API
- `GET /api/dashboard/facebook/impressions` - 获取印象数据
- `GET /api/dashboard/facebook/purchases` - 获取购买数据
- `GET /api/dashboard/facebook/performance-comparison` - 性能对比
- `GET /api/dashboard/facebook/ads-performance-overview` - 广告性能概览
- `GET /api/dashboard/facebook/adsets-performance-overview` - 广告组性能概览
- `GET /api/dashboard/facebook/ads-detail-performance-overview` - 广告详情性能
- `GET /api/dashboard/facebook/dual-account-card` - 双账户卡片数据
- `POST /api/dashboard/facebook/sync-data` - 同步 Facebook 数据
- `POST /api/dashboard/facebook/analyze-data` - AI 分析数据

#### Google Ads API
- `GET /api/dashboard/google/impressions` - 获取印象数据
- `GET /api/dashboard/google/purchases` - 获取购买数据
- `GET /api/dashboard/google/campaigns-performance-overview` - 广告系列性能概览
- `POST /api/dashboard/google/sync-data` - 同步 Google 数据
- `POST /api/dashboard/google/analyze-data` - AI 分析数据

### 请求示例

#### 获取 Facebook 印象数据
```bash
curl -X GET "http://localhost:7800/api/dashboard/facebook/impressions?startDate=2024-01-01&endDate=2024-01-31" \
  -H "Content-Type: application/json"
```

#### 同步 Facebook 数据
```bash
curl -X POST "http://localhost:7800/api/dashboard/facebook/sync-data" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "ad_account_id": "act_123456789"
  }'
```

#### AI 分析数据
```bash
curl -X POST "http://localhost:7800/api/dashboard/facebook/analyze-data" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "metrics": {
      "impressions": 10000,
      "clicks": 500,
      "spend": 1000
    }
  }'
```

### 响应格式

所有 API 响应遵循统一格式：

**成功响应**
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 返回的数据
  }
}
```

**错误响应**
```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

## 数据库

### 数据库结构

系统使用 MySQL 数据库存储广告数据，主要包含以下表：

- **facebook_ads_data** - Facebook 广告数据
- **google_ads_data** - Google 广告数据
- **sync_logs** - 数据同步日志
- **其他业务表** - 根据需要创建

### 创建数据库

```bash
mysql -u root -p < scripts/create_database.sql
```

### 数据库迁移

使用 Alembic 进行数据库迁移：

```bash
# 初始化迁移
alembic init alembic

# 生成迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 开发指南

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型注解（Type Hints）
- 编写文档字符串（Docstrings）
- 保持函数单一职责

### 项目开发流程

1. **添加新功能**
   - 在 `app/services/` 创建服务类
   - 在 `app/schemas/` 定义数据模式
   - 在 `app/api/` 添加路由
   - 在 `app/models/` 添加数据模型（如需要）

2. **运行测试**
```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 运行测试
pytest

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

3. **代码格式化**
```bash
# 安装格式化工具
pip install black isort

# 格式化代码
black .
isort .
```

4. **代码检查**
```bash
# 安装检查工具
pip install flake8 mypy

# 运行检查
flake8 app/
mypy app/
```

### 调试

1. **使用 FastAPI 自带调试**
   - 设置 `DEBUG=True` 在 `.env`
   - 访问 `/docs` 查看交互式文档

2. **使用 Python 调试器**
```python
import pdb
pdb.set_trace()  # 设置断点
```

3. **查看日志**
   - 日志自动输出到控制台
   - 可配置日志级别和输出位置

## 部署

### 生产环境配置

1. **更新环境变量**
```env
DEBUG=False
SECRET_KEY=生成一个强密码
```

2. **使用 Gunicorn + Uvicorn Workers**
```bash
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:7800 \
  --access-logfile - \
  --error-logfile -
```

3. **使用 Docker 部署**

项目已内置 `Dockerfile` 与 `docker-compose.yml` 用于启动后端容器（数据库与 Redis 请使用您已安装的实例）：
```bash
# 1) 准备环境变量
cp .env.example .env   # 根据需要填写 Facebook/Google/Gemini 等凭证
# 将数据库与 Redis 地址指向宿主机，例如：
# DB_HOST=host.docker.internal
# DB_PORT=15388        # 按您的 MySQL 监听端口填写
# REDIS_HOST=host.docker.internal
# REDIS_PORT=6379

# 2) 构建并启动（后台运行）
docker compose up -d --build

# 3) 查看状态
docker compose ps

# 4) 查看日志
docker compose logs -f backend
```

默认映射：
- API: `http://localhost:7800`
- MySQL/Redis：使用宿主机端口（示例为 `15388`、`6379`），容器内请使用 `.env` 中配置的地址（例如 `host.docker.internal`）

如需自定义端口或关闭缓存，可在 `.env` 中调整相关变量（`DB_PORT`、`REDIS_ENABLED` 等）。

4. **使用 Nginx 反向代理**

Nginx 配置示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:7800;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 性能优化

1. **数据库连接池**
   - 已配置连接池大小为 20
   - 最大溢出连接数为 40

2. **异步处理**
   - 使用 `async/await` 处理 I/O 操作
   - 使用 `httpx` 进行异步 HTTP 请求

3. **缓存策略**
   - 可集成 Redis 缓存热点数据
   - 使用 `@lru_cache` 缓存函数结果

4. **监控与日志**
   - 集成 APM 工具（如 Sentry）
   - 配置日志收集和分析

## 常见问题

### Q: 启动失败，提示数据库连接错误？
**A:** 检查以下几点：
- MySQL 服务是否启动
- `.env` 中数据库配置是否正确
- 数据库是否已创建（运行 `create_database.sql`）

### Q: Facebook API 返回认证错误？
**A:** 
- 检查 Access Token 是否有效
- 确认 Token 具有所需权限
- 尝试重新生成长期 Token

### Q: Google Ads API 无法连接？
**A:**
- 确认开发者令牌已激活
- 检查服务账号权限
- 验证 `google-ads.yaml` 配置
- 如在国内，确保代理配置正确

### Q: AI 分析功能不工作？
**A:**
- 检查 Gemini API 密钥是否正确
- 确认 API 配额未超限
- 查看控制台错误日志

### Q: 数据同步速度慢？
**A:**
- 减小同步日期范围
- 检查网络连接
- 考虑在非高峰时段同步
- 增加数据库连接池大小

### Q: 如何添加新的广告平台？
**A:**
1. 在 `app/services/` 创建平台服务类
2. 在 `app/api/` 添加路由
3. 在 `app/models/` 添加数据模型
4. 在 `main.py` 注册路由

## 技术支持

- **文档**: [项目文档](./docs)
- **问题反馈**: 在项目中提 Issue
- **API 文档**: http://localhost:7800/docs

## 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- ✅ 支持 Facebook Ads 数据获取
- ✅ 支持 Google Ads 数据获取
- ✅ 集成 Google Gemini AI
- ✅ 提供完整的 REST API

## 许可证

本项目仅供内部使用。

---

**Built with ❤️ using FastAPI**

