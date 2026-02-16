/**
 * 图表通用配置工具
 * 用于减少重复的图表配置代码
 */

/**
 * 创建基础图例配置
 */
export const createLegendConfig = (position = 'bottom', align = 'center') => ({
  position,
  align,
  labels: {
    usePointStyle: true,
    pointStyle: 'rectRounded',
    boxWidth: 8,
    boxHeight: 8,
    padding: 12,
    font: {
      size: 12,
      weight: 'normal'
    },
    generateLabels: (chart) => {
      const datasets = chart.data.datasets
      return datasets.map((dataset, i) => ({
        text: dataset.label,
        fillStyle: dataset.backgroundColor || dataset.borderColor,
        strokeStyle: dataset.backgroundColor || dataset.borderColor,
        lineWidth: 0,
        hidden: !chart.isDatasetVisible(i),
        index: i,
        pointStyle: 'rectRounded'
      }))
    }
  }
})

/**
 * 创建基础提示配置
 */
export const createTooltipConfig = (valueFormatter = null) => ({
  mode: 'index',
  intersect: false,
  backgroundColor: 'rgba(255, 255, 255, 0.95)',
  titleColor: '#000000',
  bodyColor: '#000000',
  borderColor: '#ddd',
  borderWidth: 1,
  cornerRadius: 8,
  displayColors: true,
  usePointStyle: true,   // 使用点样式
  pointStyle: 'circle',  // 圆形
  boxWidth: 6,      // 圆形直径
  boxHeight: 6,     // 圆形直径
  boxPadding: 4,    // 圆形与文字之间的间距
  callbacks: {
    label: function(context) {
      const value = valueFormatter 
        ? valueFormatter(context.parsed.y)
        : context.parsed.y.toLocaleString()
      return `${context.dataset.label}: ${value}`
    }
  }
})

/**
 * 创建X轴配置
 */
export const createXAxisConfig = (stacked = true, fontSize = 12) => ({
  stacked,
  grid: {
    display: false
  },
  ticks: {
    font: { size: fontSize },
    color: '#000000'
  }
})

/**
 * 创建Y轴配置
 */
export const createYAxisConfig = (options = {}) => {
  const {
    stacked = true,
    beginAtZero = true,
    suggestedMax = null,
    fontSize = 12,
    valueFormatter = null
  } = options

  return {
    stacked,
    beginAtZero,
    ...(suggestedMax && { suggestedMax }),
    grid: {
      color: 'rgba(0, 0, 0, 0.1)',
      drawBorder: false
    },
    ticks: {
      font: { size: fontSize },
      color: '#000000',
      ...(valueFormatter && {
        callback: valueFormatter
      })
    }
  }
}

/**
 * 创建完整的折线图/面积图配置
 */
export const createLineChartOptions = (options = {}) => {
  const {
    maxYValue = null,
    valueFormatter = (value) => value.toLocaleString(),
    stacked = true
  } = options

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: createLegendConfig(),
      tooltip: createTooltipConfig(valueFormatter)
    },
    scales: {
      x: createXAxisConfig(stacked),
      y: createYAxisConfig({
        stacked,
        suggestedMax: maxYValue,
        valueFormatter
      })
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  }
}

/**
 * 创建柱状图配置
 */
export const createBarChartOptions = (options = {}) => {
  const {
    maxYValue = null,
    valueFormatter = (value) => value.toFixed(2),
    stacked = false
  } = options

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: createLegendConfig(),
      tooltip: createTooltipConfig(valueFormatter)
    },
    scales: {
      x: createXAxisConfig(false, 12),
      y: createYAxisConfig({
        stacked,
        beginAtZero: true,
        suggestedMax: maxYValue,
        fontSize: 12,
        valueFormatter
      })
    },
    interaction: {
      mode: 'index',
      intersect: false
    }
  }
}

/**
 * 创建数据集配置
 */
export const createDataset = (label, data, color, options = {}) => {
  const {
    type = 'line', // 'line' or 'bar'
    fill = true,
    tension = 0,
    pointRadius = 0,
    pointHoverRadius = 4,
    borderWidth = 2,
    barThickness = 16,
    borderRadius = 4
  } = options

  const baseConfig = {
    label,
    data,
    borderColor: color,
    backgroundColor: color,
    borderWidth
  }

  if (type === 'line') {
    return {
      ...baseConfig,
      fill,
      tension,
      pointRadius,
      pointHoverRadius
    }
  } else {
    return {
      ...baseConfig,
      barThickness,
      borderRadius
    }
  }
}

/**
 * 格式化货币值（用于图表）
 */
export const currencyFormatter = (value) => 
  '$' + value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

/**
 * 格式化数字值（用于图表）
 */
export const numberFormatter = (value) => value.toLocaleString()

/**
 * 格式化小数值（用于图表）
 */
export const decimalFormatter = (decimals = 2) => (value) => value.toFixed(decimals)

