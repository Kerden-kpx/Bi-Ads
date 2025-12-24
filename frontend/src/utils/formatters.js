/**
 * 通用格式化工具函数
 * 用于整个应用的数据格式化
 */

/**
 * 格式化数字为货币格式（带两位小数）
 * @param {number} amount - 要格式化的金额
 * @param {number} decimals - 小数位数（默认为2）
 * @param {boolean} includeCurrency - 是否包含货币符号（默认为 false，只返回数字）
 * @param {string} currencySymbol - 货币符号（默认为 $）
 * @returns {string} 格式化后的货币字符串
 */
export const formatCurrency = (amount, decimals = 2, includeCurrency = false, currencySymbol = '$') => {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return includeCurrency ? `${currencySymbol}${'0.' + '0'.repeat(decimals)}` : '0.' + '0'.repeat(decimals)
  }
  const formatted = amount.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
  return includeCurrency ? `${currencySymbol}${formatted}` : formatted
}

// formatAmount 是 formatCurrency 的别名，保持向后兼容
export const formatAmount = formatCurrency

/**
 * 格式化数字为小数格式（带两位小数）
 * @param {number} num - 要格式化的数字
 * @param {number} decimals - 小数位数（默认为2）
 * @returns {string} 格式化后的小数字符串
 */
export const formatDecimal = (num, decimals = 2) => {
  if (num === null || num === undefined || isNaN(num)) {
    return '0.' + '0'.repeat(decimals)
  }
  return num.toFixed(decimals)
}

/**
 * 格式化数字为百分比格式（带两位小数）
 * @param {number} num - 要格式化的数字
 * @param {number} decimals - 小数位数（默认为2）
 * @returns {string} 格式化后的百分比字符串（带%符号）
 */
export const formatPercentage = (num, decimals = 2) => {
  if (num === null || num === undefined || isNaN(num)) {
    return '0.' + '0'.repeat(decimals) + '%'
  }
  return num.toFixed(decimals) + '%'
}

/**
 * 格式化大数字（添加千位分隔符）
 * @param {number} num - 要格式化的数字
 * @returns {string} 格式化后的数字字符串
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined || isNaN(num)) {
    return '0'
  }
  return num.toLocaleString('en-US')
}

/**
 * 格式化日期为简短格式（例如：Jan 15, 2025）
 * @param {string|Date} date - 要格式化的日期
 * @returns {string} 格式化后的日期字符串
 */
export const formatDate = (date) => {
  if (!date) return ''
  
  const d = new Date(date)
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  
  return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`
}

/**
 * 格式化日期范围
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {string} 格式化后的日期范围字符串
 */
export const formatDateRange = (startDate, endDate) => {
  if (!startDate || !endDate) return ''
  return `${formatDate(startDate)} - ${formatDate(endDate)}`
}

/**
 * 格式化变化百分比（带颜色类名）
 * @param {number} change - 变化百分比
 * @returns {object} 包含 value（格式化的值）和 class（CSS类名）
 */
export const formatChange = (change) => {
  if (change === null || change === undefined || isNaN(change)) {
    return { value: '0.00%', class: 'neutral' }
  }
  
  const value = Math.abs(change).toFixed(2) + '%'
  const className = change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
  
  return {
    value,
    class: className,
    icon: change > 0 ? 'top' : change < 0 ? 'bottom' : 'minus'
  }
}

/**
 * 计算变化百分比
 * @param {number} current - 当前值
 * @param {number} previous - 之前的值
 * @param {number} decimals - 小数位数（默认为2）
 * @returns {number|string} 变化百分比（数字或字符串）
 */
export const calculateChange = (current, previous, decimals = 2) => {
  if (previous === 0 || previous === null || previous === undefined) {
    return decimals !== null ? '0.' + '0'.repeat(decimals) : 0
  }
  const change = ((current - previous) / previous) * 100
  return decimals !== null ? change.toFixed(decimals) : change
}

/**
 * 缩写大数字（例如：1.2K, 3.4M）
 * @param {number} num - 要缩写的数字
 * @returns {string} 缩写后的字符串
 */
export const abbreviateNumber = (num) => {
  if (num === null || num === undefined || isNaN(num)) {
    return '0'
  }
  
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

/**
 * 验证并格式化日期字符串为 YYYY-MM-DD
 * @param {string|Date} date - 日期
 * @returns {string} YYYY-MM-DD 格式的日期字符串
 */
export const toISODateString = (date) => {
  if (!date) return ''
  
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  
  return `${year}-${month}-${day}`
}
