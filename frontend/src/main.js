import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
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

const app = createApp(App)

app.use(router)
app.use(ElementPlus)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
