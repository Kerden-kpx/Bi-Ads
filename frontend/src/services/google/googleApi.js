import { createAPI, createAIAPI, createSyncAPI, createThirdPartyAPI } from '../api'

const api = createAPI('/dashboard/google')
const aiApi = createAIAPI('/dashboard/google')
const syncApi = createSyncAPI('/dashboard/google')
const thirdPartyApi = createThirdPartyAPI('/dashboard/google')

export const googleDashboardAPI = {
  getPerformanceComparison(data) {
    return api.post('/performance-comparison', data)
  },

  getCampaignPerformanceOverview(data) {
    return api.post('/campaign-performance-overview', data)
  },

  getAdsPerformanceOverview(data) {
    return api.post('/ads-performance-overview', data)
  },

  // 获取概览汇总数据（直接从 Google Ads API，使用更长超时时间）
  getOverviewSummary(params) {
    return thirdPartyApi.get('/overview-summary', { params })
  },

  refreshData() {
    return api.post('/refresh')
  },

  // 数据同步（使用更长的超时时间）
  syncData(data) {
    return syncApi.post('/sync-data', data)
  },

  // AI 分析（使用更长的超时时间）
  analyzeTopFunnel(data) {
    return aiApi.post('/analyze-top-funnel', data)
  },

  analyzeConversionCost(data) {
    return aiApi.post('/analyze-conversion-cost', data)
  }
}

export default googleDashboardAPI
