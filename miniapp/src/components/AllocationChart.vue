<template>
  <div class="glass-card p-5">
    <h3 class="font-semibold mb-4">Asset Allocation</h3>

    <!-- Donut Chart -->
    <div class="relative flex justify-center items-center h-48">
      <canvas ref="chartCanvas" class="max-w-[200px]"></canvas>
      
      <!-- Center text -->
      <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <p class="text-xs text-tg-hint">Total</p>
        <p class="text-xl font-bold font-mono">${{ formatNumber(totalValue) }}</p>
      </div>
    </div>

    <!-- Legend -->
    <div class="grid grid-cols-2 gap-3 mt-4">
      <div 
        v-for="(item, index) in allocationData" 
        :key="item.symbol"
        class="flex items-center gap-2 p-2 rounded-lg bg-dark-border/20"
      >
        <div 
          class="w-3 h-3 rounded-full"
          :style="{ backgroundColor: colors[index] }"
        ></div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium truncate">{{ item.symbol }}</p>
          <p class="text-xs text-tg-hint">{{ item.percentage.toFixed(1) }}%</p>
        </div>
        <p class="text-xs font-mono text-tg-hint">${{ formatNumber(item.value) }}</p>
      </div>
    </div>

    <!-- Concentration Warning -->
    <div 
      v-if="concentrationWarning"
      class="mt-4 p-3 rounded-xl bg-warning/10 border border-warning/30 flex items-center gap-3"
    >
      <svg class="w-5 h-5 text-warning flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
      </svg>
      <p class="text-sm text-warning">{{ concentrationWarning }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  positions: { type: Array, required: true }
})

const chartCanvas = ref(null)
let chartInstance = null

const colors = [
  '#6c5ce7', // Purple
  '#00d26a', // Green
  '#ff4757', // Red
  '#ffa502', // Orange
  '#1e90ff', // Blue
  '#ff6b81', // Pink
  '#2ed573', // Light green
  '#ff9f43', // Light orange
]

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num)
}

const totalValue = computed(() => {
  return props.positions.reduce((sum, p) => sum + p.value, 0)
})

const allocationData = computed(() => {
  return props.positions.map(p => ({
    symbol: p.symbol,
    value: p.value,
    percentage: (p.value / totalValue.value) * 100
  })).sort((a, b) => b.value - a.value)
})

const concentrationWarning = computed(() => {
  const highConcentration = allocationData.value.find(a => a.percentage > 25)
  if (highConcentration) {
    return `${highConcentration.symbol} is ${highConcentration.percentage.toFixed(1)}% of portfolio. Consider reducing.`
  }
  return null
})

const createChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')

  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: allocationData.value.map(a => a.symbol),
      datasets: [{
        data: allocationData.value.map(a => a.value),
        backgroundColor: colors.slice(0, allocationData.value.length),
        borderColor: '#1a1a2e',
        borderWidth: 3,
        hoverBorderColor: '#fff',
        hoverBorderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(26, 26, 46, 0.95)',
          titleColor: '#fff',
          bodyColor: '#a29bfe',
          borderColor: 'rgba(108, 92, 231, 0.3)',
          borderWidth: 1,
          cornerRadius: 8,
          padding: 12,
          displayColors: true,
          callbacks: {
            label: (ctx) => {
              const percentage = ((ctx.raw / totalValue.value) * 100).toFixed(1)
              return ` $${ctx.raw.toLocaleString()} (${percentage}%)`
            }
          }
        }
      },
      animation: {
        animateRotate: true,
        animateScale: true,
      }
    }
  })
}

onMounted(() => {
  createChart()
})

watch(() => props.positions, () => {
  createChart()
}, { deep: true })
</script>
