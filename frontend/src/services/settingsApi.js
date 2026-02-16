import { createAPI } from './api'

const api = createAPI('/settings')

export const settingsAPI = {
  /**
   * 获取产品名称配置
   */
  getProductNames() {
    return api.get('/product-names')
  },

  /**
   * 更新产品名称配置
   * @param {Object} params
   * @param {Array<string>} params.facebookProductNames - Facebook产品名称列表
   * @param {Array<string>} params.googleProductNames - Google产品名称列表
   */
  updateProductNames(params) {
    return api.post('/product-names', params)
  }
}

export default settingsAPI


