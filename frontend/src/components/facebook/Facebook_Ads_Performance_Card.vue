<template>
  <PerformanceCard 
    :data="data"
    :date-range="dateRange"
    :title="title"
    :show-date-picker="showDatePicker"
    :fix-first-two-columns="true"
    :loading="loading"
    @date-change="$emit('date-change', $event)"
  />
</template>

<script>
import PerformanceCard from '../shared/Performance_Card.vue'

export default {
  name: 'Facebook_Ads_Performance_Card',
  components: { PerformanceCard },
  props: {
    data: { type: Array, required: true },
    dateRange: { type: String, default: '' },
    title: { type: String, default: 'Facebook Ads Performance Overview (Weekly)' },
    showDatePicker: { type: Boolean, default: true },
    loading: { type: Boolean, default: false }
  },
  emits: ['date-change']
}
</script>
