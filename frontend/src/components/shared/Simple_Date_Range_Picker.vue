<template>
  <div class="simple-date-picker">
    <el-popover
      v-model:visible="visible"
      placement="bottom-start"
      :width="700"
      trigger="click"
      popper-class="simple-date-popover"
    >
      <template #reference>
        <div class="date-picker-trigger">
          <el-icon><Calendar /></el-icon>
          <span class="date-range-text">{{ formatDateRange(currentRange) }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
      </template>

      <div class="date-picker-content">
        <!-- 左侧快速选择 -->
        <div class="quick-sidebar">
          <div 
            class="quick-item" 
            :class="{ active: selectedQuick === 'none' }"
            @click="selectQuick('none')"
          >
            None
          </div>
          
          <div 
            class="quick-item" 
            :class="{ active: selectedQuick === 'previous' }"
            @click="selectQuick('previous')"
          >
            Previous Period
          </div>
          
          <div 
            class="quick-item" 
            :class="{ active: selectedQuick === 'year' }"
            @click="selectQuick('year')"
          >
            Previous Year
          </div>
        </div>

        <!-- 右侧日历区域 -->
        <div class="calendar-area">
          <!-- 月份导航 -->
          <div class="month-nav-bar">
            <div class="month-nav-item">
              <el-icon class="nav-arrow" @click="prevMonth"><ArrowLeft /></el-icon>
              <span class="month-text">{{ month1Text }}</span>
              <el-icon class="nav-arrow" @click="nextMonth"><ArrowRight /></el-icon>
            </div>
            <div class="month-nav-item">
              <el-icon class="nav-arrow" @click="prevMonth2"><ArrowLeft /></el-icon>
              <span class="month-text">{{ month2Text }}</span>
              <el-icon class="nav-arrow" @click="nextMonth2"><ArrowRight /></el-icon>
            </div>
          </div>

          <!-- 双日历 -->
          <div class="dual-calendar">
            <!-- 第一个月 -->
            <div class="month-calendar">
              <div class="week-header">
                <div v-for="d in weekDays" :key="d" class="week-day">{{ d }}</div>
              </div>
              <div class="days-grid">
                <div
                  v-for="day in calendar1Days"
                  :key="`m1-${day.date}`"
                  class="day-cell"
                  :class="getDayClasses(day)"
                  @click="handleDayClick(day.date)"
                >
                  {{ day.day }}
                </div>
              </div>
            </div>

            <!-- 第二个月 -->
            <div class="month-calendar">
              <div class="week-header">
                <div v-for="d in weekDays" :key="d" class="week-day">{{ d }}</div>
              </div>
              <div class="days-grid">
                <div
                  v-for="day in calendar2Days"
                  :key="`m2-${day.date}`"
                  class="day-cell"
                  :class="getDayClasses(day)"
                  @click="handleDayClick(day.date)"
                >
                  {{ day.day }}
                </div>
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
  name: 'Simple_Date_Range_Picker',
  components: {
    Calendar,
    ArrowDown,
    ArrowLeft,
    ArrowRight
  },
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    placeholder: {
      type: String,
      default: 'Select date range'
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const visible = ref(false)
    const currentRange = ref(props.modelValue || [])
    const tempRange = ref([])
    const selectedQuick = ref('')
    
    const month1 = ref(dayjs())
    const month2 = ref(dayjs().add(1, 'month'))

    const weekDays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

    const month1Text = computed(() => month1.value.format('MMMM YYYY'))
    const month2Text = computed(() => month2.value.format('MMMM YYYY'))

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

    const calendar1Days = computed(() => buildMonthDays(month1.value))
    const calendar2Days = computed(() => buildMonthDays(month2.value))

    const getDayClasses = (day) => {
      const classes = []
      
      if (!day.isCurrentMonth) {
        classes.push('other-month')
      }
      
      if (tempRange.value.length > 0) {
        const [start, end] = tempRange.value.sort()
        if (day.date === start || day.date === end) {
          classes.push('range-selected')
        } else if (start && end && day.date > start && day.date < end) {
          classes.push('in-range')
        }
      }
      
      if (day.date === dayjs().format('YYYY-MM-DD')) {
        classes.push('is-today')
      }
      
      return classes
    }

    const handleDayClick = (date) => {
      if (tempRange.value.length === 0 || tempRange.value.length === 2) {
        tempRange.value = [date]
      } else {
        tempRange.value.push(date)
        tempRange.value.sort()
      }
      selectedQuick.value = ''
    }

    const selectQuick = (type) => {
      selectedQuick.value = type
      const today = dayjs()
      
      switch (type) {
        case 'none':
          tempRange.value = []
          break
        case 'previous':
          // Previous Period logic
          if (currentRange.value.length === 2) {
            const days = dayjs(currentRange.value[1]).diff(dayjs(currentRange.value[0]), 'day') + 1
            tempRange.value = [
              dayjs(currentRange.value[0]).subtract(days, 'day').format('YYYY-MM-DD'),
              dayjs(currentRange.value[0]).subtract(1, 'day').format('YYYY-MM-DD')
            ]
          }
          break
        case 'year':
          const lastYear = today.subtract(1, 'year')
          tempRange.value = [
            lastYear.startOf('year').format('YYYY-MM-DD'),
            lastYear.endOf('year').format('YYYY-MM-DD')
          ]
          break
      }
    }

    const prevMonth = () => {
      month1.value = month1.value.subtract(1, 'month')
      month2.value = month2.value.subtract(1, 'month')
    }

    const nextMonth = () => {
      month1.value = month1.value.add(1, 'month')
      month2.value = month2.value.add(1, 'month')
    }

    const prevMonth2 = () => {
      month2.value = month2.value.subtract(1, 'month')
      month1.value = month1.value.subtract(1, 'month')
    }

    const nextMonth2 = () => {
      month2.value = month2.value.add(1, 'month')
      month1.value = month1.value.add(1, 'month')
    }

    const formatDateRange = (range) => {
      if (!range || range.length === 0) {
        return props.placeholder
      }
      const [start, end] = range
      return `${dayjs(start).format('MMM D, YYYY')} - ${dayjs(end).format('MMM D, YYYY')}`
    }

    const handleApply = () => {
      if (tempRange.value.length === 2) {
        currentRange.value = [...tempRange.value]
        emit('update:modelValue', currentRange.value)
        visible.value = false
      }
    }

    const handleCancel = () => {
      tempRange.value = [...currentRange.value]
      visible.value = false
    }

    watch(() => props.modelValue, (val) => {
      currentRange.value = val || []
      tempRange.value = [...currentRange.value]
    })

    watch(visible, (val) => {
      if (val) {
        tempRange.value = [...currentRange.value]
      }
    })

    return {
      visible,
      currentRange,
      tempRange,
      selectedQuick,
      month1,
      month2,
      weekDays,
      month1Text,
      month2Text,
      calendar1Days,
      calendar2Days,
      getDayClasses,
      handleDayClick,
      selectQuick,
      prevMonth,
      nextMonth,
      prevMonth2,
      nextMonth2,
      formatDateRange,
      handleApply,
      handleCancel
    }
  }
}
</script>

<style scoped>
.simple-date-picker {
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

.date-range-text {
  white-space: nowrap;
}

.date-picker-content {
  display: flex;
}

.quick-sidebar {
  width: 180px;
  border-right: 1px solid #e5e7eb;
  background: #fafafa;
}

.quick-item {
  padding: 14px 20px;
  cursor: pointer;
  font-size: 14px;
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
  gap: 24px;
  margin-bottom: 16px;
}

.month-nav-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
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

.dual-calendar {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.month-calendar {
  flex: 1;
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

.day-cell.range-selected {
  background: #2f45ff;
  color: white;
  font-weight: 600;
}

.day-cell.in-range {
  background: #e8ebff;
  color: #111827;
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

