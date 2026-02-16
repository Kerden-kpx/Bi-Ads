/**
 * 通用指标获取 composable（直接使用API返回的数据，不做任何计算）
 */
import { computed } from 'vue'

/**
 * 从性能对比数据获取指标（不做计算，直接使用API返回的数据）
 */
export const useMetricsFromComparison = (performanceData, fallbackData) => {
  const metrics = computed(() => {
    // 所有指标卡数据都直接从fallbackData获取（后端API返回），不做任何计算
    if (!performanceData.value || performanceData.value.length === 0) {
      return fallbackData.value || {}
    }

    // 直接使用后端API返回的所有数据，不进行任何前端计算
    return {
      // 基础指标 - 直接从API获取
      impressions: fallbackData.value?.impressions || 0,
      reach: fallbackData.value?.reach || 0,
      clicks: fallbackData.value?.clicks || 0,
      uniqueLinkClicks: fallbackData.value?.uniqueLinkClicks || 0,
      spend: fallbackData.value?.spend || 0,
      purchases: fallbackData.value?.purchases || 0,
      purchasesValue: fallbackData.value?.purchasesValue || 0,
      addsToCart: fallbackData.value?.addsToCart || 0,
      addsPaymentInfo: fallbackData.value?.addsPaymentInfo || 0,
      
      // 比率指标 - 直接从API获取
      ctr: fallbackData.value?.ctr || 0,
      cpm: fallbackData.value?.cpm || 0,
      roas: fallbackData.value?.roas || 0,
      
      // 所有变化百分比 - 直接从API获取
      impressionsChange: fallbackData.value?.impressionsChange || 0,
      reachChange: fallbackData.value?.reachChange || 0,
      clicksChange: fallbackData.value?.clicksChange || 0,
      uniqueLinkClicksChange: fallbackData.value?.uniqueLinkClicksChange || 0,
      ctrChange: fallbackData.value?.ctrChange || 0,
      cpmChange: fallbackData.value?.cpmChange || 0,
      spendChange: fallbackData.value?.spendChange || 0,
      purchasesChange: fallbackData.value?.purchasesChange || 0,
      purchasesValueChange: fallbackData.value?.purchasesValueChange || 0,
      roasChange: fallbackData.value?.roasChange || 0,
      addsToCartChange: fallbackData.value?.addsToCartChange || 0,
      addsPaymentInfoChange: fallbackData.value?.addsPaymentInfoChange || 0
    }
  })

  return metrics
}

/**
 * 创建图表数据集
 */
export const useChartDatasets = (performanceData, config) => {
  return computed(() => {
    if (!performanceData.value || performanceData.value.length === 0) {
      return { labels: [], datasets: [] }
    }

    const labels = performanceData.value.map(item => {
      const date = new Date(item.createtime || item.date)
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      return `${months[date.getMonth()]} ${date.getDate()}`
    })

    const datasets = config.map(({ label, field, compareField, color, compareColor, ...options }) => {
      const baseDataset = {
        label,
        data: performanceData.value.map(item => parseFloat(item[field]) || item[field] || 0),
        borderColor: color,
        backgroundColor: color,
        fill: true,
        tension: 0,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 2,
        ...options
      }

      if (compareField) {
        return [
          baseDataset,
          {
            ...baseDataset,
            label: `${label} (Previous)`,
            data: performanceData.value.map(item => parseFloat(item[compareField]) || item[compareField] || 0),
            borderColor: compareColor || color,
            backgroundColor: compareColor || color
          }
        ]
      }

      return baseDataset
    }).flat()

    return { labels, datasets }
  })
}

