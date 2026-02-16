import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import { applyAuthToken, initDingTalkAuth } from './auth/dingtalk'
import './styles/variables.css'
import './style.css'

// 路由懒加载 - 优化首屏加载性能
const FacebookDashboard = () => import('./views/facebook/Facebook_Dashboard.vue')
const GoogleDashboard = () => import('./views/google/Google_Dashboard.vue')
const AdsSummary = () => import('./views/Ads_Summary.vue')

const routes = [
  { path: '/', redirect: '/facebook' },
  { 
    path: '/facebook', 
    component: FacebookDashboard, 
    name: 'FacebookDashboard',
    meta: { title: 'Facebook Ads Report' }
  },
  { 
    path: '/google', 
    component: GoogleDashboard, 
    name: 'GoogleDashboard',
    meta: { title: 'Google Ads Report' }
  },
  { 
    path: '/ads-summary', 
    component: AdsSummary, 
    name: 'AdsSummary',
    meta: { title: 'Ads Summary' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由导航守卫 - 动态更新页面标题
router.afterEach((to) => {
  document.title = to.meta.title || 'BI Dashboard'
})

const getStoredToken = () => window.localStorage.getItem('auth_token') || ''

const AUTH_STAGE_LABELS = {
  environment: '环境检查',
  'jsapi-sign': '签名接口',
  config: '钉钉 JSAPI 配置',
  'auth-code': '获取授权码',
  login: '登录接口',
  unknown: '未知阶段'
}

const escapeHtml = (value) =>
  String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const showAuthLoading = () => {
  const root = document.getElementById('app')
  if (!root) return
  root.innerHTML = `
    <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:#f7f9fb;color:#606266;font-size:14px;">
      正在登录...
    </div>
  `
}

const showAuthError = (error) => {
  const root = document.getElementById('app')
  if (!root) return
  const stage = error?.stage || 'unknown'
  const stageLabel = AUTH_STAGE_LABELS[stage] || AUTH_STAGE_LABELS.unknown
  const reason = error?.detail || error?.message || '未知错误'
  const requestId = error?.requestId || ''
  root.innerHTML = `
    <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:#f7f9fb;color:#303133;font-size:14px;">
      <div style="max-width:680px;padding:24px;text-align:center;line-height:1.7;">
        <div style="font-size:16px;font-weight:600;color:#f56c6c;">登录失败</div>
        <div style="margin-top:8px;color:#606266;">失败阶段：${escapeHtml(stageLabel)}</div>
        <div style="margin-top:8px;color:#f56c6c;word-break:break-word;">原因：${escapeHtml(reason)}</div>
        ${requestId ? `<div style="margin-top:8px;color:#909399;word-break:break-word;">请求ID：${escapeHtml(requestId)}</div>` : ''}
        <div style="margin-top:8px;color:#909399;">请在钉钉客户端内重试；如仍失败，请把请求ID发给管理员排查。</div>
      </div>
    </div>
  `
}

const mountApp = () => {
  const app = createApp(App)
  app.use(router)
  app.use(ElementPlus)

  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }

  app.mount('#app')
}

const bootstrap = async () => {
  const storedToken = getStoredToken()
  if (storedToken) {
    applyAuthToken(storedToken)
  }

  if (storedToken) {
    mountApp()
    return
  }

  showAuthLoading()
  try {
    await initDingTalkAuth()
    mountApp()
  } catch (error) {
    console.warn('DingTalk auth failed:', error)
    showAuthError(error)
  }
}

bootstrap()
