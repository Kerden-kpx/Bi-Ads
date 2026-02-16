<template>
  <div class="quick-date-picker">
    <el-popover
      v-model:visible="visible"
      placement="bottom-start"
      :width="780"
      trigger="click"
      popper-class="quick-date-popover"
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
        <div class="quick-select-sidebar">
          <div 
            class="quick-option" 
            :class="{ active: selectedQuickOption === 'today' }"
            @click="selectQuickOption({ label: 'Today', value: 'today' })"
          >
            Today
          </div>
          <div 
            class="quick-option" 
            :class="{ active: selectedQuickOption === 'yesterday' }"
            @click="selectQuickOption({ label: 'Yesterday', value: 'yesterday' })"
          >
            Yesterday
          </div>
          <div 
            class="quick-option" 
            :class="{ active: selectedQuickOption === 'last7days' }"
            @click="selectQuickOption({ label: 'Last 7 Days', value: 'last7days' })"
          >
            Last 7 Days
          </div>
          <div 
            class="quick-option" 
            :class="{ active: selectedQuickOption === 'last30days' }"
            @click="selectQuickOption({ label: 'Last 30 Days', value: 'last30days' })"
          >
            Last 30 Days
          </div>

          <div class="custom-range-section">
            <div class="custom-range-header">
              <span>Last</span>
              <input 
                v-model.number="customDays" 
                type="number" 
                min="1"
                class="custom-input"
                @input="selectCustomDays"
              />
              <span>Days</span>
            </div>
          </div>

          <div 
            class="quick-option" 
            :class="{ active: selectedQuickOption === 'thisMonth' }"
            @click="selectQuickOption({ label: 'This Month', value: 'thisMonth' })"
          >
            This Month
          </div>

          <div class="custom-range-section">
            <div class="custom-range-header">
              <span>Last</span>
              <input 
                v-model.number="customMonths" 
                type="number" 
                min="1"
                class="custom-input"
                @input="selectCustomMonths"
              />
              <span>Months</span>
            </div>
          </div>

          <div 
            class="quick-option" 
            :class="{ active: selectedQuickOption === 'lastMonth' }"
            @click="selectQuickOption({ label: 'Last Month', value: 'lastMonth' })"
          >
            Last Month
          </div>
          <div 
            class="quick-option" 
            :class="{ active: selectedQuickOption === 'thisYear' }"
            @click="selectQuickOption({ label: 'This Year', value: 'thisYear' })"
          >
            This Year
          </div>
          <div 
            class="quick-option" 
            :class="{ active: selectedQuickOption === 'lastYear' }"
            @click="selectQuickOption({ label: 'Last Year', value: 'lastYear' })"
          >
            Last Year
          </div>
        </div>

        <!-- 右侧日历 -->
        <div class="calendar-container">
          <div class="calendar-header">
            <div class="month-navigation">
              <el-icon class="nav-icon" @click="previousMonth"><ArrowLeft /></el-icon>
              <span class="current-month">{{ currentMonthText }}</span>
              <el-icon class="nav-icon" @click="goNextMonth"><ArrowRight /></el-icon>
            </div>
            <div class="month-navigation">
              <el-icon class="nav-icon" @click="previousMonth2"><ArrowLeft /></el-icon>
              <span class="current-month">{{ nextMonthText }}</span>
              <el-icon class="nav-icon" @click="nextMonth2"><ArrowRight /></el-icon>
            </div>
          </div>

          <div class="calendars">
            <!-- 第一个日历 -->
            <div class="calendar">
              <div class="calendar-weekdays">
                <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
              </div>
              <div class="calendar-days">
                <div
                  v-for="day in firstCalendarDays"
                  :key="`first-${day.date}`"
                  class="calendar-day"
                  :class="getDayClass(day)"
                  @click="selectDate(day.date)"
                >
                  {{ day.day }}
                </div>
              </div>
            </div>

            <!-- 第二个日历 -->
            <div class="calendar">
              <div class="calendar-weekdays">
                <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
              </div>
              <div class="calendar-days">
                <div
                  v-for="day in secondCalendarDays"
                  :key="`second-${day.date}`"
                  class="calendar-day"
                  :class="getDayClass(day)"
                  @click="selectDate(day.date)"
                >
                  {{ day.day }}
                </div>
              </div>
            </div>
          </div>

          <!-- 底部操作按钮 -->
          <div class="calendar-footer">
            <div class="include-today">
              <el-checkbox v-model="includeToday">Include Today</el-checkbox>
            </div>
            <div class="action-buttons">
              <el-button @click="cancel">Cancel</el-button>
              <el-button type="primary" @click="apply">Apply</el-button>
            </div>
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
  name: 'Quick_Date_Range_Picker',
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
    const selectedQuickOption = ref('')
    const customDays = ref(60)
    const customMonths = ref(3)
    const includeToday = ref(false)
    
    const currentMonth = ref(dayjs())
    const secondMonth = ref(dayjs().add(1, 'month'))

    const weekdays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

    const currentMonthText = computed(() => currentMonth.value.format('MMMM YYYY'))
    const nextMonthText = computed(() => secondMonth.value.format('MMMM YYYY'))

    const getCalendarDays = (month) => {
      const days = []
      const startOfMonth = month.startOf('month')
      const endOfMonth = month.endOf('month')
      const startDay = startOfMonth.day()
      
      // 上个月的日期
      for (let i = startDay - 1; i >= 0; i--) {
        const date = startOfMonth.subtract(i + 1, 'day')
        days.push({
          date: date.format('YYYY-MM-DD'),
          day: date.date(),
          isCurrentMonth: false
        })
      }
      
      // 当前月的日期
      for (let i = 0; i < endOfMonth.date(); i++) {
        const date = startOfMonth.add(i, 'day')
        days.push({
          date: date.format('YYYY-MM-DD'),
          day: date.date(),
          isCurrentMonth: true
        })
      }
      
      // 下个月的日期
      const remainingDays = 42 - days.length
      for (let i = 0; i < remainingDays; i++) {
        const date = endOfMonth.add(i + 1, 'day')
        days.push({
          date: date.format('YYYY-MM-DD'),
          day: date.date(),
          isCurrentMonth: false
        })
      }
      
      return days
    }

    const firstCalendarDays = computed(() => getCalendarDays(currentMonth.value))
    const secondCalendarDays = computed(() => getCalendarDays(secondMonth.value))

    const getDayClass = (day) => {
      const classes = []
      
      if (!day.isCurrentMonth) {
        classes.push('other-month')
      }
      
      if (tempRange.value.length > 0) {
        const [start, end] = tempRange.value.sort()
        if (day.date === start || day.date === end) {
          classes.push('selected')
        } else if (start && end && day.date > start && day.date < end) {
          classes.push('in-range')
        }
      }
      
      if (day.date === dayjs().format('YYYY-MM-DD')) {
        classes.push('today')
      }
      
      return classes
    }

    const selectDate = (date) => {
      if (tempRange.value.length === 0 || tempRange.value.length === 2) {
        tempRange.value = [date]
      } else {
        tempRange.value.push(date)
        tempRange.value.sort()
      }
      selectedQuickOption.value = ''
    }

    const selectQuickOption = (option) => {
      selectedQuickOption.value = option.value
      const today = dayjs()
      
      switch (option.value) {
        case 'today':
          tempRange.value = [today.format('YYYY-MM-DD'), today.format('YYYY-MM-DD')]
          break
        case 'yesterday':
          const yesterday = today.subtract(1, 'day')
          tempRange.value = [yesterday.format('YYYY-MM-DD'), yesterday.format('YYYY-MM-DD')]
          break
        case 'last7days':
          tempRange.value = [today.subtract(6, 'day').format('YYYY-MM-DD'), today.format('YYYY-MM-DD')]
          break
        case 'last30days':
          tempRange.value = [today.subtract(29, 'day').format('YYYY-MM-DD'), today.format('YYYY-MM-DD')]
          break
        case 'thisMonth':
          tempRange.value = [today.startOf('month').format('YYYY-MM-DD'), today.format('YYYY-MM-DD')]
          break
        case 'lastMonth':
          const lastMonth = today.subtract(1, 'month')
          tempRange.value = [lastMonth.startOf('month').format('YYYY-MM-DD'), lastMonth.endOf('month').format('YYYY-MM-DD')]
          break
        case 'thisYear':
          tempRange.value = [today.startOf('year').format('YYYY-MM-DD'), today.format('YYYY-MM-DD')]
          break
        case 'lastYear':
          const lastYear = today.subtract(1, 'year')
          tempRange.value = [lastYear.startOf('year').format('YYYY-MM-DD'), lastYear.endOf('year').format('YYYY-MM-DD')]
          break
      }
    }

    const selectCustomDays = () => {
      if (customDays.value > 0) {
        const today = dayjs()
        tempRange.value = [today.subtract(customDays.value - 1, 'day').format('YYYY-MM-DD'), today.format('YYYY-MM-DD')]
        selectedQuickOption.value = 'customDays'
      }
    }

    const selectCustomMonths = () => {
      if (customMonths.value > 0) {
        const today = dayjs()
        tempRange.value = [today.subtract(customMonths.value, 'month').format('YYYY-MM-DD'), today.format('YYYY-MM-DD')]
        selectedQuickOption.value = 'customMonths'
      }
    }

    const previousMonth = () => {
      currentMonth.value = currentMonth.value.subtract(1, 'month')
      secondMonth.value = secondMonth.value.subtract(1, 'month')
    }

    const goNextMonth = () => {
      currentMonth.value = currentMonth.value.add(1, 'month')
      secondMonth.value = secondMonth.value.add(1, 'month')
    }

    const previousMonth2 = () => {
      secondMonth.value = secondMonth.value.subtract(1, 'month')
      currentMonth.value = currentMonth.value.subtract(1, 'month')
    }

    const nextMonth2 = () => {
      secondMonth.value = secondMonth.value.add(1, 'month')
      currentMonth.value = currentMonth.value.add(1, 'month')
    }

    const formatDateRange = (range) => {
      if (!range || range.length === 0) {
        return props.placeholder
      }
      const [start, end] = range
      return `${dayjs(start).format('MMM D, YYYY')} - ${dayjs(end).format('MMM D, YYYY')}`
    }

    const apply = () => {
      if (tempRange.value.length === 2) {
        currentRange.value = [...tempRange.value]
        emit('update:modelValue', currentRange.value)
        visible.value = false
      }
    }

    const cancel = () => {
      tempRange.value = [...currentRange.value]
      visible.value = false
    }

    watch(() => props.modelValue, (newVal) => {
      currentRange.value = newVal || []
      tempRange.value = [...currentRange.value]
    })

    watch(visible, (newVal) => {
      if (newVal) {
        tempRange.value = [...currentRange.value]
      }
    })

    return {
      visible,
      currentRange,
      tempRange,
      selectedQuickOption,
      customDays,
      customMonths,
      includeToday,
      currentMonth,
      secondMonth,
      weekdays,
      currentMonthText,
      nextMonthText,
      firstCalendarDays,
      secondCalendarDays,
      getDayClass,
      selectDate,
      selectQuickOption,
      selectCustomDays,
      selectCustomMonths,
      previousMonth,
      goNextMonth,
      previousMonth2,
      nextMonth2,
      formatDateRange,
      apply,
      cancel
    }
  }
}
</script>

<style scoped>
.quick-date-picker {
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
  gap: 0;
}

.quick-select-sidebar {
  width: 180px;
  border-right: 1px solid #e5e7eb;
  padding: 12px 0;
  background: #ffffff;
}

.quick-option {
  padding: 8px 20px;
  cursor: pointer;
  font-size: 14px;
  color: #111827;
  transition: all 0.15s ease;
}

.quick-option:hover {
  background: #f9fafb;
}

.quick-option.active {
  background: #2f45ff;
  color: #ffffff;
  font-weight: 500;
}

.custom-range-section {
  padding: 8px 20px;
}

.custom-range-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 0;
  font-size: 14px;
  color: #374151;
}

.custom-input {
  width: 50px;
  padding: 3px 6px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  background: white;
}

.custom-input:focus {
  outline: none;
  border-color: #4f46e5;
}

.calendar-container {
  flex: 1;
  padding: 16px;
  background: white;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 24px;
}

.month-navigation {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  justify-content: center;
}

.nav-icon {
  cursor: pointer;
  font-size: 16px;
  color: #6b7280;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.nav-icon:hover {
  background: #f3f4f6;
  color: #111827;
}

.current-month {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  min-width: 140px;
  text-align: center;
}

.calendars {
  display: flex;
  gap: 24px;
}

.calendar {
  flex: 1;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  padding: 8px 0;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
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

.calendar-day:hover {
  background: #f3f4f6;
}

.calendar-day.other-month {
  color: #d1d5db;
}

.calendar-day.selected {
  background: #2f45ff;
  color: white;
  font-weight: 600;
}

.calendar-day.in-range {
  background: #e8ebff;
  color: #111827;
}

.calendar-day.today {
  border: 1px solid #2f45ff;
}

.calendar-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.include-today {
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-buttons :deep(.el-button--primary) {
  background-color: #2f45ff;
  border-color: #2f45ff;
}

.action-buttons :deep(.el-button--primary:hover) {
  background-color: #1f35ef;
  border-color: #1f35ef;
}

.action-buttons :deep(.el-button--primary:active) {
  background-color: #0f25df;
  border-color: #0f25df;
}
</style>

