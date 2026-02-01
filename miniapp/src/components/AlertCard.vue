<template>
  <div 
    class="glass-card p-4 flex items-start gap-3 cursor-pointer active:scale-[0.98] transition-transform"
    :class="borderClass"
  >
    <!-- Icon -->
    <div 
      class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
      :class="iconBgClass"
    >
      <component :is="alertIcon" class="w-5 h-5 text-white" />
    </div>

    <!-- Content -->
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 mb-1">
        <h4 class="font-semibold text-sm truncate">{{ alert.title }}</h4>
        <span 
          class="px-1.5 py-0.5 rounded text-[10px] font-medium uppercase flex-shrink-0"
          :class="urgencyClass"
        >
          {{ alert.urgency }}
        </span>
      </div>
      <p class="text-xs text-tg-hint leading-relaxed">{{ alert.message }}</p>
      <p class="text-[10px] text-tg-hint/60 mt-1">{{ alert.time }}</p>
    </div>

    <!-- Arrow -->
    <svg class="w-5 h-5 text-tg-hint flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M9 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>
</template>

<script setup>
import { computed, h } from 'vue'

const props = defineProps({
  alert: { type: Object, required: true }
})

const borderClass = computed(() => {
  const classes = {
    high: 'border-l-4 border-l-loss',
    medium: 'border-l-4 border-l-warning',
    low: 'border-l-4 border-l-accent',
  }
  return classes[props.alert.urgency] || ''
})

const iconBgClass = computed(() => {
  const classes = {
    warning: 'bg-warning/20',
    success: 'bg-profit/20',
    error: 'bg-loss/20',
    info: 'bg-accent/20',
  }
  return classes[props.alert.type] || 'bg-accent/20'
})

const urgencyClass = computed(() => {
  const classes = {
    high: 'bg-loss/20 text-loss',
    medium: 'bg-warning/20 text-warning',
    low: 'bg-accent/20 text-accent',
  }
  return classes[props.alert.urgency] || 'bg-accent/20 text-accent'
})

const WarningIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
      h('path', { d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' })
    ])
  }
}

const SuccessIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const InfoIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const alertIcon = computed(() => {
  const icons = {
    warning: WarningIcon,
    success: SuccessIcon,
    error: WarningIcon,
    info: InfoIcon,
  }
  return icons[props.alert.type] || InfoIcon
})
</script>
