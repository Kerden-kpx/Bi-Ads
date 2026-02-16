<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title">Top Funnel Overview</div>
    </div>

    <!-- Loading状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <span class="loading-text">Fetching Data. Please wait...</span>
    </div>

    <!-- 数据内容 -->
    <template v-else>
      <div class="chart-container">
        <LineChart :data="chartData" :options="chartOptions" />
      </div>

      <div class="metrics-grid">
        <MetricCard
          v-for="metric in metricsConfig"
          :key="metric.label"
          :value="data[metric.key]"
          :label="metric.label"
          :change="data[`${metric.key}Change`]"
          :date-range="formattedDateRange"
          :logo="googleAdsLogo"
          :format="metric.format"
        />
      </div>
    </template>
  </div>
</template>

<script>
import { computed } from 'vue'
import { Line as LineChart } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import MetricCard from '../shared/Metric_Card.vue'
import { useDateRangeDisplay } from '../../composables/useChartData'
import { createLineChartOptions } from '../../utils/chartConfig'
import googleAdsLogo from '@/assets/logos/google_ads_logo.png'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

export default {
  name: 'Google_Impressions_Reach_Card',
  components: { LineChart, MetricCard },
  props: {
    data: { type: Object, required: true },
    dateRange: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  setup(props) {
    const formattedDateRange = useDateRangeDisplay(computed(() => props.dateRange), 'Oct 1, 2025 - Oct 7, 2025')

    const chartData = computed(() => props.data.chartData || { labels: [], datasets: [] })
    const chartOptions = createLineChartOptions({
      valueFormatter: (value) => value.toLocaleString()
    })

    const metricsConfig = [
      { key: 'impressions', label: 'Impressions', format: 'number' },
      { key: 'clicks', label: 'Clicks', format: 'number' },
      { key: 'avgCpc', label: 'Avg. CPC', format: 'currency' },
      { key: 'ctr', label: 'Avg. CTR', format: 'percentage' }
    ]

    return {
      chartData,
      chartOptions,
      formattedDateRange,
      metricsConfig,
      googleAdsLogo
    }
  }
}
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 400px;
  color: #909399;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #909399;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 14px;
  font-weight: 400;
  color: #606266;
  white-space: nowrap;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
