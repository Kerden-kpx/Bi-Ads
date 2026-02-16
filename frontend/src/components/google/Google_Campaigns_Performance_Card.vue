<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        Campaign Performance Overview（上周花费大于0）
      </div>
      <div class="card-actions">
        <button 
          class="icon-button" 
          @click="dialogVisible = true"
          title="Full Screen"
        >
          <el-icon><FullScreen /></el-icon>
        </button>
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
          :data="displayData" 
          style="width: 100%"
          stripe
          border
          @sort-change="handleSortChange"
        >
          <el-table-column 
            prop="name" 
            label="Campaign Name" 
            sortable="custom"
            min-width="300"
            show-overflow-tooltip
            fixed="left"
          />

          <el-table-column 
            prop="purchases" 
            label="Conversions" 
            sortable="custom"
            min-width="130"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.purchases, scope.row.purchasesPrevious)" class="value-with-icon">
                {{ scope.row.isTotal ? scope.row.purchases.toFixed(2) : scope.row.purchases }}
                <el-icon v-if="getTrendIcon(scope.row.purchases, scope.row.purchasesPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIcon(scope.row.purchases, scope.row.purchasesPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="purchasesPrevious" 
            label="Conversions (Previous)" 
            sortable="custom"
            min-width="180"
          >
            <template #default="scope">
              {{ scope.row.isTotal ? scope.row.purchasesPrevious.toFixed(2) : scope.row.purchasesPrevious }}
            </template>
          </el-table-column>
      
          <el-table-column 
            prop="spend" 
            label="Cost" 
            sortable="custom"
            min-width="120"
          >
            <template #default="scope">
              <span :class="getComparisonClassReverse(scope.row.spend, scope.row.spendPrevious)" class="value-with-icon">
                ${{ formatCurrency(scope.row.spend) }}
                <el-icon v-if="getTrendIconReverse(scope.row.spend, scope.row.spendPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIconReverse(scope.row.spend, scope.row.spendPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="spendPrevious" 
            label="Cost (Previous)" 
            sortable="custom"
            min-width="150"
          >
            <template #default="scope">
              ${{ formatCurrency(scope.row.spendPrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="purchaseRoas" 
            label="ROAS" 
            sortable="custom"
            min-width="110"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.purchaseRoas, scope.row.purchaseRoasPrevious)" class="value-with-icon">
                {{ formatDecimal(scope.row.purchaseRoas) }}
                <el-icon v-if="getTrendIcon(scope.row.purchaseRoas, scope.row.purchaseRoasPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIcon(scope.row.purchaseRoas, scope.row.purchaseRoasPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="purchaseRoasPrevious" 
            label="ROAS (Previous)" 
            sortable="custom"
            min-width="150"
          >
            <template #default="scope">
              {{ formatDecimal(scope.row.purchaseRoasPrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="impression" 
            label="Impressions" 
            sortable="custom"
            min-width="130"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.impression, scope.row.impressionPrevious)" class="value-with-icon">
                {{ formatNumber(scope.row.impression) }}
                <el-icon v-if="getTrendIcon(scope.row.impression, scope.row.impressionPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIcon(scope.row.impression, scope.row.impressionPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="impressionPrevious" 
            label="Impressions (Previous)" 
            sortable="custom"
            min-width="180"
          >
            <template #default="scope">
              {{ formatNumber(scope.row.impressionPrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="ctr" 
            label="CTR" 
            sortable="custom"
            min-width="100"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.ctr, scope.row.ctrPrevious)" class="value-with-icon">
                {{ formatPercentage(scope.row.ctr) }}
                <el-icon v-if="getTrendIcon(scope.row.ctr, scope.row.ctrPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIcon(scope.row.ctr, scope.row.ctrPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="ctrPrevious" 
            label="CTR (Previous)" 
            sortable="custom"
            min-width="140"
          >
            <template #default="scope">
              {{ formatPercentage(scope.row.ctrPrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="clicks" 
            label="Clicks" 
            sortable="custom"
            min-width="110"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.clicks, scope.row.clicksPrevious)" class="value-with-icon">
                {{ formatNumber(scope.row.clicks) }}
                <el-icon v-if="getTrendIcon(scope.row.clicks, scope.row.clicksPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIcon(scope.row.clicks, scope.row.clicksPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="clicksPrevious" 
            label="Clicks (Previous)" 
            sortable="custom"
            min-width="160"
          >
            <template #default="scope">
              {{ formatNumber(scope.row.clicksPrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="cpc" 
            label="CPC" 
            sortable="custom"
            min-width="100"
          >
            <template #default="scope">
              <span :class="getComparisonClassReverse(scope.row.cpc, scope.row.cpcPrevious)" class="value-with-icon">
                ${{ formatCurrency(scope.row.cpc) }}
                <el-icon v-if="getTrendIconReverse(scope.row.cpc, scope.row.cpcPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIconReverse(scope.row.cpc, scope.row.cpcPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="cpcPrevious" 
            label="CPC (Previous)" 
            sortable="custom"
            min-width="140"
          >
            <template #default="scope">
              ${{ formatCurrency(scope.row.cpcPrevious) }}
            </template>
          </el-table-column>
        </el-table>
      </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-button 
        :disabled="currentPage === 1" 
        @click="currentPage = 1"
        size="small"
      >
        K
      </el-button>
      <el-button 
        :disabled="currentPage === 1" 
        @click="currentPage--"
        size="small"
      >
        &lt;
      </el-button>
      <span class="page-info">{{ currentPage }} of {{ totalPages }}</span>
      <el-button 
        :disabled="currentPage === totalPages" 
        @click="currentPage++"
        size="small"
      >
        &gt;
      </el-button>
      <el-button 
        :disabled="currentPage === totalPages" 
        @click="currentPage = totalPages"
        size="small"
      >
        &gt;|
      </el-button>
    </div>
    </div>

    <!-- 完整数据对话框 -->
    <el-dialog
      v-model="dialogVisible"
      width="98%"
      top="3vh"
    >
      <template #header>
        <div class="dialog-title">Campaign Performance Overview（上周花费大于0）</div>
      </template>
      <el-table 
        :data="fullDataWithTotal" 
        style="width: 100%"
        stripe
        max-height="70vh"
        @sort-change="handleSortChange"
      >
        <el-table-column 
          prop="name" 
          label="Campaign Name" 
          sortable="custom"
          min-width="300"
          show-overflow-tooltip
          fixed="left"
        />

        <el-table-column 
          prop="purchases" 
          label="Conversions" 
          sortable="custom"
          min-width="130"
        >
          <template #default="scope">
            <span :class="getComparisonClass(scope.row.purchases, scope.row.purchasesPrevious)" class="value-with-icon">
              {{ scope.row.isTotal ? scope.row.purchases.toFixed(2) : scope.row.purchases }}
              <el-icon v-if="getTrendIcon(scope.row.purchases, scope.row.purchasesPrevious) === 'up'" class="trend-icon">
                <Top />
              </el-icon>
              <el-icon v-if="getTrendIcon(scope.row.purchases, scope.row.purchasesPrevious) === 'down'" class="trend-icon">
                <Bottom />
              </el-icon>
            </span>
          </template>
        </el-table-column>

        <el-table-column 
          prop="purchasesPrevious" 
          label="Conversions (Previous)" 
          sortable="custom"
          min-width="180"
        >
          <template #default="scope">
            {{ scope.row.isTotal ? scope.row.purchasesPrevious.toFixed(2) : scope.row.purchasesPrevious }}
          </template>
        </el-table-column>
    
        <el-table-column 
          prop="spend" 
          label="Cost" 
          sortable="custom"
          min-width="120"
        >
          <template #default="scope">
            <span :class="getComparisonClassReverse(scope.row.spend, scope.row.spendPrevious)" class="value-with-icon">
              ${{ formatCurrency(scope.row.spend) }}
              <el-icon v-if="getTrendIconReverse(scope.row.spend, scope.row.spendPrevious) === 'up'" class="trend-icon">
                <Top />
              </el-icon>
              <el-icon v-if="getTrendIconReverse(scope.row.spend, scope.row.spendPrevious) === 'down'" class="trend-icon">
                <Bottom />
              </el-icon>
            </span>
          </template>
        </el-table-column>
        
        <el-table-column 
          prop="spendPrevious" 
          label="Cost (Previous)" 
          sortable="custom"
          min-width="150"
        >
          <template #default="scope">
            ${{ formatCurrency(scope.row.spendPrevious) }}
          </template>
        </el-table-column>

        <el-table-column 
          prop="purchaseRoas" 
          label="ROAS" 
          sortable="custom"
          min-width="110"
        >
          <template #default="scope">
            <span :class="getComparisonClass(scope.row.purchaseRoas, scope.row.purchaseRoasPrevious)" class="value-with-icon">
              {{ formatDecimal(scope.row.purchaseRoas) }}
              <el-icon v-if="getTrendIcon(scope.row.purchaseRoas, scope.row.purchaseRoasPrevious) === 'up'" class="trend-icon">
                <Top />
              </el-icon>
              <el-icon v-if="getTrendIcon(scope.row.purchaseRoas, scope.row.purchaseRoasPrevious) === 'down'" class="trend-icon">
                <Bottom />
              </el-icon>
            </span>
          </template>
        </el-table-column>

        <el-table-column 
          prop="purchaseRoasPrevious" 
          label="ROAS (Previous)" 
          sortable="custom"
          min-width="150"
        >
          <template #default="scope">
            {{ formatDecimal(scope.row.purchaseRoasPrevious) }}
          </template>
        </el-table-column>

        <el-table-column 
          prop="impression" 
          label="Impressions" 
          sortable="custom"
          min-width="130"
        >
          <template #default="scope">
            <span :class="getComparisonClass(scope.row.impression, scope.row.impressionPrevious)" class="value-with-icon">
              {{ formatNumber(scope.row.impression) }}
              <el-icon v-if="getTrendIcon(scope.row.impression, scope.row.impressionPrevious) === 'up'" class="trend-icon">
                <Top />
              </el-icon>
              <el-icon v-if="getTrendIcon(scope.row.impression, scope.row.impressionPrevious) === 'down'" class="trend-icon">
                <Bottom />
              </el-icon>
            </span>
          </template>
        </el-table-column>
        
        <el-table-column 
          prop="impressionPrevious" 
          label="Impressions (Previous)" 
          sortable="custom"
          min-width="180"
        >
          <template #default="scope">
            {{ formatNumber(scope.row.impressionPrevious) }}
          </template>
        </el-table-column>

        <el-table-column 
          prop="ctr" 
          label="CTR" 
          sortable="custom"
          min-width="100"
        >
          <template #default="scope">
            <span :class="getComparisonClass(scope.row.ctr, scope.row.ctrPrevious)" class="value-with-icon">
              {{ formatPercentage(scope.row.ctr) }}
              <el-icon v-if="getTrendIcon(scope.row.ctr, scope.row.ctrPrevious) === 'up'" class="trend-icon">
                <Top />
              </el-icon>
              <el-icon v-if="getTrendIcon(scope.row.ctr, scope.row.ctrPrevious) === 'down'" class="trend-icon">
                <Bottom />
              </el-icon>
            </span>
          </template>
        </el-table-column>

        <el-table-column 
          prop="ctrPrevious" 
          label="CTR (Previous)" 
          sortable="custom"
          min-width="140"
        >
          <template #default="scope">
            {{ formatPercentage(scope.row.ctrPrevious) }}
          </template>
        </el-table-column>

        <el-table-column 
          prop="clicks" 
          label="Clicks" 
          sortable="custom"
          min-width="110"
        >
          <template #default="scope">
            <span :class="getComparisonClass(scope.row.clicks, scope.row.clicksPrevious)" class="value-with-icon">
              {{ formatNumber(scope.row.clicks) }}
              <el-icon v-if="getTrendIcon(scope.row.clicks, scope.row.clicksPrevious) === 'up'" class="trend-icon">
                <Top />
              </el-icon>
              <el-icon v-if="getTrendIcon(scope.row.clicks, scope.row.clicksPrevious) === 'down'" class="trend-icon">
                <Bottom />
              </el-icon>
            </span>
          </template>
        </el-table-column>
        
        <el-table-column 
          prop="clicksPrevious" 
          label="Clicks (Previous)" 
          sortable="custom"
          min-width="160"
        >
          <template #default="scope">
            {{ formatNumber(scope.row.clicksPrevious) }}
          </template>
        </el-table-column>

        <el-table-column 
          prop="cpc" 
          label="CPC" 
          sortable="custom"
          min-width="100"
        >
          <template #default="scope">
            <span :class="getComparisonClassReverse(scope.row.cpc, scope.row.cpcPrevious)" class="value-with-icon">
              ${{ formatCurrency(scope.row.cpc) }}
              <el-icon v-if="getTrendIconReverse(scope.row.cpc, scope.row.cpcPrevious) === 'up'" class="trend-icon">
                <Top />
              </el-icon>
              <el-icon v-if="getTrendIconReverse(scope.row.cpc, scope.row.cpcPrevious) === 'down'" class="trend-icon">
                <Bottom />
              </el-icon>
            </span>
          </template>
        </el-table-column>

        <el-table-column 
          prop="cpcPrevious" 
          label="CPC (Previous)" 
          sortable="custom"
          min-width="140"
        >
          <template #default="scope">
            ${{ formatCurrency(scope.row.cpcPrevious) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { formatCurrency, formatDecimal, formatPercentage } from '../../utils/formatters'
import { FullScreen, Top, Bottom } from '@element-plus/icons-vue'

export default {
  name: 'Google_Campaigns_Performance_Card',
  props: {
    data: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const currentPage = ref(1)
    const pageSize = 10
    const sortConfig = ref({ prop: null, order: null })
    const dialogVisible = ref(false)

    const totalPages = computed(() => Math.ceil(props.data.length / pageSize))

    // 排序后的数据（不包括总计行）
    const sortedData = computed(() => {
      if (!sortConfig.value.prop || !sortConfig.value.order) {
        return props.data
      }

      const sorted = [...props.data].sort((a, b) => {
        const prop = sortConfig.value.prop
        let aVal = a[prop]
        let bVal = b[prop]

        // 处理可能为 null 或 undefined 的值
        if (aVal === null || aVal === undefined) aVal = 0
        if (bVal === null || bVal === undefined) bVal = 0

        if (sortConfig.value.order === 'ascending') {
          return aVal > bVal ? 1 : aVal < bVal ? -1 : 0
        } else {
          return aVal < bVal ? 1 : aVal > bVal ? -1 : 0
        }
      })

      return sorted
    })

    // 分页数据
    const paginatedData = computed(() => {
      const start = (currentPage.value - 1) * pageSize
      const end = start + pageSize
      return sortedData.value.slice(start, end)
    })

    // 显示数据（在最后一页添加总计行）
    const displayData = computed(() => {
      if (currentPage.value === totalPages.value || props.data.length === 0) {
        return [...paginatedData.value, { ...totalRow.value, isTotal: true }]
      }
      return paginatedData.value
    })

    // 处理排序变化
    const handleSortChange = ({ prop, order }) => {
      sortConfig.value = { prop, order }
      currentPage.value = 1 // 排序后回到第一页
    }

    // 完整数据（包含总计行）用于对话框
    const fullDataWithTotal = computed(() => {
      return [...sortedData.value, { ...totalRow.value, isTotal: true }]
    })

    // 计算总计行
    const totalRow = computed(() => {
      if (!props.data || props.data.length === 0) {
        return {
          name: 'Total',
          purchases: 0,
          purchasesPrevious: 0,
          spend: 0,
          spendPrevious: 0,
          purchaseRoas: 0,
          purchaseRoasPrevious: 0,
          impression: 0,
          impressionPrevious: 0,
          ctr: 0,
          ctrPrevious: 0,
          clicks: 0,
          clicksPrevious: 0,
          cpc: 0,
          cpcPrevious: 0
        }
      }

      const total = {
        name: 'Total',
        purchases: 0,
        purchasesPrevious: 0,
        spend: 0,
        spendPrevious: 0,
        purchaseRoas: 0,
        purchaseRoasPrevious: 0,
        impression: 0,
        impressionPrevious: 0,
        ctr: 0,
        ctrPrevious: 0,
        clicks: 0,
        clicksPrevious: 0,
        cpc: 0,
        cpcPrevious: 0
      }

      props.data.forEach(row => {
        total.purchases += row.purchases || 0
        total.purchasesPrevious += row.purchasesPrevious || 0
        total.spend += row.spend || 0
        total.spendPrevious += row.spendPrevious || 0
        total.impression += row.impression || 0
        total.impressionPrevious += row.impressionPrevious || 0
        total.clicks += row.clicks || 0
        total.clicksPrevious += row.clicksPrevious || 0
      })

      // 计算比率
      const dataLength = props.data.length
      if (dataLength > 0) {
        // ROAS = Total Purchases Value / Total Spend
        // 假设 purchasesValue 可以从 purchases 计算得出，或使用现有的 purchaseRoas
        // 这里使用聚合的逻辑：先计算总的转化价值，再除以总花费
        let totalPurchasesValue = 0
        let totalPurchasesValuePrevious = 0
        props.data.forEach(row => {
          totalPurchasesValue += (row.purchasesValue || 0)
          totalPurchasesValuePrevious += (row.purchasesValuePrevious || 0)
        })
        
        total.purchaseRoas = total.spend > 0 ? totalPurchasesValue / total.spend : 0
        total.purchaseRoasPrevious = total.spendPrevious > 0 ? totalPurchasesValuePrevious / total.spendPrevious : 0
        
        // CTR = Total Clicks / Total Impressions
        total.ctr = total.impression > 0 ? (total.clicks / total.impression) * 100 : 0
        total.ctrPrevious = total.impressionPrevious > 0 ? (total.clicksPrevious / total.impressionPrevious) * 100 : 0
        
        // CPC = Total Spend / Total Clicks
        total.cpc = total.clicks > 0 ? total.spend / total.clicks : 0
        total.cpcPrevious = total.clicksPrevious > 0 ? total.spendPrevious / total.clicksPrevious : 0
      }

      return total
    })

    const formatNumber = (value) => {
      if (value === null || value === undefined) return '-'
      return new Intl.NumberFormat('en-US').format(value)
    }

    // 比较函数：大于是好的（绿色），小于是坏的（红色）
    const getComparisonClass = (current, previous) => {
      if (!current || !previous) return ''
      if (current > previous) return 'value-increase'
      if (current < previous) return 'value-decrease'
      return ''
    }

    // 反向比较函数：小于是好的（绿色），大于是坏的（红色）- 用于 Cost 和 CPC
    const getComparisonClassReverse = (current, previous) => {
      if (!current || !previous) return ''
      if (current < previous) return 'value-decrease'  // 花费减少 → 绿色（好事）
      if (current > previous) return 'value-increase'  // 花费增加 → 红色（坏事）
      return ''
    }

    // 获取趋势图标（正常比较：增加显示向上箭头，减少显示向下箭头）
    const getTrendIcon = (current, previous) => {
      if (!current || !previous) return null
      if (current > previous) return 'up'
      if (current < previous) return 'down'
      return null
    }

    // 获取趋势图标（反向比较：减少显示向下箭头，增加显示向上箭头）- 用于 Cost 和 CPC
    const getTrendIconReverse = (current, previous) => {
      if (!current || !previous) return null
      if (current < previous) return 'down'  // 花费减少 → 向下箭头（好事）
      if (current > previous) return 'up'  // 花费增加 → 向上箭头（坏事）
      return null
    }

    return {
      currentPage,
      totalPages,
      displayData,
      totalRow,
      formatCurrency,
      formatDecimal,
      formatPercentage,
      formatNumber,
      getComparisonClass,
      getComparisonClassReverse,
      getTrendIcon,
      getTrendIconReverse,
      handleSortChange,
      dialogVisible,
      fullDataWithTotal,
      FullScreen,
      Top,
      Bottom
    }
  }
}
</script>

<style scoped>
/* Loading状态样式 */
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

/* 对话框标题样式 - 与卡片标题保持一致 */
.dialog-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 12px;
  line-height: 1.4;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

/* 数值颜色变化 */
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

/* 趋势图标 */
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-button {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
  outline: none;
}

.icon-button:hover {
  background: #f5f5f5;
  border-color: #d0d0d0;
}

.icon-button:active {
  transform: scale(0.96);
}

.icon-button .el-icon {
  font-size: 20px;
  color: #666666;
}

.card-content {
  padding: 0 24px 24px;
}

.table-wrapper {
  overflow-x: auto;
  overflow-y: hidden;
  margin-bottom: 0;
}

.total-row-wrapper {
  overflow-x: auto;
  overflow-y: hidden;
  margin-bottom: 16px;
  margin-top: -1px; /* 消除与上方表格的间隙 */
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

.total-row-wrapper::-webkit-scrollbar {
  height: 8px;
}

.total-row-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.total-row-wrapper::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.total-row-wrapper::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 0;
}

.page-info {
  font-size: 14px;
  color: #606266;
  margin: 0 12px;
  font-weight: 500;
}

.pagination .el-button {
  min-width: 36px;
  height: 36px;
  padding: 8px 12px;
  border-color: #dcdfe6;
  color: #606266;
}

.pagination .el-button:hover:not(:disabled) {
  background-color: #f5f7fa;
  border-color: #c0c4cc;
  color: #409eff;
}

.pagination .el-button:disabled {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  color: #c0c4cc;
  cursor: not-allowed;
}

:deep(.el-table) {
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

:deep(.el-table th) {
  background-color: #f5f7fa !important;
  padding: 16px 12px !important;
  height: auto !important;
  font-weight: 600;
  font-size: 13px;
  color: #000000;
}

/* 确保固定列表头背景颜色一致 */
:deep(.el-table__fixed-header-wrapper th) {
  background-color: #f5f7fa !important;
}

:deep(.el-table__fixed th) {
  background-color: #f5f7fa !important;
}

:deep(.el-table th .cell) {
  padding: 0;
  line-height: 1.6;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  white-space: nowrap;
}

/* 除了第一列，其他列的表头居中 */
:deep(.el-table th:not(:first-child) .cell) {
  justify-content: center;
}

:deep(.el-table td) {
  padding: 14px 12px !important;
  background-color: #ffffff !important;
}

:deep(.el-table td .cell) {
  padding: 0;
  line-height: 1.5;
}

/* Campaign Name 列和 Previous 列数据颜色为黑色 */
:deep(.el-table td:first-child) {
  color: #000000 !important;
}

:deep(.el-table td:nth-child(3)),
:deep(.el-table td:nth-child(5)),
:deep(.el-table td:nth-child(7)),
:deep(.el-table td:nth-child(9)),
:deep(.el-table td:nth-child(11)),
:deep(.el-table td:nth-child(13)),
:deep(.el-table td:nth-child(15)) {
  color: #000000 !important;
}

/* 除了第一列，其他列的数据居中 */
:deep(.el-table td:not(:first-child) .cell) {
  text-align: center;
  justify-content: center;
}

/* 移除斑马纹效果 */
:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: #ffffff !important;
}

/* 悬停效果 */
:deep(.el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

/* 固定列背景也为白色 */
:deep(.el-table__fixed td) {
  background-color: #ffffff !important;
}

:deep(.el-table__fixed td:first-child) {
  color: #000000 !important;
}

:deep(.el-table__fixed .el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

/* 响应式布局 */
@media screen and (max-width: 1400px) {
  :deep(.el-table) {
    font-size: 13px;
  }
  
  :deep(.el-table th) {
    padding: 14px 10px !important;
    font-size: 12px;
  }
  
  :deep(.el-table td) {
    padding: 12px 10px !important;
  }
}

@media screen and (max-width: 1200px) {
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-table th) {
    padding: 12px 8px !important;
    font-size: 11px;
  }
  
  :deep(.el-table td) {
    padding: 10px 8px !important;
  }
  
  .card-content {
    padding: 0 16px 16px;
  }
}

@media screen and (max-width: 768px) {
  .card-content {
    padding: 0 12px 12px;
  }
  
  :deep(.el-table th) {
    padding: 10px 6px !important;
  }
  
  :deep(.el-table td) {
    padding: 8px 6px !important;
  }
}
</style>
