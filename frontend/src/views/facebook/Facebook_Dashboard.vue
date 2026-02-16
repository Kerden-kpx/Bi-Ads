<template>
  <div>
    <div class="page-title-bar">
      <div class="page-title">
        <img :src="ezarcLogo" alt="EZARC" class="title-logo-img" />
        <span>Facebook Ads Report {{ dateRangeDisplay }}</span>
      </div>
      <div class="date-controls">
        <div class="account-selector-wrapper">
          <el-popover
            v-model:visible="accountPopoverVisible"
            placement="bottom-start"
            :width="200"
            trigger="click"
            popper-class="account-selector-popover"
          >
            <template #reference>
              <div class="account-selector-trigger">
                <el-icon class="account-icon"><UserFilled /></el-icon>
                <span class="account-text">{{ selectedAccountName }}</span>
                <el-icon class="arrow-icon"><ArrowDown /></el-icon>
              </div>
            </template>
            <div class="account-options">
              <div
                v-for="account in accounts"
                :key="account.id"
                class="account-option"
                :class="{ active: selectedAccount === account.id }"
                @click="selectAccount(account.id)"
              >
                {{ account.name }}
              </div>
            </div>
          </el-popover>
        </div>
        <QuickDateRangePicker
          v-model="currentDateRange"
          placeholder="Aug 4, 2025 - Aug 10, 2025"
        />
        <div class="compare-wrapper">
          <span class="compare-label">Compare to:</span>
          <SimpleDateRangePicker
            v-model="compareDateRange"
            placeholder="Jul 28 - Aug 3, 2025"
          />
        </div>
        <div class="action-buttons">
          <button class="icon-button" @click="handleRefresh" :disabled="loading" title="刷新">
            <el-icon><Refresh /></el-icon>
          </button>
          <button class="icon-button" @click="handleSync" :disabled="syncing" title="数据同步">
            <el-icon><Upload /></el-icon>
          </button>
          <button class="icon-button" @click="handleSettings" title="设置">
            <el-icon><Setting /></el-icon>
          </button>
        </div>
      </div>
    </div>

    <div class="dashboard-container">
    <section id="impression-reach-trend" class="section content-section">
      <FacebookImpressionsReachCard 
        :data="impressionsData" 
        :date-range="currentDateRange"
        :performance-comparison-data="impressionsComparisonData"
        :loading="overviewLoading"
      />
    </section>

    <section id="impression-reach-analyze" class="section content-section">
      <FacebookAnalyzeCardOne 
        :data="impressionsData" 
        :date-range="currentDateRange"
        :compare-date-range="compareDateRange"
        :account-id="selectedAccount"
        :performance-comparison-data="impressionsComparisonData"
        :loading="overviewLoading"
      />
    </section>

    <section id="purchases-spend-trend" class="section content-section">
      <FacebookPurchasesSpendCard 
        :data="purchasesData" 
        :date-range="currentDateRange"
        :compare-date-range="compareDateRange"
        :performance-comparison-data="purchasesComparisonData"
        :loading="overviewLoading"
      />
    </section>

    <section id="purchases-spend-analyze" class="section content-section">
      <FacebookAnalyzeCardTwo 
        :data="purchasesData" 
        :date-range="currentDateRange"
        :compare-date-range="compareDateRange"
        :account-id="selectedAccount"
        :performance-comparison-data="purchasesComparisonData"
        :loading="overviewLoading"
      />
    </section>

    <section id="ad-sets-performance" class="section content-section">
        <FacebookAdSetsPerformanceCard :data="adSetsData" :loading="adSetsLoading" />
    </section>

    <section id="ads-detail-performance" class="section content-section">
        <FacebookAdsDetailPerformanceCard :data="adsDetailData" :loading="adsDetailLoading" />
    </section>

    <section id="ads-performance" class="section content-section">
        <FacebookAdsPerformanceCard 
          :data="adsPerformanceData" 
          :date-range="adsPerformanceDate"
          :loading="adsPerformanceLoading"
          @date-change="handleAdsPerformanceDateChange"
        />
    </section>
    </div>

    <!-- 设置对话框 -->
    <el-dialog
      v-model="settingsDialogVisible"
      title="设置"
      width="600px"
      :close-on-click-modal="false"
      class="settings-dialog"
    >
      <div class="settings-content">
        <!-- 自动同步设置 -->
        <div class="setting-item">
          <div class="setting-header">
            <span class="setting-title">自动同步数据</span>
            <el-switch
              v-model="autoSyncEnabled"
              :active-value="true"
              :inactive-value="false"
            />
          </div>
          <div class="setting-description">
            启用后将自动刷新广告数据
          </div>
        </div>

        <div class="setting-divider"></div>

        <!-- Facebook 产品名称管理 -->
        <div class="setting-item">
          <div class="setting-header">
            <span class="setting-title">Facebook 产品</span>
          </div>
          
          <div class="product-names-manager">
            <el-tag
              v-for="(name, index) in facebookProductNames"
              :key="index"
              closable
              @close="removeFacebookProductName(index)"
              class="product-tag"
              type="info"
            >
              {{ name }}
            </el-tag>
            
            <el-input
              v-if="facebookInputVisible"
              ref="FacebookInputRef"
              v-model="facebookInputValue"
              class="product-input"
              size="small"
              placeholder="输入产品名"
              @keyup.enter="handleFacebookInputConfirm"
              @blur="handleFacebookInputConfirm"
            />
            <el-button v-else class="add-product-btn" size="small" text @click="showFacebookInput">
              + 添加
            </el-button>
          </div>
        </div>

        <div class="setting-divider"></div>

        <!-- Google 产品名称管理 -->
        <div class="setting-item">
          <div class="setting-header">
            <span class="setting-title">Google 产品</span>
          </div>
          
          <div class="product-names-manager">
            <el-tag
              v-for="(name, index) in googleProductNames"
              :key="index"
              closable
              @close="removeGoogleProductName(index)"
              class="product-tag"
              type="info"
            >
              {{ name }}
            </el-tag>
            
            <el-input
              v-if="googleInputVisible"
              ref="GoogleInputRef"
              v-model="googleInputValue"
              class="product-input"
              size="small"
              placeholder="输入产品名"
              @keyup.enter="handleGoogleInputConfirm"
              @blur="handleGoogleInputConfirm"
            />
            <el-button v-else class="add-product-btn" size="small" text @click="showGoogleInput">
              + 添加
            </el-button>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelSettings">取消</el-button>
          <el-button type="primary" @click="saveSettings" :loading="savingSettings">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { reactive, ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Upload, UserFilled, ArrowDown, Setting } from '@element-plus/icons-vue'
import { settingsAPI } from '../../services/settingsApi'
import FacebookImpressionsReachCard from '../../components/facebook/Facebook_Impressions_Reach_Card.vue'
import FacebookAnalyzeCardOne from '../../components/facebook/Facebook_Analyze_Card_One.vue'
import FacebookPurchasesSpendCard from '../../components/facebook/Facebook_Purchases_Spend_Card.vue'
import FacebookAnalyzeCardTwo from '../../components/facebook/Facebook_Analyze_Card_Two.vue'
import FacebookAdSetsPerformanceCard from '../../components/facebook/Facebook_AdSets_Performance_Card.vue'
import FacebookAdsDetailPerformanceCard from '../../components/facebook/Facebook_Ads_Detail_Performance_Card.vue'
import FacebookAdsPerformanceCard from '../../components/facebook/Facebook_Ads_Performance_Card.vue'
import QuickDateRangePicker from '../../components/shared/Quick_Date_Range_Picker.vue'
import SimpleDateRangePicker from '../../components/shared/Simple_Date_Range_Picker.vue'
import { facebookDashboardAPI } from '../../services/facebook/facebookApi'
import { useDashboard } from '../../composables/useDashboard'
import { globalSettings } from '../../utils/globalSettings'
import ezarcLogo from '@/assets/logos/ezarc-logo.jpg'
import dayjs from 'dayjs'

export default {
  name: 'Facebook_Dashboard',
  components: {
    FacebookImpressionsReachCard,
    FacebookAnalyzeCardOne,
    FacebookPurchasesSpendCard,
    FacebookAnalyzeCardTwo,
    FacebookAdSetsPerformanceCard,
    FacebookAdsDetailPerformanceCard,
    FacebookAdsPerformanceCard,
    QuickDateRangePicker,
    SimpleDateRangePicker,
    Refresh,
    Upload,
    UserFilled,
    ArrowDown,
    Setting,
  },
  setup() {
    const {
      loading,
      currentDateRange,
      compareDateRange,
      createEmptyData,
      createEmptyPurchasesData,
      createRefreshHandler,
    } = useDashboard(facebookDashboardAPI, 'facebook')

    // 账户列表
    const accounts = ref([
      { id: '2613027225660900', name: 'EZARCADS-1' },
      { id: '1069516980635624', name: 'EZARCADS-2' }
    ])
    
    // 选中的账户（默认选择EZARCADS-2）
    const selectedAccount = ref('1069516980635624')
    
    // 账户选择器弹窗可见性
    const accountPopoverVisible = ref(false)
    
    // 选中账户的名称
    const selectedAccountName = computed(() => {
      const account = accounts.value.find(a => a.id === selectedAccount.value)
      return account ? account.name : '请选择账户'
    })
    
    // 选择账户
    const selectAccount = (accountId) => {
      selectedAccount.value = accountId
      accountPopoverVisible.value = false
      handleAccountChange(accountId)
    }

    const impressionsData = createEmptyData()
    const purchasesData = createEmptyPurchasesData()
    const adSetsData = reactive([])
    const adsDetailData = reactive([])
    const adsPerformanceData = reactive([])
    const impressionsComparisonData = reactive([])  // 展示数据的对比
    const purchasesComparisonData = reactive([])    // 购买数据的对比
    const performanceComparisonData = reactive([])  // 保留用于其他地方（如果需要）
    
    // 各个Card的loading状态
    const overviewLoading = ref(false)  // 统一的loading状态，用于impressions和purchases
    const adSetsLoading = ref(false)
    const adsDetailLoading = ref(false)
    const adsPerformanceLoading = ref(false)
    
    // ADS PERFORMANCE OVERVIEW 的独立日期（默认为上周一）
    const adsPerformanceDate = ref(dayjs().subtract(1, 'week').day(1).format('YYYY-MM-DD'))

    // 加载总览数据（包含impressions和purchases，直接从Facebook API）
    const loadOverviewData = async () => {
      overviewLoading.value = true
      try {
        const params = {
          startDate: currentDateRange.value[0],
          endDate: currentDateRange.value[1],
          compareStartDate: compareDateRange.value?.[0],
          compareEndDate: compareDateRange.value?.[1],
          accountId: selectedAccount.value
        }
        
        // 使用新的合并API方法，一次性获取impressions和purchases数据
        const response = await facebookDashboardAPI.getOverviewDataFromAPI(params)
        const data = response.data || response
        
        // 更新impressions数据
        Object.assign(impressionsData, data.impressions)
        
        // 如果有对比数据，更新impressionsComparisonData用于图表
        if (data.impressions.performanceComparisonData) {
          impressionsComparisonData.splice(0, impressionsComparisonData.length, ...data.impressions.performanceComparisonData)
        } else {
          impressionsComparisonData.splice(0, impressionsComparisonData.length)
        }
        
        // 更新purchases数据
        Object.assign(purchasesData, data.purchases)
        
        // 如果有对比数据，更新purchasesComparisonData用于图表
        if (data.purchases.performanceComparisonData) {
          purchasesComparisonData.splice(0, purchasesComparisonData.length, ...data.purchases.performanceComparisonData)
        } else {
          purchasesComparisonData.splice(0, purchasesComparisonData.length)
        }
      } catch (error) {
        console.error('从API加载总览数据失败:', error)
        ElMessage.error('从API加载总览数据失败，请稍后重试')
      } finally {
        overviewLoading.value = false
      }
    }

    // 加载广告组数据
    const loadAdSetsData = async () => {
      // 如果没有对比日期，则不加载对比数据
      if (!compareDateRange.value || compareDateRange.value.length !== 2) {
        adSetsData.splice(0, adSetsData.length)
        return
      }

      adSetsLoading.value = true
      try {
        const requestData = {
          startDate1: currentDateRange.value[0],
          endDate1: currentDateRange.value[1],
          startDate2: compareDateRange.value[0],
          endDate2: compareDateRange.value[1],
          accountId: selectedAccount.value
        }
        
        const response = await facebookDashboardAPI.getAdsetsPerformanceOverview(requestData)
        const data = response.data || response || []
        
        adSetsData.splice(0, adSetsData.length, ...data)
      } catch (error) {
        console.error('加载广告组数据失败:', error)
        ElMessage.error('加载广告组数据失败，请稍后重试')
      } finally {
        adSetsLoading.value = false
      }
    }

    // 加载广告明细数据
    const loadAdsDetailData = async () => {
      // 如果没有对比日期，则不加载对比数据
      if (!compareDateRange.value || compareDateRange.value.length !== 2) {
        adsDetailData.splice(0, adsDetailData.length)
        return
      }

      adsDetailLoading.value = true
      try {
        const requestData = {
          startDate1: currentDateRange.value[0],
          endDate1: currentDateRange.value[1],
          startDate2: compareDateRange.value[0],
          endDate2: compareDateRange.value[1],
          accountId: selectedAccount.value
        }
        
        const response = await facebookDashboardAPI.getAdsDetailPerformanceOverview(requestData)
        const data = response.data || response || []
        
        adsDetailData.splice(0, adsDetailData.length, ...data)
      } catch (error) {
        console.error('加载广告明细数据失败:', error)
        ElMessage.error('加载广告明细数据失败，请稍后重试')
      } finally {
        adsDetailLoading.value = false
      }
    }

    // 加载广告表现数据
    const loadAdsPerformanceData = async (date = null) => {
      adsPerformanceLoading.value = true
      try {
        const requestData = {
          date: date || adsPerformanceDate.value,
          accountId: selectedAccount.value
        }
        
        const response = await facebookDashboardAPI.getAdsPerformanceOverview(requestData)
        const rawData = response.data || response || []
        
        // 使用转换器
        const transformedData = rawData.map(item => ({
          product: item.campaign_name,
          conversions: { thisWeek: item.current_purchases, lastWeek: item.last_purchases },
          conversionValue: { thisWeek: item.current_purchases_value, lastWeek: item.last_purchases_value },
          cost: { thisWeek: item.current_spend, lastWeek: item.last_spend },
          roas: { thisWeek: item.current_roas, lastWeek: item.last_roas }
        }))
        
        adsPerformanceData.splice(0, adsPerformanceData.length, ...transformedData)
      } catch (error) {
        console.error('加载广告表现数据失败:', error)
        ElMessage.error('加载广告表现数据失败，请稍后重试')
      } finally {
        adsPerformanceLoading.value = false
      }
    }

    // 处理 ADS PERFORMANCE OVERVIEW 的日期变化
    const handleAdsPerformanceDateChange = (newDate) => {
      adsPerformanceDate.value = newDate
      loadAdsPerformanceData(newDate)
    }

    // 加载性能对比数据（用于面积图）
    const loadPerformanceComparisonData = async () => {
      // 如果没有对比日期，则不加载对比数据
      if (!compareDateRange.value || compareDateRange.value.length !== 2) {
        performanceComparisonData.splice(0, performanceComparisonData.length)
        return
      }

      try {
        const requestData = {
          startDate1: currentDateRange.value[0],
          endDate1: currentDateRange.value[1],
          startDate2: compareDateRange.value[0],
          endDate2: compareDateRange.value[1],
          accountId: selectedAccount.value
        }
        
        const response = await facebookDashboardAPI.getPerformanceComparison(requestData)
        const data = response.data || response || []
        
        performanceComparisonData.splice(0, performanceComparisonData.length, ...data)
      } catch (error) {
        console.error('加载性能对比数据失败:', error)
        ElMessage.error('加载性能对比数据失败，请稍后重试')
      }
    }

    // 并行加载所有数据（性能优化版本）
    const loadAllDataParallel = async () => {
      loading.value = true
      overviewLoading.value = true
      
      try {
        // 使用 Promise.allSettled 并行执行所有请求
        const results = await Promise.allSettled([
          loadOverviewData(),
          loadAdSetsData(),
          loadAdsDetailData(),
          loadAdsPerformanceData()
        ])
        
        // 检查失败的请求并记录
        results.forEach((result, index) => {
          if (result.status === 'rejected') {
            console.error(`数据加载失败 (索引${index}):`, result.reason)
          }
        })
      } catch (error) {
        console.error('并行加载数据失败:', error)
      } finally {
        loading.value = false
        overviewLoading.value = false
      }
    }

    // 使用合并的loadOverviewData一次性获取impressions和purchases数据
    const loadFunctions = [loadOverviewData, loadAdSetsData, loadAdsDetailData, loadAdsPerformanceData]
    const handleRefresh = createRefreshHandler(loadFunctions)
    
    // 自定义同步处理（包含账户ID）
    const syncing = ref(false)
    
    // 实际执行同步的内部函数
    const executeFacebookSync = async (showMessage = true) => {
      try {
        if (showMessage) {
          ElMessage({
            message: '正在后台同步 Facebook Ads 数据...',
            type: 'info',
            duration: 3000
          })
        }
        
        // 并行同步主日期范围和对比日期范围的数据
        const syncPromises = [
          facebookDashboardAPI.syncData({
            start_date: currentDateRange.value[0],
            end_date: currentDateRange.value[1],
            ad_account_id: selectedAccount.value,
            status_filter: 'ACTIVE'
          })
        ]
        
        // 如果有对比日期范围,添加到并行任务中
        if (compareDateRange.value && compareDateRange.value.length === 2) {
          syncPromises.push(
            facebookDashboardAPI.syncData({
              start_date: compareDateRange.value[0],
              end_date: compareDateRange.value[1],
              ad_account_id: selectedAccount.value,
              status_filter: 'ACTIVE'
            })
          )
        }
        
        // 等待所有同步任务并行完成
        await Promise.all(syncPromises)
        
        if (showMessage) {
          ElMessage({
            message: 'Facebook Ads 数据同步完成！',
            type: 'success',
            duration: 3000
          })
        }
        
        // 同步完成后刷新页面数据
        await handleRefresh()
        return true
      } catch (error) {
        console.error('Facebook Ads 数据同步失败:', error)
        if (showMessage) {
          ElMessage.error('数据同步失败，请稍后重试')
        }
        return false
      }
    }
    
    // 手动同步（显示确认对话框）
    const handleSync = async () => {
      try {
        // 显示确认对话框
        await ElMessageBox.confirm(
          `确定要同步账户 ${accounts.value.find(a => a.id === selectedAccount.value)?.name} 的数据吗？这可能需要一些时间。`,
          '确认同步',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        syncing.value = true
        ElMessage({
          message: '开始同步 Facebook Ads 数据，可能需要几分钟，请耐心等待...',
          type: 'info',
          duration: 6000
        })
        
        await executeFacebookSync(true)
      } catch (error) {
        if (error === 'cancel') {
          return
        }
        console.error('Facebook Ads 数据同步失败:', error)
        ElMessage.error('数据同步失败，请稍后重试')
      } finally {
        syncing.value = false
      }
    }
    
    // 自动同步（不显示确认对话框，静默执行）
    const autoSyncFacebookData = async () => {
      if (syncing.value) {
        console.log('Facebook Ads 数据正在同步中，跳过本次自动同步')
        return
      }
      
      syncing.value = true
      try {
        await executeFacebookSync(false)
      } finally {
        syncing.value = false
      }
    }
    
    // 监听设置变化的取消函数
    let unsubscribe = null
    
    // 页面加载时加载设置和条件性自动同步
    onMounted(async () => {
      loadSettings()
      
      // 监听全局设置变化
      unsubscribe = globalSettings.onSettingsChange((newValue) => {
        console.log('Facebook Dashboard: 检测到全局设置变化', newValue)
        autoSyncEnabled.value = newValue
      })
      
      // 先并行加载显示数据（性能优化）
      await loadAllDataParallel()
      
      // 根据设置决定是否自动同步
      if (autoSyncEnabled.value) {
        console.log('页面加载，自动同步 Facebook Ads 数据')
        await autoSyncFacebookData()
      } else {
        console.log('自动同步已禁用，跳过页面加载时的自动同步')
      }
    })
    
    // 页面卸载时取消监听
    onUnmounted(() => {
      if (unsubscribe) {
        unsubscribe()
      }
    })
    
    // 日期变化时条件性自动同步
    watch(currentDateRange, async (newVal, oldVal) => {
      if (JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
        if (autoSyncEnabled.value) {
          console.log('日期变化，自动同步 Facebook Ads 数据')
          await autoSyncFacebookData()
        } else {
          console.log('自动同步已禁用，跳过日期变化时的自动同步')
        }
      }
    }, { deep: true })

    // 设置对话框可见性
    const settingsDialogVisible = ref(false)
    const savingSettings = ref(false)
    
    // 自动同步设置（默认不自动同步）
    const autoSyncEnabled = ref(false)
    
    // Facebook 产品名称管理
    const facebookProductNames = ref([])
    const originalFacebookProductNames = ref([])
    const facebookInputVisible = ref(false)
    const facebookInputValue = ref('')
    const FacebookInputRef = ref(null)
    
    // Google 产品名称管理
    const googleProductNames = ref([])
    const originalGoogleProductNames = ref([])
    const googleInputVisible = ref(false)
    const googleInputValue = ref('')
    const GoogleInputRef = ref(null)
    
    // 加载产品名称列表
    const loadProductNames = async () => {
      try {
        const response = await settingsAPI.getProductNames()
        const data = response.data || response
        facebookProductNames.value = [...(data.facebook_product_names || [])]
        originalFacebookProductNames.value = [...(data.facebook_product_names || [])]
        googleProductNames.value = [...(data.google_product_names || [])]
        originalGoogleProductNames.value = [...(data.google_product_names || [])]
      } catch (error) {
        console.error('加载产品名称失败:', error)
        ElMessage.error('加载产品名称失败')
      }
    }
    
    // Facebook 产品名称操作
    const removeFacebookProductName = (index) => {
      facebookProductNames.value.splice(index, 1)
    }
    
    const showFacebookInput = () => {
      facebookInputVisible.value = true
      nextTick(() => {
        FacebookInputRef.value && FacebookInputRef.value.focus()
      })
    }
    
    const handleFacebookInputConfirm = () => {
      if (facebookInputValue.value && facebookInputValue.value.trim()) {
        const newName = facebookInputValue.value.trim()
        if (!facebookProductNames.value.includes(newName)) {
          facebookProductNames.value.push(newName)
        } else {
          ElMessage.warning('该产品名称已存在')
        }
      }
      facebookInputVisible.value = false
      facebookInputValue.value = ''
    }
    
    // Google 产品名称操作
    const removeGoogleProductName = (index) => {
      googleProductNames.value.splice(index, 1)
    }
    
    const showGoogleInput = () => {
      googleInputVisible.value = true
      nextTick(() => {
        GoogleInputRef.value && GoogleInputRef.value.focus()
      })
    }
    
    const handleGoogleInputConfirm = () => {
      if (googleInputValue.value && googleInputValue.value.trim()) {
        const newName = googleInputValue.value.trim()
        if (!googleProductNames.value.includes(newName)) {
          googleProductNames.value.push(newName)
        } else {
          ElMessage.warning('该产品名称已存在')
        }
      }
      googleInputVisible.value = false
      googleInputValue.value = ''
    }
    
    // 处理设置按钮点击
    const handleSettings = async () => {
      settingsDialogVisible.value = true
      await loadProductNames()
    }
    
    // 保存设置
    const saveSettings = async () => {
      savingSettings.value = true
      try {
        // 检查自动同步设置是否有变化
        const originalAutoSyncEnabled = globalSettings.getAutoSyncEnabled()
        const hasAutoSyncChanged = autoSyncEnabled.value !== originalAutoSyncEnabled
        
        // 保存自动同步设置
        globalSettings.setAutoSyncEnabled(autoSyncEnabled.value)
        
        // 检查产品名称是否有变化
        const hasFacebookChanged = JSON.stringify(facebookProductNames.value) !== JSON.stringify(originalFacebookProductNames.value)
        const hasGoogleChanged = JSON.stringify(googleProductNames.value) !== JSON.stringify(originalGoogleProductNames.value)
        
        // 判断是否需要刷新数据
        const needsRefresh = hasFacebookChanged || hasGoogleChanged || hasAutoSyncChanged
        
        if (hasFacebookChanged || hasGoogleChanged) {
          // 验证不为空
          if (hasFacebookChanged && facebookProductNames.value.length === 0) {
            ElMessage.warning('Facebook 产品名称列表不能为空')
            savingSettings.value = false
            return
          }
          if (hasGoogleChanged && googleProductNames.value.length === 0) {
            ElMessage.warning('Google 产品名称列表不能为空')
            savingSettings.value = false
            return
          }
          
          // 保存产品名称
          const updateParams = {}
          if (hasFacebookChanged) {
            updateParams.facebookProductNames = facebookProductNames.value
          }
          if (hasGoogleChanged) {
            updateParams.googleProductNames = googleProductNames.value
          }
          
          await settingsAPI.updateProductNames(updateParams)
        }
        
        if (needsRefresh) {
          // 有设置变化，刷新页面数据
          ElMessage({
            message: '设置已保存，正在刷新数据...',
            type: 'success'
          })
          
          // 关闭对话框
          settingsDialogVisible.value = false
          
          // 刷新页面数据
          await loadAllDataParallel()
        } else {
          // 没有任何变化
          ElMessage({
            message: '设置已保存',
            type: 'success'
          })
          
          settingsDialogVisible.value = false
        }
      } catch (error) {
        console.error('保存设置失败:', error)
        ElMessage.error('保存设置失败，请稍后重试')
      } finally {
        savingSettings.value = false
      }
    }
    
    // 取消设置
    const cancelSettings = () => {
      // 恢复为保存的值
      autoSyncEnabled.value = globalSettings.getAutoSyncEnabled()
      facebookProductNames.value = [...originalFacebookProductNames.value]
      googleProductNames.value = [...originalGoogleProductNames.value]
      facebookInputVisible.value = false
      facebookInputValue.value = ''
      googleInputVisible.value = false
      googleInputValue.value = ''
      settingsDialogVisible.value = false
    }
    
    // 初始化时加载设置
    const loadSettings = () => {
      autoSyncEnabled.value = globalSettings.getAutoSyncEnabled()
    }
    
    // 处理账户变更
    const handleAccountChange = async (accountId) => {
      console.log('账户切换至:', accountId)
      // 并行重新加载所有数据（性能优化）
      await loadAllDataParallel()
    }
    
    // 注释掉原有的自动加载逻辑，使用自定义的条件性加载
    
    // 日期变化时加载显示数据（不同于同步数据）
    watch([currentDateRange, compareDateRange], () => {
      loadAllDataParallel()
    }, { deep: true })

    // 根据第一个日期范围筛选框计算日期显示
    const dateRangeDisplay = computed(() => {
      if (!currentDateRange.value || currentDateRange.value.length !== 2) return ''
      
      const startDate = dayjs(currentDateRange.value[0])
      const endDate = dayjs(currentDateRange.value[1])
      
      // 格式化为 MM.DD-MM.DD
      const startFormat = startDate.format('MM.DD')
      const endFormat = endDate.format('MM.DD')
      
      return `${startFormat}-${endFormat}`
    })

    return {
      loading,
      syncing,
      accounts,
      selectedAccount,
      selectedAccountName,
      accountPopoverVisible,
      selectAccount,
      currentDateRange,
      compareDateRange,
      dateRangeDisplay,
      impressionsData,
      purchasesData,
      adSetsData,
      adsDetailData,
      adsPerformanceData,
      adsPerformanceDate,
      impressionsComparisonData,
      overviewLoading,
      adSetsLoading,
      adsDetailLoading,
      adsPerformanceLoading,
      purchasesComparisonData,
      performanceComparisonData,
      handleRefresh,
      handleSync,
      handleSettings,
      handleAccountChange,
      handleAdsPerformanceDateChange,
      settingsDialogVisible,
      savingSettings,
      autoSyncEnabled,
      facebookProductNames,
      facebookInputVisible,
      facebookInputValue,
      FacebookInputRef,
      removeFacebookProductName,
      showFacebookInput,
      handleFacebookInputConfirm,
      googleProductNames,
      googleInputVisible,
      googleInputValue,
      GoogleInputRef,
      removeGoogleProductName,
      showGoogleInput,
      handleGoogleInputConfirm,
      saveSettings,
      cancelSettings,
      ezarcLogo,
    }
  }
}
</script>

<style scoped>
.account-selector-wrapper {
  display: flex;
  align-items: center;
  margin-right: 4px;
}

.account-selector-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  color: #374151;
  min-width: 150px;
}

.account-selector-trigger:hover {
  border-color: #9ca3af;
  background: #f9fafb;
}

.account-icon {
  font-size: 16px;
  color: #374151;
  flex-shrink: 0;
}

.account-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.arrow-icon {
  font-size: 14px;
  color: #6b7280;
  flex-shrink: 0;
}

.account-options {
  display: flex;
  flex-direction: column;
  padding: 4px 0;
}

.account-option {
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
  transition: all 0.15s ease;
}

.account-option:hover {
  background: #f3f4f6;
}

.account-option.active {
  background: #e5e7eb;
  color: #111827;
  font-weight: 500;
}

/* 设置对话框样式 - 简约版 */
.settings-dialog :deep(.el-dialog__header) {
  padding: 24px 28px 20px;
  border-bottom: none;
}

.settings-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.settings-dialog :deep(.el-dialog__body) {
  padding: 0 28px 24px;
}

.settings-dialog :deep(.el-dialog__footer) {
  padding: 16px 28px;
  border-top: 1px solid #f3f4f6;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.setting-item {
  padding: 20px 0;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.setting-title {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.setting-description {
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.5;
}

.setting-divider {
  height: 1px;
  background: #f3f4f6;
}

/* 产品名称管理 */
.product-names-manager {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  min-height: 32px;
}

.product-tag {
  border-radius: 4px;
  font-size: 13px;
  height: 28px;
  padding: 0 10px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  color: #4b5563;
}

.product-tag:hover {
  background: #f3f4f6;
}

.product-input {
  width: 140px;
}

.product-input :deep(.el-input__wrapper) {
  border-radius: 4px;
  box-shadow: 0 0 0 1px #e5e7eb;
}

.product-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #d1d5db;
}

.product-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #2f45ff;
}

.add-product-btn {
  color: #6b7280;
  font-size: 13px;
  padding: 6px 12px;
  height: 28px;
}

.add-product-btn:hover {
  color: #2f45ff;
  background: #f9fafb;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.dialog-footer .el-button {
  min-width: 80px;
}
</style>
