/**
 * 图表数据处理的通用 composable
 */
import { computed } from 'vue'
import { formatDate } from '../utils/formatters'

/**
 * 格式化日期范围显示
 */
export const useDateRangeDisplay = (dateRange, defaultValue = '') => {
  return computed(() => {
    if (!dateRange.value || dateRange.value.length !== 2) {
      return defaultValue
    }
    
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    
    return `${formatDate(startDate)} - ${formatDate(endDate)}`
  })
}

