/**
 * Lingxing Data API
 * 独立站数据API服务
 */
import apiClient from '../api'

export const lingxingAPI = {
  /**
   * 获取独立站全站月度模拟数据
   * @param {Object} params - 请求参数
   * @param {string} params.date - 日期字符串 (YYYY-MM-DD)
   * @returns {Promise} API响应
   */
  getWebsiteMonthlySimulation: (params = {}) => {
    return apiClient.get('/dashboard/lingxing/website-monthly-simulation', { params })
  },

  /**
   * 获取所有月的数据
   * @returns {Promise} API响应
   */
  getAllMonths: () => {
    return apiClient.get('/dashboard/lingxing/all-months')
  },

  /**
   * 获取月度花费数据
   * @param {Object} params - 请求参数
   * @param {string} params.date - 日期字符串 (YYYY-MM-DD)
   * @returns {Promise} API响应
   */
  getMonthlyCost: (params = {}) => {
    return apiClient.get('/dashboard/lingxing/monthly-cost', { params })
  },

  /**
   * 获取独立站销售目标数据
   * @param {Object} params - 请求参数
   * @param {string} params.date - 日期字符串 (YYYY-MM-DD)
   * @returns {Promise} API响应
   */
  getSalesTarget: (params = {}) => {
    return apiClient.get('/dashboard/lingxing/sales-target', { params })
  },

  /**
   * 更新独立站销售目标数据
   * @param {Object} data - 更新数据
   * @param {number} data.month - 月份 (1-12)
   * @param {number} data.year - 年份
   * @param {number} data.conversion_value - 转化价值
   * @returns {Promise} API响应
   */
  updateSalesTarget: (data) => {
    return apiClient.put('/dashboard/lingxing/sales-target', null, { params: data })
  }
}

