<template>
  <div class="metric-card">
    <div class="metric-icon-wrapper">
      <img :src="logo" :alt="label" class="metric-logo">
    </div>
    <div class="metric-info">
      <div class="metric-value">{{ formattedValue }}</div>
      <div class="metric-label">{{ label }}</div>
      <div class="metric-date">
        <el-icon><Calendar /></el-icon>
        <span>{{ dateRange }}</span>
      </div>
      <div class="metric-change" :class="changeClass">
        <el-icon v-if="change >= 0"><Top /></el-icon>
        <el-icon v-else><Bottom /></el-icon>
        {{ Math.abs(change).toFixed(2) }}%
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { Top, Bottom, Calendar } from '@element-plus/icons-vue'
import { formatCurrency, formatNumber } from '../../utils/formatters'

export default {
  name: 'MetricCard',
  components: { Top, Bottom, Calendar },
  props: {
    value: { type: [Number, String], required: true },
    label: { type: String, required: true },
    change: { type: Number, default: 0 },
    dateRange: { type: String, required: true },
    logo: { type: String, required: true },
    format: { type: String, default: 'number' }, // 'number', 'currency', 'percentage', 'raw'
    reverseColor: { type: Boolean, default: false } // true for cost-like metrics where decrease is good
  },
  setup(props) {
    const formattedValue = computed(() => {
      switch (props.format) {
        case 'currency':
          return `$${formatCurrency(props.value)}`
        case 'percentage':
          return `${props.value}%`
        case 'number':
          return formatNumber(props.value)
        default:
          return props.value
      }
    })

    const changeClass = computed(() => {
      if (props.change === 0) return ''
      const isPositive = props.change >= 0
      // For normal metrics, positive is good (green)
      // For reverse metrics (like cost), negative is good (green)
      if (props.reverseColor) {
        return isPositive ? 'positive' : 'negative'
      }
      return isPositive ? 'positive' : 'negative'
    })

    return { formattedValue, changeClass }
  }
}
</script>

<style scoped>
.metric-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.metric-icon-wrapper {
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: 6px;
}

.metric-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 12px;
  color: #000000;
  margin-bottom: 4px;
}

.metric-date {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 11px;
  color: #000000;
  margin-bottom: 4px;
}

.metric-date .el-icon {
  font-size: 12px;
}

.metric-change {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  font-size: 11px;
  font-weight: 600;
}

.metric-change.positive {
  color: #ef4444;
}

.metric-change.negative {
  color: #10b981;
}
</style>

