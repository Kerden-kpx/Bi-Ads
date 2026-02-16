<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        {{ title }}
      </div>
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
          :data="mergedData" 
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
            fixed
            :index="indexMethod"
          />
          <el-table-column 
            prop="product" 
            label="产品名称" 
            min-width="150"
            width="auto"
            align="center"
            fixed
            show-overflow-tooltip
          />
      
          <!-- 账户1数据 -->
          <el-table-column label="EZARCADS-1" align="center">
            <el-table-column label="转化" align="center">
              <el-table-column 
                prop="account1.conversions.thisWeek" 
                label="本周" 
                min-width="90"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  <span :class="getComparisonClass(scope.row.account1?.conversions?.thisWeek, scope.row.account1?.conversions?.lastWeek)" class="value-with-icon">
                    {{ formatDecimal(scope.row.account1?.conversions?.thisWeek) }}
                    <el-icon v-if="getTrendIcon(scope.row.account1?.conversions?.thisWeek, scope.row.account1?.conversions?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="getTrendIcon(scope.row.account1?.conversions?.thisWeek, scope.row.account1?.conversions?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </span>
                </template>
              </el-table-column>
              <el-table-column 
                prop="account1.conversions.lastWeek" 
                label="上周" 
                min-width="90"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  {{ formatDecimal(scope.row.account1?.conversions?.lastWeek) }}
                </template>
              </el-table-column>
            </el-table-column>
            
            <el-table-column label="转化价值" align="center">
              <el-table-column 
                prop="account1.conversionValue.thisWeek" 
                label="本周" 
                min-width="130"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  <span :class="getComparisonClass(scope.row.account1?.conversionValue?.thisWeek, scope.row.account1?.conversionValue?.lastWeek)" class="value-with-icon">
                    ${{ formatCurrency(scope.row.account1?.conversionValue?.thisWeek || 0) }}
                    <el-icon v-if="getTrendIcon(scope.row.account1?.conversionValue?.thisWeek, scope.row.account1?.conversionValue?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="getTrendIcon(scope.row.account1?.conversionValue?.thisWeek, scope.row.account1?.conversionValue?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </span>
                </template>
              </el-table-column>
              <el-table-column 
                prop="account1.conversionValue.lastWeek" 
                label="上周" 
                min-width="130"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  ${{ formatCurrency(scope.row.account1?.conversionValue?.lastWeek || 0) }}
                </template>
              </el-table-column>
            </el-table-column>
            
            <el-table-column label="花费" align="center">
              <el-table-column 
                prop="account1.cost.thisWeek" 
                label="本周" 
                min-width="130"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  <span :class="getComparisonClassReverse(scope.row.account1?.cost?.thisWeek, scope.row.account1?.cost?.lastWeek)" class="value-with-icon">
                    ${{ formatCurrency(scope.row.account1?.cost?.thisWeek || 0) }}
                    <el-icon v-if="getTrendIconReverse(scope.row.account1?.cost?.thisWeek, scope.row.account1?.cost?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="getTrendIconReverse(scope.row.account1?.cost?.thisWeek, scope.row.account1?.cost?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </span>
                </template>
              </el-table-column>
              <el-table-column 
                prop="account1.cost.lastWeek" 
                label="上周" 
                min-width="130"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  ${{ formatCurrency(scope.row.account1?.cost?.lastWeek || 0) }}
                </template>
              </el-table-column>
            </el-table-column>
            
            <el-table-column label="ROAS" align="center">
              <el-table-column 
                prop="account1.roas.thisWeek" 
                label="本周" 
                min-width="90"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  <span :class="getComparisonClass(scope.row.account1?.roas?.thisWeek, scope.row.account1?.roas?.lastWeek)" class="value-with-icon">
                    {{ formatDecimal(scope.row.account1?.roas?.thisWeek) }}
                    <el-icon v-if="getTrendIcon(scope.row.account1?.roas?.thisWeek, scope.row.account1?.roas?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="getTrendIcon(scope.row.account1?.roas?.thisWeek, scope.row.account1?.roas?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </span>
                </template>
              </el-table-column>
              <el-table-column 
                prop="account1.roas.lastWeek" 
                label="上周" 
                min-width="90"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  {{ formatDecimal(scope.row.account1?.roas?.lastWeek) }}
                </template>
              </el-table-column>
            </el-table-column>
          </el-table-column>
          
          <!-- 账户2数据 -->
          <el-table-column label="EZARCADS-2" align="center">
            <el-table-column label="转化" align="center">
              <el-table-column 
                prop="account2.conversions.thisWeek" 
                label="本周" 
                min-width="90"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  <span :class="getComparisonClass(scope.row.account2?.conversions?.thisWeek, scope.row.account2?.conversions?.lastWeek)" class="value-with-icon">
                    {{ formatDecimal(scope.row.account2?.conversions?.thisWeek) }}
                    <el-icon v-if="getTrendIcon(scope.row.account2?.conversions?.thisWeek, scope.row.account2?.conversions?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="getTrendIcon(scope.row.account2?.conversions?.thisWeek, scope.row.account2?.conversions?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </span>
                </template>
              </el-table-column>
              <el-table-column 
                prop="account2.conversions.lastWeek" 
                label="上周" 
                min-width="90"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  {{ formatDecimal(scope.row.account2?.conversions?.lastWeek) }}
                </template>
              </el-table-column>
            </el-table-column>
            
            <el-table-column label="转化价值" align="center">
              <el-table-column 
                prop="account2.conversionValue.thisWeek" 
                label="本周" 
                min-width="130"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  <span :class="getComparisonClass(scope.row.account2?.conversionValue?.thisWeek, scope.row.account2?.conversionValue?.lastWeek)" class="value-with-icon">
                    ${{ formatCurrency(scope.row.account2?.conversionValue?.thisWeek || 0) }}
                    <el-icon v-if="getTrendIcon(scope.row.account2?.conversionValue?.thisWeek, scope.row.account2?.conversionValue?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="getTrendIcon(scope.row.account2?.conversionValue?.thisWeek, scope.row.account2?.conversionValue?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </span>
                </template>
              </el-table-column>
              <el-table-column 
                prop="account2.conversionValue.lastWeek" 
                label="上周" 
                min-width="130"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  ${{ formatCurrency(scope.row.account2?.conversionValue?.lastWeek || 0) }}
                </template>
              </el-table-column>
            </el-table-column>
            
            <el-table-column label="花费" align="center">
              <el-table-column 
                prop="account2.cost.thisWeek" 
                label="本周" 
                min-width="130"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  <span :class="getComparisonClassReverse(scope.row.account2?.cost?.thisWeek, scope.row.account2?.cost?.lastWeek)" class="value-with-icon">
                    ${{ formatCurrency(scope.row.account2?.cost?.thisWeek || 0) }}
                    <el-icon v-if="getTrendIconReverse(scope.row.account2?.cost?.thisWeek, scope.row.account2?.cost?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="getTrendIconReverse(scope.row.account2?.cost?.thisWeek, scope.row.account2?.cost?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </span>
                </template>
              </el-table-column>
              <el-table-column 
                prop="account2.cost.lastWeek" 
                label="上周" 
                min-width="130"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  ${{ formatCurrency(scope.row.account2?.cost?.lastWeek || 0) }}
                </template>
              </el-table-column>
            </el-table-column>
            
            <el-table-column label="ROAS" align="center">
              <el-table-column 
                prop="account2.roas.thisWeek" 
                label="本周" 
                min-width="90"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  <span :class="getComparisonClass(scope.row.account2?.roas?.thisWeek, scope.row.account2?.roas?.lastWeek)" class="value-with-icon">
                    {{ formatDecimal(scope.row.account2?.roas?.thisWeek) }}
                    <el-icon v-if="getTrendIcon(scope.row.account2?.roas?.thisWeek, scope.row.account2?.roas?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="getTrendIcon(scope.row.account2?.roas?.thisWeek, scope.row.account2?.roas?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </span>
                </template>
              </el-table-column>
              <el-table-column 
                prop="account2.roas.lastWeek" 
                label="上周" 
                min-width="90"
                width="auto"
                align="center"
              >
                <template #default="scope">
                  {{ formatDecimal(scope.row.account2?.roas?.lastWeek) }}
                </template>
              </el-table-column>
            </el-table-column>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'
import { formatCurrency } from '../../utils/formatters'
import SingleDatePicker from '../shared/Single_Date_Picker.vue'
import { Top, Bottom } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

export default {
  name: 'Facebook_Ads_Dual_Account_Card',
  components: {
    SingleDatePicker,
    Top,
    Bottom
  },
  props: {
    account1Data: {
      type: Array,
      required: true
    },
    account2Data: {
      type: Array,
      required: true
    },
    dateRange: {
      type: String,
      default: () => dayjs().format('YYYY-MM-DD')
    },
    title: {
      type: String,
      default: 'Facebook Ads Performance Overview (Dual Account)'
    },
    showDatePicker: {
      type: Boolean,
      default: true
    },
    loading: {
      type: Boolean,
      default: false
    }
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

    // 合并两个账户的数据
    const mergedData = computed(() => {
      // 获取所有产品名称
      const productSet = new Set()
      
      props.account1Data.forEach(item => {
        if (item.product) productSet.add(item.product)
      })
      
      props.account2Data.forEach(item => {
        if (item.product) productSet.add(item.product)
      })

      // 为每个产品创建一行数据
      const merged = []
      productSet.forEach(productName => {
        const account1Item = props.account1Data.find(item => item.product === productName)
        const account2Item = props.account2Data.find(item => item.product === productName)

        merged.push({
          product: productName,
          account1: {
            conversions: {
              thisWeek: account1Item?.conversions?.thisWeek || 0,
              lastWeek: account1Item?.conversions?.lastWeek || 0
            },
            conversionValue: {
              thisWeek: account1Item?.conversionValue?.thisWeek || 0,
              lastWeek: account1Item?.conversionValue?.lastWeek || 0
            },
            cost: {
              thisWeek: account1Item?.cost?.thisWeek || 0,
              lastWeek: account1Item?.cost?.lastWeek || 0
            },
            roas: {
              thisWeek: account1Item?.roas?.thisWeek || 0,
              lastWeek: account1Item?.roas?.lastWeek || 0
            }
          },
          account2: {
            conversions: {
              thisWeek: account2Item?.conversions?.thisWeek || 0,
              lastWeek: account2Item?.conversions?.lastWeek || 0
            },
            conversionValue: {
              thisWeek: account2Item?.conversionValue?.thisWeek || 0,
              lastWeek: account2Item?.conversionValue?.lastWeek || 0
            },
            cost: {
              thisWeek: account2Item?.cost?.thisWeek || 0,
              lastWeek: account2Item?.cost?.lastWeek || 0
            },
            roas: {
              thisWeek: account2Item?.roas?.thisWeek || 0,
              lastWeek: account2Item?.roas?.lastWeek || 0
            }
          }
        })
      })

      // 计算总计行
      const totalRow = {
        product: '合计',
        account1: {
          conversions: { thisWeek: 0, lastWeek: 0 },
          conversionValue: { thisWeek: 0, lastWeek: 0 },
          cost: { thisWeek: 0, lastWeek: 0 },
          roas: { thisWeek: 0, lastWeek: 0 }
        },
        account2: {
          conversions: { thisWeek: 0, lastWeek: 0 },
          conversionValue: { thisWeek: 0, lastWeek: 0 },
          cost: { thisWeek: 0, lastWeek: 0 },
          roas: { thisWeek: 0, lastWeek: 0 }
        }
      }

      merged.forEach(row => {
        totalRow.account1.conversions.thisWeek += row.account1.conversions.thisWeek
        totalRow.account1.conversions.lastWeek += row.account1.conversions.lastWeek
        totalRow.account1.conversionValue.thisWeek += row.account1.conversionValue.thisWeek
        totalRow.account1.conversionValue.lastWeek += row.account1.conversionValue.lastWeek
        totalRow.account1.cost.thisWeek += row.account1.cost.thisWeek
        totalRow.account1.cost.lastWeek += row.account1.cost.lastWeek
        
        totalRow.account2.conversions.thisWeek += row.account2.conversions.thisWeek
        totalRow.account2.conversions.lastWeek += row.account2.conversions.lastWeek
        totalRow.account2.conversionValue.thisWeek += row.account2.conversionValue.thisWeek
        totalRow.account2.conversionValue.lastWeek += row.account2.conversionValue.lastWeek
        totalRow.account2.cost.thisWeek += row.account2.cost.thisWeek
        totalRow.account2.cost.lastWeek += row.account2.cost.lastWeek
      })

      // 计算总ROAS
      totalRow.account1.roas.thisWeek = totalRow.account1.cost.thisWeek > 0 
        ? totalRow.account1.conversionValue.thisWeek / totalRow.account1.cost.thisWeek 
        : 0
      totalRow.account1.roas.lastWeek = totalRow.account1.cost.lastWeek > 0 
        ? totalRow.account1.conversionValue.lastWeek / totalRow.account1.cost.lastWeek 
        : 0
      totalRow.account2.roas.thisWeek = totalRow.account2.cost.thisWeek > 0 
        ? totalRow.account2.conversionValue.thisWeek / totalRow.account2.cost.thisWeek 
        : 0
      totalRow.account2.roas.lastWeek = totalRow.account2.cost.lastWeek > 0 
        ? totalRow.account2.conversionValue.lastWeek / totalRow.account2.cost.lastWeek 
        : 0

      return [...merged, totalRow]
    })

    // 格式化数值为两位小数
    const formatDecimal = (value) => {
      if (value === null || value === undefined) return '0.00'
      return parseFloat(value).toFixed(2)
    }

    // 比较函数：大于是好的（绿色），小于是坏的（红色）
    const getComparisonClass = (current, previous) => {
      if (!current || !previous) return ''
      if (current > previous) return 'value-increase'
      if (current < previous) return 'value-decrease'
      return ''
    }

    // 反向比较函数：小于是好的（绿色），大于是坏的（红色）- 用于 Cost
    const getComparisonClassReverse = (current, previous) => {
      if (!current || !previous) return ''
      if (current < previous) return 'value-decrease'
      if (current > previous) return 'value-increase'
      return ''
    }

    // 获取趋势图标（正常比较：增加显示向上箭头，减少显示向下箭头）
    const getTrendIcon = (current, previous) => {
      if (!current || !previous) return null
      if (current > previous) return 'up'
      if (current < previous) return 'down'
      return null
    }

    // 获取趋势图标（正常方向：减少显示向下箭头，增加显示向上箭头）- 用于 Cost
    const getTrendIconReverse = (current, previous) => {
      if (!current || !previous) return null
      if (current < previous) return 'down'  // 花费减少，显示向下箭头
      if (current > previous) return 'up'    // 花费增加，显示向上箭头
      return null
    }

    // 自定义编号方法（最后一行为合计，不显示编号）
    const indexMethod = (index) => {
      if (index === mergedData.value.length - 1) {
        return ''  // 合计行不显示编号
      }
      return index + 1
    }

    return {
      selectedDate,
      handleDateChange,
      formatCurrency,
      formatDecimal,
      mergedData,
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

<style scoped>
/* 加载状态样式 */
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

/* 动态颜色样式 */
.value-increase {
  color: #ef4444;
  font-weight: 600;
}

.value-decrease {
  color: #10b981;
  font-weight: 600;
}

/* 带图标的数值容器 */
.value-with-icon {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.trend-icon {
  font-size: 14px;
  vertical-align: middle;
}

.value-increase .trend-icon {
  color: #ef4444;
}

.value-decrease .trend-icon {
  color: #10b981;
}

.card {
  width: 100%;
  box-sizing: border-box;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
  flex-wrap: wrap;
  gap: 12px;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-content {
  padding: 0 24px 24px;
  width: 100%;
  box-sizing: border-box;
}

.table-wrapper {
  overflow-x: auto;
  overflow-y: hidden;
  margin-bottom: 16px;
  -webkit-overflow-scrolling: touch;
  width: 100%;
  box-sizing: border-box;
}

/* 为小屏幕添加滚动条样式 */
.table-wrapper::-webkit-scrollbar {
  height: 8px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 基础表格样式 */
:deep(.responsive-table) {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  width: 100% !important;
  table-layout: auto;
}

:deep(.el-table) {
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  padding: 6px 12px !important;
  height: auto !important;
  font-weight: 600;
  font-size: 13px;
  color: #000000;
  white-space: nowrap;
}

:deep(.el-table th .cell) {
  padding: 0;
  line-height: 1.6;
  word-break: keep-all;
  white-space: nowrap;
}

:deep(.el-table td) {
  padding: 4px 12px !important;
  font-size: 13px;
  background-color: #ffffff !important;
  color: #000000;
}

:deep(.el-table td .cell) {
  padding: 0;
  line-height: 1.5;
  word-break: keep-all;
}

/* 移除斑马纹效果 */
:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: #ffffff !important;
}

/* 悬停效果 */
:deep(.el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

/* 大屏幕优化 (> 1600px) */
@media screen and (min-width: 1600px) {
  :deep(.el-table th) {
    padding: 8px 16px !important;
    font-size: 14px;
  }
  
  :deep(.el-table td) {
    padding: 6px 16px !important;
    font-size: 14px;
  }
}

/* 中大屏幕 (1200px - 1400px) */
@media screen and (max-width: 1400px) {
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-table th) {
    padding: 6px 10px !important;
    font-size: 12px;
  }
  
  :deep(.el-table td) {
    padding: 4px 10px !important;
    font-size: 12px;
  }
}

/* 中屏幕 (768px - 1200px) */
@media screen and (max-width: 1200px) {
  :deep(.el-table) {
    font-size: 11px;
  }
  
  :deep(.el-table th) {
    padding: 5px 8px !important;
    font-size: 11px;
  }
  
  :deep(.el-table td) {
    padding: 4px 8px !important;
    font-size: 11px;
  }
  
  .card-content {
    padding: 0 16px 16px;
  }
  
  .card-header {
    padding: 16px 16px;
  }
}

/* 小屏幕 (480px - 768px) */
@media screen and (max-width: 768px) {
  .card-header {
    padding: 12px 12px;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .card-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .card-content {
    padding: 0 12px 12px;
  }
  
  :deep(.el-table) {
    font-size: 10px;
  }
  
  :deep(.el-table th) {
    padding: 8px 6px !important;
    font-size: 10px;
  }
  
  :deep(.el-table td) {
    padding: 8px 6px !important;
    font-size: 10px;
  }
  
  .table-wrapper {
    margin-bottom: 12px;
  }
}

/* 超小屏幕 (< 480px) */
@media screen and (max-width: 480px) {
  .card-header {
    padding: 10px 10px;
  }
  
  .card-content {
    padding: 0 10px 10px;
  }
  
  :deep(.el-table) {
    font-size: 9px;
  }
  
  :deep(.el-table th) {
    padding: 6px 4px !important;
    font-size: 9px;
  }
  
  :deep(.el-table td) {
    padding: 6px 4px !important;
    font-size: 9px;
  }
  
  :deep(.el-table th .cell),
  :deep(.el-table td .cell) {
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>

