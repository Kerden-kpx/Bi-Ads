import { createAPI, createAIAPI, createSyncAPI, createThirdPartyAPI } from '../api'

const api = createAPI('/dashboard/facebook')
const aiApi = createAIAPI('/dashboard/facebook')
const syncApi = createSyncAPI('/dashboard/facebook')
const thirdPartyApi = createThirdPartyAPI('/dashboard/facebook')

export const facebookDashboardAPI = {
  // 从数据库获取数据
  getImpressionsData(params) {
    return api.get('/impressions', { params })
  },

  getPurchasesData(params) {
    return api.get('/purchases', { params })
  },

  // 从Facebook API直接获取数据（使用更长超时时间）
  getImpressionsDataFromAPI(params) {
    return thirdPartyApi.get('/impressions/api', { params })
  },

  getPurchasesDataFromAPI(params) {
    return thirdPartyApi.get('/purchases/api', { params })
  },

  // 从Facebook API直接获取总览数据（合并impressions和purchases，使用更长超时时间）
  getOverviewDataFromAPI(params) {
    return thirdPartyApi.get('/overview/api', { params })
  },

  getPerformanceComparison(data) {
    return api.post('/performance-comparison', data)
  },

  getAdsPerformanceOverview(data) {
    return api.post('/ads-performance-overview', data)
  },

  getAdsetsPerformanceOverview(data) {
    return api.post('/adsets-performance-overview', data)
  },

  getAdsDetailPerformanceOverview(data) {
    return api.post('/ads-detail-performance-overview', data)
  },

  // 数据同步（使用更长的超时时间）
  syncData(data) {
    return syncApi.post('/sync-data', data)
  },

  // AI 分析（使用更长的超时时间）
  analyzeImpressionsReach(data) {
    return aiApi.post('/analyze-impressions-reach', data)
  },

  analyzePurchasesSpend(data) {
    return aiApi.post('/analyze-purchases-spend', data)
  }
}

export default facebookDashboardAPI
