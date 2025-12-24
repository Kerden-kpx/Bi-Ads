<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title">Conversion Value & Cost Overview Analyze</div>
      <button 
        class="icon-button" 
        @click="handleAnalyze" 
        :disabled="analyzing || loading"
        :title="analyzing ? '分析中...' : '生成AI分析'"
      >
        <el-icon v-if="analyzing" class="rotating"><Loading /></el-icon>
        <el-icon v-else><DataAnalysis /></el-icon>
      </button>
    </div>

    <!-- Loading状态 -->
    <div v-if="loading || analyzing" class="loading-container">
      <div class="loading-spinner"></div>
      <span class="loading-text">{{ analyzing ? `${currentModel} analyzing data. Please wait...` : 'Fetching Data. Please wait...' }}</span>
    </div>

    <!-- 分析报告内容 -->
    <template v-else>
      <!-- 未分析提示 -->
      <div v-if="!analyzeReport" class="empty-state">
        <el-icon class="empty-icon"><DataAnalysis /></el-icon>
        <p class="empty-text">点击右上角按钮进行AI分析</p>
      </div>
      
      <!-- 分析报告 -->
      <div v-else class="analyze-content">
        <!-- 数据分析 -->
        <div class="report-section">
          <h3 class="report-section-title">数据分析</h3>
          <div class="report-content" v-html="analyzeReport.trendAnalysis"></div>
        </div>

        <!-- 总结 -->
        <div class="report-section">
          <h3 class="report-section-title">总结</h3>
          <div class="report-content">
            <p v-for="(finding, index) in analyzeReport.keyFindings" :key="index">
              {{ finding }}
            </p>
          </div>
        </div>

        <!-- 下一步计划建议 -->
        <div class="report-section">
          <h3 class="report-section-title">下一步计划建议</h3>
          <div class="report-content report-recommendations">
            <div v-for="(rec, index) in analyzeReport.recommendations" :key="index" class="report-recommendation" v-html="rec"></div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Loading, 
  DataAnalysis
} from '@element-plus/icons-vue'
import { googleDashboardAPI } from '../../services/google/googleApi'

export default {
  name: 'Google_Analyze_Card_Two',
  components: {
    Loading,
    DataAnalysis
  },
  props: {
    data: { type: Object, default: () => ({}) },
    dateRange: { type: Array, default: () => [] },
    compareDateRange: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false }
  },
  setup(props) {
    const analyzing = ref(false)
    const analyzeReport = ref(null)
    const currentModel = ref('AI')

    // 组件挂载时，尝试从 sessionStorage 恢复之前的分析结果
    const restoreAnalysisFromCache = () => {
      try {
        const cacheKey = `google_conversion_cost_analysis`
        const cached = sessionStorage.getItem(cacheKey)
        if (cached) {
          analyzeReport.value = JSON.parse(cached)
          console.log('[AI分析] 已从缓存恢复分析结果')
        }
      } catch (error) {
        console.error('[AI分析] 恢复缓存失败:', error)
      }
    }

    // 保存分析结果到 sessionStorage
    const saveAnalysisToCache = (data) => {
      try {
        const cacheKey = `google_conversion_cost_analysis`
        sessionStorage.setItem(cacheKey, JSON.stringify(data))
        console.log('[AI分析] 已保存分析结果到缓存')
      } catch (error) {
        console.error('[AI分析] 保存缓存失败:', error)
      }
    }

    // 调用真实的 Gemini AI API 生成分析
    const handleAnalyze = async () => {
      if (!props.dateRange || props.dateRange.length !== 2) {
        return
      }

      // 如果数据不完整，不触发分析
      if (!props.data || !props.data.purchasesValue || props.data.purchasesValue === 0) {
        return
      }

      analyzing.value = true
      currentModel.value = 'AI'
      
      try {
        const requestData = {
          startDate: props.dateRange[0],
          endDate: props.dateRange[1],
          compareStartDate: props.compareDateRange?.[0] || null,
          compareEndDate: props.compareDateRange?.[1] || null,
          metricsData: props.data || {}  // 传递指标卡数据
        }
        
        console.log('Google Conversion & Cost 分析请求数据:', requestData)
        console.log('传递的指标数据:', props.data)
        
        // 调用后端 AI 分析接口
        const response = await googleDashboardAPI.analyzeConversionCost(requestData)
        console.log('完整响应:', response)
        console.log('response.data:', response.data)
        
        // 后端返回格式: { code: 200, message: "AI分析完成", data: {...} }
        // 所以实际数据在 response.data.data 中
        const data = response.data?.data || response.data || response
        
        console.log('提取的AI分析结果:', data)
        
        // 验证数据结构
        if (data && data.trendAnalysis && data.keyFindings && data.recommendations) {
          analyzeReport.value = data
          // 提取模型名称
          if (data.model) {
            currentModel.value = data.model
          }
          // 保存到缓存
          saveAnalysisToCache(data)
        } else {
          console.error('AI返回的数据结构不正确:', data)
        }
      } catch (error) {
        console.error('生成分析报告失败:', error)
        
        // 提取错误消息
        let errorMessage = '生成AI分析报告失败，请稍后重试'
        
        if (error.response?.data?.detail) {
          const detail = error.response.data.detail
          // 检查是否是配额错误
          if (detail.includes('配额') || detail.includes('quota') || detail.includes('RESOURCE_EXHAUSTED')) {
            errorMessage = 'AI分析服务配额已用完'
            ElMessage({
              message: '⚠️ AI分析服务配额已达上限，请明天再试或升级到付费计划',
              type: 'warning',
              duration: 5000,
              showClose: true
            })
          } else {
            ElMessage({
              message: detail,
              type: 'error',
              duration: 4000,
              showClose: true
            })
          }
        } else if (error.message) {
          ElMessage({
            message: error.message,
            type: 'error',
            duration: 4000,
            showClose: true
          })
        } else {
          ElMessage({
            message: errorMessage,
            type: 'error',
            duration: 4000,
            showClose: true
          })
        }
      } finally {
        analyzing.value = false
      }
    }

    // 移除自动触发，改为手动点击按钮触发
    
    // 组件挂载时恢复缓存
    restoreAnalysisFromCache()
    
    return {
      analyzing,
      analyzeReport,
      handleAnalyze,
      currentModel
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.icon-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6b7280;
}

.icon-button:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
  color: #374151;
}

.icon-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.icon-button .el-icon {
  font-size: 16px;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 300px;
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  font-weight: 400;
  color: #606266;
}

.analyze-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 0 32px;
}

.report-section {
  margin-bottom: 32px;
}

.report-section:last-of-type {
  margin-bottom: 0;
}

.report-section-title {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 12px 0;
}

.report-content {
  font-size: 14px;
  line-height: 1.8;
  color: #374151;
}

/* 数据分析列表样式 */
.report-content :deep(ul) {
  list-style: disc;
  padding-left: 20px;
  margin: 0;
}

.report-content :deep(li) {
  margin-bottom: 8px;
  line-height: 1.8;
  color: #374151;
}

.report-content :deep(strong) {
  color: #111827;
  font-weight: 600;
}

.report-content :deep(.trend-up),
.report-content :deep(.trend-down),
.report-content :deep(.trend-stable) {
  color: #374151;
  font-weight: normal;
}

/* 总结段落样式 */
.report-content p {
  margin: 0 0 8px 0;
  line-height: 1.8;
}

.report-content p:last-child {
  margin-bottom: 0;
}

/* 建议列表样式 */
.report-recommendations {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-recommendation {
  line-height: 1.8;
  color: #374151;
}

.report-recommendation :deep(strong) {
  color: #111827;
  font-weight: 700;
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  color: #d1d5db;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 15px;
  color: #9ca3af;
  margin: 0;
  text-align: center;
}

@media (max-width: 768px) {
  .analyze-content {
    padding: 0 16px;
  }
  
  .analyze-section {
    flex-direction: column;
  }
  
  .empty-state {
    min-height: 200px;
    padding: 32px 16px;
  }
  
  .empty-icon {
    font-size: 48px;
  }
}
</style>

