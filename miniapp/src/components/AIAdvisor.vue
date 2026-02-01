<template>
  <div class="space-y-4">
    <!-- AI Status Card -->
    <div class="glass-card p-5">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
          <svg class="w-7 h-7 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
        </div>
        <div>
          <h3 class="font-semibold">AI Advisor</h3>
          <p class="text-xs text-tg-hint">3-way debate system</p>
        </div>
        <div class="ml-auto">
          <span class="px-2 py-1 rounded-full text-xs font-medium bg-profit/20 text-profit flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-profit animate-pulse"></span>
            Active
          </span>
        </div>
      </div>

      <!-- Quick Analysis Input -->
      <div class="relative mb-4">
        <input 
          v-model="query"
          @keyup.enter="analyzeQuery"
          type="text"
          placeholder="Ask about any stock or strategy..."
          class="w-full px-4 py-3 rounded-xl bg-dark-border/30 border border-dark-border/50 text-white placeholder-tg-hint focus:outline-none focus:border-accent transition-colors"
        />
        <button 
          @click="analyzeQuery"
          class="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-accent text-white"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <!-- Quick Action Chips -->
      <div class="flex flex-wrap gap-2">
        <button 
          v-for="chip in quickChips" 
          :key="chip"
          @click="query = chip; analyzeQuery()"
          class="px-3 py-1.5 rounded-full text-xs font-medium bg-dark-border/30 text-tg-hint hover:bg-dark-border/50 transition-colors"
        >
          {{ chip }}
        </button>
      </div>
    </div>

    <!-- Portfolio Assessment -->
    <div class="glass-card p-5">
      <h4 class="font-semibold mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Portfolio Assessment
      </h4>

      <!-- AI Debate Results -->
      <div class="space-y-3">
        <div 
          v-for="analyst in analysts" 
          :key="analyst.type"
          class="p-3 rounded-xl bg-dark-border/20 border border-dark-border/30"
        >
          <div class="flex items-center gap-2 mb-2">
            <div 
              class="w-8 h-8 rounded-lg flex items-center justify-center"
              :class="analyst.bgClass"
            >
              {{ analyst.emoji }}
            </div>
            <div>
              <p class="text-sm font-medium">{{ analyst.name }}</p>
              <p class="text-xs text-tg-hint">{{ analyst.stance }}</p>
            </div>
          </div>
          <p class="text-sm text-tg-hint leading-relaxed">{{ analyst.opinion }}</p>
        </div>
      </div>

      <!-- Final Verdict -->
      <div class="mt-4 p-4 rounded-xl bg-accent/10 border border-accent/30">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p class="font-semibold text-accent">Final Verdict</p>
        </div>
        <p class="text-sm">{{ finalVerdict }}</p>
      </div>
    </div>

    <!-- Recommended Actions -->
    <div class="glass-card p-5">
      <h4 class="font-semibold mb-4">Recommended Actions</h4>
      
      <div class="space-y-3">
        <div 
          v-for="action in recommendedActions" 
          :key="action.symbol"
          class="flex items-center justify-between p-3 rounded-xl bg-dark-border/20"
        >
          <div class="flex items-center gap-3">
            <div 
              class="w-10 h-10 rounded-lg flex items-center justify-center text-white text-sm font-bold"
              :class="action.actionClass"
            >
              {{ action.symbol.slice(0, 2) }}
            </div>
            <div>
              <p class="font-medium">{{ action.symbol }}</p>
              <p class="text-xs text-tg-hint">{{ action.reason }}</p>
            </div>
          </div>
          <button 
            @click="executeAction(action)"
            class="px-3 py-1.5 rounded-lg text-sm font-medium"
            :class="action.buttonClass"
          >
            {{ action.action }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  portfolio: { type: Object, required: true },
  positions: { type: Array, required: true }
})

const query = ref('')
const quickChips = [
  'Analyze TSLA',
  'Should I hold NVDA?',
  'Rebalance portfolio',
  'Best strategy now?',
]

const analysts = [
  {
    type: 'aggressive',
    name: 'Bull Analyst',
    emoji: '🐂',
    stance: 'Aggressive View',
    bgClass: 'bg-profit/20',
    opinion: 'NVDA gains are strong but momentum continues. Hold for further upside. TSLA is oversold and could bounce.'
  },
  {
    type: 'neutral',
    name: 'Neutral Analyst',
    emoji: '⚖️',
    stance: 'Balanced View',
    bgClass: 'bg-accent/20',
    opinion: 'Consider taking partial profits on NVDA to reduce concentration. TSLA requires careful monitoring.'
  },
  {
    type: 'conservative',
    name: 'Bear Analyst',
    emoji: '🐻',
    stance: 'Conservative View',
    bgClass: 'bg-loss/20',
    opinion: 'TSLA is showing weakness - cut losses now. NVDA is overextended at 94% gain, take profits immediately.'
  },
]

const finalVerdict = ref('Reduce NVDA by 30% to lock in profits and improve diversification. Exit TSLA to stop further losses. Hold AAPL and MSFT as core positions.')

const recommendedActions = ref([
  {
    symbol: 'NVDA',
    action: 'REDUCE',
    reason: 'Take profits at +94%',
    actionClass: 'bg-warning',
    buttonClass: 'bg-warning/20 text-warning',
  },
  {
    symbol: 'TSLA',
    action: 'EXIT',
    reason: 'Stop loss at -12.5%',
    actionClass: 'bg-loss',
    buttonClass: 'bg-loss/20 text-loss',
  },
  {
    symbol: 'AAPL',
    action: 'HOLD',
    reason: 'Within target range',
    actionClass: 'bg-profit',
    buttonClass: 'bg-profit/20 text-profit',
  },
])

const analyzeQuery = () => {
  if (!query.value.trim()) return
  console.log('Analyzing:', query.value)
  // TODO: Call AI API
  query.value = ''
}

const executeAction = (action) => {
  console.log('Executing:', action)
  // TODO: Execute trade
}
</script>
