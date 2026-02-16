<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title">Conversion Value & Cost Overview</div>
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

      <div class="additional-charts-grid">
        <div class="chart-wrapper">
          <div class="chart-container-small">
            <BarChart :data="conversionsChartData" :options="conversionsChartOptions" />
          </div>
        </div>
        <div class="chart-wrapper">
          <div class="chart-container-small">
            <LineChart :data="roasChartData" :options="roasChartOptions" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { computed } from 'vue'
import { Line as LineChart, Bar as BarChart } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import MetricCard from '../shared/Metric_Card.vue'
import { useDateRangeDisplay } from '../../composables/useChartData'
import { createLineChartOptions, createBarChartOptions, currencyFormatter, decimalFormatter } from '../../utils/chartConfig'
import googleAdsLogo from '@/assets/logos/google_ads_logo.png'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler)

export default {
  name: 'Google_Purchases_Spend_Card',
  components: { LineChart, BarChart, MetricCard },
  props: {
    data: { type: Object, required: true },
    dateRange: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  setup(props) {
    const formattedDateRange = useDateRangeDisplay(computed(() => props.dateRange), 'Aug 4, 2025 - Aug 10, 2025')

    const chartData = computed(() => props.data.chartData || { labels: [], datasets: [] })
    const chartOptions = createLineChartOptions({ valueFormatter: currencyFormatter })

    const metricsConfig = [
      { key: 'purchasesValue', label: 'Conversion Value', format: 'currency' },
      { key: 'spend', label: 'Cost', format: 'currency' },
      { key: 'purchases', label: 'Conversions', format: 'number' },
      { key: 'roas', label: 'ROAS', format: 'raw' }
    ]

    const conversionsChartData = computed(() => ({
      labels: props.data.chartData?.labels || [],
      datasets: [
        {
          label: 'Conversions',
          data: props.data.conversionsData || [],
          backgroundColor: '#5676ff',
          borderRadius: 4,
          barThickness: 16
        },
        {
          label: 'Conversions (Previous)',
          data: props.data.conversionsPreviousData || [],
          backgroundColor: '#bbc8ff',
          borderRadius: 4,
          barThickness: 16
        }
      ]
    }))

    const maxConversionsValue = computed(() => {
      const allValues = [
        ...(props.data.conversionsData || []),
        ...(props.data.conversionsPreviousData || [])
      ]
      const max = Math.max(...allValues, 0)
      return max > 0 ? Math.ceil(max * 1.1) : 20
    })

    const conversionsChartOptions = createBarChartOptions({
      maxYValue: maxConversionsValue.value,
      valueFormatter: decimalFormatter(2)
    })

    const roasChartData = computed(() => ({
      labels: props.data.chartData?.labels || [],
      datasets: [
        {
          label: 'ROAS',
          data: props.data.roasData || [],
          borderColor: '#5676ff',
          backgroundColor: '#5676ff',
          fill: false,
          tension: 0,
          pointRadius: 0,
          pointHoverRadius: 4,
          borderWidth: 2
        },
        {
          label: 'ROAS (Previous)',
          data: props.data.roasPreviousData || [],
          borderColor: '#bbc8ff',
          backgroundColor: '#bbc8ff',
          fill: false,
          tension: 0,
          pointRadius: 0,
          pointHoverRadius: 4,
          borderWidth: 2
        }
      ]
    }))

    const maxRoasValue = computed(() => {
      const allValues = [
        ...(props.data.roasData || []).map(v => parseFloat(v) || 0),
        ...(props.data.roasPreviousData || []).map(v => parseFloat(v) || 0)
      ]
      const max = Math.max(...allValues, 0)
      return max > 0 ? Math.ceil(max * 1.1) : 9
    })

    const roasChartOptions = createLineChartOptions({
      maxYValue: maxRoasValue.value,
      valueFormatter: decimalFormatter(2),
      stacked: false
    })

    return {
      chartData,
      chartOptions,
      conversionsChartData,
      conversionsChartOptions,
      roasChartData,
      roasChartOptions,
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

.additional-charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 24px;
}

.chart-wrapper {
  width: 100%;
  background: white;
  border-radius: 8px;
  padding: 16px;
}

.chart-container-small {
  width: 100%;
  height: 280px;
  position: relative;
}

@media (max-width: 768px) {
  .metrics-grid,
  .additional-charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
