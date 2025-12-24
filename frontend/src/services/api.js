import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api',
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// AI分析专用客户端（更长的超时时间）
const aiApiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api',
  timeout: parseInt(import.meta.env.VITE_AI_TIMEOUT) || 120000, // 默认120秒，足够模型轮换
  headers: {
    'Content-Type': 'application/json'
  }
})

// 数据同步专用客户端（超长超时时间）
const syncApiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api',
  timeout: parseInt(import.meta.env.VITE_SYNC_TIMEOUT) || 300000, // 默认300秒（5分钟）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 第三方API调用专用客户端（较长超时时间，用于Facebook/Google API）
const thirdPartyApiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api',
  timeout: parseInt(import.meta.env.VITE_THIRD_PARTY_TIMEOUT) || 90000, // 默认90秒（1.5分钟）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// AI分析专用客户端的响应拦截器
aiApiClient.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('AI API Error:', error)
    return Promise.reject(error)
  }
)

// 数据同步专用客户端的响应拦截器
syncApiClient.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('Sync API Error:', error)
    return Promise.reject(error)
  }
)

// 第三方API客户端的响应拦截器
thirdPartyApiClient.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('Third Party API Error:', error)
    return Promise.reject(error)
  }
)

/**
 * 通用API调用工具
 */
export const createAPI = (basePath) => ({
  get(endpoint, params = {}) {
    return apiClient.get(`${basePath}${endpoint}`, params)
  },
  
  post(endpoint, data = {}) {
    return apiClient.post(`${basePath}${endpoint}`, data)
  },
  
  put(endpoint, data = {}) {
    return apiClient.put(`${basePath}${endpoint}`, data)
  },
  
  delete(endpoint) {
    return apiClient.delete(`${basePath}${endpoint}`)
  }
})

/**
 * AI分析专用API调用工具（超时时间更长）
 */
export const createAIAPI = (basePath) => ({
  get(endpoint, params = {}) {
    return aiApiClient.get(`${basePath}${endpoint}`, params)
  },
  
  post(endpoint, data = {}) {
    return aiApiClient.post(`${basePath}${endpoint}`, data)
  },
  
  put(endpoint, data = {}) {
    return aiApiClient.put(`${basePath}${endpoint}`, data)
  },
  
  delete(endpoint) {
    return aiApiClient.delete(`${basePath}${endpoint}`)
  }
})

/**
 * 数据同步专用API调用工具（超长超时时间）
 */
export const createSyncAPI = (basePath) => ({
  get(endpoint, params = {}) {
    return syncApiClient.get(`${basePath}${endpoint}`, params)
  },
  
  post(endpoint, data = {}) {
    return syncApiClient.post(`${basePath}${endpoint}`, data)
  },
  
  put(endpoint, data = {}) {
    return syncApiClient.put(`${basePath}${endpoint}`, data)
  },
  
  delete(endpoint) {
    return syncApiClient.delete(`${basePath}${endpoint}`)
  }
})

/**
 * 第三方API调用工具（较长超时时间，用于Facebook/Google Ads API）
 */
export const createThirdPartyAPI = (basePath) => ({
  get(endpoint, params = {}) {
    return thirdPartyApiClient.get(`${basePath}${endpoint}`, params)
  },
  
  post(endpoint, data = {}) {
    return thirdPartyApiClient.post(`${basePath}${endpoint}`, data)
  },
  
  put(endpoint, data = {}) {
    return thirdPartyApiClient.put(`${basePath}${endpoint}`, data)
  },
  
  delete(endpoint) {
    return thirdPartyApiClient.delete(`${basePath}${endpoint}`)
  }
})

export default apiClient
