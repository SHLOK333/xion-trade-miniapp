<template>
  <Transition name="modal">
    <div 
      v-if="visible" 
      class="fixed inset-0 z-[100] flex items-end justify-center"
      @click.self="$emit('close')"
    >
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
      
      <!-- Modal Content -->
      <div class="relative w-full max-h-[85vh] bg-dark-card rounded-t-[32px] overflow-hidden animate-slide-up">
        <!-- Drag handle -->
        <div class="flex justify-center pt-3 pb-2">
          <div class="w-12 h-1 rounded-full bg-dark-border/50"></div>
        </div>
        
        <!-- Header -->
        <div class="px-6 pb-4 flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div 
              class="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-bold"
              :class="position.change >= 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'"
            >
              {{ position.symbol.substring(0, 2) }}
            </div>
            <div>
              <h2 class="text-xl font-bold text-white">{{ position.symbol }}</h2>
              <p class="text-tg-hint text-sm">{{ position.name }}</p>
            </div>
          </div>
          <button @click="$emit('close')" class="p-2 rounded-full bg-dark/50 text-tg-hint hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Price Section -->
        <div class="px-6 py-4 bg-dark/30">
          <div class="flex justify-between items-center">
            <div>
              <p class="text-3xl font-bold text-white">${{ position.currentPrice.toFixed(2) }}</p>
              <div class="flex items-center gap-2 mt-1">
                <span 
                  class="text-sm font-semibold"
                  :class="position.change >= 0 ? 'text-green-400' : 'text-red-400'"
                >
                  {{ position.change >= 0 ? '+' : '' }}{{ position.changePercent.toFixed(2) }}%
                </span>
                <span class="text-tg-hint text-sm">Today</span>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm text-tg-hint">Total P&L</p>
              <p 
                class="text-xl font-bold"
                :class="position.totalPnL >= 0 ? 'text-green-400' : 'text-red-400'"
              >
                {{ position.totalPnL >= 0 ? '+' : '' }}${{ position.totalPnL.toFixed(2) }}
              </p>
            </div>
          </div>
        </div>
        
        <!-- Interactive Chart -->
        <div class="px-6 py-4">
          <div class="flex gap-2 mb-4">
            <button 
              v-for="period in periods" 
              :key="period"
              @click="selectedPeriod = period"
              class="px-3 py-1 rounded-full text-xs font-medium transition-all"
              :class="selectedPeriod === period 
                ? 'bg-accent text-black' 
                : 'bg-dark/50 text-tg-hint hover:text-white'"
            >
              {{ period }}
            </button>
          </div>
          
          <!-- Chart Area -->
          <div class="h-48 bg-dark/30 rounded-2xl overflow-hidden">
            <canvas ref="chartCanvas"></canvas>
          </div>
        </div>
        
        <!-- Position Details Grid -->
        <div class="px-6 py-4">
          <h3 class="text-sm font-semibold text-tg-hint mb-3">Position Details</h3>
          <div class="grid grid-cols-2 gap-3">
            <div class="bg-dark/30 rounded-xl p-3">
              <p class="text-xs text-tg-hint">Shares</p>
              <p class="text-lg font-semibold text-white">{{ position.shares }}</p>
            </div>
            <div class="bg-dark/30 rounded-xl p-3">
              <p class="text-xs text-tg-hint">Avg Cost</p>
              <p class="text-lg font-semibold text-white">${{ position.avgCost.toFixed(2) }}</p>
            </div>
            <div class="bg-dark/30 rounded-xl p-3">
              <p class="text-xs text-tg-hint">Market Value</p>
              <p class="text-lg font-semibold text-white">${{ position.marketValue.toFixed(2) }}</p>
            </div>
            <div class="bg-dark/30 rounded-xl p-3">
              <p class="text-xs text-tg-hint">Cost Basis</p>
              <p class="text-lg font-semibold text-white">${{ position.costBasis.toFixed(2) }}</p>
            </div>
          </div>
        </div>
        
        <!-- AI Recommendation -->
        <div class="px-6 py-4" v-if="position.aiRecommendation">
          <div 
            class="rounded-2xl p-4"
            :class="{
              'bg-green-500/10 border border-green-500/30': position.aiRecommendation.action === 'HOLD',
              'bg-yellow-500/10 border border-yellow-500/30': position.aiRecommendation.action === 'REDUCE',
              'bg-red-500/10 border border-red-500/30': position.aiRecommendation.action === 'EXIT'
            }"
          >
            <div class="flex items-center gap-3 mb-2">
              <svg class="w-5 h-5 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              <span class="font-semibold text-white">AI Recommendation: {{ position.aiRecommendation.action }}</span>
            </div>
            <p class="text-sm text-tg-hint">{{ position.aiRecommendation.reason }}</p>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="px-6 py-6 pb-8 flex gap-3">
          <button class="flex-1 py-4 rounded-2xl bg-green-500 text-white font-semibold text-center hover:bg-green-600 transition-colors">
            Buy More
          </button>
          <button class="flex-1 py-4 rounded-2xl bg-red-500 text-white font-semibold text-center hover:bg-red-600 transition-colors">
            Sell
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  visible: { type: Boolean, default: false },
  position: { 
    type: Object, 
    default: () => ({
      symbol: 'AAPL',
      name: 'Apple Inc.',
      currentPrice: 178.50,
      change: 2.35,
      changePercent: 1.33,
      shares: 50,
      avgCost: 165.00,
      marketValue: 8925.00,
      costBasis: 8250.00,
      totalPnL: 675.00,
      aiRecommendation: {
        action: 'HOLD',
        reason: 'Strong fundamentals with consistent revenue growth. Current volatility within acceptable range.'
      }
    })
  }
})

defineEmits(['close'])

const periods = ['1D', '1W', '1M', '3M', '1Y', 'ALL']
const selectedPeriod = ref('1M')
const chartCanvas = ref(null)
let chartInstance = null

const generateChartData = (period) => {
  const points = period === '1D' ? 24 : period === '1W' ? 7 : period === '1M' ? 30 : period === '3M' ? 90 : 365
  const data = []
  let price = props.position.avgCost
  
  for (let i = 0; i < points; i++) {
    price = price * (1 + (Math.random() - 0.48) * 0.02)
    data.push(price)
  }
  
  // End at current price
  data[data.length - 1] = props.position.currentPrice
  return data
}

const createChart = () => {
  if (!chartCanvas.value) return
  
  if (chartInstance) {
    chartInstance.destroy()
  }
  
  const ctx = chartCanvas.value.getContext('2d')
  const data = generateChartData(selectedPeriod.value)
  const isPositive = data[data.length - 1] >= data[0]
  
  const gradient = ctx.createLinearGradient(0, 0, 0, 180)
  gradient.addColorStop(0, isPositive ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)')
  gradient.addColorStop(1, 'transparent')
  
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map((_, i) => i),
      datasets: [{
        data: data,
        borderColor: isPositive ? '#22c55e' : '#ef4444',
        borderWidth: 2,
        fill: true,
        backgroundColor: gradient,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: isPositive ? '#22c55e' : '#ef4444',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: isPositive ? '#22c55e' : '#ef4444',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => `$${ctx.raw.toFixed(2)}`
          }
        }
      },
      scales: {
        x: { display: false },
        y: { display: false }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  })
}

watch(selectedPeriod, () => {
  nextTick(() => createChart())
})

watch(() => props.visible, (newVal) => {
  if (newVal) {
    nextTick(() => createChart())
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from .absolute,
.modal-leave-to .absolute {
  opacity: 0;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: translateY(100%);
}

.safe-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
