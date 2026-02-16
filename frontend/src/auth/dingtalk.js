import { clearAuthToken, setAuthToken } from '../services/api'
import { joinApiUrl } from '../utils/apiUrl'

const AUTH_TOKEN_STORAGE_KEY = 'auth_token'
const AUTH_USER_STORAGE_KEY = 'auth_user'
const DEFAULT_AUTH_TIMEOUT_MS = Number(import.meta.env.VITE_DINGTALK_AUTH_TIMEOUT_MS || 8000)

const isBrowser = () => typeof window !== 'undefined'

const withApiBase = (path) => joinApiUrl(import.meta.env.VITE_API_BASE_URL, path)

const parseApiErrorMessage = (payload) => {
  if (!payload || typeof payload !== 'object') return ''
  if (typeof payload.message === 'string' && payload.message.trim()) return payload.message.trim()
  if (typeof payload.detail === 'string' && payload.detail.trim()) return payload.detail.trim()
  if (payload.detail && typeof payload.detail === 'object') {
    if (typeof payload.detail.message === 'string' && payload.detail.message.trim()) return payload.detail.message.trim()
    if (typeof payload.detail.errmsg === 'string' && payload.detail.errmsg.trim()) return payload.detail.errmsg.trim()
  }
  if (typeof payload.errmsg === 'string' && payload.errmsg.trim()) return payload.errmsg.trim()
  return ''
}

const stringifyError = (error) => {
  if (!error) return ''
  if (typeof error === 'string') return error
  if (error instanceof Error) return error.message
  try {
    return JSON.stringify(error)
  } catch (_) {
    return String(error)
  }
}

const buildAuthError = ({ stage, message, status, requestId, detail, cause }) => {
  const error = new Error(message || '钉钉鉴权失败')
  error.name = 'DingTalkAuthError'
  error.stage = stage || 'unknown'
  if (typeof status === 'number') {
    error.status = status
  }
  if (requestId) {
    error.requestId = requestId
  }
  if (detail) {
    error.detail = detail
  }
  if (cause) {
    error.cause = cause
  }
  return error
}

const getRequestIdFromResponse = (response) =>
  response?.headers?.get?.('X-Request-ID') || response?.headers?.get?.('x-request-id') || ''

const readResponsePayload = async (response) => {
  try {
    return await response.json()
  } catch (_) {
    return null
  }
}

const throwStageHttpError = async (stage, response, defaultMessage) => {
  const payload = await readResponsePayload(response)
  const detail = parseApiErrorMessage(payload)
  const requestId = getRequestIdFromResponse(response)
  const message = detail
    ? `${defaultMessage}: ${detail}`
    : `${defaultMessage}: HTTP ${response.status}`
  throw buildAuthError({
    stage,
    message,
    status: response.status,
    requestId,
    detail
  })
}

const withTimeout = async (promise, timeoutMs, stage) => {
  let timer = 0
  const timeoutPromise = new Promise((_, reject) => {
    timer = window.setTimeout(() => {
      reject(new Error(`${stage} timeout after ${timeoutMs}ms`))
    }, timeoutMs)
  })
  try {
    return await Promise.race([promise, timeoutPromise])
  } finally {
    if (timer) {
      window.clearTimeout(timer)
    }
  }
}

const getAuthCode = (corpId) =>
  new Promise((resolve, reject) => {
    const dd = window.dd
    dd.runtime.permission.requestAuthCode({
      corpId,
      onSuccess: (res) => resolve(res),
      onFail: (err) => reject(err)
    })
  })

const ddConfigReady = (config) =>
  new Promise((resolve, reject) => {
    const dd = window.dd
    dd.config({
      corpId: config.corpId,
      agentId: config.agentId ? Number(config.agentId) : undefined,
      timeStamp: config.timeStamp,
      nonceStr: config.nonceStr,
      signature: config.signature,
      jsApiList: ['runtime.permission.requestAuthCode']
    })
    dd.ready(() => resolve())
    dd.error((err) => reject(err))
  })

export const applyAuthToken = (token) => {
  if (!token) return
  setAuthToken(token)
}

export const clearLocalAuth = () => {
  if (!isBrowser()) return
  window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY)
  window.localStorage.removeItem(AUTH_USER_STORAGE_KEY)
  clearAuthToken()
  window.dispatchEvent(new Event('auth_user_updated'))
}

const saveSession = (token, user) => {
  if (!isBrowser()) return
  if (token) {
    window.localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token)
    applyAuthToken(token)
  }
  if (user) {
    window.localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(user))
    window.dispatchEvent(new Event('auth_user_updated'))
  }
}

const parseApiData = (payload) => {
  if (!payload || typeof payload !== 'object') return null
  if (payload.data && typeof payload.data === 'object') {
    return payload.data
  }
  return payload
}

export const initDingTalkAuth = async () => {
  if (!isBrowser() || !window.dd) {
    throw buildAuthError({
      stage: 'environment',
      message: '当前环境不支持钉钉鉴权，请在钉钉客户端内打开'
    })
  }

  const timeoutMs =
    Number.isFinite(DEFAULT_AUTH_TIMEOUT_MS) && DEFAULT_AUTH_TIMEOUT_MS > 0
      ? DEFAULT_AUTH_TIMEOUT_MS
      : 8000

  let signResponse
  try {
    signResponse = await withTimeout(
      fetch(withApiBase('/auth/dingtalk/jsapi-sign'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: window.location.href.split('#')[0] })
      }),
      timeoutMs,
      'dingtalk jsapi-sign'
    )
  } catch (error) {
    throw buildAuthError({
      stage: 'jsapi-sign',
      message: `签名接口请求失败: ${stringifyError(error) || 'unknown error'}`,
      cause: error
    })
  }
  if (!signResponse.ok) {
    await throwStageHttpError('jsapi-sign', signResponse, '签名接口调用失败')
  }
  const signRawPayload = await readResponsePayload(signResponse)
  const signPayload = parseApiData(signRawPayload)
  if (!signPayload?.corpId) {
    throw buildAuthError({
      stage: 'jsapi-sign',
      message: '签名接口返回缺少 corpId',
      requestId: getRequestIdFromResponse(signResponse),
      detail: parseApiErrorMessage(signRawPayload)
    })
  }

  try {
    await withTimeout(ddConfigReady(signPayload), timeoutMs, 'dingtalk config')
  } catch (error) {
    throw buildAuthError({
      stage: 'config',
      message: `钉钉 JSAPI 配置失败: ${stringifyError(error) || 'unknown error'}`,
      cause: error
    })
  }

  let codeResult
  try {
    codeResult = await withTimeout(getAuthCode(signPayload.corpId), timeoutMs, 'dingtalk auth-code')
  } catch (error) {
    throw buildAuthError({
      stage: 'auth-code',
      message: `获取钉钉授权码失败: ${stringifyError(error) || 'unknown error'}`,
      cause: error
    })
  }
  const authCode = codeResult?.code || codeResult?.authCode
  if (!authCode) {
    throw buildAuthError({
      stage: 'auth-code',
      message: '授权码为空，无法继续登录'
    })
  }

  let loginResponse
  try {
    loginResponse = await withTimeout(
      fetch(withApiBase('/auth/dingtalk/login'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ auth_code: authCode })
      }),
      timeoutMs,
      'dingtalk login'
    )
  } catch (error) {
    throw buildAuthError({
      stage: 'login',
      message: `登录接口请求失败: ${stringifyError(error) || 'unknown error'}`,
      cause: error
    })
  }
  if (!loginResponse.ok) {
    await throwStageHttpError('login', loginResponse, '登录接口调用失败')
  }

  const loginRawPayload = await readResponsePayload(loginResponse)
  const loginPayload = parseApiData(loginRawPayload)
  const token = loginPayload?.token || ''
  const user = loginPayload?.user || null
  if (!token) {
    throw buildAuthError({
      stage: 'login',
      message: '登录接口未返回 token',
      requestId: getRequestIdFromResponse(loginResponse),
      detail: parseApiErrorMessage(loginRawPayload)
    })
  }
  saveSession(token, user)

  return loginPayload
}
