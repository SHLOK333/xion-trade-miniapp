<template>
  <div class="bg-dark-card border border-dark-border rounded-xl p-5">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold text-dark-text">Portfolio Performance</h3>
      <div class="flex gap-1">
        <button 
          v-for="period in periods" 
          :key="period.value"
          @click="selectedPeriod = period.value"
          class="px-3 py-1 rounded-lg text-xs font-medium transition-all"
          :class="selectedPeriod === period.value 
            ? 'bg-profit text-dark' 
            : 'bg-dark-secondary text-dark-hint hover:bg-dark-border'"
        >
          {{ period.label }}
        </button>
      </div>
    </div>

    <!-- Main Chart -->
    <div class="chart-container" ref="chartContainer">
      <canvas ref="chartCanvas"></canvas>
    </div>

    <!-- Stats below chart -->
    <div class="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-dark-border">
      <div class="text-center">
        <p class="text-xs text-dark-hint mb-1">High</p>
        <p class="font-mono font-semibold text-profit">${{ formatNumber(stats.high) }}</p>
      </div>
      <div class="text-center">
        <p class="text-xs text-dark-hint mb-1">Low</p>
        <p class="font-mono font-semibold text-loss">${{ formatNumber(stats.low) }}</p>
      </div>
      <div class="text-center">
        <p class="text-xs text-dark-hint mb-1">Avg</p>
        <p class="font-mono font-semibold text-dark-text">${{ formatNumber(stats.avg) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  data: { type: Object, required: true }
})

const chartContainer = ref(null)
const chartCanvas = ref(null)
const selectedPeriod = ref('1W')
let chartInstance = null

const periods = [
  { label: '1D', value: '1D' },
  { label: '1W', value: '1W' },
  { label: '1M', value: '1M' },
  { label: '3M', value: '3M' },
  { label: '1Y', value: '1Y' },
]

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num)
}

const stats = computed(() => {
  const values = props.data.values
  return {
    high: Math.max(...values),
    low: Math.min(...values),
    avg: values.reduce((a, b) => a + b, 0) / values.length,
  }
})

const createChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  
  // Create gradient
  const gradient = ctx.createLinearGradient(0, 0, 0, 200)
  gradient.addColorStop(0, 'rgba(108, 92, 231, 0.4)')
  gradient.addColorStop(0.5, 'rgba(108, 92, 231, 0.1)')
  gradient.addColorStop(1, 'rgba(108, 92, 231, 0)')

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: props.data.labels,
      datasets: [{
        data: props.data.values,
        borderColor: '#6c5ce7',
        borderWidth: 3,
        fill: true,
        backgroundColor: gradient,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#6c5ce7',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index',
      },
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
          displayColors: false,
          titleFont: { weight: '600' },
          callbacks: {
            label: (ctx) => `$${ctx.parsed.y.toLocaleString()}`
          }
        }
      },
      scales: {
        x: {
          display: true,
          grid: { display: false },
          ticks: {
            color: 'rgba(122, 122, 140, 0.7)',
            font: { size: 10 }
          },
          border: { display: false }
        },
        y: {
          display: true,
          position: 'right',
          grid: {
            color: 'rgba(45, 45, 68, 0.5)',
            drawBorder: false,
          },
          ticks: {
            color: 'rgba(122, 122, 140, 0.7)',
            font: { size: 10 },
            callback: (val) => '$' + (val / 1000) + 'k'
          },
          border: { display: false }
        }
      }
    }
  })
}

onMounted(() => {
  createChart()
})

watch(() => props.data, () => {
  createChart()
}, { deep: true })

watch(selectedPeriod, () => {
  // TODO: Fetch new data based on period
  console.log('Period changed:', selectedPeriod.value)
})
</script>
