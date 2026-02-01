<template>
  <div class="bg-dark-card border border-dark-border rounded-xl p-5 animate-slide-up">
    <!-- Value Display -->
    <div class="flex justify-between items-start mb-4">
      <div>
        <p class="text-dark-hint text-sm mb-1">Portfolio Value</p>
        <h2 class="text-3xl font-bold tracking-tight text-dark-text">
          <span class="font-mono">${{ formatNumber(totalValue) }}</span>
        </h2>
      </div>
      <div 
        class="px-3 py-1.5 rounded-lg text-sm font-semibold flex items-center gap-1"
        :class="dayChange >= 0 ? 'bg-profit/15 text-profit' : 'bg-loss/15 text-loss'"
      >
        <svg class="w-4 h-4" :class="dayChange >= 0 ? '' : 'rotate-180'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 4l-8 8h5v8h6v-8h5z"/>
        </svg>
        {{ dayChange >= 0 ? '+' : '' }}{{ dayChangePct.toFixed(2) }}%
      </div>
    </div>

    <!-- Day Change -->
    <div class="flex items-center gap-2 mb-5">
      <span class="text-dark-hint text-sm">Today:</span>
      <span 
        class="font-mono font-semibold"
        :class="dayChange >= 0 ? 'text-profit' : 'text-loss'"
      >
        {{ dayChange >= 0 ? '+' : '' }}${{ formatNumber(Math.abs(dayChange)) }}
      </span>
    </div>

    <!-- Risk Gauge -->
    <div class="mt-4">
      <div class="flex justify-between items-center mb-2">
        <span class="text-sm text-dark-hint">Portfolio Risk</span>
        <span class="text-sm font-semibold" :class="riskColor">{{ riskLabel }}</span>
      </div>
      <div class="risk-gauge" :style="{ '--risk-level': riskLevel + '%' }"></div>
      <div class="flex justify-between text-xs text-dark-hint mt-1">
        <span>Low</span>
        <span>Moderate</span>
        <span>High</span>
      </div>
    </div>

    <!-- Mini Sparkline -->
    <div class="mt-5 h-16 relative overflow-hidden rounded-lg bg-dark-secondary">
      <svg class="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 40">
        <defs>
          <linearGradient id="sparkGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" :stop-color="dayChange >= 0 ? '#00d26a' : '#ff3b3b'" stop-opacity="0.2"/>
            <stop offset="100%" :stop-color="dayChange >= 0 ? '#00d26a' : '#ff3b3b'" stop-opacity="0"/>
          </linearGradient>
        </defs>
        <path 
          :d="sparklinePath" 
          fill="url(#sparkGradient)"
          class="transition-all duration-500"
        />
        <path 
          :d="sparklineStroke" 
          fill="none" 
          :stroke="dayChange >= 0 ? '#00d26a' : '#ff3b3b'" 
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="transition-all duration-500"
        />
      </svg>
      <!-- Animated dot at end -->
      <div 
        class="absolute w-2 h-2 rounded-full"
        :class="dayChange >= 0 ? 'bg-profit' : 'bg-loss'"
        :style="{ right: '4px', top: lastPointY + 'px' }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  totalValue: { type: Number, default: 0 },
  dayChange: { type: Number, default: 0 },
  dayChangePct: { type: Number, default: 0 },
  riskLevel: { type: Number, default: 50 },
})

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num)
}

const riskLabel = computed(() => {
  if (props.riskLevel < 25) return 'Low'
  if (props.riskLevel < 50) return 'Moderate'
  if (props.riskLevel < 75) return 'High'
  return 'Critical'
})

const riskColor = computed(() => {
  if (props.riskLevel < 25) return 'text-profit'
  if (props.riskLevel < 50) return 'text-warning'
  if (props.riskLevel < 75) return 'text-orange-500'
  return 'text-loss'
})

// Generate sparkline data
const sparklineData = [35, 32, 38, 30, 35, 42, 38, 45, 40, 48, 45, 50, 48, 55, 52]

const sparklineStroke = computed(() => {
  const width = 100
  const height = 40
  const padding = 2
  const dataLength = sparklineData.length
  const xStep = width / (dataLength - 1)
  
  const min = Math.min(...sparklineData)
  const max = Math.max(...sparklineData)
  const range = max - min || 1
  
  const points = sparklineData.map((val, i) => {
    const x = i * xStep
    const y = height - padding - ((val - min) / range) * (height - padding * 2)
    return `${x},${y}`
  })
  
  return `M${points.join(' L')}`
})

const sparklinePath = computed(() => {
  return sparklineStroke.value + ' L100,40 L0,40 Z'
})

const lastPointY = computed(() => {
  const min = Math.min(...sparklineData)
  const max = Math.max(...sparklineData)
  const range = max - min || 1
  const lastVal = sparklineData[sparklineData.length - 1]
  return 64 - ((lastVal - min) / range) * 60 - 6
})
</script>
