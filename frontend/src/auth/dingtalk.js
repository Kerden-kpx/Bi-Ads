import { clearAuthToken, setAuthToken } from '../services/api'

const AUTH_TOKEN_STORAGE_KEY = 'auth_token'
const AUTH_USER_STORAGE_KEY = 'auth_user'
const DEFAULT_AUTH_TIMEOUT_MS = Number(import.meta.env.VITE_DINGTALK_AUTH_TIMEOUT_MS || 8000)

const isBrowser = () => typeof window !== 'undefined'

const withApiBase = (path) => {
  const apiBase = import.meta.env.VITE_API_BASE_URL || ''
  return `${apiBase}${path}`
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
    throw new Error('当前环境不支持钉钉鉴权')
  }

  const timeoutMs =
    Number.isFinite(DEFAULT_AUTH_TIMEOUT_MS) && DEFAULT_AUTH_TIMEOUT_MS > 0
      ? DEFAULT_AUTH_TIMEOUT_MS
      : 8000

  const signResponse = await withTimeout(
    fetch(withApiBase('/api/auth/dingtalk/jsapi-sign'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: window.location.href.split('#')[0] })
    }),
    timeoutMs,
    'dingtalk jsapi-sign'
  )
  if (!signResponse.ok) {
    throw new Error(`JSAPI sign failed: HTTP ${signResponse.status}`)
  }
  const signPayload = parseApiData(await signResponse.json())
  if (!signPayload?.corpId) {
    throw new Error('Missing corpId in sign response')
  }

  await withTimeout(ddConfigReady(signPayload), timeoutMs, 'dingtalk config')

  const codeResult = await withTimeout(getAuthCode(signPayload.corpId), timeoutMs, 'dingtalk auth-code')
  const authCode = codeResult?.code || codeResult?.authCode
  if (!authCode) {
    throw new Error('Missing auth code')
  }

  const loginResponse = await withTimeout(
    fetch(withApiBase('/api/auth/dingtalk/login'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ auth_code: authCode })
    }),
    timeoutMs,
    'dingtalk login'
  )
  if (!loginResponse.ok) {
    throw new Error(`Login failed: HTTP ${loginResponse.status}`)
  }

  const loginPayload = parseApiData(await loginResponse.json())
  const token = loginPayload?.token || ''
  const user = loginPayload?.user || null
  saveSession(token, user)

  return loginPayload
}
