# Ads BI Dashboard Frontend

广告数据 BI 仪表板前端应用 - 支持 Facebook Ads 和 Google Ads 数据可视化分析

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [开发指南](#开发指南)
- [组件说明](#组件说明)
- [API 集成](#api-集成)
- [构建部署](#构建部署)
- [性能优化](#性能优化)
- [常见问题](#常见问题)

## 项目简介

这是一个基于 Vue 3 + Vite 构建的现代化广告数据 BI 仪表板前端应用，提供直观的数据可视化和交互式分析功能。支持 Facebook Ads 和 Google Ads 两大主流广告平台的数据展示与分析。

### 核心亮点

- 🎨 **现代化 UI**：基于 Element Plus 打造的美观界面
- 📊 **数据可视化**：使用 Chart.js 实现丰富的图表展示
- ⚡ **高性能**：Vite 构建工具，开发体验极佳
- 📱 **响应式设计**：适配不同屏幕尺寸
- 🔄 **实时数据**：支持数据刷新和时间范围筛选
- 🤖 **AI 分析**：集成 AI 智能分析功能
- 🌐 **多平台支持**：同时支持 Facebook 和 Google Ads

## 功能特性

### 📈 Facebook Ads 功能
- ✅ 广告账户性能概览
- ✅ 广告系列（Campaigns）数据展示
- ✅ 广告组（AdSets）性能分析
- ✅ 广告详情（Ads）数据统计
- ✅ 印象与触达趋势图表
- ✅ 购买与花费分析
- ✅ 双账户对比功能
- ✅ AI 智能分析建议
- ✅ 自定义日期范围筛选
- ✅ 数据同步功能

### 📊 Google Ads 功能
- ✅ 广告账户性能概览
- ✅ 广告系列性能分析
- ✅ 印象与点击数据统计
- ✅ 购买与花费分析
- ✅ 时间段对比功能
- ✅ AI 智能分析建议
- ✅ 自定义日期范围筛选
- ✅ 数据同步功能

### 📋 综合功能
- ✅ 多平台数据汇总
- ✅ 跨平台数据对比
- ✅ 灵活的日期选择器
- ✅ 数据导出功能
- ✅ 响应式布局设计

## 技术栈

### 核心框架
- **Vue 3.4+** - 渐进式 JavaScript 框架
- **Vite 5.0+** - 下一代前端构建工具
- **Vue Router 4.2+** - Vue.js 官方路由管理器

### UI 框架
- **Element Plus 2.4+** - 基于 Vue 3 的组件库
- **@element-plus/icons-vue** - Element Plus 图标库

### 数据可视化
- **Chart.js 4.4+** - 简洁、灵活的 JavaScript 图表库
- **vue-chartjs 5.3+** - Chart.js 的 Vue 3 封装

### 工具库
- **Axios 1.12+** - HTTP 客户端
- **Day.js 1.11+** - 轻量级日期处理库

### 开发工具
- **ESLint** - 代码质量检查
- **eslint-plugin-vue** - Vue.js 代码规范

## 项目结构

```
frontend/
├── public/                      # 静态资源
├── src/
│   ├── assets/                  # 资源文件
│   │   ├── images/             # 图片资源
│   │   └── logos/              # Logo 资源
│   │       ├── ezarc-icon.png
│   │       ├── ezarc-logo.jpg
│   │       ├── facebook_ads_logo.png
│   │       └── google_ads_logo.png
│   ├── components/              # 组件目录
│   │   ├── common/             # 通用组件
│   │   │   └── Sidebar.vue    # 侧边栏导航
│   │   ├── facebook/           # Facebook Ads 组件
│   │   │   ├── Facebook_Ads_Performance_Card.vue
│   │   │   ├── Facebook_Ads_Detail_Performance_Card.vue
│   │   │   ├── Facebook_Ads_Dual_Account_Card.vue
│   │   │   ├── Facebook_AdSets_Performance_Card.vue
│   │   │   ├── Facebook_Analyze_Card_One.vue
│   │   │   ├── Facebook_Analyze_Card_Two.vue
│   │   │   ├── Facebook_Impressions_Reach_Card.vue
│   │   │   └── Facebook_Purchases_Spend_Card.vue
│   │   ├── google/             # Google Ads 组件
│   │   │   ├── Google_Ads_Performance_Card.vue
│   │   │   ├── Google_Campaigns_Performance_Card.vue
│   │   │   ├── Google_Analyze_Card_One.vue
│   │   │   ├── Google_Analyze_Card_Two.vue
│   │   │   ├── Google_Impressions_Reach_Card.vue
│   │   │   └── Google_Purchases_Spend_Card.vue
│   │   ├── shared/             # 共享组件
│   │   │   ├── Metric_Card.vue
│   │   │   ├── Performance_Card.vue
│   │   │   ├── Quick_Date_Range_Picker.vue
│   │   │   ├── Simple_Date_Range_Picker.vue
│   │   │   └── Single_Date_Picker.vue
│   │   └── summary/            # 汇总组件
│   │       └── Summary_Ads_Performance_Card.vue
│   ├── composables/             # 组合式函数
│   │   ├── useChartData.js     # 图表数据处理
│   │   ├── useDashboard.js     # 仪表板逻辑
│   │   └── useMetrics.js       # 指标计算
│   ├── services/                # API 服务
│   │   ├── api.js              # API 基础配置
│   │   ├── facebook/
│   │   │   └── facebookApi.js  # Facebook API
│   │   └── google/
│   │       └── googleApi.js    # Google API
│   ├── styles/                  # 样式文件
│   │   ├── variables.css       # CSS 变量
│   │   └── performance-card.css
│   ├── utils/                   # 工具函数
│   │   ├── chartConfig.js      # 图表配置
│   │   ├── dataTransformers.js # 数据转换
│   │   └── formatters.js       # 格式化工具
│   ├── views/                   # 页面视图
│   │   ├── facebook/
│   │   │   └── Facebook_Dashboard.vue
│   │   ├── google/
│   │   │   └── Google_Dashboard.vue
│   │   └── Ads_Summary.vue
│   ├── App.vue                  # 根组件
│   ├── main.js                  # 应用入口
│   └── style.css                # 全局样式
├── index.html                   # HTML 模板
├── vite.config.js               # Vite 配置
├── package.json                 # 项目配置
├── .env.development             # 开发环境变量
├── .env.production              # 生产环境变量
└── README.md                    # 项目文档
```

## 快速开始

### 前置要求

- **Node.js** 16.0 或更高版本
- **npm** 7.0 或更高版本（或 **yarn** / **pnpm**）

### 安装步骤

1. **进入前端目录**
```bash
cd frontend
```

2. **安装依赖**
```bash
npm install

# 或使用 yarn
yarn install

# 或使用 pnpm
pnpm install
```

3. **配置环境变量**

创建 `.env.development` 文件（开发环境）：
```env
# API 基础地址
VITE_API_BASE_URL=http://localhost:7800/api

# API 超时时间（毫秒）
VITE_API_TIMEOUT=30000

# 开发服务器主机
VITE_HOST=0.0.0.0

# 开发服务器端口
VITE_PORT=5173
```

创建 `.env.production` 文件（生产环境）：
```env
# API 基础地址（生产环境）
VITE_API_BASE_URL=https://your-api-domain.com/api

# API 超时时间
VITE_API_TIMEOUT=30000
```

4. **启动开发服务器**
```bash
npm run dev
```

5. **访问应用**
```
http://localhost:5173
```

### 可用脚本

```bash
# 启动开发服务器（带热更新）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查和修复
npm run lint
```

## 环境配置

### 环境变量说明

应用使用 Vite 的环境变量系统，所有环境变量必须以 `VITE_` 前缀开头。

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `VITE_API_BASE_URL` | 后端 API 地址 | `http://localhost:7800/api` | ✅ |
| `VITE_API_TIMEOUT` | API 请求超时时间（毫秒） | `30000` | ❌ |
| `VITE_HOST` | 开发服务器主机 | `0.0.0.0` | ❌ |
| `VITE_PORT` | 开发服务器端口 | `5173` | ❌ |

### 配置文件说明

#### vite.config.js
- 构建配置和优化
- 路径别名配置（`@` 指向 `src` 目录）
- 代码分割策略
- 开发服务器配置

#### package.json
- 项目依赖管理
- 脚本命令定义
- 项目元信息

## 开发指南

### 代码规范

- 遵循 Vue 3 官方风格指南
- 使用 Composition API
- 组件命名使用 PascalCase
- 文件命名使用 Snake_Case（与项目现有规范一致）
- 使用 ESLint 进行代码检查

### 组件开发规范

#### 单文件组件结构
```vue
<template>
  <!-- 模板 -->
</template>

<script setup>
// 导入
import { ref, computed } from 'vue'

// 组合式函数
const { data, loading } = useDashboard()

// 响应式数据
const count = ref(0)

// 计算属性
const doubleCount = computed(() => count.value * 2)

// 方法
const handleClick = () => {
  // 处理逻辑
}
</script>

<style scoped>
/* 组件样式 */
</style>
```

### 使用 Composables

项目采用 Composition API 和可复用的 Composables：

```javascript
// 使用示例
import { useDashboard } from '@/composables/useDashboard'
import { useMetrics } from '@/composables/useMetrics'

const { 
  data, 
  loading, 
  error, 
  fetchData 
} = useDashboard()

const { 
  calculateCTR, 
  calculateROAS 
} = useMetrics()
```

### 路由管理

添加新路由：

```javascript
// src/main.js
const routes = [
  {
    path: '/new-page',
    component: () => import('./views/NewPage.vue'),
    name: 'NewPage',
    meta: { title: 'New Page Title' }
  }
]
```

### API 调用

使用统一的 API 服务：

```javascript
// 导入 API 服务
import { facebookAPI } from '@/services/facebook/facebookApi'

// 调用 API
const data = await facebookAPI.getImpressions({
  startDate: '2024-01-01',
  endDate: '2024-01-31'
})
```

### 状态管理

项目使用 Composables 进行轻量级状态管理，无需引入 Vuex/Pinia：

```javascript
// composables/useDashboard.js
export function useDashboard() {
  const state = reactive({
    data: null,
    loading: false,
    error: null
  })
  
  const fetchData = async () => {
    state.loading = true
    try {
      state.data = await api.getData()
    } catch (error) {
      state.error = error
    } finally {
      state.loading = false
    }
  }
  
  return {
    ...toRefs(state),
    fetchData
  }
}
```

## 组件说明

### 共享组件

#### Metric_Card.vue
指标卡片组件，展示单个指标数据。

**Props:**
- `title` - 卡片标题
- `value` - 指标值
- `change` - 变化百分比
- `trend` - 趋势（up/down）

#### Performance_Card.vue
性能卡片组件，展示性能数据和图表。

#### Date Pickers
- `Quick_Date_Range_Picker.vue` - 快速日期范围选择
- `Simple_Date_Range_Picker.vue` - 简单日期范围选择
- `Single_Date_Picker.vue` - 单日期选择

### Facebook 组件

- `Facebook_Ads_Performance_Card.vue` - 广告性能卡片
- `Facebook_AdSets_Performance_Card.vue` - 广告组性能卡片
- `Facebook_Impressions_Reach_Card.vue` - 印象触达卡片
- `Facebook_Purchases_Spend_Card.vue` - 购买花费卡片
- `Facebook_Analyze_Card_One.vue` - AI 分析卡片 1
- `Facebook_Analyze_Card_Two.vue` - AI 分析卡片 2

### Google 组件

- `Google_Ads_Performance_Card.vue` - 广告性能卡片
- `Google_Campaigns_Performance_Card.vue` - 广告系列性能卡片
- `Google_Impressions_Reach_Card.vue` - 印象点击卡片
- `Google_Purchases_Spend_Card.vue` - 购买花费卡片
- `Google_Analyze_Card_One.vue` - AI 分析卡片 1
- `Google_Analyze_Card_Two.vue` - AI 分析卡片 2

## API 集成

### API 配置

```javascript
// src/services/api.js
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: import.meta.env.VITE_API_TIMEOUT || 30000
})

// 请求拦截器
apiClient.interceptors.request.use(config => {
  // 可添加认证 token 等
  return config
})

// 响应拦截器
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    // 统一错误处理
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)
```

### Facebook API 调用示例

```javascript
import { facebookAPI } from '@/services/facebook/facebookApi'

// 获取印象数据
const impressions = await facebookAPI.getImpressions({
  startDate: '2024-01-01',
  endDate: '2024-01-31',
  accountId: 'act_123456789'
})

// 同步数据
const result = await facebookAPI.syncData({
  start_date: '2024-01-01',
  end_date: '2024-01-31'
})
```

### Google API 调用示例

```javascript
import { googleAPI } from '@/services/google/googleApi'

// 获取广告系列数据
const campaigns = await googleAPI.getCampaignsPerformance({
  startDate: '2024-01-01',
  endDate: '2024-01-31'
})
```

## 构建部署

### 构建生产版本

```bash
npm run build
```

构建输出在 `dist/` 目录，包含：
- 优化的 JavaScript 代码
- 压缩的 CSS 文件
- 静态资源文件

### 构建优化

#### 代码分割
项目配置了智能代码分割：
- **vue-vendor**: Vue 核心库
- **element-plus**: UI 组件库
- **charts**: 图表库
- **utils**: 工具库

#### 性能优化
- 路由懒加载
- Tree-shaking（自动移除未使用代码）
- 生产环境移除 console
- CSS 代码分割
- 资源压缩和优化

### 部署到服务器

#### 使用 Nginx

1. **构建项目**
```bash
npm run build
```

2. **Nginx 配置**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    # 处理 Vue Router 的 history 模式
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

3. **重启 Nginx**
```bash
sudo nginx -t
sudo systemctl restart nginx
```

#### 使用 Docker

创建 `Dockerfile`:
```dockerfile
# 构建阶段
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

构建和运行：
```bash
docker build -t ads-dashboard-frontend .
docker run -p 80:80 ads-dashboard-frontend
```

#### 部署到 Vercel

```bash
# 安装 Vercel CLI
npm install -g vercel

# 部署
vercel
```

#### 部署到 Netlify

1. 在 Netlify 创建新站点
2. 连接 Git 仓库
3. 配置构建命令：`npm run build`
4. 配置发布目录：`dist`

### 环境变量配置（生产环境）

确保在生产环境配置正确的环境变量：

```env
VITE_API_BASE_URL=https://api.your-domain.com/api
VITE_API_TIMEOUT=30000
```

## 性能优化

### 已实施的优化

1. **路由懒加载**
   - 所有页面组件按需加载
   - 减少首屏加载时间

2. **代码分割**
   - 第三方库独立打包
   - 按功能模块分割代码

3. **资源优化**
   - 图片懒加载
   - 静态资源压缩
   - CSS 提取和压缩

4. **构建优化**
   - Tree-shaking 移除未使用代码
   - 生产环境移除 console
   - 启用 Terser 压缩

5. **依赖预构建**
   - Vite 自动预构建优化
   - 加速开发服务器启动

### 性能监控

使用浏览器开发者工具：
- **Network**: 监控资源加载
- **Performance**: 分析运行时性能
- **Lighthouse**: 综合性能评分

## 常见问题

### Q: 开发服务器启动失败？
**A:** 检查以下几点：
- Node.js 版本是否符合要求（>= 16.0）
- 端口 5173 是否被占用
- 依赖是否正确安装（尝试删除 `node_modules` 重新安装）

### Q: API 调用失败，出现 CORS 错误？
**A:**
- 确认后端服务已启动
- 检查 `.env` 中的 `VITE_API_BASE_URL` 配置
- 确认后端已正确配置 CORS

### Q: 图表不显示？
**A:**
- 检查控制台是否有错误
- 确认数据格式正确
- 检查 Chart.js 版本兼容性

### Q: 打包后页面空白？
**A:**
- 检查路由配置是否正确
- 确认 `base` 配置（如部署到子目录）
- 检查浏览器控制台错误信息

### Q: 如何添加新的广告平台？
**A:**
1. 在 `src/views/` 创建新页面
2. 在 `src/components/` 创建平台组件
3. 在 `src/services/` 创建 API 服务
4. 在 `src/main.js` 添加路由
5. 在 `Sidebar.vue` 添加导航项

### Q: 如何自定义主题？
**A:**
修改 `src/styles/variables.css`:
```css
:root {
  --primary-color: #409eff;
  --success-color: #67c23a;
  --warning-color: #e6a23c;
  --danger-color: #f56c6c;
  /* 添加更多自定义变量 */
}
```

### Q: 开发时如何配置代理？
**A:**
在 `vite.config.js` 添加代理配置：
```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:7800',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 技术支持

- **在线文档**: http://localhost:5173
- **API 文档**: http://localhost:7800/docs
- **问题反馈**: 在项目中提 Issue

## 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- ✅ Facebook Ads 数据可视化
- ✅ Google Ads 数据可视化
- ✅ 多种图表类型支持
- ✅ AI 分析集成
- ✅ 响应式设计
- ✅ 数据同步功能

## 开发团队

如需技术支持，请联系开发团队。

## 许可证

本项目仅供内部使用。

---

**Built with ❤️ using Vue 3 + Vite + Element Plus**

