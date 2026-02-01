<template>
  <div class="min-h-screen bg-dark text-dark-text">
    <!-- Header -->
    <header class="sticky top-0 z-40 bg-dark border-b border-dark-border safe-top">
      <div class="flex items-center justify-between px-4 py-3">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-profit flex items-center justify-center">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.5">
              <path d="M3 17L9 11L13 15L21 7" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M17 7H21V11" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <h1 class="text-base font-semibold text-dark-text">XION Trade</h1>
            <p class="text-xs text-dark-hint">Risk-Aware Trading</p>
          </div>
        </div>
        <button @click="showSettings = true" class="p-2 rounded-lg hover:bg-dark-secondary transition-colors">
          <svg class="w-5 h-5 text-dark-hint" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="pb-24">
      <!-- Portfolio Summary Card -->
      <PortfolioSummary 
        :totalValue="portfolio.totalValue"
        :dayChange="portfolio.dayChange"
        :dayChangePct="portfolio.dayChangePct"
        :riskLevel="portfolio.riskLevel"
      />

      <!-- Quick Actions -->
      <QuickActions @action="handleQuickAction" />

      <!-- Tab Navigation -->
      <div class="sticky top-16 z-30 bg-dark border-b border-dark-border">
        <div class="flex px-4 relative">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            class="flex-1 py-3 text-sm font-medium transition-colors relative"
            :class="activeTab === tab.id ? 'text-profit' : 'text-dark-hint'"
          >
            {{ tab.label }}
          </button>
          <div 
            class="tab-indicator"
            :style="{ 
              width: `${100 / tabs.length}%`, 
              left: `${(tabs.findIndex(t => t.id === activeTab) * 100) / tabs.length}%` 
            }"
          ></div>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="px-4 py-4">
        <!-- Positions Tab -->
        <div v-if="activeTab === 'positions'" class="space-y-3 animate-fade-in">
          <PositionCard 
            v-for="position in positions" 
            :key="position.symbol"
            :position="position"
            @click="openPosition(position)"
          />
        </div>

        <!-- Charts Tab -->
        <div v-if="activeTab === 'charts'" class="space-y-4 animate-fade-in">
          <PortfolioChart :data="chartData" />
          <AllocationChart :positions="positions" />
        </div>

        <!-- AI Tab -->
        <div v-if="activeTab === 'ai'" class="space-y-4 animate-fade-in">
          <AIAdvisor :portfolio="portfolio" :positions="positions" />
        </div>

        <!-- Alerts Tab -->
        <div v-if="activeTab === 'alerts'" class="space-y-3 animate-fade-in">
          <AlertCard v-for="alert in alerts" :key="alert.id" :alert="alert" />
        </div>
      </div>
    </main>

    <!-- Bottom Navigation -->
    <BottomNav :activeTab="activeTab" @change="activeTab = $event" />

    <!-- Floating AI Button -->
    <button 
      @click="openAIChat" 
      class="fab"
      v-if="activeTab !== 'ai'"
    >
      <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2">
        <path d="M12 2a10 10 0 0110 10c0 5.523-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2z"/>
        <path d="M8 12h.01M12 12h.01M16 12h.01"/>
      </svg>
    </button>

    <!-- Position Detail Modal -->
    <PositionModal 
      :visible="!!selectedPosition"
      :position="selectedPosition || defaultPosition"
      @close="selectedPosition = null"
    />

    <!-- Settings Modal -->
    <SettingsModal :visible="showSettings" @close="showSettings = false" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import PortfolioSummary from './components/PortfolioSummary.vue'
import QuickActions from './components/QuickActions.vue'
import PositionCard from './components/PositionCard.vue'
import PortfolioChart from './components/PortfolioChart.vue'
import AllocationChart from './components/AllocationChart.vue'
import AIAdvisor from './components/AIAdvisor.vue'
import AlertCard from './components/AlertCard.vue'
import BottomNav from './components/BottomNav.vue'
import PositionModal from './components/PositionModal.vue'
import SettingsModal from './components/SettingsModal.vue'
import api from './services/api'

const tg = window.Telegram?.WebApp

// State
const activeTab = ref('positions')
const selectedPosition = ref(null)
const showSettings = ref(false)
const isLoading = ref(true)

// Default position for modal
const defaultPosition = {
  symbol: 'AAPL',
  name: 'Apple Inc.',
  currentPrice: 178.50,
  change: 0,
  changePercent: 0,
  shares: 0,
  avgCost: 0,
  marketValue: 0,
  costBasis: 0,
  totalPnL: 0
}

const tabs = [
  { id: 'positions', label: 'Positions' },
  { id: 'charts', label: 'Charts' },
  { id: 'ai', label: 'AI Advisor' },
  { id: 'alerts', label: 'Alerts' },
]

// Portfolio data
const portfolio = reactive({
  totalValue: 125430.50,
  dayChange: 1234.56,
  dayChangePct: 0.99,
  riskLevel: 35, // 0-100
  cash: 15000,
  invested: 110430.50,
})

// Positions
const positions = ref([
  {
    symbol: 'AAPL',
    name: 'Apple Inc.',
    quantity: 50,
    avgPrice: 175.00,
    currentPrice: 189.50,
    value: 9475.00,
    pnl: 725.00,
    pnlPct: 8.29,
    dayChange: 2.35,
    dayChangePct: 1.26,
    riskLevel: 'low',
    action: 'hold',
    strategy: 'value_investing',
  },
  {
    symbol: 'NVDA',
    name: 'NVIDIA Corp.',
    quantity: 20,
    avgPrice: 450.00,
    currentPrice: 875.00,
    value: 17500.00,
    pnl: 8500.00,
    pnlPct: 94.44,
    dayChange: -12.50,
    dayChangePct: -1.41,
    riskLevel: 'moderate',
    action: 'reduce',
    strategy: 'growth_investing',
  },
  {
    symbol: 'TSLA',
    name: 'Tesla Inc.',
    quantity: 30,
    avgPrice: 280.00,
    currentPrice: 245.00,
    value: 7350.00,
    pnl: -1050.00,
    pnlPct: -12.50,
    dayChange: -8.25,
    dayChangePct: -3.26,
    riskLevel: 'high',
    action: 'exit',
    strategy: 'momentum_trading',
  },
  {
    symbol: 'MSFT',
    name: 'Microsoft Corp.',
    quantity: 25,
    avgPrice: 380.00,
    currentPrice: 415.00,
    value: 10375.00,
    pnl: 875.00,
    pnlPct: 9.21,
    dayChange: 3.50,
    dayChangePct: 0.85,
    riskLevel: 'low',
    action: 'hold',
    strategy: 'dividend_growth',
  },
])

// Chart data
const chartData = ref({
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  values: [120000, 122500, 121000, 124500, 123000, 125000, 125430],
})

// Alerts
const alerts = ref([
  {
    id: 1,
    type: 'warning',
    title: 'TSLA Stop-Loss Alert',
    message: 'Position down 12.5%. Consider exiting.',
    time: '2 min ago',
    urgency: 'high',
  },
  {
    id: 2,
    type: 'success',
    title: 'NVDA Take-Profit',
    message: 'Position up 94%. Consider taking profits.',
    time: '15 min ago',
    urgency: 'medium',
  },
  {
    id: 3,
    type: 'info',
    title: 'Portfolio Rebalance',
    message: 'NVDA concentration at 32%. Reduce recommended.',
    time: '1 hour ago',
    urgency: 'low',
  },
])

// Methods
const openPosition = (position) => {
  selectedPosition.value = position
  tg?.HapticFeedback?.impactOccurred('light')
}

const openAIChat = () => {
  activeTab.value = 'ai'
  tg?.HapticFeedback?.impactOccurred('medium')
}

const handleQuickAction = (action) => {
  tg?.HapticFeedback?.impactOccurred('medium')
  console.log('Quick action:', action)
}

const handlePositionAction = (action, position) => {
  tg?.HapticFeedback?.notificationOccurred('success')
  console.log('Position action:', action, position)
  selectedPosition.value = null
}

// Fetch real data from API
const fetchPortfolioData = async () => {
  try {
    isLoading.value = true
    
    // Fetch portfolio positions
    const portfolioData = await api.getPortfolio(1)
    if (portfolioData && portfolioData.positions) {
      positions.value = portfolioData.positions.map(p => ({
        symbol: p.symbol,
        name: p.name || p.symbol,
        quantity: p.quantity,
        avgPrice: p.avg_price,
        currentPrice: p.current_price,
        value: p.market_value,
        pnl: p.unrealized_pnl,
        pnlPct: p.unrealized_pnl_pct,
        dayChange: p.day_change || 0,
        dayChangePct: p.day_change_pct || 0,
        riskLevel: p.risk_level || 'moderate',
        action: p.recommended_action || 'hold',
        strategy: p.strategy || 'value_investing',
      }))
      
      // Update portfolio summary
      portfolio.totalValue = portfolioData.total_value || portfolio.totalValue
      portfolio.dayChange = portfolioData.day_change || portfolio.dayChange
      portfolio.dayChangePct = portfolioData.day_change_pct || portfolio.dayChangePct
    }
    
    // Fetch alerts
    try {
      const alertsData = await api.getAlerts(1)
      if (alertsData && alertsData.alerts) {
        alerts.value = alertsData.alerts.map((a, i) => ({
          id: a.id || i,
          type: a.type || 'info',
          title: a.title,
          message: a.message,
          time: a.time || 'Just now',
          urgency: a.urgency || 'low',
        }))
      }
    } catch (err) {
      console.log('Alerts not available')
    }
    
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    isLoading.value = false
  }
}

// Fetch real data on mount
onMounted(async () => {
  console.log('Mini app mounted')
  
  // Setup Telegram theme
  if (tg) {
    tg.ready()
    tg.expand()
  }
  
  // Fetch data
  await fetchPortfolioData()
  
  // Refresh every 60 seconds
  setInterval(fetchPortfolioData, 60000)
})
</script>
