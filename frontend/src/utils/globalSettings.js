/**
 * 全局设置管理器
 * 用于同步所有页面的设置状态
 */

const GLOBAL_SETTINGS_KEY = 'global_auto_sync_enabled'

export const globalSettings = {
  /**
   * 获取自动同步设置
   */
  getAutoSyncEnabled() {
    const saved = localStorage.getItem(GLOBAL_SETTINGS_KEY)
    return saved ? JSON.parse(saved) : false
  },

  /**
   * 保存自动同步设置
   */
  setAutoSyncEnabled(value) {
    localStorage.setItem(GLOBAL_SETTINGS_KEY, JSON.stringify(value))
    // 触发自定义事件，通知其他页面
    window.dispatchEvent(new CustomEvent('global-settings-changed', {
      detail: { autoSyncEnabled: value }
    }))
  },

  /**
   * 监听设置变化
   */
  onSettingsChange(callback) {
    const handler = (event) => {
      if (event.detail) {
        callback(event.detail.autoSyncEnabled)
      }
    }
    window.addEventListener('global-settings-changed', handler)
    
    // 返回取消监听的函数
    return () => {
      window.removeEventListener('global-settings-changed', handler)
    }
  }
}

export default globalSettings


