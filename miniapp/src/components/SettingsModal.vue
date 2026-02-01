<template>
  <Transition name="slide">
    <div 
      v-if="visible" 
      class="fixed inset-0 z-[100]"
      @click.self="$emit('close')"
    >
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="$emit('close')"></div>
      
      <!-- Panel -->
      <div class="absolute right-0 top-0 bottom-0 w-80 bg-dark-card shadow-2xl animate-slide-in">
        <!-- Header -->
        <div class="p-6 border-b border-dark-border/30">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-bold text-white">Settings</h2>
            <button @click="$emit('close')" class="p-2 rounded-full bg-dark/50 text-tg-hint hover:text-white">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Settings Content -->
        <div class="p-6 space-y-6 overflow-y-auto h-[calc(100%-80px)]">
          <!-- Risk Tolerance -->
          <div>
            <h3 class="text-sm font-semibold text-white mb-3">Risk Tolerance</h3>
            <div class="grid grid-cols-3 gap-2">
              <button 
                v-for="level in riskLevels" 
                :key="level.id"
                @click="settings.riskLevel = level.id"
                class="py-2 px-3 rounded-xl text-sm font-medium transition-all"
                :class="settings.riskLevel === level.id 
                  ? level.activeClass 
                  : 'bg-dark/50 text-tg-hint hover:text-white'"
              >
                {{ level.label }}
              </button>
            </div>
          </div>
          
          <!-- Notifications -->
          <div>
            <h3 class="text-sm font-semibold text-white mb-3">Notifications</h3>
            <div class="space-y-3">
              <div 
                v-for="notification in notifications" 
                :key="notification.id"
                class="flex items-center justify-between p-3 bg-dark/30 rounded-xl"
              >
                <div>
                  <p class="text-sm font-medium text-white">{{ notification.label }}</p>
                  <p class="text-xs text-tg-hint">{{ notification.description }}</p>
                </div>
                <button 
                  @click="notification.enabled = !notification.enabled"
                  class="w-12 h-6 rounded-full transition-colors relative"
                  :class="notification.enabled ? 'bg-accent' : 'bg-dark-border'"
                >
                  <span 
                    class="absolute top-1 w-4 h-4 rounded-full bg-white transition-transform"
                    :class="notification.enabled ? 'left-7' : 'left-1'"
                  ></span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Auto Trading -->
          <div>
            <h3 class="text-sm font-semibold text-white mb-3">Auto Trading</h3>
            <div class="bg-dark/30 rounded-xl p-4">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <p class="text-sm font-medium text-white">Enable Auto-Rebalance</p>
                  <p class="text-xs text-tg-hint">Automatically rebalance portfolio</p>
                </div>
                <button 
                  @click="settings.autoRebalance = !settings.autoRebalance"
                  class="w-12 h-6 rounded-full transition-colors relative"
                  :class="settings.autoRebalance ? 'bg-accent' : 'bg-dark-border'"
                >
                  <span 
                    class="absolute top-1 w-4 h-4 rounded-full bg-white transition-transform"
                    :class="settings.autoRebalance ? 'left-7' : 'left-1'"
                  ></span>
                </button>
              </div>
              
              <div v-if="settings.autoRebalance" class="space-y-3 pt-3 border-t border-dark-border/30">
                <div>
                  <label class="text-xs text-tg-hint">Max Daily Trades</label>
                  <input 
                    type="range" 
                    v-model="settings.maxDailyTrades" 
                    min="1" 
                    max="20"
                    class="w-full mt-1 accent-accent"
                  />
                  <p class="text-sm text-white text-right">{{ settings.maxDailyTrades }} trades</p>
                </div>
                
                <div>
                  <label class="text-xs text-tg-hint">Stop Loss Threshold</label>
                  <input 
                    type="range" 
                    v-model="settings.stopLoss" 
                    min="5" 
                    max="30"
                    class="w-full mt-1 accent-accent"
                  />
                  <p class="text-sm text-white text-right">-{{ settings.stopLoss }}%</p>
                </div>
                
                <div>
                  <label class="text-xs text-tg-hint">Take Profit Threshold</label>
                  <input 
                    type="range" 
                    v-model="settings.takeProfit" 
                    min="10" 
                    max="100"
                    class="w-full mt-1 accent-accent"
                  />
                  <p class="text-sm text-white text-right">+{{ settings.takeProfit }}%</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- AI Preferences -->
          <div>
            <h3 class="text-sm font-semibold text-white mb-3">AI Preferences</h3>
            <div class="space-y-3">
              <div class="p-3 bg-dark/30 rounded-xl">
                <label class="text-xs text-tg-hint">Preferred AI Model</label>
                <select 
                  v-model="settings.aiModel"
                  class="w-full mt-2 p-2 bg-dark rounded-lg text-white border border-dark-border focus:border-accent outline-none"
                >
                  <option value="gpt-4o-mini">GPT-4o Mini (Fast)</option>
                  <option value="gpt-4o">GPT-4o (Powerful)</option>
                  <option value="claude-3">Claude 3 Sonnet</option>
                </select>
              </div>
              
              <div class="p-3 bg-dark/30 rounded-xl">
                <label class="text-xs text-tg-hint">Analysis Style</label>
                <div class="grid grid-cols-2 gap-2 mt-2">
                  <button 
                    v-for="style in analysisStyles" 
                    :key="style"
                    @click="settings.analysisStyle = style"
                    class="py-2 px-3 rounded-lg text-sm font-medium transition-all"
                    :class="settings.analysisStyle === style 
                      ? 'bg-accent text-black' 
                      : 'bg-dark text-tg-hint hover:text-white'"
                  >
                    {{ style }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- About -->
          <div class="pt-4 border-t border-dark-border/30">
            <div class="text-center">
              <p class="text-sm text-tg-hint">Paper Profit v1.0</p>
              <p class="text-xs text-tg-hint mt-1">AI-Powered Trading Assistant</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { reactive } from 'vue'

defineProps({
  visible: { type: Boolean, default: false }
})

defineEmits(['close'])

const settings = reactive({
  riskLevel: 'moderate',
  autoRebalance: false,
  maxDailyTrades: 10,
  stopLoss: 15,
  takeProfit: 30,
  aiModel: 'gpt-4o-mini',
  analysisStyle: 'Balanced'
})

const riskLevels = [
  { id: 'low', label: 'Low', activeClass: 'bg-green-500 text-white' },
  { id: 'moderate', label: 'Moderate', activeClass: 'bg-yellow-500 text-black' },
  { id: 'high', label: 'High', activeClass: 'bg-red-500 text-white' },
]

const notifications = reactive([
  { id: 'price', label: 'Price Alerts', description: 'Get notified on price changes', enabled: true },
  { id: 'ai', label: 'AI Recommendations', description: 'Receive AI trading signals', enabled: true },
  { id: 'risk', label: 'Risk Warnings', description: 'Alerts for high-risk situations', enabled: true },
  { id: 'market', label: 'Market News', description: 'Important market updates', enabled: false },
])

const analysisStyles = ['Conservative', 'Balanced', 'Aggressive', 'Technical']
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from .absolute:first-child,
.slide-leave-to .absolute:first-child {
  opacity: 0;
}

.slide-enter-from .absolute:last-child,
.slide-leave-to .absolute:last-child {
  transform: translateX(100%);
}

.animate-slide-in {
  animation: slideIn 0.3s ease forwards;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
</style>
