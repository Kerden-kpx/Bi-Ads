<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title">{{ title }}</div>
      <div class="card-actions" v-if="showDatePicker">
        <SingleDatePicker
          v-model="selectedDate"
          placeholder="Select date"
          @update:modelValue="handleDateChange"
        />
      </div>
    </div>

    <!-- Loading状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <span class="loading-text">Fetching Data. Please wait...</span>
    </div>

    <!-- 数据内容 -->
    <div v-else class="card-content">
      <div class="table-wrapper">
        <el-table 
          :data="dataWithTotal" 
          class="responsive-table"
          stripe
          border
          :fit="true"
        >
          <el-table-column 
            type="index" 
            label="编号" 
            width="80"
            align="center"
            :index="indexMethod"
            :fixed="fixFirstTwoColumns ? 'left' : false"
          />
          <el-table-column 
            prop="product" 
            label="产品名称" 
            min-width="150"
            align="center"
            show-overflow-tooltip
            :fixed="fixFirstTwoColumns ? 'left' : false"
          />
      
          <el-table-column label="转化" align="center">
            <el-table-column 
              prop="conversions.thisWeek" 
              label="本周" 
              min-width="90"
              align="center"
            >
              <template #default="scope">
                <span :class="getComparisonClass(scope.row.conversions?.thisWeek, scope.row.conversions?.lastWeek)" class="value-with-icon">
                  {{ formatDecimal(scope.row.conversions?.thisWeek) }}
                  <el-icon v-if="getTrendIcon(scope.row.conversions?.thisWeek, scope.row.conversions?.lastWeek) === 'up'" class="trend-icon">
                    <Top />
                  </el-icon>
                  <el-icon v-if="getTrendIcon(scope.row.conversions?.thisWeek, scope.row.conversions?.lastWeek) === 'down'" class="trend-icon">
                    <Bottom />
                  </el-icon>
                </span>
              </template>
            </el-table-column>
            <el-table-column 
              prop="conversions.lastWeek" 
              label="上周" 
              min-width="90"
              align="center"
            >
              <template #default="scope">
                {{ formatDecimal(scope.row.conversions?.lastWeek) }}
              </template>
            </el-table-column>
          </el-table-column>
          
          <el-table-column label="转化价值" align="center">
            <el-table-column 
              prop="conversionValue.thisWeek" 
              label="本周" 
              min-width="130"
              align="center"
            >
              <template #default="scope">
                <span :class="getComparisonClass(scope.row.conversionValue?.thisWeek, scope.row.conversionValue?.lastWeek)" class="value-with-icon">
                  ${{ formatCurrency(scope.row.conversionValue?.thisWeek || 0) }}
                  <el-icon v-if="getTrendIcon(scope.row.conversionValue?.thisWeek, scope.row.conversionValue?.lastWeek) === 'up'" class="trend-icon">
                    <Top />
                  </el-icon>
                  <el-icon v-if="getTrendIcon(scope.row.conversionValue?.thisWeek, scope.row.conversionValue?.lastWeek) === 'down'" class="trend-icon">
                    <Bottom />
                  </el-icon>
                </span>
              </template>
            </el-table-column>
            <el-table-column 
              prop="conversionValue.lastWeek" 
              label="上周" 
              min-width="130"
              align="center"
            >
              <template #default="scope">
                ${{ formatCurrency(scope.row.conversionValue?.lastWeek || 0) }}
              </template>
            </el-table-column>
          </el-table-column>
          
          <el-table-column label="花费" align="center">
            <el-table-column 
              prop="cost.thisWeek" 
              label="本周" 
              min-width="130"
              align="center"
            >
              <template #default="scope">
                <span :class="getComparisonClassReverse(scope.row.cost?.thisWeek, scope.row.cost?.lastWeek)" class="value-with-icon">
                  ${{ formatCurrency(scope.row.cost?.thisWeek || 0) }}
                  <el-icon v-if="getTrendIconReverse(scope.row.cost?.thisWeek, scope.row.cost?.lastWeek) === 'up'" class="trend-icon">
                    <Top />
                  </el-icon>
                  <el-icon v-if="getTrendIconReverse(scope.row.cost?.thisWeek, scope.row.cost?.lastWeek) === 'down'" class="trend-icon">
                    <Bottom />
                  </el-icon>
                </span>
              </template>
            </el-table-column>
            <el-table-column 
              prop="cost.lastWeek" 
              label="上周" 
              min-width="130"
              align="center"
            >
              <template #default="scope">
                ${{ formatCurrency(scope.row.cost.lastWeek) }}
              </template>
            </el-table-column>
          </el-table-column>
          
          <el-table-column label="ROAS" align="center">
            <el-table-column 
              prop="roas.thisWeek" 
              label="本周" 
              min-width="90"
              align="center"
            >
              <template #default="scope">
                <span :class="getComparisonClass(scope.row.roas?.thisWeek, scope.row.roas?.lastWeek)" class="value-with-icon">
                  {{ formatDecimal(scope.row.roas?.thisWeek) }}
                  <el-icon v-if="getTrendIcon(scope.row.roas?.thisWeek, scope.row.roas?.lastWeek) === 'up'" class="trend-icon">
                    <Top />
                  </el-icon>
                  <el-icon v-if="getTrendIcon(scope.row.roas?.thisWeek, scope.row.roas?.lastWeek) === 'down'" class="trend-icon">
                    <Bottom />
                  </el-icon>
                </span>
              </template>
            </el-table-column>
            <el-table-column 
              prop="roas.lastWeek" 
              label="上周" 
              min-width="90"
              align="center"
            >
              <template #default="scope">
                {{ formatDecimal(scope.row.roas?.lastWeek) }}
              </template>
            </el-table-column>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'
import { formatCurrency, formatDecimal as formatDec } from '../../utils/formatters'
import SingleDatePicker from './Single_Date_Picker.vue'
import { Top, Bottom } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

export default {
  name: 'PerformanceCard',
  components: { SingleDatePicker, Top, Bottom },
  props: {
    data: { type: Array, required: true },
    dateRange: { type: String, default: () => dayjs().format('YYYY-MM-DD') },
    title: { type: String, default: 'Performance Overview (Weekly)' },
    showDatePicker: { type: Boolean, default: true },
    fixFirstTwoColumns: { type: Boolean, default: false },
    loading: { type: Boolean, default: false }
  },
  emits: ['date-change'],
  setup(props, { emit }) {
    const selectedDate = ref(props.dateRange)

    const handleDateChange = (newDate) => {
      emit('date-change', newDate)
    }

    watch(() => props.dateRange, (val) => {
      selectedDate.value = val
    })

    const totalRow = computed(() => {
      if (!props.data || props.data.length === 0) {
        return {
          product: '合计',
          conversions: { lastWeek: 0, thisWeek: 0 },
          conversionValue: { lastWeek: 0, thisWeek: 0 },
          cost: { lastWeek: 0, thisWeek: 0 },
          roas: { lastWeek: 0, thisWeek: 0 }
        }
      }

      const total = {
        product: '合计',
        conversions: { lastWeek: 0, thisWeek: 0 },
        conversionValue: { lastWeek: 0, thisWeek: 0 },
        cost: { lastWeek: 0, thisWeek: 0 },
        roas: { lastWeek: 0, thisWeek: 0 }
      }

      props.data.forEach(row => {
        total.conversions.lastWeek += row.conversions?.lastWeek || 0
        total.conversions.thisWeek += row.conversions?.thisWeek || 0
        total.conversionValue.lastWeek += row.conversionValue?.lastWeek || 0
        total.conversionValue.thisWeek += row.conversionValue?.thisWeek || 0
        total.cost.lastWeek += row.cost?.lastWeek || 0
        total.cost.thisWeek += row.cost?.thisWeek || 0
      })
      total.conversions.lastWeek = parseFloat(total.conversions.lastWeek.toFixed(2))
      total.conversions.thisWeek = parseFloat(total.conversions.thisWeek.toFixed(2))
      total.conversionValue.lastWeek = parseFloat(total.conversionValue.lastWeek.toFixed(2))
      total.conversionValue.thisWeek = parseFloat(total.conversionValue.thisWeek.toFixed(2))
      total.cost.lastWeek = parseFloat(total.cost.lastWeek.toFixed(2))
      total.cost.thisWeek = parseFloat(total.cost.thisWeek.toFixed(2))
      total.roas.lastWeek = total.cost.lastWeek > 0 
        ? parseFloat((total.conversionValue.lastWeek / total.cost.lastWeek).toFixed(2))
        : 0
      total.roas.thisWeek = total.cost.thisWeek > 0 
        ? parseFloat((total.conversionValue.thisWeek / total.cost.thisWeek).toFixed(2))
        : 0

      return total
    })

    const dataWithTotal = computed(() => {
      if (!props.data || props.data.length === 0) {
        return [totalRow.value]
      }
      return [...props.data, totalRow.value]
    })

    const getComparisonClass = (current, previous) => {
      if (!current || !previous) return ''
      if (current > previous) return 'value-increase'
      if (current < previous) return 'value-decrease'
      return ''
    }

    const getComparisonClassReverse = (current, previous) => {
      if (!current || !previous) return ''
      if (current < previous) return 'value-decrease'
      if (current > previous) return 'value-increase'
      return ''
    }

    const getTrendIcon = (current, previous) => {
      if (!current || !previous) return null
      if (current > previous) return 'up'
      if (current < previous) return 'down'
      return null
    }

    const getTrendIconReverse = (current, previous) => {
      if (!current || !previous) return null
      if (current < previous) return 'down'
      if (current > previous) return 'up'
      return null
    }

    const formatDecimal = (value) => {
      if (value === null || value === undefined) return '0.00'
      return parseFloat(value).toFixed(2)
    }

    const indexMethod = (index) => {
      if (index === dataWithTotal.value.length - 1) {
        return ''
      }
      return index + 1
    }

    return {
      selectedDate,
      handleDateChange,
      formatCurrency,
      formatDecimal,
      dataWithTotal,
      getComparisonClass,
      getComparisonClassReverse,
      getTrendIcon,
      getTrendIconReverse,
      indexMethod,
      Top,
      Bottom
    }
  }
}
</script>

<style scoped src="../../styles/performance-card.css"></style>

