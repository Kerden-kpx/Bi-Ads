<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        Ads Performance Overview
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
            label="Ad Creative" 
            sortable="custom"
            min-width="550"
            fixed="left"
          >
            <template #default="scope">
              <div class="ad-creative-cell">
                <el-image
                  v-if="scope.row.imageUrl"
                  :src="scope.row.imageUrl"
                  fit="cover"
                  class="ad-thumbnail"
                  :preview-src-list="[scope.row.imageUrl]"
                  preview-teleported
                />
                <div class="ad-info">
                  <div 
                    class="ad-name" 
                    :class="{ 'clickable': scope.row.previewUrl }"
                    :title="scope.row.name"
                    @click="scope.row.previewUrl ? showPreview(scope.row) : null"
                  >
                    {{ scope.row.name }}
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column 
            prop="purchases" 
            label="Purchases" 
            sortable="custom"
            min-width="130"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.purchases, scope.row.purchasesPrevious)" class="value-with-icon">
                {{ scope.row.purchases }}
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
            label="Purchases (Previous)" 
            sortable="custom"
            min-width="180"
          >
            <template #default="scope">
              {{ scope.row.purchasesPrevious }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="spend" 
            label="Spend" 
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
            label="Spend (Previous)" 
            sortable="custom"
            min-width="150"
          >
            <template #default="scope">
              ${{ formatCurrency(scope.row.spendPrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="purchaseRoas" 
            label="Purchase ROAS" 
            sortable="custom"
            min-width="160"
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
            label="Purchase ROAS (Previous)" 
            sortable="custom"
            min-width="200"
          >
            <template #default="scope">
              {{ formatDecimal(scope.row.purchaseRoasPrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="addsPaymentInfo" 
            label="Adds Payment Info" 
            sortable="custom"
            min-width="150"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.addsPaymentInfo, scope.row.addsPaymentInfoPrevious)" class="value-with-icon">
                {{ scope.row.addsPaymentInfo }}
                <el-icon v-if="getTrendIcon(scope.row.addsPaymentInfo, scope.row.addsPaymentInfoPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIcon(scope.row.addsPaymentInfo, scope.row.addsPaymentInfoPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="addsPaymentInfoPrevious" 
            label="Adds Payment Info (Previous)" 
            sortable="custom"
            min-width="220"
          >
            <template #default="scope">
              {{ scope.row.addsPaymentInfoPrevious }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="addsToCart" 
            label="Adds To Cart" 
            sortable="custom"
            min-width="140"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.addsToCart, scope.row.addsToCartPrevious)" class="value-with-icon">
                {{ scope.row.addsToCart }}
                <el-icon v-if="getTrendIcon(scope.row.addsToCart, scope.row.addsToCartPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIcon(scope.row.addsToCart, scope.row.addsToCartPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="addsToCartPrevious" 
            label="Adds To Cart (Previous)" 
            sortable="custom"
            min-width="200"
          >
            <template #default="scope">
              {{ scope.row.addsToCartPrevious }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="purchasesValue" 
            label="Purchases Value" 
            sortable="custom"
            min-width="150"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.purchasesValue, scope.row.purchasesValuePrevious)" class="value-with-icon">
                ${{ formatCurrency(scope.row.purchasesValue) }}
                <el-icon v-if="getTrendIcon(scope.row.purchasesValue, scope.row.purchasesValuePrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIcon(scope.row.purchasesValue, scope.row.purchasesValuePrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="purchasesValuePrevious" 
            label="Purchases Value (Previous)" 
            sortable="custom"
            min-width="210"
          >
            <template #default="scope">
              ${{ formatCurrency(scope.row.purchasesValuePrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="ctr" 
            label="CTR (Link Click-Through Rate)" 
            sortable="custom"
            min-width="230"
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
            label="CTR (Link Click-Through Rate) (Previous)" 
            sortable="custom"
            min-width="280"
          >
            <template #default="scope">
              {{ formatPercentage(scope.row.ctrPrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="cpm" 
            label="CPM" 
            sortable="custom"
            min-width="110"
          >
            <template #default="scope">
              <span :class="getComparisonClassReverse(scope.row.cpm, scope.row.cpmPrevious)" class="value-with-icon">
                ${{ formatCurrency(scope.row.cpm) }}
                <el-icon v-if="getTrendIconReverse(scope.row.cpm, scope.row.cpmPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIconReverse(scope.row.cpm, scope.row.cpmPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="cpmPrevious" 
            label="CPM (Previous)" 
            sortable="custom"
            min-width="150"
          >
            <template #default="scope">
              ${{ formatCurrency(scope.row.cpmPrevious) }}
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
          &lt;&lt;
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
          &gt;&gt;
        </el-button>
      </div>
    </div>

    <!-- 全屏对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="Ads Performance Overview"
      width="95%"
      top="2vh"
      :close-on-click-modal="false"
    >
      <div class="dialog-table-wrapper">
        <el-table 
          :data="allData" 
          style="width: 100%"
          stripe
          border
          max-height="75vh"
          @sort-change="handleSortChange"
        >
          <el-table-column 
            prop="name" 
            label="Ad Creative" 
            sortable="custom"
            min-width="600"
            fixed="left"
          >
            <template #default="scope">
              <div class="ad-creative-cell">
                <el-image
                  v-if="scope.row.imageUrl"
                  :src="scope.row.imageUrl"
                  fit="cover"
                  class="ad-thumbnail"
                  :preview-src-list="[scope.row.imageUrl]"
                  preview-teleported
                />
                <div class="ad-info">
                  <div 
                    class="ad-name" 
                    :class="{ 'clickable': scope.row.previewUrl }"
                    :title="scope.row.name"
                    @click="scope.row.previewUrl ? showPreview(scope.row) : null"
                  >
                    {{ scope.row.name }}
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column 
            prop="purchases" 
            label="Purchases" 
            sortable="custom"
            min-width="130"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.purchases, scope.row.purchasesPrevious)" class="value-with-icon">
                {{ scope.row.purchases }}
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
            label="Purchases (Previous)" 
            sortable="custom"
            min-width="180"
          >
            <template #default="scope">
              {{ scope.row.purchasesPrevious }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="spend" 
            label="Spend" 
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
            label="Spend (Previous)" 
            sortable="custom"
            min-width="150"
          >
            <template #default="scope">
              ${{ formatCurrency(scope.row.spendPrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="purchaseRoas" 
            label="Purchase ROAS" 
            sortable="custom"
            min-width="160"
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
            label="Purchase ROAS (Previous)" 
            sortable="custom"
            min-width="200"
          >
            <template #default="scope">
              {{ formatDecimal(scope.row.purchaseRoasPrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="addsPaymentInfo" 
            label="Adds Payment Info" 
            sortable="custom"
            min-width="150"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.addsPaymentInfo, scope.row.addsPaymentInfoPrevious)" class="value-with-icon">
                {{ scope.row.addsPaymentInfo }}
                <el-icon v-if="getTrendIcon(scope.row.addsPaymentInfo, scope.row.addsPaymentInfoPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIcon(scope.row.addsPaymentInfo, scope.row.addsPaymentInfoPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="addsPaymentInfoPrevious" 
            label="Adds Payment Info (Previous)" 
            sortable="custom"
            min-width="220"
          >
            <template #default="scope">
              {{ scope.row.addsPaymentInfoPrevious }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="addsToCart" 
            label="Adds To Cart" 
            sortable="custom"
            min-width="140"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.addsToCart, scope.row.addsToCartPrevious)" class="value-with-icon">
                {{ scope.row.addsToCart }}
                <el-icon v-if="getTrendIcon(scope.row.addsToCart, scope.row.addsToCartPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIcon(scope.row.addsToCart, scope.row.addsToCartPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="addsToCartPrevious" 
            label="Adds To Cart (Previous)" 
            sortable="custom"
            min-width="200"
          >
            <template #default="scope">
              {{ scope.row.addsToCartPrevious }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="purchasesValue" 
            label="Purchases Value" 
            sortable="custom"
            min-width="150"
          >
            <template #default="scope">
              <span :class="getComparisonClass(scope.row.purchasesValue, scope.row.purchasesValuePrevious)" class="value-with-icon">
                ${{ formatCurrency(scope.row.purchasesValue) }}
                <el-icon v-if="getTrendIcon(scope.row.purchasesValue, scope.row.purchasesValuePrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIcon(scope.row.purchasesValue, scope.row.purchasesValuePrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="purchasesValuePrevious" 
            label="Purchases Value (Previous)" 
            sortable="custom"
            min-width="210"
          >
            <template #default="scope">
              ${{ formatCurrency(scope.row.purchasesValuePrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="ctr" 
            label="CTR (Link Click-Through Rate)" 
            sortable="custom"
            min-width="230"
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
            label="CTR (Link Click-Through Rate) (Previous)" 
            sortable="custom"
            min-width="280"
          >
            <template #default="scope">
              {{ formatPercentage(scope.row.ctrPrevious) }}
            </template>
          </el-table-column>

          <el-table-column 
            prop="cpm" 
            label="CPM" 
            sortable="custom"
            min-width="110"
          >
            <template #default="scope">
              <span :class="getComparisonClassReverse(scope.row.cpm, scope.row.cpmPrevious)" class="value-with-icon">
                ${{ formatCurrency(scope.row.cpm) }}
                <el-icon v-if="getTrendIconReverse(scope.row.cpm, scope.row.cpmPrevious) === 'up'" class="trend-icon">
                  <Top />
                </el-icon>
                <el-icon v-if="getTrendIconReverse(scope.row.cpm, scope.row.cpmPrevious) === 'down'" class="trend-icon">
                  <Bottom />
                </el-icon>
              </span>
            </template>
          </el-table-column>

          <el-table-column 
            prop="cpmPrevious" 
            label="CPM (Previous)" 
            sortable="custom"
            min-width="150"
          >
            <template #default="scope">
              ${{ formatCurrency(scope.row.cpmPrevious) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 广告预览抽屉 -->
    <el-drawer
      v-model="previewDialogVisible"
      direction="rtl"
      size="500px"
      :show-close="false"
      :with-header="false"
      :close-on-click-modal="true"
    >
      <div v-if="currentPreview" class="preview-container">
        <!-- 自定义关闭按钮 -->
        <div class="drawer-close-btn" @click="previewDialogVisible = false">
          <el-icon><Close /></el-icon>
        </div>
        
        <div class="preview-content" v-if="currentPreview.previewUrl">
          <div class="preview-html" v-html="currentPreview.previewUrl"></div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { formatCurrency, formatDecimal, formatPercentage, formatNumber } from '../../utils/formatters'
import { FullScreen, Top, Bottom, View, Close } from '@element-plus/icons-vue'

export default {
  name: 'Facebook_Ads_Detail_Performance_Card',
  components: {
    FullScreen,
    Top,
    Bottom,
    View,
    Close
  },
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
    const dialogVisible = ref(false)
    const previewDialogVisible = ref(false)
    const currentPreview = ref(null)
    const sortProp = ref('')
    const sortOrder = ref('')

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
          purchasesValue: 0,
          purchasesValuePrevious: 0,
          ctr: 0,
          ctrPrevious: 0,
          cpm: 0,
          cpmPrevious: 0,
          isTotal: true
        }
      }

      const totals = props.data.reduce((acc, row) => {
        acc.purchases += row.purchases || 0
        acc.purchasesPrevious += row.purchasesPrevious || 0
        acc.spend += row.spend || 0
        acc.spendPrevious += row.spendPrevious || 0
        acc.purchasesValue += row.purchasesValue || 0
        acc.purchasesValuePrevious += row.purchasesValuePrevious || 0
        return acc
      }, {
        purchases: 0,
        purchasesPrevious: 0,
        spend: 0,
        spendPrevious: 0,
        purchasesValue: 0,
        purchasesValuePrevious: 0
      })

      return {
        name: 'Total',
        purchases: totals.purchases,
        purchasesPrevious: totals.purchasesPrevious,
        spend: totals.spend,
        spendPrevious: totals.spendPrevious,
        purchaseRoas: totals.spend > 0 ? totals.purchasesValue / totals.spend : 0,
        purchaseRoasPrevious: totals.spendPrevious > 0 ? totals.purchasesValuePrevious / totals.spendPrevious : 0,
        purchasesValue: totals.purchasesValue,
        purchasesValuePrevious: totals.purchasesValuePrevious,
        ctr: 0, // CTR 不能简单相加
        ctrPrevious: 0,
        cpm: 0, // CPM 不能简单相加
        cpmPrevious: 0,
        isTotal: true
      }
    })

    // 排序数据
    const sortedData = computed(() => {
      if (!sortProp.value || !sortOrder.value) {
        return [...props.data]
      }

      const data = [...props.data]
      return data.sort((a, b) => {
        const aVal = a[sortProp.value]
        const bVal = b[sortProp.value]
        
        if (sortOrder.value === 'ascending') {
          return aVal > bVal ? 1 : -1
        } else {
          return aVal < bVal ? 1 : -1
        }
      })
    })

    // 所有数据（包含总计行）
    const allData = computed(() => {
      return [...sortedData.value, totalRow.value]
    })

    // 分页数据
    const paginatedData = computed(() => {
      const start = (currentPage.value - 1) * pageSize
      const end = start + pageSize
      return sortedData.value.slice(start, end)
    })

    // 显示数据（分页数据 + 总计行）
    const displayData = computed(() => {
      return [...paginatedData.value, totalRow.value]
    })

    const totalPages = computed(() => Math.ceil(props.data.length / pageSize) || 1)

    // 处理排序变化
    const handleSortChange = ({ prop, order }) => {
      sortProp.value = prop
      sortOrder.value = order
    }

    const showPreview = (row) => {
      currentPreview.value = row
      previewDialogVisible.value = true
    }

    // 获取对比样式类（值越大越好）
    const getComparisonClass = (current, previous) => {
      if (current > previous) return 'value-increase'
      if (current < previous) return 'value-decrease'
      return ''
    }

    // 获取对比样式类（值越小越好，如Cost）
    const getComparisonClassReverse = (current, previous) => {
      if (current < previous) return 'value-decrease'  // 花费减少 → 绿色（好事）
      if (current > previous) return 'value-increase'  // 花费增加 → 红色（坏事）
      return ''
    }

    // 获取趋势图标（值越大越好）
    const getTrendIcon = (current, previous) => {
      if (current > previous) return 'up'
      if (current < previous) return 'down'
      return null
    }

    // 获取趋势图标（值越小越好）
    const getTrendIconReverse = (current, previous) => {
      if (current < previous) return 'down'  // 花费减少 → 向下箭头（好事）
      if (current > previous) return 'up'  // 花费增加 → 向上箭头（坏事）
      return null
    }

    return {
      currentPage,
      totalPages,
      displayData,
      allData,
      dialogVisible,
      previewDialogVisible,
      currentPreview,
      handleSortChange,
      showPreview,
      formatCurrency,
      formatDecimal,
      formatPercentage,
      formatNumber,
      getComparisonClass,
      getComparisonClassReverse,
      getTrendIcon,
      getTrendIconReverse,
      FullScreen,
      Top,
      Bottom,
      View
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

.card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
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

/* 趋势样式 */
.value-increase {
  color: #ef4444 !important;
  font-weight: 600;
}

.value-decrease {
  color: #10b981 !important;
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

/* Ad Name 列和 Previous 列数据颜色为黑色 */
:deep(.el-table td:first-child) {
  color: #000000 !important;
}

:deep(.el-table td:nth-child(3)),
:deep(.el-table td:nth-child(5)),
:deep(.el-table td:nth-child(7)),
:deep(.el-table td:nth-child(9)),
:deep(.el-table td:nth-child(11)),
:deep(.el-table td:nth-child(13)) {
  color: #000000 !important;
}

/* 当前数据列的默认颜色为黑色 */
:deep(.el-table td:nth-child(2)),
:deep(.el-table td:nth-child(4)),
:deep(.el-table td:nth-child(6)),
:deep(.el-table td:nth-child(8)),
:deep(.el-table td:nth-child(10)),
:deep(.el-table td:nth-child(12)) {
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

.dialog-table-wrapper {
  overflow-x: auto;
  max-height: 75vh;
}

:deep(.el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

:deep(.el-dialog__body) {
  padding: 24px;
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

/* 广告创意单元格样式 */
.ad-creative-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ad-thumbnail {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  flex-shrink: 0;
  cursor: pointer;
  transition: transform 0.2s;
}

.ad-thumbnail:hover {
  transform: scale(1.05);
}

.ad-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ad-name {
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ad-name.clickable {
  cursor: pointer;
  color: #303133;
  transition: all 0.2s ease;
}

.ad-name.clickable:hover {
  color: #303133;
  text-decoration: underline;
}

/* 预览抽屉样式 */
:deep(.el-drawer__body) {
  padding: 0;
  background: #ffffff;
  height: 100%;
  overflow: hidden;
  position: relative;
}

/* 自定义关闭按钮 */
.drawer-close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  z-index: 1000;
  transition: all 0.2s ease;
}

.drawer-close-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.drawer-close-btn .el-icon {
  font-size: 18px;
  color: #6b7280;
}

.preview-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  position: relative;
}

.preview-content {
  flex: 1;
  width: 100%;
  padding-top: 60px;
  overflow-y: auto;
  overflow-x: hidden;
}

.preview-html {
  padding: 0;
  margin: 0;
  background-color: transparent;
  border: none;
  width: 100%;
  min-height: calc(100vh - 60px);
}

.preview-html::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.preview-html::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.preview-html::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.preview-html::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>

