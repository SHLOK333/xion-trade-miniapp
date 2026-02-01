<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-dark border-t border-dark-border safe-bottom z-50">
    <div class="flex justify-around items-center py-2">
      <button 
        v-for="item in navItems" 
        :key="item.id"
        @click="$emit('change', item.id)"
        class="flex flex-col items-center gap-1 py-2 px-4 rounded-lg transition-all relative"
        :class="activeTab === item.id ? 'text-profit' : 'text-dark-hint'"
      >
        <component :is="item.icon" class="w-5 h-5" />
        <span class="text-[10px] font-medium">{{ item.label }}</span>
        
        <!-- Active indicator -->
        <div 
          v-if="activeTab === item.id"
          class="absolute -top-0.5 w-6 h-0.5 rounded-full bg-profit"
        ></div>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { h } from 'vue'

defineProps({
  activeTab: { type: String, required: true }
})

defineEmits(['change'])

const PositionsIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const ChartsIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
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

const AlertsIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
    ])
  }
}

const navItems = [
  { id: 'positions', label: 'Positions', icon: PositionsIcon },
  { id: 'charts', label: 'Charts', icon: ChartsIcon },
  { id: 'ai', label: 'AI', icon: AIIcon },
  { id: 'alerts', label: 'Alerts', icon: AlertsIcon },
]
</script>
