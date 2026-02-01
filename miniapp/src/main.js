import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

// Initialize Telegram WebApp
const tg = window.Telegram?.WebApp

if (tg) {
  tg.ready()
  tg.expand()
  tg.enableClosingConfirmation()
  
  // Set header color
  tg.setHeaderColor('#0f0f23')
  tg.setBackgroundColor('#0f0f23')
}

// Create and mount app
const app = createApp(App)

// Global properties
app.config.globalProperties.$tg = tg
app.config.globalProperties.$user = tg?.initDataUnsafe?.user || {
  id: 'demo',
  first_name: 'Demo',
  username: 'demo_user'
}

app.mount('#app')

// Hide loading screen
setTimeout(() => {
  const loading = document.getElementById('loading')
  if (loading) {
    loading.style.opacity = '0'
    loading.style.transition = 'opacity 0.5s'
    setTimeout(() => loading.remove(), 500)
  }
}, 1000)
