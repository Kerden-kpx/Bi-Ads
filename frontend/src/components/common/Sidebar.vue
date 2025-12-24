<template>
  <div class="sidebar">
    <!-- 菜单项 -->
    <nav class="sidebar-nav">
      <ul class="nav-list">
        <li 
          v-for="item in menuItems" 
          :key="item.id"
          class="nav-item"
          :class="{ active: activeSection === item.id }"
        >
          <a 
            :href="`#${item.id}`" 
            class="nav-link"
            @click="scrollToSection(item.id, $event)"
          >
            {{ item.name }}
          </a>
        </li>
      </ul>
    </nav>

    <!-- 平台切换 -->
    <div class="platform-switcher">
      <router-link to="/facebook" class="platform-btn" :class="{ active: route.path.includes('facebook') || route.path === '/' }">
        <img :src="facebookAdsLogo" alt="Facebook Ads" class="platform-icon">
        <span>Facebook Ads</span>
      </router-link>
      <router-link to="/google" class="platform-btn" :class="{ active: route.path.includes('google') }">
        <img :src="googleAdsLogo" alt="Google Ads" class="platform-icon">
        <span>Google Ads</span>
      </router-link>
      <router-link to="/ads-summary" class="platform-btn" :class="{ active: route.path.includes('ads-summary') }">
        <img :src="ezarcIcon" alt="Ads Summary" class="platform-icon">
        <span>Ads Summary</span>
      </router-link>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import googleAdsLogo from '@/assets/logos/google_ads_logo.png'
import facebookAdsLogo from '@/assets/logos/facebook_ads_logo.png'
import ezarcIcon from '@/assets/logos/ezarc-icon.png'

export default {
  name: 'Sidebar',
  setup() {
    const route = useRoute()
    const getInitialActiveSection = () => {
      if (route.path.includes('google')) return 'google-impression-reach-trend'
      if (route.path.includes('ads-summary')) return 'facebook-ads-performance'
      return 'impression-reach-trend'
    }
    const activeSection = ref(getInitialActiveSection())

    // 根据当前路由动态生成菜单项
    const menuItems = computed(() => {
      if (route.path.includes('facebook') || route.path === '/') {
        return [
          { id: 'impression-reach-trend', name: 'FB Ads Impression & Reach Trend' },
          { id: 'impression-reach-analyze', name: 'FB Ads Impression & Reach Analyze' },
          { id: 'purchases-spend-trend', name: 'FB Ads Purchases Value & Spend Trend' },
          { id: 'purchases-spend-analyze', name: 'FB Ads Purchases Value & Spend Analyze' },
          { id: 'ad-sets-performance', name: 'Ad Sets Performance Overview Table' },
          { id: 'ads-detail-performance', name: 'Ads Performance Overview' },
          { id: 'ads-performance', name: 'Ads Performance Overview (Weekly)' }
        ]
      } else if (route.path.includes('google')) {
        return [
          { id: 'google-impression-reach-trend', name: 'Top Funnel Overview' },
          { id: 'google-top-funnel-analyze', name: 'Top Funnel Overview Analyze' },
          { id: 'google-conversions-spend-trend', name: 'Conversion Value & Cost Overview' },
          { id: 'google-conversion-cost-analyze', name: 'Conversion Value & Cost Analyze' },
          { id: 'google-campaigns-performance', name: 'Campaign Performance Overview' },
          { id: 'google-ads-performance', name: 'Ads Performance Overview (Weekly)' }
        ]
      } else if (route.path.includes('ads-summary')) {
        return [
          { id: 'facebook-ads-performance', name: 'Facebook Ads Performance Overview' },
          { id: 'google-ads-performance', name: 'Google Ads Performance Overview' },
          { id: 'summary-ads-performance', name: 'Summary Ads Performance Overview' }
        ]
      }
      return []
    })

    const scrollToSection = (sectionId, event) => {
      event.preventDefault()
      // 立即更新activeSection
      activeSection.value = sectionId
      
      const element = document.getElementById(sectionId)
      if (element) {
        element.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        })
      }
    }

    const updateActiveSection = () => {
      const currentMenuItems = menuItems.value
      const sections = currentMenuItems.map(item => document.getElementById(item.id))
      const scrollPosition = window.scrollY + 100

      // 找到当前视口中最接近顶部的section
      let closestSection = null
      let minDistance = Infinity

      for (let i = 0; i < sections.length; i++) {
        if (sections[i]) {
          const distance = Math.abs(sections[i].offsetTop - scrollPosition)
          if (distance < minDistance) {
            minDistance = distance
            closestSection = currentMenuItems[i].id
          }
        }
      }

      if (closestSection) {
        activeSection.value = closestSection
      }
    }

    onMounted(() => {
      window.addEventListener('scroll', updateActiveSection)
      updateActiveSection()
    })

    onUnmounted(() => {
      window.removeEventListener('scroll', updateActiveSection)
    })

    return {
      route,
      activeSection,
      menuItems,
      scrollToSection,
      googleAdsLogo,
      facebookAdsLogo,
      ezarcIcon
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 280px;
  height: calc(100vh - 60px);
  background: #f8f9fa;
  color: #333;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 60px;
  z-index: 90;
  border-right: 1px solid #e5e7eb;
}

.platform-switcher {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: auto;
}

.platform-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  text-decoration: none;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  background: #ffffff;
  border: 1px solid transparent;
}

.platform-btn:hover {
  background: #f3f4f6;
  color: #374151;
  border-color: #e5e7eb;
}

.platform-btn.active {
  background: #3b82f6;
  color: #ffffff;
  border-color: #3b82f6;
  font-weight: 600;
}

.platform-btn .el-icon {
  font-size: 18px;
}

.platform-btn .platform-icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.logo {
  margin-bottom: 8px;
}

.logo-icon {
  font-size: 12px;
  font-weight: 400;
  color: #6b7280;
  letter-spacing: 0.5px;
}

.report-title {
  font-size: 14px;
  font-weight: 400;
  color: #111827;
  line-height: 1.4;
}

.sidebar-nav {
  flex: 1;
  padding: 0;
  padding-top: 0;
  overflow-y: auto;
}

/* 滚动条样式 */
.sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  border-bottom: 1px solid #e5e7eb;
}

.nav-link {
  display: block;
  padding: 14px 16px;
  color: #4b5563;
  text-decoration: none;
  font-size: 13px;
  font-weight: 400;
  line-height: 1.4;
  transition: all 0.15s ease;
  cursor: pointer;
  background: white;
  /* 文本溢出处理 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  word-break: break-word;
}

.nav-link:hover {
  background-color: #f3f4f6;
  color: #111827;
}

.nav-item.active .nav-link {
  background-color: #e5e7eb;
  color: #111827;
  font-weight: 400;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 0;
    overflow: hidden;
  }
}
</style>
