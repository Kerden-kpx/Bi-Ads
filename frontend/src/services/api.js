import axios from 'axios'

const AUTH_TOKEN_STORAGE_KEY = 'auth_token'
const AUTH_USER_STORAGE_KEY = 'auth_user'

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

const clients = [apiClient, aiApiClient, syncApiClient, thirdPartyApiClient]

const getStoredAuthToken = () => {
  if (typeof window === 'undefined') return ''
  return window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) || ''
}

const purgeStoredAuth = () => {
  if (typeof window === 'undefined') return
  window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY)
  window.localStorage.removeItem(AUTH_USER_STORAGE_KEY)
  window.dispatchEvent(new Event('auth_user_updated'))
}

export const setAuthToken = (token) => {
  if (!token) return
  clients.forEach((client) => {
    client.defaults.headers.common.Authorization = `Bearer ${token}`
  })
}

export const clearAuthToken = () => {
  clients.forEach((client) => {
    delete client.defaults.headers.common.Authorization
  })
}

const withAuthRequest = (config) => {
  const token = getStoredAuthToken()
  if (!token) return config

  config.headers = config.headers || {}
  if (!config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}

const withResponse = (label) => ({
  success(response) {
    return response.data
  },
  error(error) {
    if (error?.response?.status === 401) {
      clearAuthToken()
      purgeStoredAuth()
    }
    console.error(`${label}:`, error)
    return Promise.reject(error)
  }
})

clients.forEach((client) => {
  client.interceptors.request.use(
    (config) => withAuthRequest(config),
    (error) => Promise.reject(error)
  )
})

const apiResponse = withResponse('API Error')
apiClient.interceptors.response.use(apiResponse.success, apiResponse.error)

const aiResponse = withResponse('AI API Error')
aiApiClient.interceptors.response.use(aiResponse.success, aiResponse.error)

const syncResponse = withResponse('Sync API Error')
syncApiClient.interceptors.response.use(syncResponse.success, syncResponse.error)

const thirdPartyResponse = withResponse('Third Party API Error')
thirdPartyApiClient.interceptors.response.use(thirdPartyResponse.success, thirdPartyResponse.error)

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
