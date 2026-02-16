const DEFAULT_API_BASE_URL = '/api'

const trimTrailingSlash = (value) => value.replace(/\/+$/, '')

const ensureLeadingSlash = (value) => (value.startsWith('/') ? value : `/${value}`)

const collapseRepeatedApiSegments = (value) => {
  let current = value
  let next = current.replace(/(\/api)\/api(?=\/|$)/gi, '$1')
  while (next !== current) {
    current = next
    next = current.replace(/(\/api)\/api(?=\/|$)/gi, '$1')
  }
  return current
}

export const normalizeApiBaseUrl = (rawBaseUrl) => {
  const candidate = String(rawBaseUrl || '').trim()
  if (!candidate) return DEFAULT_API_BASE_URL

  const withoutTrailingSlash = trimTrailingSlash(candidate)
  if (/^https?:\/\//i.test(withoutTrailingSlash)) {
    return collapseRepeatedApiSegments(withoutTrailingSlash)
  }

  return collapseRepeatedApiSegments(ensureLeadingSlash(withoutTrailingSlash))
}

export const joinApiUrl = (baseUrl, path) => {
  const normalizedBase = normalizeApiBaseUrl(baseUrl)
  const normalizedPath = ensureLeadingSlash(String(path || '').trim())
  const merged = `${normalizedBase}${normalizedPath}`
  return collapseRepeatedApiSegments(merged).replace(/([^:]\/)\/+/g, '$1')
}

export const joinUrlPath = (basePath, endpoint) => {
  const normalizedBase = ensureLeadingSlash(trimTrailingSlash(String(basePath || '')))
  const normalizedEndpoint = ensureLeadingSlash(String(endpoint || '').trim())
  return `${normalizedBase}${normalizedEndpoint}`.replace(/\/+/g, '/')
}
