/**
 * 前端内存缓存管理器
 * 支持 TTL（过期时间）和自动清理
 */

const isDevEnv = typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.DEV
const logDebug = (...args) => {
  if (isDevEnv) {
    console.log(...args)
  }
}

class CacheManager {
  constructor() {
    this.cache = new Map()
    this.timers = new Map()
  }

  /**
   * 生成缓存键
   * @param {string} prefix - 缓存前缀
   * @param {Object} params - 参数对象
   * @returns {string} 缓存键
   */
  generateKey(prefix, params = {}) {
    const paramStr = Object.keys(params)
      .sort()
      .map(key => `${key}=${JSON.stringify(params[key])}`)
      .join('&')
    return paramStr ? `${prefix}:${paramStr}` : prefix
  }

  /**
   * 获取缓存数据
   * @param {string} key - 缓存键
   * @returns {any} 缓存的数据，如果不存在或已过期返回 null
   */
  get(key) {
    const item = this.cache.get(key)
    
    if (!item) {
      return null
    }

    // 检查是否过期
    if (item.expireAt && Date.now() > item.expireAt) {
      this.delete(key)
      return null
    }

    logDebug(`✅ 缓存命中: ${key}`)
    return item.data
  }

  /**
   * 设置缓存数据
   * @param {string} key - 缓存键
   * @param {any} data - 要缓存的数据
   * @param {number} ttl - 过期时间（秒），默认 300 秒（5 分钟）
   */
  set(key, data, ttl = 300) {
    // 清除旧的定时器
    if (this.timers.has(key)) {
      clearTimeout(this.timers.get(key))
    }

    const expireAt = ttl > 0 ? Date.now() + ttl * 1000 : null

    this.cache.set(key, {
      data,
      expireAt,
      createdAt: Date.now()
    })

    // 设置自动清理定时器
    if (ttl > 0) {
      const timer = setTimeout(() => {
        this.delete(key)
      }, ttl * 1000)
      this.timers.set(key, timer)
    }

    logDebug(`💾 缓存已设置: ${key} (TTL: ${ttl}s)`)
  }

  /**
   * 删除缓存数据
   * @param {string} key - 缓存键
   */
  delete(key) {
    // 清除定时器
    if (this.timers.has(key)) {
      clearTimeout(this.timers.get(key))
      this.timers.delete(key)
    }

    const deleted = this.cache.delete(key)
    if (deleted) {
      logDebug(`🗑️ 缓存已删除: ${key}`)
    }
    return deleted
  }

  /**
   * 清除匹配模式的缓存
   * @param {string} pattern - 匹配模式（支持 * 通配符）
   * @returns {number} 删除的缓存数量
   */
  clearPattern(pattern) {
    let count = 0
    const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$')
    
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.delete(key)
        count++
      }
    }

    if (count > 0) {
      logDebug(`🗑️ 清除缓存模式 '${pattern}': ${count} 个`)
    }
    return count
  }

  /**
   * 清空所有缓存
   */
  clear() {
    // 清除所有定时器
    for (const timer of this.timers.values()) {
      clearTimeout(timer)
    }
    
    this.cache.clear()
    this.timers.clear()
    logDebug('🗑️ 已清空所有缓存')
  }

  /**
   * 获取缓存统计信息
   * @returns {Object} 统计信息
   */
  getStats() {
    const stats = {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
      items: []
    }

    for (const [key, item] of this.cache.entries()) {
      stats.items.push({
        key,
        size: JSON.stringify(item.data).length,
        createdAt: new Date(item.createdAt).toISOString(),
        expiresIn: item.expireAt ? Math.max(0, Math.round((item.expireAt - Date.now()) / 1000)) : null
      })
    }

    return stats
  }

  /**
   * 检查缓存是否存在且未过期
   * @param {string} key - 缓存键
   * @returns {boolean}
   */
  has(key) {
    return this.get(key) !== null
  }
}

// 创建全局缓存管理器实例
export const cacheManager = new CacheManager()

/**
 * 缓存装饰器 - 用于函数结果缓存
 * @param {string} prefix - 缓存键前缀
 * @param {number} ttl - 过期时间（秒）
 * @param {Function} keyBuilder - 自定义键生成函数
 */
export function cached(prefix, ttl = 300, keyBuilder = null) {
  return function(target, propertyKey, descriptor) {
    const originalMethod = descriptor.value

    descriptor.value = async function(...args) {
      // 生成缓存键
      const cacheKey = keyBuilder 
        ? keyBuilder(...args)
        : cacheManager.generateKey(prefix, args[0] || {})

      // 尝试从缓存获取
      const cachedData = cacheManager.get(cacheKey)
      if (cachedData !== null) {
        return cachedData
      }

      // 执行原函数
      const result = await originalMethod.apply(this, args)

      // 存入缓存
      if (result !== null && result !== undefined) {
        cacheManager.set(cacheKey, result, ttl)
      }

      return result
    }

    return descriptor
  }
}

export default cacheManager

