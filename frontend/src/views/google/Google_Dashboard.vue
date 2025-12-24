<template>
  <div>
    <div class="page-title-bar">
      <div class="page-title">
        <img :src="ezarcLogo" alt="EZARC" class="title-logo-img" />
        <span>Google Ads Report {{ dateRangeDisplay }}</span>
      </div>
      <div class="date-controls">
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
    <section id="google-impression-reach-trend" class="section content-section">
      <GoogleImpressionsReachCard 
        :data="impressionsData" 
        :date-range="currentDateRange"
        :loading="overviewLoading"
      />
    </section>

    <section id="google-top-funnel-analyze" class="section content-section">
      <GoogleAnalyzeCardOne 
        :data="impressionsData" 
        :date-range="currentDateRange"
        :compare-date-range="compareDateRange"
        :loading="overviewLoading"
      />
    </section>

    <section id="google-conversions-spend-trend" class="section content-section">
      <GooglePurchasesSpendCard 
        :data="purchasesData" 
        :date-range="currentDateRange"
        :compare-date-range="compareDateRange"
        :loading="overviewLoading"
      />
    </section>

    <section id="google-conversion-cost-analyze" class="section content-section">
      <GoogleAnalyzeCardTwo 
        :data="purchasesData" 
        :date-range="currentDateRange"
        :compare-date-range="compareDateRange"
        :loading="overviewLoading"
      />
    </section>

    <section id="google-campaigns-performance" class="section content-section">
        <GoogleCampaignsPerformanceCard :data="campaignsData" :loading="campaignsLoading" />
    </section>

    <section id="google-ads-performance" class="section content-section">
      <GoogleAdsPerformanceCard 
        :data="adsPerformanceData"
        :date-range="adsPerformanceDate"
        :loading="adsPerformanceLoading"
        @date-change="handleAdsDateChange"
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
import { ref, reactive, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Upload, Setting } from '@element-plus/icons-vue'
import { globalSettings } from '../../utils/globalSettings'
import { settingsAPI } from '../../services/settingsApi'
import GoogleImpressionsReachCard from '../../components/google/Google_Impressions_Reach_Card.vue'
import GoogleAnalyzeCardOne from '../../components/google/Google_Analyze_Card_One.vue'
import GooglePurchasesSpendCard from '../../components/google/Google_Purchases_Spend_Card.vue'
import GoogleAnalyzeCardTwo from '../../components/google/Google_Analyze_Card_Two.vue'
import GoogleCampaignsPerformanceCard from '../../components/google/Google_Campaigns_Performance_Card.vue'
import GoogleAdsPerformanceCard from '../../components/google/Google_Ads_Performance_Card.vue'
import QuickDateRangePicker from '../../components/shared/Quick_Date_Range_Picker.vue'
import SimpleDateRangePicker from '../../components/shared/Simple_Date_Range_Picker.vue'
import { googleDashboardAPI } from '../../services/google/googleApi'
import { useDashboard } from '../../composables/useDashboard'
import ezarcLogo from '@/assets/logos/ezarc-logo.jpg'
import dayjs from 'dayjs'
import {
  transformGoogleCampaignData,
  transformGoogleAdsPerformanceData,
  transformGoogleOverviewSummary
} from '../../utils/dataTransformers'

export default {
  name: 'Google_Dashboard',
  components: {
    GoogleImpressionsReachCard,
    GoogleAnalyzeCardOne,
    GooglePurchasesSpendCard,
    GoogleAnalyzeCardTwo,
    GoogleCampaignsPerformanceCard,
    GoogleAdsPerformanceCard,
    QuickDateRangePicker,
    SimpleDateRangePicker,
    Refresh,
    Upload,
    Setting,
  },
  setup() {
    const {
      loading,
      currentDateRange,
      compareDateRange,
      createEmptyData,
      createEmptyPurchasesData,
      createRefreshHandler
    } = useDashboard(googleDashboardAPI, 'google')
    const adsPerformanceDate = ref(dayjs().subtract(1, 'week').day(1).format('YYYY-MM-DD'))
    const impressionsData = createEmptyData()
    const purchasesData = createEmptyPurchasesData()
    const campaignsData = reactive([])
    const adsPerformanceData = reactive([])
    
    // Overview卡片的loading状态
    const overviewLoading = ref(false)
    // Campaign Performance卡片的loading状态
    const campaignsLoading = ref(false)
    // Ads Performance卡片的loading状态
    const adsPerformanceLoading = ref(false)

    // 加载概览汇总数据（直接从Google Ads API获取）
    const loadOverviewSummaryData = async () => {
      overviewLoading.value = true
      try {
        const params = {
          startDate: currentDateRange.value[0],
          endDate: currentDateRange.value[1],
          compareStartDate: compareDateRange.value?.[0] || null,
          compareEndDate: compareDateRange.value?.[1] || null,
          customer_id: import.meta.env.VITE_GOOGLE_CUSTOMER_ID || '7206000909',
          // 不从前端传代理，交由后端配置环境变量决定
          proxy_url: null
        }
        
        const response = await googleDashboardAPI.getOverviewSummary(params)
        const summaryData = response.data?.summary || {}
        
        // 使用工具函数转换汇总数据
        const transformed = transformGoogleOverviewSummary(summaryData)
        
        // 更新展示数据
        Object.assign(impressionsData, transformed.impressionsData)
        
        // 更新购买数据
        Object.assign(purchasesData, transformed.purchasesData)
        
      } catch (error) {
        console.error('加载概览汇总数据失败:', error)
        ElMessage.error('加载概览汇总数据失败，请检查代理和网络连接')
      } finally {
        overviewLoading.value = false
      }
    }

    // 加载广告系列数据
    const loadCampaignsData = async () => {
      campaignsLoading.value = true
      try {
        const params = {
          startDate1: currentDateRange.value[0],
          endDate1: currentDateRange.value[1],
          startDate2: compareDateRange.value?.[0] || currentDateRange.value[0],
          endDate2: compareDateRange.value?.[1] || currentDateRange.value[1]
        }
        
        const response = await googleDashboardAPI.getCampaignPerformanceOverview(params)
        const rawData = response.data || response || []
        
        // 使用工具函数转换数据
        const transformedData = transformGoogleCampaignData(rawData)
        campaignsData.splice(0, campaignsData.length, ...transformedData)
      } catch (error) {
        console.error('加载广告系列数据失败:', error)
        ElMessage.error('加载广告系列数据失败，请稍后重试')
      } finally {
        campaignsLoading.value = false
      }
    }

    // 加载广告表现数据
    const loadAdsPerformanceData = async (customDate = null) => {
      adsPerformanceLoading.value = true
      try {
        const targetDate = customDate || adsPerformanceDate.value
        const response = await googleDashboardAPI.getAdsPerformanceOverview({ date: targetDate })
        const rawData = response.data || response || []
        
        // 使用工具函数转换数据
        const transformedData = transformGoogleAdsPerformanceData(rawData)
        adsPerformanceData.splice(0, adsPerformanceData.length, ...transformedData)
      } catch (error) {
        console.error('加载广告表现数据失败:', error)
        ElMessage.error('加载广告表现数据失败，请稍后重试')
      } finally {
        adsPerformanceLoading.value = false
      }
    }
    
    // 并行加载所有数据（优化版本，提升速度）
    const loadAllDataParallel = async () => {
      loading.value = true
      overviewLoading.value = true
      
      try {
        // 使用 Promise.allSettled 并行执行所有请求，即使某个失败也不影响其他请求
        const results = await Promise.allSettled([
          loadOverviewSummaryData(),
          loadCampaignsData(),
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

    // 处理广告表现日期变化
    const handleAdsDateChange = (newDate) => {
      if (newDate) {
        adsPerformanceDate.value = newDate
        loadAdsPerformanceData(newDate)
        // 数据加载成功时不显示提示
      }
    }

    const loadFunctions = [loadOverviewSummaryData, loadCampaignsData, loadAdsPerformanceData]
    const handleRefresh = createRefreshHandler(loadFunctions)
    
    // 自定义同步处理（支持对比日期）
    const syncing = ref(false)
    
    // 实际执行同步的内部函数
    const executeGoogleSync = async (showMessage = true) => {
      try {
        if (showMessage) {
          ElMessage({
            message: '正在后台同步 Google Ads 数据...',
            type: 'info',
            duration: 3000
          })
        }
        
        // 并行同步主日期范围和对比日期范围的数据
        const syncPromises = [
          googleDashboardAPI.syncData({
            start_date: currentDateRange.value[0],
            end_date: currentDateRange.value[1]
          })
        ]
        
        // 如果有对比日期范围,添加到并行任务中
        if (compareDateRange.value && compareDateRange.value.length === 2) {
          syncPromises.push(
            googleDashboardAPI.syncData({
              start_date: compareDateRange.value[0],
              end_date: compareDateRange.value[1]
            })
          )
        }
        
        // 等待所有同步任务并行完成
        await Promise.all(syncPromises)
        
        if (showMessage) {
          ElMessage({
            message: 'Google Ads 数据同步完成！',
            type: 'success',
            duration: 3000
          })
        }
        
        // 同步完成后刷新页面数据
        await handleRefresh()
        return true
      } catch (error) {
        console.error('Google Ads 数据同步失败:', error)
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
          '确定要同步 Google Ads 数据吗？这可能需要一些时间。',
          '确认同步',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        syncing.value = true
        ElMessage({
          message: '开始同步 Google Ads 数据，可能需要几分钟，请耐心等待...',
          type: 'info',
          duration: 6000
        })
        
        await executeGoogleSync(true)
      } catch (error) {
        if (error === 'cancel') {
          return
        }
        console.error('Google Ads 数据同步失败:', error)
        ElMessage.error('数据同步失败，请稍后重试')
      } finally {
        syncing.value = false
      }
    }
    
    // 自动同步（不显示确认对话框，静默执行）
    const autoSyncGoogleData = async () => {
      if (syncing.value) {
        console.log('Google Ads 数据正在同步中，跳过本次自动同步')
        return
      }
      
      syncing.value = true
      try {
        await executeGoogleSync(false)
      } finally {
        syncing.value = false
      }
    }
    
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
    
    // 监听设置变化的取消函数
    let unsubscribe = null
    
    // 页面加载时加载设置和条件性自动同步
    onMounted(async () => {
      loadSettings()
      
      // 监听全局设置变化
      unsubscribe = globalSettings.onSettingsChange((newValue) => {
        console.log('Google Dashboard: 检测到全局设置变化', newValue)
        autoSyncEnabled.value = newValue
      })
      
      // 先加载显示数据
      await loadAllDataParallel()
      
      // 根据设置决定是否自动同步
      if (autoSyncEnabled.value) {
        console.log('页面加载，自动同步 Google Ads 数据')
        await autoSyncGoogleData()
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
          console.log('日期变化，自动同步 Google Ads 数据')
          await autoSyncGoogleData()
        } else {
          console.log('自动同步已禁用，跳过日期变化时的自动同步')
        }
      }
    }, { deep: true })
    
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
      currentDateRange,
      compareDateRange,
      dateRangeDisplay,
      adsPerformanceDate,
      impressionsData,
      purchasesData,
      campaignsData,
      adsPerformanceData,
      overviewLoading,
      campaignsLoading,
      adsPerformanceLoading,
      handleRefresh,
      handleSync,
      handleSettings,
      handleAdsDateChange,
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
