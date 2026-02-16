/**
 * 数据转换工具函数
 */
import { calculateChange } from './formatters'

/**
 * 格式化日期为图表标签
 */
export const formatDateLabel = (dateString) => {
  const date = new Date(dateString)
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${date.getDate()} ${months[date.getMonth()]}`
}

/**
 * 计算数组总和
 */
export const sumByKey = (data, key) => {
  if (!data || !Array.isArray(data) || data.length === 0) return 0
  return data.reduce((sum, item) => sum + (parseFloat(item[key]) || item[key] || 0), 0)
}

/**
 * 计算ROAS数据
 */
export const calculateRoasData = (costs, conversionValues) => {
  return costs.map((cost, index) => {
    return cost > 0 ? (conversionValues[index] / cost).toFixed(2) : 0
  })
}

/**
 * 转换Google Ads性能对比数据
 */
export const transformGooglePerformanceData = (rawData) => {
  if (!rawData || !Array.isArray(rawData) || rawData.length === 0) {
    return {
      chartData: { labels: [], datasets: [] },
      totals: {},
      metrics: {},
      labels: []
    }
  }
  
  const labels = rawData.map(item => formatDateLabel(item.createtime))
  
  const metrics = {
    impressions: rawData.map(item => item.impression || 0),
    compareImpressions: rawData.map(item => item.compare_impression || 0),
    clicks: rawData.map(item => item.clicks || 0),
    compareClicks: rawData.map(item => item.compare_clicks || 0),
    conversions: rawData.map(item => item.conversions || 0),
    compareConversions: rawData.map(item => item.compare_conversions || 0),
    conversionValues: rawData.map(item => item.conversion_value || 0),
    compareConversionValues: rawData.map(item => item.compare_conversion_value || 0),
    costs: rawData.map(item => item.cost || 0),
    compareCosts: rawData.map(item => item.compare_cost || 0)
  }
  
  const totals = {
    impression: sumByKey(rawData, 'impression'),
    compare_impression: sumByKey(rawData, 'compare_impression'),
    clicks: sumByKey(rawData, 'clicks'),
    compare_clicks: sumByKey(rawData, 'compare_clicks'),
    cost: sumByKey(rawData, 'cost'),
    compare_cost: sumByKey(rawData, 'compare_cost'),
    conversions: sumByKey(rawData, 'conversions'),
    compare_conversions: sumByKey(rawData, 'compare_conversions'),
    conversion_value: sumByKey(rawData, 'conversion_value'),
    compare_conversion_value: sumByKey(rawData, 'compare_conversion_value')
  }
  
  const chartData = {
    labels,
    datasets: [
      { label: 'Impressions', data: metrics.impressions, borderColor: '#5676ff', backgroundColor: '#5676ff', fill: true, tension: 0, pointRadius: 0, pointHoverRadius: 6 },
      { label: 'Impressions(previous)', data: metrics.compareImpressions, borderColor: '#bbc8ff', backgroundColor: '#bbc8ff', fill: true, tension: 0, pointRadius: 0, pointHoverRadius: 6 },
      { label: 'Clicks', data: metrics.clicks, borderColor: '#0a0b5c', backgroundColor: '#0a0b5c', fill: true, tension: 0, pointRadius: 0, pointHoverRadius: 6 },
      { label: 'Clicks(previous)', data: metrics.compareClicks, borderColor: '#9d9dbe', backgroundColor: '#9d9dbe', fill: true, tension: 0, pointRadius: 0, pointHoverRadius: 6 }
    ]
  }
  
  return { chartData, totals, metrics, labels }
}

/**
 * 创建转换值和成本图表数据
 */
export const createConversionCostChartData = (metrics, labels) => ({
  labels,
  datasets: [
    { label: 'Conversion Value', data: metrics.conversionValues, borderColor: '#5676ff', backgroundColor: '#5676ff', fill: true, tension: 0, pointRadius: 0, pointHoverRadius: 4, borderWidth: 0 },
    { label: 'Conversion Value (Previous)', data: metrics.compareConversionValues, borderColor: '#bbc8ff', backgroundColor: '#bbc8ff', fill: true, tension: 0, pointRadius: 0, pointHoverRadius: 4, borderWidth: 0 },
    { label: 'Cost', data: metrics.costs, borderColor: '#0a0b5c', backgroundColor: '#0a0b5c', fill: true, tension: 0, pointRadius: 0, pointHoverRadius: 4, borderWidth: 0 },
    { label: 'Cost (Previous)', data: metrics.compareCosts, borderColor: '#9d9dbe', backgroundColor: '#9d9dbe', fill: true, tension: 0, pointRadius: 0, pointHoverRadius: 4, borderWidth: 0 }
  ]
})

/**
 * 更新展示数据指标
 */
export const updateImpressionsMetrics = (impressionsData, totals) => {
  impressionsData.impressions = totals.impression
  impressionsData.clicks = totals.clicks
  impressionsData.avgCpc = totals.clicks > 0 ? (totals.cost / totals.clicks).toFixed(2) : 0
  impressionsData.ctr = totals.impression > 0 ? ((totals.clicks / totals.impression) * 100).toFixed(2) : 0
  
  if (totals.compare_impression > 0) {
    impressionsData.impressionsChange = calculateChange(totals.impression, totals.compare_impression)
    impressionsData.clicksChange = calculateChange(totals.clicks, totals.compare_clicks)
    const compareAvgCpc = totals.compare_clicks > 0 ? totals.compare_cost / totals.compare_clicks : 0
    const currentAvgCpc = parseFloat(impressionsData.avgCpc)
    impressionsData.avgCpcChange = compareAvgCpc > 0 ? calculateChange(currentAvgCpc, compareAvgCpc) : 0
    const compareCtr = (totals.compare_clicks / totals.compare_impression) * 100
    const currentCtr = parseFloat(impressionsData.ctr)
    impressionsData.ctrChange = compareCtr > 0 ? calculateChange(currentCtr, compareCtr) : 0
  }
}

/**
 * 更新购买数据指标
 */
export const updatePurchasesMetrics = (purchasesData, totals, metrics) => {
  purchasesData.purchasesValue = totals.conversion_value
  purchasesData.spend = totals.cost
  purchasesData.purchases = totals.conversions
  purchasesData.roas = totals.cost > 0 ? (totals.conversion_value / totals.cost).toFixed(2) : 0
  
  if (totals.compare_conversion_value > 0) {
    purchasesData.purchasesValueChange = calculateChange(totals.conversion_value, totals.compare_conversion_value)
    purchasesData.spendChange = calculateChange(totals.cost, totals.compare_cost)
    purchasesData.purchasesChange = calculateChange(totals.conversions, totals.compare_conversions)
    const compareRoas = totals.compare_cost > 0 ? totals.compare_conversion_value / totals.compare_cost : 0
    const currentRoas = parseFloat(purchasesData.roas)
    purchasesData.roasChange = compareRoas > 0 ? calculateChange(currentRoas, compareRoas) : 0
  }
  
  purchasesData.conversionsData = metrics.conversions
  purchasesData.conversionsPreviousData = metrics.compareConversions
  purchasesData.roasData = calculateRoasData(metrics.costs, metrics.conversionValues)
  purchasesData.roasPreviousData = calculateRoasData(metrics.compareCosts, metrics.compareConversionValues)
}

/**
 * 转换Google Ads广告系列数据
 */
export const transformGoogleCampaignData = (rawData) => {
  if (!rawData || !Array.isArray(rawData)) return []
  
  return rawData.map(item => ({
    name: item.campaign || 'Unknown',
    impression: item.impression || 0,
    impressionPrevious: item.compare_impression || 0,
    clicks: item.clicks || 0,
    clicksPrevious: item.compare_clicks || 0,
    spend: item.cost || 0,
    spendPrevious: item.compare_cost || 0,
    purchases: item.conversions || 0,
    purchasesPrevious: item.compare_conversions || 0,
    purchaseRoas: item.roas || 0,
    purchaseRoasPrevious: item.compare_roas || 0,
    purchasesValue: item.conversion_value || 0,
    purchasesValuePrevious: item.compare_conversion_value || 0,
    ctr: item.ctr ? (item.ctr * 100) : 0,
    ctrPrevious: item.compare_ctr ? (item.compare_ctr * 100) : 0,
    cpc: item.cpc || 0,
    cpcPrevious: item.compare_cpc || 0
  }))
}

/**
 * 转换Google Ads广告表现数据
 */
export const transformGoogleAdsPerformanceData = (rawData) => {
  if (!rawData || !Array.isArray(rawData)) return []
  
  return rawData.map(item => ({
    product: item.campaign_name || 'Unknown',
    conversions: {
      lastWeek: item.last_conversions || 0,
      thisWeek: item.current_conversions || 0
    },
    conversionValue: {
      lastWeek: item.last_conversion_value || 0,
      thisWeek: item.current_conversion_value || 0
    },
    cost: {
      lastWeek: item.last_cost || 0,
      thisWeek: item.current_cost || 0
    },
    roas: {
      lastWeek: item.last_roas || 0,
      thisWeek: item.current_roas || 0
    }
  }))
}

/**
 * 转换Google Ads概览汇总数据（直接从API获取，支持对比数据）
 */
export const transformGoogleOverviewSummary = (summaryData) => {
  if (!summaryData || typeof summaryData !== 'object') {
    return {
      impressionsData: {},
      purchasesData: {}
    }
  }
  
  // 处理当前期每日数据用于图表
  const dailyData = summaryData.daily_data || []
  const labels = dailyData.map(item => formatDateLabel(item.date))
  const impressionsArray = dailyData.map(item => item.impressions || 0)
  const clicksArray = dailyData.map(item => item.clicks || 0)
  const conversionsArray = dailyData.map(item => item.conversions || 0)
  const conversionsValueArray = dailyData.map(item => item.conversions_value || 0)
  const costArray = dailyData.map(item => item.cost || 0)
  
  // 处理对比期每日数据
  const compareDailyData = summaryData.compare_daily_data || []
  const compareImpressionsArray = compareDailyData.map(item => item.impressions || 0)
  const compareClicksArray = compareDailyData.map(item => item.clicks || 0)
  const compareConversionsArray = compareDailyData.map(item => item.conversions || 0)
  const compareConversionsValueArray = compareDailyData.map(item => item.conversions_value || 0)
  const compareCostArray = compareDailyData.map(item => item.cost || 0)
  
  // 构建展示趋势图表数据（包含对比数据）
  const impressionsChartDatasets = [
    {
      label: 'Impressions',
      data: impressionsArray,
      borderColor: '#5676ff',
      backgroundColor: '#5676ff',
      fill: true,
      tension: 0,
      pointRadius: 0,
      pointHoverRadius: 4,
      borderWidth: 2
    },
    {
      label: 'Clicks',
      data: clicksArray,
      borderColor: '#0a0b5c',
      backgroundColor: '#0a0b5c',
      fill: true,
      tension: 0,
      pointRadius: 0,
      pointHoverRadius: 4,
      borderWidth: 2
    }
  ]
  
  // 如果有对比数据，添加对比数据线
  if (compareDailyData.length > 0) {
    impressionsChartDatasets.push(
      {
        label: 'Impressions (Previous)',
        data: compareImpressionsArray,
        borderColor: '#bbc8ff',
        backgroundColor: '#bbc8ff',
        fill: true,
        tension: 0,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 2
      },
      {
        label: 'Clicks (Previous)',
        data: compareClicksArray,
        borderColor: '#9d9dbe',
        backgroundColor: '#9d9dbe',
        fill: true,
        tension: 0,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 2
      }
    )
  }
  
  const impressionsChartData = {
    labels,
    datasets: impressionsChartDatasets
  }
  
  // 构建转化价值和成本图表数据（包含对比数据）
  const purchasesChartDatasets = [
    {
      label: 'Conversion Value',
      data: conversionsValueArray,
      borderColor: '#5676ff',
      backgroundColor: '#5676ff',
      fill: true,
      tension: 0,
      pointRadius: 0,
      pointHoverRadius: 4,
      borderWidth: 2
    },
    {
      label: 'Cost',
      data: costArray,
      borderColor: '#0a0b5c',
      backgroundColor: '#0a0b5c',
      fill: true,
      tension: 0,
      pointRadius: 0,
      pointHoverRadius: 4,
      borderWidth: 2
    }
  ]
  
  // 如果有对比数据，添加对比数据线
  if (compareDailyData.length > 0) {
    purchasesChartDatasets.push(
      {
        label: 'Conversion Value (Previous)',
        data: compareConversionsValueArray,
        borderColor: '#bbc8ff',
        backgroundColor: '#bbc8ff',
        fill: true,
        tension: 0,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 2
      },
      {
        label: 'Cost (Previous)',
        data: compareCostArray,
        borderColor: '#9d9dbe',
        backgroundColor: '#9d9dbe',
        fill: true,
        tension: 0,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 2
      }
    )
  }
  
  const purchasesChartData = {
    labels,
    datasets: purchasesChartDatasets
  }
  
  // 计算 ROAS 数据
  const roasArray = costArray.map((cost, index) => {
    return cost > 0 ? (conversionsValueArray[index] / cost).toFixed(2) : 0
  })
  
  const compareRoasArray = compareCostArray.map((cost, index) => {
    return cost > 0 ? (compareConversionsValueArray[index] / cost).toFixed(2) : 0
  })
  
  // 计算变化百分比
  const impressionsChange = summaryData.compare_impressions > 0 
    ? calculateChange(summaryData.impressions, summaryData.compare_impressions)
    : 0
  const clicksChange = summaryData.compare_clicks > 0
    ? calculateChange(summaryData.clicks, summaryData.compare_clicks)
    : 0
  const avgCpcChange = summaryData.compare_average_cpc > 0
    ? calculateChange(summaryData.average_cpc, summaryData.compare_average_cpc)
    : 0
  const ctrChange = summaryData.compare_ctr > 0
    ? calculateChange(summaryData.ctr, summaryData.compare_ctr)
    : 0
  const purchasesValueChange = summaryData.compare_conversions_value > 0
    ? calculateChange(summaryData.conversions_value, summaryData.compare_conversions_value)
    : 0
  const spendChange = summaryData.compare_cost > 0
    ? calculateChange(summaryData.cost, summaryData.compare_cost)
    : 0
  const purchasesChange = summaryData.compare_conversions > 0
    ? calculateChange(summaryData.conversions, summaryData.compare_conversions)
    : 0
  
  // 计算 ROAS 变化
  const currentRoas = summaryData.cost > 0 
    ? summaryData.conversions_value / summaryData.cost 
    : 0
  const compareRoas = summaryData.compare_cost > 0
    ? summaryData.compare_conversions_value / summaryData.compare_cost
    : 0
  const roasChange = compareRoas > 0 ? calculateChange(currentRoas, compareRoas) : 0
  
  // 转换为展示数据格式（用原始数据计算完环比后，再对显示值进行格式化）
  const impressionsData = {
    impressions: summaryData.impressions || 0,
    clicks: summaryData.clicks || 0,
    avgCpc: Number((summaryData.average_cpc || 0).toFixed(2)),
    ctr: Number((summaryData.ctr || 0).toFixed(2)),
    impressionsChange,
    clicksChange,
    avgCpcChange,
    ctrChange,
    chartData: impressionsChartData
  }
  
  // 转换为购买数据格式（用原始数据计算完环比后，再对显示值进行格式化）
  const purchasesData = {
    purchasesValue: Number((summaryData.conversions_value || 0).toFixed(2)),
    spend: Number((summaryData.cost || 0).toFixed(2)),
    purchases: Number((summaryData.conversions || 0).toFixed(2)),
    roas: Number(currentRoas.toFixed(2)),
    purchasesValueChange,
    spendChange,
    purchasesChange,
    roasChange,
    conversionsData: conversionsArray,
    conversionsPreviousData: compareConversionsArray,
    roasData: roasArray,
    roasPreviousData: compareRoasArray,
    chartData: purchasesChartData
  }
  
  return {
    impressionsData,
    purchasesData
  }
}