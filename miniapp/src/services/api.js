/**
 * API Service for XION Trade Mini App
 * Connects to the FastAPI backend
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'

class ApiService {
  constructor() {
    this.baseUrl = API_BASE
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error)
      throw error
    }
  }

  // =====================
  // Portfolio Endpoints
  // =====================

  async getPortfolio(accountId = 1) {
    return this.request(`/api/accounts/${accountId}/positions`)
  }

  async getPortfolioSummary(accountId = 1) {
    return this.request(`/api/accounts/${accountId}/summary`)
  }

  async getAccount(accountId = 1) {
    return this.request(`/api/accounts/${accountId}`)
  }

  // =====================
  // Risk Management
  // =====================

  async getPortfolioRisk(accountId = 1) {
    return this.request(`/api/risk/portfolio/${accountId}`)
  }

  async getPositionAdvice(symbol, accountId = 1) {
    return this.request(`/api/risk/position/${symbol}/advice?account_id=${accountId}`)
  }

  async getOptimalAllocation(accountId = 1, riskTolerance = 'moderate') {
    return this.request(`/api/risk/portfolio/${accountId}/allocation?risk_tolerance=${riskTolerance}`)
  }

  async getRebalanceRecommendations(accountId = 1) {
    return this.request(`/api/risk/portfolio/${accountId}/rebalance`)
  }

  // =====================
  // Rebalancer Endpoints
  // =====================

  async getRebalancerStatus() {
    return this.request('/api/rebalance/status')
  }

  async startRebalancer(accountId = 1) {
    return this.request('/api/rebalance/start', {
      method: 'POST',
      body: JSON.stringify({ account_id: accountId }),
    })
  }

  async stopRebalancer() {
    return this.request('/api/rebalance/stop', { method: 'POST' })
  }

  async getRecentTrades() {
    return this.request('/api/rebalance/trades')
  }

  // =====================
  // Market Data
  // =====================

  async getStockPrice(symbol) {
    return this.request(`/api/stock/${symbol}/price`)
  }

  async getStockAnalysis(symbol) {
    return this.request(`/api/stock/${symbol}/analysis`)
  }

  async getMarketHours() {
    return this.request('/api/market/hours')
  }

  // =====================
  // AI Analysis
  // =====================

  async getAIAnalysis(symbol, question = null) {
    const params = new URLSearchParams({ symbol })
    if (question) params.append('question', question)
    
    return this.request(`/api/ai/analyze?${params}`)
  }

  async getThreeWayDebate(symbol) {
    return this.request(`/api/ai/debate/${symbol}`)
  }

  // =====================
  // Strategies
  // =====================

  async getStrategies() {
    return this.request('/api/strategies')
  }

  async getStrategy(strategyId) {
    return this.request(`/api/strategies/${strategyId}`)
  }

  // =====================
  // Alerts
  // =====================

  async getAlerts(accountId = 1) {
    return this.request(`/api/alerts/${accountId}`)
  }

  async dismissAlert(alertId) {
    return this.request(`/api/alerts/${alertId}/dismiss`, { method: 'POST' })
  }
}

// Singleton instance
const api = new ApiService()

export default api
export { api, ApiService }
