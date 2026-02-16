/**
 * 通用 Dashboard 组合式工具
 * 提供日期范围、加载状态和常用数据结构
 */
import { ref, reactive } from 'vue'
import { cacheManager } from '../utils/cache'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

/**
 * 默认日期范围：上周周一到周日
 */
export const getDefaultDateRange = () => {
  const today = dayjs()
  const thisWeekMonday = today.startOf('week').add(1, 'day')
  const lastWeekMonday = thisWeekMonday.subtract(7, 'day')
  const lastWeekSunday = lastWeekMonday.add(6, 'day')
  return [lastWeekMonday.format('YYYY-MM-DD'), lastWeekSunday.format('YYYY-MM-DD')]
}

/**
 * 默认对比范围：上上周周一到周日
 */
export const getDefaultCompareDateRange = () => {
  const today = dayjs()
  const thisWeekMonday = today.startOf('week').add(1, 'day')
  const lastWeekMonday = thisWeekMonday.subtract(7, 'day')
  const twoWeeksAgoMonday = lastWeekMonday.subtract(7, 'day')
  const twoWeeksAgoSunday = twoWeeksAgoMonday.add(6, 'day')
  return [twoWeeksAgoMonday.format('YYYY-MM-DD'), twoWeeksAgoSunday.format('YYYY-MM-DD')]
}

/**
 * Dashboard 通用逻辑
 */
export function useDashboard(_apiService = null, platformName = 'Dashboard') {
  const loading = ref(false)
  const currentDateRange = ref(getDefaultDateRange())
  const compareDateRange = ref(getDefaultCompareDateRange())

  const createEmptyData = () =>
    reactive({
      impressions: 0,
      clicks: 0,
      reach: 0,
      ctr: 0,
      cpm: 0,
      avgCpc: 0,
      uniqueLinkClicks: 0,
      impressionsChange: 0,
      clicksChange: 0,
      reachChange: 0,
      ctrChange: 0,
      cpmChange: 0,
      avgCpcChange: 0,
      uniqueLinkClicksChange: 0,
      chartData: { labels: [], datasets: [] }
    })

  const createEmptyPurchasesData = () =>
    reactive({
      purchasesValue: 0,
      spend: 0,
      roas: 0,
      addsToCart: 0,
      addsPaymentInfo: 0,
      purchases: 0,
      conversions: 0,
      purchasesValueChange: 0,
      spendChange: 0,
      roasChange: 0,
      addsToCartChange: 0,
      addsPaymentInfoChange: 0,
      purchasesChange: 0,
      conversionsData: [],
      conversionsPreviousData: [],
      roasData: [],
      roasPreviousData: [],
      chartData: { labels: [], datasets: [] }
    })

  const loadAllData = async (loadFunctions = []) => {
    loading.value = true
    try {
      if (loadFunctions.length) {
        await Promise.all(loadFunctions.map((fn) => fn()))
      }
    } catch (error) {
      console.error(`${platformName} 数据加载失败:`, error)
      ElMessage.error('部分数据加载失败，请检查网络连接')
    } finally {
      loading.value = false
    }
  }

  const createRefreshHandler = (loadFunctions = []) => {
    return async () => {
      // 在刷新时清除相关缓存，确保强制读取最新数据
      try {
        cacheManager.clearPattern('summary:*')
        cacheManager.clearPattern('lingxing:*')
        // 清除与平台相关的缓存前缀（如果传入了 platformName）
        if (platformName) {
          const prefix = platformName.toLowerCase()
          cacheManager.clearPattern(`${prefix}:*`)
        }
      } catch (err) {
        console.warn('清除缓存时出错:', err)
      }

      await loadAllData(loadFunctions)
    }
  }

  return {
    loading,
    currentDateRange,
    compareDateRange,
    createEmptyData,
    createEmptyPurchasesData,
    loadAllData,
    createRefreshHandler
  }
}

