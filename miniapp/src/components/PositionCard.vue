<template>
  <div 
    class="position-card cursor-pointer"
    @click="$emit('click', position)"
  >
    <div class="flex items-center justify-between">
      <!-- Left: Symbol & Name -->
      <div class="flex items-center gap-3">
        <div 
          class="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold"
          :class="logoClass"
        >
          {{ position.symbol.slice(0, 2) }}
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h3 class="font-semibold text-base">{{ position.symbol }}</h3>
            <span 
              class="px-1.5 py-0.5 rounded text-[10px] font-medium uppercase"
              :class="actionBadgeClass"
            >
              {{ position.action }}
            </span>
          </div>
          <p class="text-xs text-tg-hint">{{ position.quantity }} shares</p>
        </div>
      </div>

      <!-- Right: Price & P&L -->
      <div class="text-right">
        <p class="font-mono font-semibold">${{ formatNumber(position.currentPrice) }}</p>
        <p 
          class="text-sm font-mono"
          :class="position.pnl >= 0 ? 'text-profit' : 'text-loss'"
        >
          {{ position.pnl >= 0 ? '+' : '' }}{{ position.pnlPct.toFixed(2) }}%
        </p>
      </div>
    </div>

    <!-- Mini chart preview -->
    <div class="mt-3 h-10 relative">
      <svg class="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 30">
        <defs>
          <linearGradient :id="'miniGrad' + position.symbol" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" :stop-color="position.pnl >= 0 ? '#00d26a' : '#ff4757'" stop-opacity="0.2"/>
            <stop offset="100%" :stop-color="position.pnl >= 0 ? '#00d26a' : '#ff4757'" stop-opacity="0"/>
          </linearGradient>
        </defs>
        <path 
          :d="areaPath" 
          :fill="'url(#miniGrad' + position.symbol + ')'"
        />
        <path 
          :d="linePath" 
          fill="none" 
          :stroke="position.pnl >= 0 ? '#00d26a' : '#ff4757'" 
          stroke-width="1.5"
          stroke-linecap="round"
        />
      </svg>
    </div>

    <!-- Day change indicator -->
    <div class="flex items-center justify-between mt-2 pt-2 border-t border-dark-border/30">
      <span class="text-xs text-tg-hint">Today</span>
      <span 
        class="text-xs font-mono font-medium flex items-center gap-1"
        :class="position.dayChange >= 0 ? 'text-profit' : 'text-loss'"
      >
        <svg 
          class="w-3 h-3" 
          :class="position.dayChange >= 0 ? '' : 'rotate-180'"
          viewBox="0 0 24 24" 
          fill="currentColor"
        >
          <path d="M12 4l-8 8h5v8h6v-8h5z"/>
        </svg>
        {{ position.dayChange >= 0 ? '+' : '' }}${{ Math.abs(position.dayChange).toFixed(2) }}
        ({{ position.dayChangePct >= 0 ? '+' : '' }}{{ position.dayChangePct.toFixed(2) }}%)
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  position: { type: Object, required: true }
})

defineEmits(['click'])

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num)
}

const logoClass = computed(() => {
  const colors = {
    'AAPL': 'bg-gradient-to-br from-gray-600 to-gray-800',
    'NVDA': 'bg-gradient-to-br from-green-600 to-green-800',
    'TSLA': 'bg-gradient-to-br from-red-600 to-red-800',
    'MSFT': 'bg-gradient-to-br from-blue-600 to-blue-800',
    'GOOGL': 'bg-gradient-to-br from-yellow-500 to-red-500',
    'AMZN': 'bg-gradient-to-br from-orange-500 to-yellow-500',
  }
  return colors[props.position.symbol] || 'bg-gradient-to-br from-accent to-accent-light'
})

const actionBadgeClass = computed(() => {
  const classes = {
    'hold': 'bg-accent/20 text-accent',
    'reduce': 'bg-warning/20 text-warning',
    'exit': 'bg-loss/20 text-loss',
    'add': 'bg-profit/20 text-profit',
  }
  return classes[props.position.action] || 'bg-tg-hint/20 text-tg-hint'
})

// Generate random mini chart data
const chartData = computed(() => {
  const baseValue = props.position.avgPrice
  const trend = props.position.pnl >= 0 ? 1 : -1
  const data = []
  let value = baseValue
  
  for (let i = 0; i < 20; i++) {
    const change = (Math.random() - 0.4) * 2 + (trend * 0.3)
    value += change
    data.push(value)
  }
  
  // End at current price
  data.push(props.position.currentPrice)
  return data
})

const linePath = computed(() => {
  const data = chartData.value
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  
  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * 100
    const y = 30 - ((val - min) / range) * 28 - 1
    return `${x},${y}`
  })
  
  return `M${points.join(' L')}`
})

const areaPath = computed(() => {
  return linePath.value + ' L100,30 L0,30 Z'
})
</script>
