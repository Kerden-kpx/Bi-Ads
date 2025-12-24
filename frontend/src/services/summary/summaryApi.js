/**
 * Summary Dashboard API
 * 批量获取汇总数据的 API 服务
 */
import { createThirdPartyAPI } from '../api'

const api = createThirdPartyAPI('/dashboard/summary')

export const summaryAPI = {
  /**
   * 批量获取所有 Summary 数据（Facebook + Google + Lingxing）
   * 一次请求替代 8+ 个独立请求
   * 
   * @param {Object} params - 请求参数
   * @param {Array<string>} params.account_ids - Facebook 账户 ID 列表
   * @param {string} params.this_week_start - 本周开始日期 (YYYY-MM-DD)
   * @param {string} params.this_week_end - 本周结束日期 (YYYY-MM-DD)
   * @param {string} params.last_week_start - 上周开始日期 (YYYY-MM-DD)
   * @param {string} params.last_week_end - 上周结束日期 (YYYY-MM-DD)
   * @param {string} params.customer_id - Google Ads 客户 ID（可选）
   * @param {string} params.proxy_url - 代理 URL（可选）
   * @returns {Promise} API 响应
   * 
   * @example
   * const data = await summaryAPI.getAllSummaryData({
   *   account_ids: ['2613027225660900', '1069516980635624'],
   *   this_week_start: '2025-01-20',
   *   this_week_end: '2025-01-26',
   *   last_week_start: '2025-01-13',
   *   last_week_end: '2025-01-19'
   * })
   * 
   * 返回格式：
   * {
   *   facebook: {
   *     '2613027225660900': {
   *       this_week: { purchases: 100, purchasesValue: 5000, ... },
   *       last_week: { purchases: 90, purchasesValue: 4500, ... }
   *     },
   *     '1069516980635624': { ... }
   *   },
   *   google: {
   *     this_week: { conversions: 50, conversions_value: 2500, ... },
   *     last_week: { conversions: 45, conversions_value: 2250, ... }
   *   }
   * }
   */
  getAllSummaryData: (params) => {
    return api.post('/all-summary', params)
  },

  /**
   * 批量获取多个 Facebook 账户的两周汇总数据
   * 
   * @param {Object} params - 请求参数
   * @param {Array<string>} params.account_ids - Facebook 账户 ID 列表
   * @param {string} params.this_week_start - 本周开始日期
   * @param {string} params.this_week_end - 本周结束日期
   * @param {string} params.last_week_start - 上周开始日期
   * @param {string} params.last_week_end - 上周结束日期
   * @returns {Promise} API 响应
   */
  getFacebookMultiAccountSummary: (params) => {
    return api.post('/facebook-multi-account', params)
  },

  /**
   * 批量获取 Google Ads 的两周汇总数据
   * 
   * @param {Object} params - 请求参数
   * @param {string} params.this_week_start - 本周开始日期
   * @param {string} params.this_week_end - 本周结束日期
   * @param {string} params.last_week_start - 上周开始日期
   * @param {string} params.last_week_end - 上周结束日期
   * @param {string} params.customer_id - Google Ads 客户 ID（可选）
   * @param {string} params.proxy_url - 代理 URL（可选）
   * @returns {Promise} API 响应
   */
  getGoogleTwoWeeksSummary: (params) => {
    return api.post('/google-two-weeks', params)
  }
}

export default summaryAPI

