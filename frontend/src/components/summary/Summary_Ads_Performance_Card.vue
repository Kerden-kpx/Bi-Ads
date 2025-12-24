<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        {{ title }}
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
          :data="summaryDataWithTotal" 
          class="responsive-table"
          stripe
          border
          :fit="true"
          :span-method="spanMethod"
          :row-class-name="getRowClassName"
        >
          <el-table-column 
            type="index" 
            label="编号" 
            width="80"
            align="center"
            :index="indexMethod"
            fixed="left"
          />
          <el-table-column 
            prop="product" 
            label="产品名称" 
            min-width="200"
            width="200"
            align="center"
            show-overflow-tooltip
            fixed="left"
          />
      
          <el-table-column label="转化" align="center">
            <el-table-column 
              prop="conversions.thisWeek" 
              label="本周" 
              min-width="130"
              width="auto"
              align="center"
            >
              <template #default="scope">
                <span :class="!scope.row.isMonthlyHeader && getComparisonClass(scope.row.conversions?.thisWeek, scope.row.conversions?.lastWeek)" class="value-with-icon">
                  <template v-if="typeof scope.row.conversions?.thisWeek === 'string'">
                    {{ scope.row.conversions?.thisWeek }}
                  </template>
                  <template v-else>
                    {{ formatDecimal(scope.row.conversions?.thisWeek) }}
                    <el-icon v-if="!scope.row.isMonthlyHeader && getTrendIcon(scope.row.conversions?.thisWeek, scope.row.conversions?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="!scope.row.isMonthlyHeader && getTrendIcon(scope.row.conversions?.thisWeek, scope.row.conversions?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </template>
                </span>
              </template>
            </el-table-column>
            <el-table-column 
              prop="conversions.lastWeek" 
              label="上周" 
              min-width="130"
              width="auto"
              align="center"
            >
              <template #default="scope">
                <span>
                  <template v-if="typeof scope.row.conversions?.lastWeek === 'string'">
                    {{ scope.row.conversions?.lastWeek }}
                  </template>
                  <template v-else>
                    {{ formatDecimal(scope.row.conversions?.lastWeek) }}
                  </template>
                </span>
              </template>
            </el-table-column>
          </el-table-column>
          
          <el-table-column label="转化价值" align="center">
            <el-table-column 
              prop="conversionValue.thisWeek" 
              label="本周" 
              min-width="130"
              width="auto"
              align="center"
            >
              <template #default="scope">
                <!-- 独立站销售目标可编辑 -->
                <div v-if="scope.row.product === '独立站销售目标'" class="editable-cell">
                  <template v-if="editingCell.row === scope.$index && editingCell.col === 'thisWeek'">
                    <el-input
                      v-model="editingValue"
                      ref="editInput"
                      size="small"
                      type="number"
                      @blur="saveEdit(scope.row, 'thisWeek', scope.$index)"
                      @keyup.enter="saveEdit(scope.row, 'thisWeek', scope.$index)"
                      @keyup.esc="cancelEdit"
                      class="edit-input"
                    />
                  </template>
                  <template v-else>
                    <span 
                      class="editable-value" 
                      @click="startEdit(scope.row, 'thisWeek', scope.$index)"
                      :title="'点击编辑'"
                    >
                      ${{ formatCurrency(scope.row.conversionValue?.thisWeek || 0) }}
                      <el-icon class="edit-icon"><Edit /></el-icon>
                    </span>
                  </template>
                </div>
                <!-- 其他行不可编辑 -->
                <span v-else :class="!scope.row.isMonthlyHeader && getComparisonClass(scope.row.conversionValue?.thisWeek, scope.row.conversionValue?.lastWeek)" class="value-with-icon">
                  <template v-if="typeof scope.row.conversionValue?.thisWeek === 'string'">
                    {{ scope.row.conversionValue?.thisWeek }}
                  </template>
                  <template v-else>
                    ${{ formatCurrency(scope.row.conversionValue?.thisWeek || 0) }}
                    <el-icon v-if="!scope.row.isMonthlyHeader && getTrendIcon(scope.row.conversionValue?.thisWeek, scope.row.conversionValue?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="!scope.row.isMonthlyHeader && getTrendIcon(scope.row.conversionValue?.thisWeek, scope.row.conversionValue?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </template>
                </span>
              </template>
            </el-table-column>
            <el-table-column 
              prop="conversionValue.lastWeek" 
              label="上周" 
              min-width="130"
              width="auto"
              align="center"
            >
              <template #default="scope">
                <!-- 独立站销售目标可编辑 -->
                <div v-if="scope.row.product === '独立站销售目标'" class="editable-cell">
                  <template v-if="editingCell.row === scope.$index && editingCell.col === 'lastWeek'">
                    <el-input
                      v-model="editingValue"
                      ref="editInput"
                      size="small"
                      type="number"
                      @blur="saveEdit(scope.row, 'lastWeek', scope.$index)"
                      @keyup.enter="saveEdit(scope.row, 'lastWeek', scope.$index)"
                      @keyup.esc="cancelEdit"
                      class="edit-input"
                    />
                  </template>
                  <template v-else>
                    <span 
                      class="editable-value" 
                      @click="startEdit(scope.row, 'lastWeek', scope.$index)"
                      :title="'点击编辑'"
                    >
                      ${{ formatCurrency(scope.row.conversionValue?.lastWeek || 0) }}
                      <el-icon class="edit-icon"><Edit /></el-icon>
                    </span>
                  </template>
                </div>
                <!-- 其他行不可编辑 -->
                <span v-else>
                  <template v-if="typeof scope.row.conversionValue?.lastWeek === 'string'">
                    {{ scope.row.conversionValue?.lastWeek }}
                  </template>
                  <template v-else>
                    ${{ formatCurrency(scope.row.conversionValue?.lastWeek || 0) }}
                  </template>
                </span>
              </template>
            </el-table-column>
          </el-table-column>
          
          <el-table-column label="花费" align="center">
            <el-table-column 
              prop="cost.thisWeek" 
              label="本周" 
              min-width="130"
              width="auto"
              align="center"
            >
              <template #default="scope">
                <span :class="!scope.row.isMonthlyHeader && getComparisonClassReverse(scope.row.cost?.thisWeek, scope.row.cost?.lastWeek)" class="value-with-icon">
                  <template v-if="typeof scope.row.cost?.thisWeek === 'string'">
                    {{ scope.row.cost?.thisWeek }}
                  </template>
                  <template v-else>
                    ${{ formatCurrency(scope.row.cost?.thisWeek || 0) }}
                    <el-icon v-if="!scope.row.isMonthlyHeader && getTrendIconReverse(scope.row.cost?.thisWeek, scope.row.cost?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="!scope.row.isMonthlyHeader && getTrendIconReverse(scope.row.cost?.thisWeek, scope.row.cost?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </template>
                </span>
              </template>
            </el-table-column>
            <el-table-column 
              prop="cost.lastWeek" 
              label="上周" 
              min-width="130"
              width="auto"
              align="center"
            >
              <template #default="scope">
                <span>
                  <template v-if="typeof scope.row.cost?.lastWeek === 'string'">
                    {{ scope.row.cost?.lastWeek }}
                  </template>
                  <template v-else>
                    ${{ formatCurrency(scope.row.cost?.lastWeek || 0) }}
                  </template>
                </span>
              </template>
            </el-table-column>
          </el-table-column>
          
          <el-table-column label="ROAS" align="center">
            <el-table-column 
              prop="roas.thisWeek" 
              label="本周" 
              min-width="90"
              width="auto"
              align="center"
            >
              <template #default="scope">
                <span :class="!scope.row.isMonthlyHeader && getComparisonClass(scope.row.roas?.thisWeek, scope.row.roas?.lastWeek)" class="value-with-icon">
                  <template v-if="typeof scope.row.roas?.thisWeek === 'string'">
                    {{ scope.row.roas?.thisWeek }}
                  </template>
                  <template v-else>
                    {{ formatDecimal(scope.row.roas?.thisWeek) }}
                    <el-icon v-if="!scope.row.isMonthlyHeader && getTrendIcon(scope.row.roas?.thisWeek, scope.row.roas?.lastWeek) === 'up'" class="trend-icon">
                      <Top />
                    </el-icon>
                    <el-icon v-if="!scope.row.isMonthlyHeader && getTrendIcon(scope.row.roas?.thisWeek, scope.row.roas?.lastWeek) === 'down'" class="trend-icon">
                      <Bottom />
                    </el-icon>
                  </template>
                </span>
              </template>
            </el-table-column>
            <el-table-column 
              prop="roas.lastWeek" 
              label="上周" 
              min-width="90"
              width="auto"
              align="center"
            >
              <template #default="scope">
                <template v-if="typeof scope.row.roas?.lastWeek === 'string'">
                  {{ scope.row.roas?.lastWeek }}
                </template>
                <template v-else>
                  {{ formatDecimal(scope.row.roas?.lastWeek) }}
                </template>
              </template>
            </el-table-column>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick } from 'vue'
import { formatCurrency } from '../../utils/formatters'
import { Top, Bottom, Edit } from '@element-plus/icons-vue'
import { lingxingAPI } from '../../services/lingxing/lingxingApi'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

export default {
  name: 'Summary_Ads_Performance_Card',
  components: {
    Top,
    Bottom,
    Edit
  },
  emits: ['update-success'],
  props: {
    facebookAccount1Data: {
      type: Array,
      required: true
    },
    facebookAccount2Data: {
      type: Array,
      required: true
    },
    googleData: {
      type: Array,
      required: true
    },
    lingxingData: {
      type: Object,
      default: () => ({
        conversions: { thisWeek: 0, lastWeek: 0 },
        conversionValue: { thisWeek: 0, lastWeek: 0 }
      })
    },
    lingxingMonthlyCost: {
      type: Object,
      default: () => ({
        cost: { thisWeek: 0, lastWeek: 0 }
      })
    },
    salesTargetData: {
      type: Object,
      default: () => ({
        conversionValue: { thisWeek: 0, lastWeek: 0 }
      })
    },
    facebookSummaryData: {
      type: Object,
      default: () => ({
        conversions: { thisWeek: 0, lastWeek: 0 },
        conversionValue: { thisWeek: 0, lastWeek: 0 },
        cost: { thisWeek: 0, lastWeek: 0 },
        roas: { thisWeek: 0, lastWeek: 0 }
      })
    },
    googleSummaryData: {
      type: Object,
      default: () => ({
        conversions: { thisWeek: 0, lastWeek: 0 },
        conversionValue: { thisWeek: 0, lastWeek: 0 },
        cost: { thisWeek: 0, lastWeek: 0 },
        roas: { thisWeek: 0, lastWeek: 0 }
      })
    },
    dateRange: {
      type: String,
      default: () => dayjs().format('YYYY-MM-DD')
    },
    title: {
      type: String,
      default: 'Summary Ads Performance Overview'
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { emit }) {
    // 编辑状态
    const editingCell = ref({ row: null, col: null })
    const editingValue = ref('')
    const editInput = ref(null)
    const monthInfoCache = ref({ current: null, last: null })

    // 开始编辑
    const startEdit = async (row, col, rowIndex) => {
      const value = col === 'thisWeek' ? row.conversionValue?.thisWeek : row.conversionValue?.lastWeek
      editingValue.value = value || 0
      editingCell.value = { row: rowIndex, col }
      
      // 等待DOM更新后自动聚焦输入框
      await nextTick()
      if (editInput.value) {
        editInput.value.focus()
        editInput.value.select()
      }
    }

    // 取消编辑
    const cancelEdit = () => {
      editingCell.value = { row: null, col: null }
      editingValue.value = ''
    }

    // 保存编辑
    const saveEdit = async (row, col, rowIndex) => {
      try {
        const newValue = parseFloat(editingValue.value)
        
        // 验证输入
        if (isNaN(newValue) || newValue < 0) {
          ElMessage.warning('请输入有效的数值')
          cancelEdit()
          return
        }

        // 确定月份和年份 - 使用传入的dateRange而不是当前日期
        // col === 'thisWeek' 是本月，'lastWeek' 是上月
        const targetDate = dayjs(props.dateRange || undefined)
        let month, year
        
        if (col === 'thisWeek') {
          // 本月
          month = targetDate.month() + 1  // dayjs的月份从0开始
          year = targetDate.year()
        } else {
          // 上个月
          const lastMonth = targetDate.subtract(1, 'month')
          month = lastMonth.month() + 1
          year = lastMonth.year()
        }

        console.log(`更新销售目标: ${year}年${month}月 = ${newValue}`)

        // 调用API更新
        const response = await lingxingAPI.updateSalesTarget({
          month,
          year,
          conversion_value: newValue
        })

        if (response && (response.code === 200 || response.status === 200)) {
          ElMessage.success('销售目标更新成功')
          
          // 更新本地数据
          if (col === 'thisWeek') {
            row.conversionValue.thisWeek = newValue
          } else {
            row.conversionValue.lastWeek = newValue
          }
          
          // 通知父组件刷新数据
          emit('update-success')
        } else {
          ElMessage.error('更新失败，请重试')
        }
      } catch (error) {
        console.error('保存销售目标失败:', error)
        ElMessage.error('保存失败: ' + (error.message || '未知错误'))
      } finally {
        cancelEdit()
      }
    }

    // 汇总所有产品数据
    const summaryData = computed(() => {
      const productMap = new Map()

      // 合并Facebook账户1的数据
      props.facebookAccount1Data.forEach(item => {
        if (!item.product) return
        
        if (!productMap.has(item.product)) {
          productMap.set(item.product, {
            product: item.product,
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 }
          })
        }
        
        const data = productMap.get(item.product)
        data.conversions.thisWeek += item.conversions?.thisWeek || 0
        data.conversions.lastWeek += item.conversions?.lastWeek || 0
        data.conversionValue.thisWeek += item.conversionValue?.thisWeek || 0
        data.conversionValue.lastWeek += item.conversionValue?.lastWeek || 0
        data.cost.thisWeek += item.cost?.thisWeek || 0
        data.cost.lastWeek += item.cost?.lastWeek || 0
      })

      // 合并Facebook账户2的数据
      props.facebookAccount2Data.forEach(item => {
        if (!item.product) return
        
        if (!productMap.has(item.product)) {
          productMap.set(item.product, {
            product: item.product,
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 }
          })
        }
        
        const data = productMap.get(item.product)
        data.conversions.thisWeek += item.conversions?.thisWeek || 0
        data.conversions.lastWeek += item.conversions?.lastWeek || 0
        data.conversionValue.thisWeek += item.conversionValue?.thisWeek || 0
        data.conversionValue.lastWeek += item.conversionValue?.lastWeek || 0
        data.cost.thisWeek += item.cost?.thisWeek || 0
        data.cost.lastWeek += item.cost?.lastWeek || 0
      })

      // 合并Google的数据
      props.googleData.forEach(item => {
        if (!item.product) return
        
        if (!productMap.has(item.product)) {
          productMap.set(item.product, {
            product: item.product,
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 }
          })
        }
        
        const data = productMap.get(item.product)
        data.conversions.thisWeek += item.conversions?.thisWeek || 0
        data.conversions.lastWeek += item.conversions?.lastWeek || 0
        data.conversionValue.thisWeek += item.conversionValue?.thisWeek || 0
        data.conversionValue.lastWeek += item.conversionValue?.lastWeek || 0
        data.cost.thisWeek += item.cost?.thisWeek || 0
        data.cost.lastWeek += item.cost?.lastWeek || 0
      })

      // 计算每个产品的ROAS
      const result = Array.from(productMap.values()).map(item => {
        item.roas.thisWeek = item.cost.thisWeek > 0 
          ? item.conversionValue.thisWeek / item.cost.thisWeek 
          : 0
        item.roas.lastWeek = item.cost.lastWeek > 0 
          ? item.conversionValue.lastWeek / item.cost.lastWeek 
          : 0
        return item
      })

      return result
    })

    // 计算汇总行
    const summaryDataWithTotal = computed(() => {
      if (!summaryData.value || summaryData.value.length === 0) {
        return [
          {
            product: 'Facebook合计',
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 },
            isSubTotal: true
          },
          {
            product: 'Google合计',
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 },
            isSubTotal: true
          },
          {
            product: '合计',
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 },
            isProductTotal: true
          },
          {
            product: '账号汇总',
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 },
            isSummaryHeader: true
          },
          {
            product: 'Facebook广告',
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 },
            isSubTotal: true
          },
          {
            product: 'Google广告',
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 },
            isSubTotal: true
          },
          {
            product: '总计广告平台',
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 },
            isTotal: true
          },
          {
            product: '广告平台月度模拟',
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 },
            isSimulation: true
          },
          {
            product: '独立站全站月度模拟',
            conversions: { thisWeek: 0, lastWeek: 0 },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: 0, lastWeek: 0 },
            roas: { thisWeek: 0, lastWeek: 0 },
            isSimulation: true
          },
          {
            product: '独立站销售目标',
            conversions: { thisWeek: '-', lastWeek: '-' },
            conversionValue: { thisWeek: 0, lastWeek: 0 },
            cost: { thisWeek: '-', lastWeek: '-' },
            roas: { thisWeek: '-', lastWeek: '-' },
            isSimulation: true
          }
        ]
      }

      // 计算Facebook广告总计（使用汇总API数据）
      const facebookTotal = {
        product: 'Facebook广告',
        conversions: { 
          thisWeek: props.facebookSummaryData.conversions.thisWeek, 
          lastWeek: props.facebookSummaryData.conversions.lastWeek 
        },
        conversionValue: { 
          thisWeek: props.facebookSummaryData.conversionValue.thisWeek, 
          lastWeek: props.facebookSummaryData.conversionValue.lastWeek 
        },
        cost: { 
          thisWeek: props.facebookSummaryData.cost.thisWeek, 
          lastWeek: props.facebookSummaryData.cost.lastWeek 
        },
        roas: { 
          thisWeek: props.facebookSummaryData.roas.thisWeek, 
          lastWeek: props.facebookSummaryData.roas.lastWeek 
        },
        isSubTotal: true
      }

      // 计算Google广告总计（使用汇总API数据）
      const googleTotal = {
        product: 'Google广告',
        conversions: { 
          thisWeek: props.googleSummaryData.conversions.thisWeek, 
          lastWeek: props.googleSummaryData.conversions.lastWeek 
        },
        conversionValue: { 
          thisWeek: props.googleSummaryData.conversionValue.thisWeek, 
          lastWeek: props.googleSummaryData.conversionValue.lastWeek 
        },
        cost: { 
          thisWeek: props.googleSummaryData.cost.thisWeek, 
          lastWeek: props.googleSummaryData.cost.lastWeek 
        },
        roas: { 
          thisWeek: props.googleSummaryData.roas.thisWeek, 
          lastWeek: props.googleSummaryData.roas.lastWeek 
        },
        isSubTotal: true
      }

      // 计算总计广告平台
      const total = {
        product: '总计广告平台',
        conversions: { thisWeek: 0, lastWeek: 0 },
        conversionValue: { thisWeek: 0, lastWeek: 0 },
        cost: { thisWeek: 0, lastWeek: 0 },
        roas: { thisWeek: 0, lastWeek: 0 },
        isTotal: true
      }

      summaryData.value.forEach(row => {
        total.conversions.thisWeek += row.conversions.thisWeek
        total.conversions.lastWeek += row.conversions.lastWeek
        total.conversionValue.thisWeek += row.conversionValue.thisWeek
        total.conversionValue.lastWeek += row.conversionValue.lastWeek
        total.cost.thisWeek += row.cost.thisWeek
        total.cost.lastWeek += row.cost.lastWeek
      })

      // 计算总ROAS
      total.roas.thisWeek = total.cost.thisWeek > 0 
        ? total.conversionValue.thisWeek / total.cost.thisWeek 
        : 0
      total.roas.lastWeek = total.cost.lastWeek > 0 
        ? total.conversionValue.lastWeek / total.cost.lastWeek 
        : 0

      // 月度列名行（在广告平台月度模拟之前）
      const monthlyHeaderRow = {
        product: '',
        conversions: { 
          thisWeek: '本月', 
          lastWeek: '上月' 
        },
        conversionValue: { 
          thisWeek: '本月', 
          lastWeek: '上月' 
        },
        cost: { 
          thisWeek: '本月', 
          lastWeek: '上月' 
        },
        roas: { 
          thisWeek: '本月',
          lastWeek: '上月'
        },
        isMonthlyHeader: true
      }

      // 广告平台月度模拟（总计广告平台 × 4）
      const adsPlatformMonthly = {
        product: '广告平台月度模拟',
        conversions: { 
          thisWeek: total.conversions.thisWeek * 4, 
          lastWeek: total.conversions.lastWeek * 4 
        },
        conversionValue: { 
          thisWeek: total.conversionValue.thisWeek * 4, 
          lastWeek: total.conversionValue.lastWeek * 4 
        },
        cost: { 
          thisWeek: total.cost.thisWeek * 4, 
          lastWeek: total.cost.lastWeek * 4 
        },
        roas: { 
          // ROAS = 转化价值 / 花费，乘以4后比例不变，与总计ROAS相同
          thisWeek: total.roas.thisWeek,
          lastWeek: total.roas.lastWeek
        },
        isSimulation: true
      }

      // 独立站全站月度模拟（使用lingxing月度数据 + 月度花费数据）
      const websiteMonthly = {
        product: '独立站全站月度模拟',
        conversions: { 
          thisWeek: props.lingxingData.conversions.thisWeek, 
          lastWeek: props.lingxingData.conversions.lastWeek
        },
        conversionValue: { 
          thisWeek: props.lingxingData.conversionValue.thisWeek, 
          lastWeek: props.lingxingData.conversionValue.lastWeek
        },
        cost: { 
          thisWeek: props.lingxingMonthlyCost.cost.thisWeek, 
          lastWeek: props.lingxingMonthlyCost.cost.lastWeek
        },
        roas: { 
          thisWeek: props.lingxingMonthlyCost.cost.thisWeek > 0 
            ? props.lingxingData.conversionValue.thisWeek / props.lingxingMonthlyCost.cost.thisWeek
            : 0,
          lastWeek: props.lingxingMonthlyCost.cost.lastWeek > 0 
            ? props.lingxingData.conversionValue.lastWeek / props.lingxingMonthlyCost.cost.lastWeek
            : 0
        },
        isSimulation: true
      }

      // 独立站销售目标（使用独立站销售目标数据）
      const salesTarget = {
        product: '独立站销售目标',
        conversions: { 
          thisWeek: '-', 
          lastWeek: '-'
        },
        conversionValue: { 
          thisWeek: props.salesTargetData.conversionValue.thisWeek, 
          lastWeek: props.salesTargetData.conversionValue.lastWeek
        },
        cost: { 
          thisWeek: '-', 
          lastWeek: '-'
        },
        roas: { 
          thisWeek: '-',
          lastWeek: '-'
        },
        isSimulation: true
      }

      // 计算Facebook产品合计（汇总两个Facebook账户的所有产品数据）
      const facebookProductTotal = {
        product: 'Facebook合计',
        conversions: { thisWeek: 0, lastWeek: 0 },
        conversionValue: { thisWeek: 0, lastWeek: 0 },
        cost: { thisWeek: 0, lastWeek: 0 },
        roas: { thisWeek: 0, lastWeek: 0 },
        isSubTotal: true  // 标记为分类合计行
      }

      // 汇总Facebook账户1的数据
      props.facebookAccount1Data.forEach(row => {
        facebookProductTotal.conversions.thisWeek += row.conversions?.thisWeek || 0
        facebookProductTotal.conversions.lastWeek += row.conversions?.lastWeek || 0
        facebookProductTotal.conversionValue.thisWeek += row.conversionValue?.thisWeek || 0
        facebookProductTotal.conversionValue.lastWeek += row.conversionValue?.lastWeek || 0
        facebookProductTotal.cost.thisWeek += row.cost?.thisWeek || 0
        facebookProductTotal.cost.lastWeek += row.cost?.lastWeek || 0
      })

      // 汇总Facebook账户2的数据
      props.facebookAccount2Data.forEach(row => {
        facebookProductTotal.conversions.thisWeek += row.conversions?.thisWeek || 0
        facebookProductTotal.conversions.lastWeek += row.conversions?.lastWeek || 0
        facebookProductTotal.conversionValue.thisWeek += row.conversionValue?.thisWeek || 0
        facebookProductTotal.conversionValue.lastWeek += row.conversionValue?.lastWeek || 0
        facebookProductTotal.cost.thisWeek += row.cost?.thisWeek || 0
        facebookProductTotal.cost.lastWeek += row.cost?.lastWeek || 0
      })

      // 计算Facebook产品合计的ROAS
      facebookProductTotal.roas.thisWeek = facebookProductTotal.cost.thisWeek > 0 
        ? facebookProductTotal.conversionValue.thisWeek / facebookProductTotal.cost.thisWeek 
        : 0
      facebookProductTotal.roas.lastWeek = facebookProductTotal.cost.lastWeek > 0 
        ? facebookProductTotal.conversionValue.lastWeek / facebookProductTotal.cost.lastWeek 
        : 0

      // 计算Google产品合计（汇总Google的所有产品数据）
      const googleProductTotal = {
        product: 'Google合计',
        conversions: { thisWeek: 0, lastWeek: 0 },
        conversionValue: { thisWeek: 0, lastWeek: 0 },
        cost: { thisWeek: 0, lastWeek: 0 },
        roas: { thisWeek: 0, lastWeek: 0 },
        isSubTotal: true  // 标记为分类合计行
      }

      // 汇总Google的数据
      props.googleData.forEach(row => {
        googleProductTotal.conversions.thisWeek += row.conversions?.thisWeek || 0
        googleProductTotal.conversions.lastWeek += row.conversions?.lastWeek || 0
        googleProductTotal.conversionValue.thisWeek += row.conversionValue?.thisWeek || 0
        googleProductTotal.conversionValue.lastWeek += row.conversionValue?.lastWeek || 0
        googleProductTotal.cost.thisWeek += row.cost?.thisWeek || 0
        googleProductTotal.cost.lastWeek += row.cost?.lastWeek || 0
      })

      // 计算Google产品合计的ROAS
      googleProductTotal.roas.thisWeek = googleProductTotal.cost.thisWeek > 0 
        ? googleProductTotal.conversionValue.thisWeek / googleProductTotal.cost.thisWeek 
        : 0
      googleProductTotal.roas.lastWeek = googleProductTotal.cost.lastWeek > 0 
        ? googleProductTotal.conversionValue.lastWeek / googleProductTotal.cost.lastWeek 
        : 0

      // 计算产品合计行（汇总所有产品数据）
      const productTotal = {
        product: '合计',
        conversions: { thisWeek: 0, lastWeek: 0 },
        conversionValue: { thisWeek: 0, lastWeek: 0 },
        cost: { thisWeek: 0, lastWeek: 0 },
        roas: { thisWeek: 0, lastWeek: 0 },
        isProductTotal: true  // 标记为产品合计行
      }

      summaryData.value.forEach(row => {
        productTotal.conversions.thisWeek += row.conversions.thisWeek
        productTotal.conversions.lastWeek += row.conversions.lastWeek
        productTotal.conversionValue.thisWeek += row.conversionValue.thisWeek
        productTotal.conversionValue.lastWeek += row.conversionValue.lastWeek
        productTotal.cost.thisWeek += row.cost.thisWeek
        productTotal.cost.lastWeek += row.cost.lastWeek
      })

      // 计算产品合计的ROAS
      productTotal.roas.thisWeek = productTotal.cost.thisWeek > 0 
        ? productTotal.conversionValue.thisWeek / productTotal.cost.thisWeek 
        : 0
      productTotal.roas.lastWeek = productTotal.cost.lastWeek > 0 
        ? productTotal.conversionValue.lastWeek / productTotal.cost.lastWeek 
        : 0

      // 账号汇总行（在Facebook广告之前，合并单元格显示"账号汇总"）
      const blankRow = {
        product: '账号汇总',
        conversions: { thisWeek: 0, lastWeek: 0 },
        conversionValue: { thisWeek: 0, lastWeek: 0 },
        cost: { thisWeek: 0, lastWeek: 0 },
        roas: { thisWeek: 0, lastWeek: 0 },
        isSummaryHeader: true  // 标记为汇总标题行，用于合并单元格
      }

      return [...summaryData.value, facebookProductTotal, googleProductTotal, productTotal, blankRow, facebookTotal, googleTotal, total, monthlyHeaderRow, adsPlatformMonthly, websiteMonthly, salesTarget]
    })

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

    // 格式化数值为两位小数
    const formatDecimal = (value) => {
      if (value === null || value === undefined) return '0.00'
      // 如果是字符串（如"本月"、"上月"），直接返回
      if (typeof value === 'string' && isNaN(parseFloat(value))) return value
      return parseFloat(value).toFixed(2)
    }

    // 格式化货币，处理字符串情况
    const formatCurrencyLocal = (value) => {
      if (value === null || value === undefined) return formatCurrency(0)
      // 如果是字符串（如"本月"、"上月"），直接返回
      if (typeof value === 'string' && isNaN(parseFloat(value))) return value
      return formatCurrency(value)
    }

    // 自定义编号方法（账号汇总行显示文字，其他汇总行和模拟行不显示编号）
    const indexMethod = (index) => {
      const dataLength = summaryDataWithTotal.value.length
      const row = summaryDataWithTotal.value[index]
      
      // 如果是账号汇总行，显示"账号汇总"文字
      if (row && row.isSummaryHeader) {
        return '账号汇总'
      }
      
      // 如果是月度列名行，不显示编号
      if (row && row.isMonthlyHeader) {
        return ''
      }
      
      // 如果是产品合计行或分类合计行（Facebook合计、Google合计），不显示编号
      if (row && (row.isProductTotal || row.isSubTotal)) {
        return ''
      }
      
      // 最后七行是：Facebook广告、Google广告、总计广告平台、月度列名行、广告平台月度模拟、独立站全站月度模拟、独立站销售目标，都不显示编号
      if (index >= dataLength - 7) {
        return ''
      }
      return index + 1
    }

    // 合并单元格方法（用于"账号汇总"行）
    const spanMethod = ({ row, column, rowIndex, columnIndex }) => {
      // 如果是账号汇总行（isSummaryHeader为true）
      if (row.isSummaryHeader) {
        // 第一列（编号列）合并所有列
        if (columnIndex === 0) {
          return [1, 10]  // 合并10列：编号 + 产品名称 + 转化(2) + 转化价值(2) + 花费(2) + ROAS(2)
        }
        // 其他列被合并，不显示
        return [0, 0]
      }
      // 其他行正常显示
      return [1, 1]
    }

    // 给特定行添加class名称
    const getRowClassName = ({ row, rowIndex }) => {
      if (row.isSummaryHeader) {
        return 'summary-header-row'
      }
      if (row.isMonthlyHeader) {
        return 'monthly-header-row'
      }
      if (row.isSubTotal) {
        return 'subtotal-row'
      }
      if (row.isSimulation) {
        return 'simulation-row'
      }
      return ''
    }

    return {
      formatCurrency,
      formatCurrencyLocal,
      formatDecimal,
      summaryDataWithTotal,
      getComparisonClass,
      getComparisonClassReverse,
      getTrendIcon,
      getTrendIconReverse,
      indexMethod,
      spanMethod,
      getRowClassName,
      editingCell,
      editingValue,
      editInput,
      startEdit,
      cancelEdit,
      saveEdit,
      Top,
      Bottom,
      Edit
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
  flex-wrap: wrap;
  gap: 12px;
}

.card-content {
  padding: 0 24px 24px;
}

.table-wrapper {
  overflow-x: auto;
  overflow-y: hidden;
  margin-bottom: 16px;
  -webkit-overflow-scrolling: touch;
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

/* 账号汇总行样式 - 与表头样式一致（必须在通用td样式之后，使用更高优先级） */
:deep(.el-table__body tr.summary-header-row td) {
  background-color: #f5f7fa !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  color: #000000 !important;
  text-align: center !important;
}

:deep(.el-table__body tr.summary-header-row td .cell) {
  text-align: center !important;
  justify-content: center !important;
}

:deep(.el-table__body tr.summary-header-row:hover td) {
  background-color: #e5e7eb !important;
}

/* 月度列名行样式 - 与表头样式一致 */
:deep(.el-table__body tr.monthly-header-row td) {
  background-color: #f5f7fa !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  color: #000000 !important;
  text-align: center !important;
}

:deep(.el-table__body tr.monthly-header-row td .cell) {
  text-align: center !important;
  justify-content: center !important;
}

:deep(.el-table__body tr.monthly-header-row:hover td) {
  background-color: #e5e7eb !important;
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

/* 可编辑单元格样式 */
.editable-cell {
  width: 100%;
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.editable-value {
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  position: relative;
}

.editable-value:hover {
  background-color: #f0f9ff;
  color: #2f45ff;
}

.edit-icon {
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.2s;
  color: #909399;
}

.editable-value:hover .edit-icon {
  opacity: 1;
}

.edit-input {
  width: 120px;
}

.edit-input :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #2f45ff;
}

.edit-input :deep(.el-input__inner) {
  text-align: center;
  font-size: 13px;
}
</style>

