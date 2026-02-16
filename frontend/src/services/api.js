import axios from 'axios'
import { joinUrlPath, normalizeApiBaseUrl } from '../utils/apiUrl'

const AUTH_TOKEN_STORAGE_KEY = 'auth_token'
const AUTH_USER_STORAGE_KEY = 'auth_user'
const API_BASE_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL)

const REQUEST_TYPES = {
  DEFAULT: 'default',
  AI: 'ai',
  SYNC: 'sync',
  THIRD_PARTY: 'thirdParty'
}

const REQUEST_TIMEOUTS = {
  [REQUEST_TYPES.DEFAULT]: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000,
  [REQUEST_TYPES.AI]: parseInt(import.meta.env.VITE_AI_TIMEOUT) || 120000,
  [REQUEST_TYPES.SYNC]: parseInt(import.meta.env.VITE_SYNC_TIMEOUT) || 300000,
  [REQUEST_TYPES.THIRD_PARTY]: parseInt(import.meta.env.VITE_THIRD_PARTY_TIMEOUT) || 90000
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUTS[REQUEST_TYPES.DEFAULT],
  headers: {
    'Content-Type': 'application/json'
  }
})

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

const withRequestTypeConfig = (requestType, config = {}) => {
  const timeout = REQUEST_TIMEOUTS[requestType] || REQUEST_TIMEOUTS[REQUEST_TYPES.DEFAULT]
  if (typeof config.timeout === 'number' && config.timeout > 0) {
    return config
  }
  return { ...config, timeout }
}

apiClient.interceptors.request.use(
  (config) => withAuthRequest(config),
  (error) => Promise.reject(error)
)

const apiResponse = withResponse('API Error')
apiClient.interceptors.response.use(apiResponse.success, apiResponse.error)

export const setAuthToken = (token) => {
  if (!token) return
  apiClient.defaults.headers.common.Authorization = `Bearer ${token}`
}

export const clearAuthToken = () => {
  delete apiClient.defaults.headers.common.Authorization
}

const createScopedAPI = (basePath, requestType) => ({
  get(endpoint, config = {}) {
    return apiClient.get(
      joinUrlPath(basePath, endpoint),
      withRequestTypeConfig(requestType, config)
    )
  },

  post(endpoint, data = {}, config = {}) {
    return apiClient.post(
      joinUrlPath(basePath, endpoint),
      data,
      withRequestTypeConfig(requestType, config)
    )
  },

  put(endpoint, data = {}, config = {}) {
    return apiClient.put(
      joinUrlPath(basePath, endpoint),
      data,
      withRequestTypeConfig(requestType, config)
    )
  },

  delete(endpoint, config = {}) {
    return apiClient.delete(
      joinUrlPath(basePath, endpoint),
      withRequestTypeConfig(requestType, config)
    )
  }
})

export const createAPI = (basePath) => createScopedAPI(basePath, REQUEST_TYPES.DEFAULT)

export const createAIAPI = (basePath) => createScopedAPI(basePath, REQUEST_TYPES.AI)

export const createSyncAPI = (basePath) => createScopedAPI(basePath, REQUEST_TYPES.SYNC)

export const createThirdPartyAPI = (basePath) =>
  createScopedAPI(basePath, REQUEST_TYPES.THIRD_PARTY)

export default apiClient
