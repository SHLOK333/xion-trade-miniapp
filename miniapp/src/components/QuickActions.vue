<template>
  <div class="py-4 px-4 overflow-x-auto scroll-x -mx-4">
    <div class="flex gap-2 min-w-max px-4">
      <button 
        v-for="action in actions" 
        :key="action.id"
        @click="$emit('action', action.id)"
        class="flex flex-col items-center gap-2 p-3 rounded-xl bg-dark-card border border-dark-border min-w-[72px] transition-all duration-200 active:scale-95 hover:border-dark-hint"
      >
        <div 
          class="w-10 h-10 rounded-lg flex items-center justify-center bg-dark-secondary"
        >
          <component :is="action.icon" class="w-5 h-5 text-profit" />
        </div>
        <span class="text-[10px] font-medium text-dark-hint">{{ action.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { h } from 'vue'

defineEmits(['action'])

const RebalanceIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const AnalyzeIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const AlertIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const TradeIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const AIIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const actions = [
  { id: 'rebalance', label: 'Rebalance', icon: RebalanceIcon },
  { id: 'analyze', label: 'Analyze', icon: AnalyzeIcon },
  { id: 'alerts', label: 'Alerts', icon: AlertIcon },
  { id: 'trade', label: 'Trade', icon: TradeIcon },
  { id: 'ai', label: 'Ask AI', icon: AIIcon },
]
</script>
