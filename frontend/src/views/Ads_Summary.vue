<template>
  <div>
    <div class="page-title-bar">
      <div class="page-title">
        <img :src="ezarcLogo" alt="EZARC" class="title-logo-img" />
        <span>Ads Summary Report {{ dateRangeDisplay }}</span>
      </div>
      <div class="date-controls">
        <SingleDatePicker
          v-model="sharedDateString"
          placeholder="Select date"
          @update:modelValue="handleDateChange"
        />
        <div class="action-buttons">
          <button class="icon-button" @click="handleRefresh" :disabled="loading" title="刷新">
            <el-icon><Refresh /></el-icon>
          </button>
          <button class="icon-button" @click="toggleFullscreen" title="全屏显示">
            <el-icon><Monitor /></el-icon>
          </button>
          <button class="icon-button" @click="handleSettings" title="设置">
            <el-icon><Setting /></el-icon>
          </button>
        </div>
      </div>
    </div>

    <div class="dashboard-container">
      <!-- 骨架屏加载状态 -->
      <SkeletonLoading 
        v-if="facebookLoading && googleLoading && summaryLoading" 
        :cardCount="3" 
        :rowsPerCard="6"
        :columnsPerRow="4"
      />
      
      <!-- 数据加载完成后显示 -->
      <template v-else>
        <!-- Facebook Ads Performance Overview - Dual Account -->
        <section id="facebook-ads-performance" class="section content-section">
          <FacebookAdsDualAccountCard 
            :account1Data="facebookAdsPerformanceAccount1Data"
            :account2Data="facebookAdsPerformanceAccount2Data"
            :dateRange="sharedDateString"
            :loading="facebookLoading"
            title="Facebook Ads Performance Overview"
            :show-date-picker="false"
          />
        </section>

        <!-- Google Ads Performance Overview -->
        <section id="google-ads-performance" class="section content-section">
          <GoogleAdsPerformanceCard 
            :data="googleAdsPerformanceData"
            :dateRange="sharedDateString"
            :loading="googleLoading"
            title="Google Ads Performance Overview"
            :show-date-picker="false"
          />
        </section>

        <!-- Summary Ads Performance Overview -->
        <section id="summary-ads-performance" class="section content-section">
          <SummaryAdsPerformanceCard 
            :facebookAccount1Data="facebookAdsPerformanceAccount1Data"
            :facebookAccount2Data="facebookAdsPerformanceAccount2Data"
            :googleData="googleAdsPerformanceData"
            :lingxingData="lingxingData"
            :lingxingMonthlyCost="lingxingMonthlyCost"
            :salesTargetData="salesTargetData"
            :facebookSummaryData="facebookSummaryData"
            :googleSummaryData="googleSummaryData"
            :dateRange="sharedDateString"
            :loading="summaryLoading"
            title="Summary Ads Performance Overview"
            @update-success="handleSalesTargetUpdate"
          />
        </section>
      </template>
    </div>

    <!-- 全屏显示容器 -->
    <div v-if="fullscreenDialogVisible" class="fullscreen-overlay">
      <div class="fullscreen-container">
        <!-- 关闭按钮 -->
        <button class="close-fullscreen-btn" @click="fullscreenDialogVisible = false" title="关闭">
          <el-icon><Close /></el-icon>
        </button>
        
        <div class="fullscreen-content">
          <!-- Facebook Ads Performance Overview -->
          <section class="dialog-section">
            <FacebookAdsDualAccountCard 
              :account1Data="facebookAdsPerformanceAccount1Data"
              :account2Data="facebookAdsPerformanceAccount2Data"
              :dateRange="sharedDateString"
              :loading="facebookLoading"
              title="Facebook Ads Performance Overview"
              :show-date-picker="false"
            />
          </section>

          <!-- Google Ads Performance Overview -->
          <section class="dialog-section">
            <GoogleAdsPerformanceCard 
              :data="googleAdsPerformanceData"
              :dateRange="sharedDateString"
              :loading="googleLoading"
              title="Google Ads Performance Overview"
              :show-date-picker="false"
            />
          </section>

          <!-- Summary Ads Performance Overview -->
          <section class="dialog-section">
          <SummaryAdsPerformanceCard 
            :facebookAccount1Data="facebookAdsPerformanceAccount1Data"
            :facebookAccount2Data="facebookAdsPerformanceAccount2Data"
            :googleData="googleAdsPerformanceData"
            :lingxingData="lingxingData"
            :lingxingMonthlyCost="lingxingMonthlyCost"
            :salesTargetData="salesTargetData"
            :facebookSummaryData="facebookSummaryData"
            :googleSummaryData="googleSummaryData"
            :dateRange="sharedDateString"
            :loading="summaryLoading"
            title="Summary Ads Performance Overview"
            @update-success="handleSalesTargetUpdate"
          />
          </section>
        </div>
      </div>
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
import { ref, computed, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Refresh, Monitor, Close, Setting } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { settingsAPI } from '../services/settingsApi'
import { globalSettings } from '../utils/globalSettings'
import FacebookAdsDualAccountCard from '../components/facebook/Facebook_Ads_Dual_Account_Card.vue'
import GoogleAdsPerformanceCard from '../components/google/Google_Ads_Performance_Card.vue'
import SummaryAdsPerformanceCard from '../components/summary/Summary_Ads_Performance_Card.vue'
import SingleDatePicker from '../components/shared/Single_Date_Picker.vue'
import SkeletonLoading from '../components/shared/Skeleton_Loading.vue'
import { formatCurrency, formatDecimal } from '@/utils/formatters'
import { facebookDashboardAPI } from '../services/facebook/facebookApi'
import { googleDashboardAPI } from '../services/google/googleApi'
import { lingxingAPI } from '../services/lingxing/lingxingApi'
import { summaryAPI } from '../services/summary/summaryApi'
import { transformGoogleAdsPerformanceData } from '../utils/dataTransformers'
import { cacheManager } from '../utils/cache'
import ezarcLogo from '@/assets/logos/ezarc-logo.jpg'
import dayjs from 'dayjs'

export default {
  name: 'Ads_Summary',
  components: {
    FacebookAdsDualAccountCard,
    GoogleAdsPerformanceCard,
    SummaryAdsPerformanceCard,
    SingleDatePicker,
    SkeletonLoading,
    Refresh,
    Monitor,
    Close,
    Setting,
  },
  setup() {
    const loading = ref(false)
    const facebookLoading = ref(false)  // Facebook 卡片的加载状态
    const googleLoading = ref(false)  // Google 卡片的加载状态
    const summaryLoading = ref(false)  // Summary 卡片的加载状态
    const fullscreenDialogVisible = ref(false)
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
    
    // 共享的日期（默认为上周一）- 同时控制 Facebook 和 Google Ads Performance
    const sharedDateString = ref(dayjs().subtract(1, 'week').day(1).format('YYYY-MM-DD'))
    const facebookAdsPerformanceAccount1Data = reactive([])
    const facebookAdsPerformanceAccount2Data = reactive([])
    const googleAdsPerformanceData = reactive([])
    const lingxingData = ref({
      conversions: { thisWeek: 0, lastWeek: 0 },
      conversionValue: { thisWeek: 0, lastWeek: 0 }
    })
    // 月度花费数据
    const lingxingMonthlyCost = ref({
      cost: { thisWeek: 0, lastWeek: 0 }
    })
    // 销售目标数据
    const salesTargetData = ref({
      conversionValue: { thisWeek: 0, lastWeek: 0 }
    })
    // Facebook 汇总数据（用于Summary表格的Facebook广告行）
    const facebookSummaryData = ref({
      conversions: { thisWeek: 0, lastWeek: 0 },
      conversionValue: { thisWeek: 0, lastWeek: 0 },
      cost: { thisWeek: 0, lastWeek: 0 },
      roas: { thisWeek: 0, lastWeek: 0 }
    })
    // Google 汇总数据（用于Summary表格的Google广告行）
    const googleSummaryData = ref({
      conversions: { thisWeek: 0, lastWeek: 0 },
      conversionValue: { thisWeek: 0, lastWeek: 0 },
      cost: { thisWeek: 0, lastWeek: 0 },
      roas: { thisWeek: 0, lastWeek: 0 }
    })

    // 加载 Facebook Ads Performance 数据（从数据库获取，分别请求两个账户）
    const loadFacebookAdsPerformanceData = async (date = null) => {
      facebookLoading.value = true
      try {
        const targetDate = date || sharedDateString.value
        
        // 两个Facebook账户ID
        const account1Id = '2613027225660900'  // EZARCADS-1
        const account2Id = '1069516980635624'  // EZARCADS-2
        
        // 并行请求两个账户的数据
        const [account1Response, account2Response] = await Promise.all([
          facebookDashboardAPI.getAdsPerformanceOverview({
            date: targetDate,
            accountId: account1Id
          }),
          facebookDashboardAPI.getAdsPerformanceOverview({
            date: targetDate,
            accountId: account2Id
          })
        ])
        
        const account1RawData = account1Response.data || account1Response || []
        const account2RawData = account2Response.data || account2Response || []
        
        // 转换账户1的数据
        const account1Data = account1RawData.map(item => ({
          product: item.campaign_name,
          conversions: {
            thisWeek: item.current_purchases,
            lastWeek: item.last_purchases
          },
          conversionValue: {
            thisWeek: item.current_purchases_value,
            lastWeek: item.last_purchases_value
          },
          cost: {
            thisWeek: item.current_spend,
            lastWeek: item.last_spend
          },
          roas: {
            thisWeek: item.current_roas,
            lastWeek: item.last_roas
          }
        }))
        
        // 转换账户2的数据
        const account2Data = account2RawData.map(item => ({
          product: item.campaign_name,
          conversions: {
            thisWeek: item.current_purchases,
            lastWeek: item.last_purchases
          },
          conversionValue: {
            thisWeek: item.current_purchases_value,
            lastWeek: item.last_purchases_value
          },
          cost: {
            thisWeek: item.current_spend,
            lastWeek: item.last_spend
          },
          roas: {
            thisWeek: item.current_roas,
            lastWeek: item.last_roas
          }
        }))
        
        facebookAdsPerformanceAccount1Data.splice(0, facebookAdsPerformanceAccount1Data.length, ...account1Data)
        facebookAdsPerformanceAccount2Data.splice(0, facebookAdsPerformanceAccount2Data.length, ...account2Data)
      } catch (error) {
        console.error('加载 Facebook Ads Performance 数据失败:', error)
        ElMessage.error('加载 Facebook Ads Performance 数据失败，请稍后重试')
      } finally {
        facebookLoading.value = false
      }
    }

    // 加载 Google Ads Performance 数据
    const loadGoogleAdsPerformanceData = async (date = null) => {
      googleLoading.value = true
      try {
        const targetDate = date || sharedDateString.value
        const response = await googleDashboardAPI.getAdsPerformanceOverview({ date: targetDate })
        const rawData = response.data || response || []
        
        // 使用工具函数转换数据
        const transformedData = transformGoogleAdsPerformanceData(rawData)
        googleAdsPerformanceData.splice(0, googleAdsPerformanceData.length, ...transformedData)
      } catch (error) {
        console.error('加载 Google Ads Performance 数据失败:', error)
        ElMessage.error('加载 Google Ads Performance 数据失败，请稍后重试')
      } finally {
        googleLoading.value = false
      }
    }

    // 加载 Lingxing 独立站月度数据
    const loadLingxingData = async (date = null) => {
      try {
        const targetDate = date || sharedDateString.value
        const response = await lingxingAPI.getWebsiteMonthlySimulation({ date: targetDate })
        const data = response.data || response || {}
        
        // 注意：虽然字段名仍是 thisWeek/lastWeek，但实际数据已经是月度数据
        lingxingData.value = {
          conversions: data.conversions || { thisWeek: 0, lastWeek: 0 },
          conversionValue: data.conversionValue || { thisWeek: 0, lastWeek: 0 }
        }
      } catch (error) {
        console.error('加载独立站月度数据失败:', error)
        ElMessage.error('加载独立站月度数据失败，请稍后重试')
      }
    }

    // 加载 Lingxing 独立站月度花费数据
    const loadLingxingMonthlyCost = async (date = null) => {
      try {
        const targetDate = date || sharedDateString.value
        const response = await lingxingAPI.getMonthlyCost({ date: targetDate })
        const data = response.data || response || {}
        
        lingxingMonthlyCost.value = {
          cost: data.cost || { thisWeek: 0, lastWeek: 0 }
        }
      } catch (error) {
        console.error('加载独立站月度花费数据失败:', error)
        ElMessage.error('加载独立站月度花费数据失败，请稍后重试')
      }
    }

    // 加载销售目标数据
    const loadSalesTarget = async (date = null) => {
      try {
        const targetDate = date || sharedDateString.value
        const response = await lingxingAPI.getSalesTarget({ date: targetDate })
        const data = response.data || response || {}
        
        salesTargetData.value = {
          conversionValue: data.conversionValue || { thisWeek: 0, lastWeek: 0 }
        }
      } catch (error) {
        console.error('加载销售目标数据失败:', error)
        ElMessage.error('加载销售目标数据失败，请稍后重试')
      }
    }

    // 计算周的起止日期
    const getWeekRange = (dateString) => {
      const date = dayjs(dateString)
      // 计算该周的周一
      const monday = date.day() === 0 ? date.subtract(6, 'day') : date.day(1)
      // 计算该周的周日
      const sunday = monday.add(6, 'day')
      return {
        start: monday.format('YYYY-MM-DD'),
        end: sunday.format('YYYY-MM-DD')
      }
    }

    // 加载 Facebook 汇总数据（用于Summary表格的Facebook广告行）
    const loadFacebookSummaryData = async (date = null) => {
      try {
        const targetDate = date || sharedDateString.value
        
        // 计算本周的起止日期
        const thisWeek = getWeekRange(targetDate)
        // 计算上周的起止日期
        const lastWeekStart = dayjs(thisWeek.start).subtract(7, 'day').format('YYYY-MM-DD')
        const lastWeekEnd = dayjs(thisWeek.end).subtract(7, 'day').format('YYYY-MM-DD')
        
        console.log('加载 Facebook 汇总数据:')
        console.log('本周:', thisWeek.start, '到', thisWeek.end)
        console.log('上周:', lastWeekStart, '到', lastWeekEnd)
        
        // 两个Facebook账户ID
        const account1Id = '2613027225660900'  // EZARCADS-1
        const account2Id = '1069516980635624'  // EZARCADS-2
        
        // 并行请求两个账户的两周数据（共4个请求）
        const [
          account1ThisWeekResponse,
          account1LastWeekResponse,
          account2ThisWeekResponse,
          account2LastWeekResponse
        ] = await Promise.all([
          // 账户1 - 本周
          facebookDashboardAPI.getOverviewDataFromAPI({
            startDate: thisWeek.start,
            endDate: thisWeek.end,
            accountId: account1Id
          }),
          // 账户1 - 上周
          facebookDashboardAPI.getOverviewDataFromAPI({
            startDate: lastWeekStart,
            endDate: lastWeekEnd,
            accountId: account1Id
          }),
          // 账户2 - 本周
          facebookDashboardAPI.getOverviewDataFromAPI({
            startDate: thisWeek.start,
            endDate: thisWeek.end,
            accountId: account2Id
          }),
          // 账户2 - 上周
          facebookDashboardAPI.getOverviewDataFromAPI({
            startDate: lastWeekStart,
            endDate: lastWeekEnd,
            accountId: account2Id
          })
        ])
        
        // 提取各个账户的数据
        const account1ThisWeek = (account1ThisWeekResponse.data || account1ThisWeekResponse || {}).purchases || {}
        const account1LastWeek = (account1LastWeekResponse.data || account1LastWeekResponse || {}).purchases || {}
        const account2ThisWeek = (account2ThisWeekResponse.data || account2ThisWeekResponse || {}).purchases || {}
        const account2LastWeek = (account2LastWeekResponse.data || account2LastWeekResponse || {}).purchases || {}
        
        console.log('账户1本周:', account1ThisWeek)
        console.log('账户1上周:', account1LastWeek)
        console.log('账户2本周:', account2ThisWeek)
        console.log('账户2上周:', account2LastWeek)
        
        // 汇总两个账户的数据
        const thisWeekPurchases = (account1ThisWeek.purchases || 0) + (account2ThisWeek.purchases || 0)
        const lastWeekPurchases = (account1LastWeek.purchases || 0) + (account2LastWeek.purchases || 0)
        
        const thisWeekPurchasesValue = (account1ThisWeek.purchasesValue || 0) + (account2ThisWeek.purchasesValue || 0)
        const lastWeekPurchasesValue = (account1LastWeek.purchasesValue || 0) + (account2LastWeek.purchasesValue || 0)
        
        const thisWeekSpend = (account1ThisWeek.spend || 0) + (account2ThisWeek.spend || 0)
        const lastWeekSpend = (account1LastWeek.spend || 0) + (account2LastWeek.spend || 0)
        
        // 计算汇总ROAS
        const thisWeekRoas = thisWeekSpend > 0 ? thisWeekPurchasesValue / thisWeekSpend : 0
        const lastWeekRoas = lastWeekSpend > 0 ? lastWeekPurchasesValue / lastWeekSpend : 0
        
        // 更新汇总数据
        facebookSummaryData.value = {
          conversions: {
            thisWeek: thisWeekPurchases,
            lastWeek: lastWeekPurchases
          },
          conversionValue: {
            thisWeek: thisWeekPurchasesValue,
            lastWeek: lastWeekPurchasesValue
          },
          cost: {
            thisWeek: thisWeekSpend,
            lastWeek: lastWeekSpend
          },
          roas: {
            thisWeek: thisWeekRoas,
            lastWeek: lastWeekRoas
          }
        }
        
        console.log('Facebook 汇总数据加载完成:', facebookSummaryData.value)
      } catch (error) {
        console.error('加载 Facebook 汇总数据失败:', error)
        ElMessage.error('加载 Facebook 汇总数据失败，请稍后重试')
      }
    }

    // 加载 Google 汇总数据（用于Summary表格的Google广告行）
    const loadGoogleSummaryData = async (date = null) => {
      try {
        const targetDate = date || sharedDateString.value
        
        // 计算本周的起止日期
        const thisWeek = getWeekRange(targetDate)
        // 计算上周的起止日期
        const lastWeekStart = dayjs(thisWeek.start).subtract(7, 'day').format('YYYY-MM-DD')
        const lastWeekEnd = dayjs(thisWeek.end).subtract(7, 'day').format('YYYY-MM-DD')
        
        console.log('加载 Google 汇总数据:')
        console.log('本周:', thisWeek.start, '到', thisWeek.end)
        console.log('上周:', lastWeekStart, '到', lastWeekEnd)
        
        // 并行请求本周和上周的数据
        const [thisWeekResponse, lastWeekResponse] = await Promise.all([
          // 本周数据
          googleDashboardAPI.getOverviewSummary({
            startDate: thisWeek.start,
            endDate: thisWeek.end
          }),
          // 上周数据
          googleDashboardAPI.getOverviewSummary({
            startDate: lastWeekStart,
            endDate: lastWeekEnd
          })
        ])
        
        // 提取数据
        const thisWeekData = (thisWeekResponse.data || thisWeekResponse || {}).summary || {}
        const lastWeekData = (lastWeekResponse.data || lastWeekResponse || {}).summary || {}
        
        console.log('Google本周数据:', thisWeekData)
        console.log('Google上周数据:', lastWeekData)
        
        // 提取关键指标
        const thisWeekConversions = thisWeekData.conversions || 0
        const lastWeekConversions = lastWeekData.conversions || 0
        
        const thisWeekConversionValue = thisWeekData.conversions_value || 0
        const lastWeekConversionValue = lastWeekData.conversions_value || 0
        
        const thisWeekCost = thisWeekData.cost || 0
        const lastWeekCost = lastWeekData.cost || 0
        
        // 计算 ROAS
        const thisWeekRoas = thisWeekCost > 0 ? thisWeekConversionValue / thisWeekCost : 0
        const lastWeekRoas = lastWeekCost > 0 ? lastWeekConversionValue / lastWeekCost : 0
        
        // 更新汇总数据
        googleSummaryData.value = {
          conversions: {
            thisWeek: thisWeekConversions,
            lastWeek: lastWeekConversions
          },
          conversionValue: {
            thisWeek: thisWeekConversionValue,
            lastWeek: lastWeekConversionValue
          },
          cost: {
            thisWeek: thisWeekCost,
            lastWeek: lastWeekCost
          },
          roas: {
            thisWeek: thisWeekRoas,
            lastWeek: lastWeekRoas
          }
        }
        
        console.log('Google 汇总数据加载完成:', googleSummaryData.value)
      } catch (error) {
        console.error('加载 Google 汇总数据失败:', error)
        ElMessage.error('加载 Google 汇总数据失败，请稍后重试')
      }
    }

    // 🚀 【新增】批量加载所有数据 - 使用后端批量 API（推荐）
    const loadAllDataBatch = async (date = null, useCache = true) => {
      const targetDate = date || sharedDateString.value
      
      // Facebook 账户 ID
      const account1Id = '2613027225660900'  // EZARCADS-1
      const account2Id = '1069516980635624'  // EZARCADS-2
      
      // 计算本周和上周的日期范围
      const thisWeek = getWeekRange(targetDate)
      const lastWeekStart = dayjs(thisWeek.start).subtract(7, 'day').format('YYYY-MM-DD')
      const lastWeekEnd = dayjs(thisWeek.end).subtract(7, 'day').format('YYYY-MM-DD')
      
      // 生成缓存键
      const cacheKey = cacheManager.generateKey('summary:all-data', {
        date: targetDate,
        thisWeekStart: thisWeek.start,
        thisWeekEnd: thisWeek.end,
        lastWeekStart,
        lastWeekEnd
      })
      
      // 尝试从缓存获取
      if (useCache) {
        const cachedData = cacheManager.get(cacheKey)
        if (cachedData) {
          console.log('📦 使用缓存数据，跳过 API 请求')
          applyBatchDataToState(cachedData)
          // 即使命中缓存，也需要加载 Lingxing 数据（独立站月度模拟与销售目标）
          // 否则切换路由返回时这两项会保持默认 0 值
          try {
            await Promise.all([
              loadLingxingData(targetDate),
              loadLingxingMonthlyCost(targetDate),
              loadSalesTarget(targetDate)
            ])
          } catch (err) {
            console.warn('加载 Lingxing 或 SalesTarget 数据时出错（缓存命中路径）:', err)
          }
          return
        }
      }
      
      // 设置所有加载状态
      facebookLoading.value = true
      googleLoading.value = true
      summaryLoading.value = true
      
      try {
        console.log('🚀 发起批量 API 请求...')
        const startTime = Date.now()
        
        // 调用批量 API
        const response = await summaryAPI.getAllSummaryData({
          account_ids: [account1Id, account2Id],
          this_week_start: thisWeek.start,
          this_week_end: thisWeek.end,
          last_week_start: lastWeekStart,
          last_week_end: lastWeekEnd
        })
        
        const endTime = Date.now()
        console.log(`✅ 批量 API 请求完成，耗时: ${endTime - startTime}ms`)
        
        const data = response.data || response
        
        // 存入缓存（5 分钟 TTL）
        cacheManager.set(cacheKey, data, 300)
        
        // 应用数据到状态
        applyBatchDataToState(data)
        
        // 同时加载 Lingxing 数据（独立的数据源）
        await Promise.all([
          loadLingxingData(targetDate),
          loadLingxingMonthlyCost(targetDate),
          loadSalesTarget(targetDate)
        ])
        
      } catch (error) {
        console.error('❌ 批量 API 请求失败，降级到独立请求:', error)
        ElMessage.warning('使用备用方式加载数据...')
        
        // 降级策略：使用原有的独立请求方式
        await loadAllDataFallback(targetDate)
      } finally {
        facebookLoading.value = false
        googleLoading.value = false
        summaryLoading.value = false
      }
    }
    
    // 应用批量 API 数据到组件状态
    const applyBatchDataToState = (data) => {
      const facebookData = data.facebook || {}
      const googleData = data.google || {}
      
      // 处理 Facebook 数据
      const account1Id = '2613027225660900'
      const account2Id = '1069516980635624'
      
      const account1 = facebookData[account1Id] || {}
      const account2 = facebookData[account2Id] || {}
      
      // 更新 Facebook 汇总数据
      const account1ThisWeek = account1.this_week || {}
      const account1LastWeek = account1.last_week || {}
      const account2ThisWeek = account2.this_week || {}
      const account2LastWeek = account2.last_week || {}
      
      const thisWeekPurchases = (account1ThisWeek.purchases || 0) + (account2ThisWeek.purchases || 0)
      const lastWeekPurchases = (account1LastWeek.purchases || 0) + (account2LastWeek.purchases || 0)
      
      const thisWeekPurchasesValue = (account1ThisWeek.purchasesValue || 0) + (account2ThisWeek.purchasesValue || 0)
      const lastWeekPurchasesValue = (account1LastWeek.purchasesValue || 0) + (account2LastWeek.purchasesValue || 0)
      
      const thisWeekSpend = (account1ThisWeek.spend || 0) + (account2ThisWeek.spend || 0)
      const lastWeekSpend = (account1LastWeek.spend || 0) + (account2LastWeek.spend || 0)
      
      const thisWeekRoas = thisWeekSpend > 0 ? thisWeekPurchasesValue / thisWeekSpend : 0
      const lastWeekRoas = lastWeekSpend > 0 ? lastWeekPurchasesValue / lastWeekSpend : 0
      
      facebookSummaryData.value = {
        conversions: { thisWeek: thisWeekPurchases, lastWeek: lastWeekPurchases },
        conversionValue: { thisWeek: thisWeekPurchasesValue, lastWeek: lastWeekPurchasesValue },
        cost: { thisWeek: thisWeekSpend, lastWeek: lastWeekSpend },
        roas: { thisWeek: thisWeekRoas, lastWeek: lastWeekRoas }
      }
      
      // 处理 Google 数据
      const googleThisWeek = googleData.this_week || {}
      const googleLastWeek = googleData.last_week || {}
      
      const googleThisWeekConversions = googleThisWeek.conversions || 0
      const googleLastWeekConversions = googleLastWeek.conversions || 0
      
      const googleThisWeekConversionValue = googleThisWeek.conversions_value || 0
      const googleLastWeekConversionValue = googleLastWeek.conversions_value || 0
      
      const googleThisWeekCost = googleThisWeek.cost || 0
      const googleLastWeekCost = googleLastWeek.cost || 0
      
      const googleThisWeekRoas = googleThisWeekCost > 0 ? googleThisWeekConversionValue / googleThisWeekCost : 0
      const googleLastWeekRoas = googleLastWeekCost > 0 ? googleLastWeekConversionValue / googleLastWeekCost : 0
      
      googleSummaryData.value = {
        conversions: { thisWeek: googleThisWeekConversions, lastWeek: googleLastWeekConversions },
        conversionValue: { thisWeek: googleThisWeekConversionValue, lastWeek: googleLastWeekConversionValue },
        cost: { thisWeek: googleThisWeekCost, lastWeek: googleLastWeekCost },
        roas: { thisWeek: googleThisWeekRoas, lastWeek: googleLastWeekRoas }
      }
      
      console.log('✅ 批量数据已应用到组件状态')
    }
    
    // 降级方案：使用独立请求加载数据
    const loadAllDataFallback = async (date = null) => {
      await Promise.all([
        loadFacebookAdsPerformanceData(date),
        loadGoogleAdsPerformanceData(date),
        loadAllSummaryData(date)
      ])
    }

    // 加载所有汇总数据（Facebook + Google + Lingxing）- 保留作为降级方案
    const loadAllSummaryData = async (date = null) => {
      summaryLoading.value = true
      try {
        await Promise.all([
          loadFacebookSummaryData(date),
          loadGoogleSummaryData(date),
          loadLingxingData(date),
          loadLingxingMonthlyCost(date),
          loadSalesTarget(date)
        ])
      } catch (error) {
        console.error('加载汇总数据失败:', error)
      } finally {
        summaryLoading.value = false
      }
    }

    // 统一的日期变更处理 - 使用批量 API
    const handleDateChange = async (newDate) => {
      sharedDateString.value = newDate
      // 日期变化时，根据设置决定是否自动同步
      if (autoSyncEnabled.value) {
        console.log('日期变化，自动同步并刷新数据')
        loading.value = true
        facebookLoading.value = true
        googleLoading.value = true
        summaryLoading.value = true
        // 先同步数据（并发执行本周和上周）
        try {
          await syncWeeklyData(newDate, { silent: true })
          await Promise.all([
            loadAllDataBatch(newDate, false),
            loadFacebookAdsPerformanceData(newDate),
            loadGoogleAdsPerformanceData(newDate)
          ])
        } catch (error) {
          console.error('自动同步刷新数据失败:', error)
        } finally {
          loading.value = false
          facebookLoading.value = false
          googleLoading.value = false
          summaryLoading.value = false
        }
      } else {
        console.log('自动同步已禁用，使用缓存数据')
        // 使用缓存
        loadAllDataBatch(newDate, true)
        loadFacebookAdsPerformanceData(newDate)
        loadGoogleAdsPerformanceData(newDate)
      }
    }

    // 根据选择的日期计算周期范围显示
    const dateRangeDisplay = computed(() => {
      if (!sharedDateString.value) return ''
      
      const selectedDate = dayjs(sharedDateString.value)
      // 计算该周的周一（day(1)）
      const monday = selectedDate.day(1)
      // 计算该周的周日（day(0) 表示周日，需要加7天到下周日）
      const sunday = monday.add(6, 'day')
      
      // 格式化为 MM.DD-MM.DD
      const startFormat = monday.format('MM.DD')
      const endFormat = sunday.format('MM.DD')
      
      return `${startFormat}-${endFormat}`
    })

    const handleRefresh = async () => {
      // 清除相关缓存，强制刷新（summary + lingxing）
      cacheManager.clearPattern('summary:*')
      cacheManager.clearPattern('lingxing:*')
      // 进入加载状态
      loading.value = true
      facebookLoading.value = true
      googleLoading.value = true
      summaryLoading.value = true

      try {
        // 并发重新加载所有数据（禁用缓存）
        await Promise.all([
          loadAllDataBatch(null, false),
          loadFacebookAdsPerformanceData(),
          loadGoogleAdsPerformanceData(),
          // 确保独立站相关数据也被刷新
          loadLingxingData(null),
          loadLingxingMonthlyCost(null),
          loadSalesTarget(null)
        ])
      } catch (error) {
        console.error('手动刷新失败:', error)
      } finally {
        // 结束加载状态
        loading.value = false
        facebookLoading.value = false
        googleLoading.value = false
        summaryLoading.value = false
      }
    }
    
    // 同步本周和上周的数据（并发执行）
    const syncWeeklyData = async (date = null, options = {}) => {
      const { silent = false } = options
      const targetDate = date || sharedDateString.value
      
      // Facebook 账户 ID
      const account1Id = '2613027225660900'  // EZARCADS-1
      const account2Id = '1069516980635624'  // EZARCADS-2
      
      // 计算本周和上周的日期范围
      const thisWeek = getWeekRange(targetDate)
      const lastWeekStart = dayjs(thisWeek.start).subtract(7, 'day').format('YYYY-MM-DD')
      const lastWeekEnd = dayjs(thisWeek.end).subtract(7, 'day').format('YYYY-MM-DD')
      
      console.log('🔄 开始同步周数据:')
      console.log('本周:', thisWeek.start, '到', thisWeek.end)
      console.log('上周:', lastWeekStart, '到', lastWeekEnd)
      
      try {
        if (!silent) {
          ElMessage({
            message: '正在后台同步数据...',
            type: 'info',
            duration: 3000
          })
        }
        
        // 并发同步所有数据
        // Facebook: 2个账户 x 2个周期 = 4个请求
        // Google: 2个周期 = 2个请求
        // 总共 6 个并发请求
        const syncPromises = [
          // Facebook 账户1 - 本周
          facebookDashboardAPI.syncData({
            start_date: thisWeek.start,
            end_date: thisWeek.end,
            ad_account_id: account1Id,
            status_filter: 'ACTIVE'
          }),
          // Facebook 账户1 - 上周
          facebookDashboardAPI.syncData({
            start_date: lastWeekStart,
            end_date: lastWeekEnd,
            ad_account_id: account1Id,
            status_filter: 'ACTIVE'
          }),
          // Facebook 账户2 - 本周
          facebookDashboardAPI.syncData({
            start_date: thisWeek.start,
            end_date: thisWeek.end,
            ad_account_id: account2Id,
            status_filter: 'ACTIVE'
          }),
          // Facebook 账户2 - 上周
          facebookDashboardAPI.syncData({
            start_date: lastWeekStart,
            end_date: lastWeekEnd,
            ad_account_id: account2Id,
            status_filter: 'ACTIVE'
          }),
          // Google Ads - 本周
          googleDashboardAPI.syncData({
            start_date: thisWeek.start,
            end_date: thisWeek.end
          }),
          // Google Ads - 上周
          googleDashboardAPI.syncData({
            start_date: lastWeekStart,
            end_date: lastWeekEnd
          })
        ]
        
        // 并发执行所有同步任务
        await Promise.all(syncPromises)
        
        console.log('✅ 所有周数据同步完成')
        if (!silent) {
          ElMessage({
            message: '数据同步完成！',
            type: 'success',
            duration: 3000
          })
        }
        
        return true
      } catch (error) {
        console.error('❌ 数据同步失败:', error)
        ElMessage.error('数据同步失败，请稍后重试')
        return false
      }
    }

    // 打开全屏显示对话框
    const toggleFullscreen = () => {
      fullscreenDialogVisible.value = true
    }

    // 处理设置按钮点击
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
          // 关闭对话框
          settingsDialogVisible.value = false
          
          // 如果开启了自动同步，先同步数据再刷新
          if (autoSyncEnabled.value && hasAutoSyncChanged) {
            ElMessage({
              message: '设置已保存，正在同步并刷新数据...',
              type: 'success'
            })
            
            // 先同步数据（并发执行本周和上周）
            const syncSuccess = await syncWeeklyData(null, { silent: autoSyncEnabled.value })
            
            // 同步完成后刷新页面数据
            if (syncSuccess) {
              await loadAllDataBatch(null, false)  // 不使用缓存，强制重新加载
            }
          } else {
            // 只是修改了产品名称或关闭了自动同步，直接刷新数据
            ElMessage({
              message: '设置已保存，正在刷新数据...',
              type: 'success'
            })
            
            // 刷新页面数据
            await loadAllDataBatch(null, false)  // 不使用缓存，强制重新加载
          }
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

    // 处理销售目标更新成功
    const handleSalesTargetUpdate = async () => {
      console.log('销售目标已更新，重新加载数据...')
      // 重新加载销售目标数据
      await loadSalesTarget(sharedDateString.value)
    }

    // 监听全屏状态，控制body滚动
    watch(fullscreenDialogVisible, (newVal) => {
      if (newVal) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    })

    // 监听设置变化的取消函数
    let unsubscribe = null
    
    // 组件挂载时加载数据 - 使用批量 API
    onMounted(async () => {
      // 加载设置
      loadSettings()
      
      // 监听全局设置变化
      unsubscribe = globalSettings.onSettingsChange((newValue) => {
        console.log('Ads Summary: 检测到全局设置变化', newValue)
        autoSyncEnabled.value = newValue
      })
      
      // 根据设置决定是否自动同步
      if (autoSyncEnabled.value) {
        console.log('页面加载，自动同步并刷新数据')
        loading.value = true
        facebookLoading.value = true
        googleLoading.value = true
        summaryLoading.value = true
        try {
          // 先同步数据（并发执行本周和上周）
          await syncWeeklyData(null, { silent: true })
          // 同步完成后刷新数据（禁用缓存，强制刷新）
          await Promise.all([
            loadAllDataBatch(null, false),
            loadFacebookAdsPerformanceData(),
            loadGoogleAdsPerformanceData()
          ])
        } catch (error) {
          console.error('自动同步加载页面数据失败:', error)
        } finally {
          loading.value = false
          facebookLoading.value = false
          googleLoading.value = false
          summaryLoading.value = false
        }
      } else {
        console.log('自动同步已禁用，使用缓存数据')
        // 使用缓存
        loadAllDataBatch(null, true)
        loadFacebookAdsPerformanceData()
        loadGoogleAdsPerformanceData()
      }
    })
    
    // 页面卸载时取消监听
    onUnmounted(() => {
      if (unsubscribe) {
        unsubscribe()
      }
    })

    return {
      loading,
      facebookLoading,  // Facebook 卡片加载状态
      googleLoading,  // Google 卡片加载状态
      summaryLoading,  // Summary 卡片加载状态
      fullscreenDialogVisible,
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
      sharedDateString,
      dateRangeDisplay,
      facebookAdsPerformanceAccount1Data,
      facebookAdsPerformanceAccount2Data,
      googleAdsPerformanceData,
      lingxingData,
      lingxingMonthlyCost,  // 添加月度花费数据
      salesTargetData,  // 添加销售目标数据
      facebookSummaryData,  // 添加 Facebook 汇总数据
      googleSummaryData,  // 添加 Google 汇总数据
      handleDateChange,
      formatCurrency,
      formatDecimal,
      handleRefresh,
      toggleFullscreen,
      handleSettings,
      saveSettings,
      cancelSettings,
      handleSalesTargetUpdate,  // 添加销售目标更新处理
      ezarcLogo
    }
  }
}
</script>

<style scoped>
/* 全屏显示样式 */
.fullscreen-overlay {
  position: fixed;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  background: #f9fafb;
  z-index: 99999 !important;
  display: block;
}

.fullscreen-container {
  width: 100% !important;
  height: 100% !important;
  background: #f9fafb;
  position: relative;
  overflow: hidden;
  margin: 0;
  padding: 0;
}

.fullscreen-content {
  padding: 70px 30px 30px 30px;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

.close-fullscreen-btn {
  position: fixed !important;
  top: 20px !important;
  right: 20px !important;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100000 !important;
  transition: all 0.2s ease;
}

.close-fullscreen-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.close-fullscreen-btn:active {
  transform: scale(0.95);
}

.close-fullscreen-btn .el-icon {
  font-size: 18px;
  color: #6b7280;
}

.dialog-section {
  margin-bottom: 24px;
}

.dialog-section:last-child {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .fullscreen-content {
    padding: 60px 20px 20px 20px;
  }
  
  .close-fullscreen-btn {
    top: 15px;
    right: 15px;
    width: 36px;
    height: 36px;
  }
  
  .close-fullscreen-btn .el-icon {
    font-size: 18px;
  }
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
