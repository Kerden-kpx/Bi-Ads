<template>
  <div class="single-date-picker">
    <el-popover
      v-model:visible="visible"
      placement="bottom-start"
      :width="420"
      trigger="click"
      popper-class="single-date-popover"
    >
      <template #reference>
        <div class="date-picker-trigger">
          <el-icon><Calendar /></el-icon>
          <span class="date-text">{{ formatDate(currentDate) }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
      </template>

      <div class="date-picker-content">
        <!-- 左侧快速选择 -->
        <div class="quick-sidebar">
          <div 
            class="quick-item" 
            :class="{ active: selectedQuick === 'today' }"
            @click="selectQuick('today')"
          >
            Today
          </div>
          
          <div 
            class="quick-item" 
            :class="{ active: selectedQuick === 'yesterday' }"
            @click="selectQuick('yesterday')"
          >
            Yesterday
          </div>
          
          <div 
            class="quick-item" 
            :class="{ active: selectedQuick === 'week' }"
            @click="selectQuick('week')"
          >
            Last Week
          </div>

          <div 
            class="quick-item" 
            :class="{ active: selectedQuick === 'month' }"
            @click="selectQuick('month')"
          >
            Last Month
          </div>
        </div>

        <!-- 右侧日历区域 -->
        <div class="calendar-area">
          <!-- 月份导航 -->
          <div class="month-nav-bar">
            <el-icon class="nav-arrow" @click="prevMonth"><ArrowLeft /></el-icon>
            <span class="month-text">{{ monthText }}</span>
            <el-icon class="nav-arrow" @click="nextMonth"><ArrowRight /></el-icon>
          </div>

          <!-- 日历 -->
          <div class="month-calendar">
            <div class="week-header">
              <div v-for="d in weekDays" :key="d" class="week-day">{{ d }}</div>
            </div>
            <div class="days-grid">
              <div
                v-for="day in calendarDays"
                :key="`day-${day.date}`"
                class="day-cell"
                :class="getDayClasses(day)"
                @click="handleDayClick(day.date)"
              >
                {{ day.day }}
              </div>
            </div>
          </div>

          <!-- 底部按钮 -->
          <div class="footer-actions">
            <el-button @click="handleCancel">Cancel</el-button>
            <el-button type="primary" @click="handleApply">Apply</el-button>
          </div>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { Calendar, ArrowDown, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

export default {
  name: 'Single_Date_Picker',
  components: {
    Calendar,
    ArrowDown,
    ArrowLeft,
    ArrowRight
  },
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Select date'
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const visible = ref(false)
    const currentDate = ref(props.modelValue || dayjs().format('YYYY-MM-DD'))
    const tempDate = ref('')
    const selectedQuick = ref('')
    
    const currentMonth = ref(dayjs())

    const weekDays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

    const monthText = computed(() => currentMonth.value.format('MMMM YYYY'))

    const buildMonthDays = (monthDate) => {
      const days = []
      const startOfMonth = monthDate.startOf('month')
      const endOfMonth = monthDate.endOf('month')
      const startDay = startOfMonth.day()
      
      // 上月日期
      for (let i = startDay - 1; i >= 0; i--) {
        const d = startOfMonth.subtract(i + 1, 'day')
        days.push({
          date: d.format('YYYY-MM-DD'),
          day: d.date(),
          isCurrentMonth: false
        })
      }
      
      // 当月日期
      for (let i = 0; i < endOfMonth.date(); i++) {
        const d = startOfMonth.add(i, 'day')
        days.push({
          date: d.format('YYYY-MM-DD'),
          day: d.date(),
          isCurrentMonth: true
        })
      }
      
      // 补齐下月日期
      const remaining = 42 - days.length
      for (let i = 0; i < remaining; i++) {
        const d = endOfMonth.add(i + 1, 'day')
        days.push({
          date: d.format('YYYY-MM-DD'),
          day: d.date(),
          isCurrentMonth: false
        })
      }
      
      return days
    }

    const calendarDays = computed(() => buildMonthDays(currentMonth.value))

    const getDayClasses = (day) => {
      const classes = []
      
      if (!day.isCurrentMonth) {
        classes.push('other-month')
      }
      
      if (day.date === tempDate.value) {
        classes.push('selected')
      }
      
      if (day.date === dayjs().format('YYYY-MM-DD')) {
        classes.push('is-today')
      }
      
      return classes
    }

    const handleDayClick = (date) => {
      tempDate.value = date
      selectedQuick.value = ''
    }

    const selectQuick = (type) => {
      selectedQuick.value = type
      const today = dayjs()
      
      switch (type) {
        case 'today':
          tempDate.value = today.format('YYYY-MM-DD')
          break
        case 'yesterday':
          tempDate.value = today.subtract(1, 'day').format('YYYY-MM-DD')
          break
        case 'week':
          tempDate.value = today.subtract(7, 'day').format('YYYY-MM-DD')
          break
        case 'month':
          tempDate.value = today.subtract(1, 'month').format('YYYY-MM-DD')
          break
      }
    }

    const prevMonth = () => {
      currentMonth.value = currentMonth.value.subtract(1, 'month')
    }

    const nextMonth = () => {
      currentMonth.value = currentMonth.value.add(1, 'month')
    }

    const formatDate = (date) => {
      if (!date) {
        return props.placeholder
      }
      return dayjs(date).format('MMM D, YYYY')
    }

    const handleApply = () => {
      if (tempDate.value) {
        currentDate.value = tempDate.value
        emit('update:modelValue', currentDate.value)
        visible.value = false
      }
    }

    const handleCancel = () => {
      tempDate.value = currentDate.value
      visible.value = false
    }

    watch(() => props.modelValue, (val) => {
      currentDate.value = val || dayjs().format('YYYY-MM-DD')
      tempDate.value = currentDate.value
    })

    watch(visible, (val) => {
      if (val) {
        tempDate.value = currentDate.value
        // 设置日历月份为当前选中日期的月份
        currentMonth.value = dayjs(currentDate.value)
      }
    })

    return {
      visible,
      currentDate,
      tempDate,
      selectedQuick,
      currentMonth,
      weekDays,
      monthText,
      calendarDays,
      getDayClasses,
      handleDayClick,
      selectQuick,
      prevMonth,
      nextMonth,
      formatDate,
      handleApply,
      handleCancel
    }
  }
}
</script>

<style scoped>
.single-date-picker {
  display: inline-block;
}

.date-picker-trigger {
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
}

.date-picker-trigger:hover {
  border-color: #9ca3af;
  background: #f9fafb;
}

.date-text {
  white-space: nowrap;
  min-width: 100px;
}

.date-picker-content {
  display: flex;
}

.quick-sidebar {
  width: 140px;
  border-right: 1px solid #e5e7eb;
  background: #fafafa;
}

.quick-item {
  padding: 12px 16px;
  cursor: pointer;
  font-size: 13px;
  color: #374151;
  transition: all 0.15s ease;
}

.quick-item:hover {
  background: #f3f4f6;
}

.quick-item.active {
  background: #2f45ff;
  color: #ffffff;
  font-weight: 500;
}

.calendar-area {
  flex: 1;
  padding: 16px;
  background: white;
}

.month-nav-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.nav-arrow {
  cursor: pointer;
  font-size: 16px;
  color: #6b7280;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.nav-arrow:hover {
  background: #f3f4f6;
  color: #111827;
}

.month-text {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  min-width: 140px;
  text-align: center;
}

.month-calendar {
  width: 100%;
}

.week-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.week-day {
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  padding: 8px 0;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-cell {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s ease;
  color: #111827;
}

.day-cell:hover {
  background: #f3f4f6;
}

.day-cell.other-month {
  color: #d1d5db;
}

.day-cell.selected {
  background: #2f45ff;
  color: white;
  font-weight: 600;
}

.day-cell.is-today {
  border: 2px solid #2f45ff;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
  margin-top: 16px;
}

.footer-actions :deep(.el-button--primary) {
  background-color: #2f45ff;
  border-color: #2f45ff;
}

.footer-actions :deep(.el-button--primary:hover) {
  background-color: #1f35ef;
  border-color: #1f35ef;
}

.footer-actions :deep(.el-button--primary:active) {
  background-color: #0f25df;
  border-color: #0f25df;
}
</style>

