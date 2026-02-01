# Paper Profit - Continuous Decision-Making for Risk-Aware Trading

## 🎯 Hackathon Problem Statement Mapping

| Requirement | Implementation | API Endpoint |
|-------------|----------------|--------------|
| **Continuously assess risk** for open positions | ✅ `PortfolioRiskService` | `GET /api/risk/portfolio/{account_id}` |
| **Track positions & estimate risk/return** | ✅ `PositionRiskAssessment` | `GET /api/risk/position/{account_id}/{symbol}` |
| **Recommend: hold, reduce, exit, reallocate** | ✅ 4 action types + AI debate | `POST /api/ai/position-debate/{symbol}` |
| **Manage multiple positions together** | ✅ Portfolio-level analysis | `POST /api/ai/portfolio-recommendations/{account_id}` |
| **Capital reallocation suggestions** | ✅ `ReallocationSuggestion` | `POST /api/risk/reallocation/{account_id}` |
| **Reasoning and adaptability** (not fixed strategies) | ✅ 3-way AI debate system | Aggressive/Neutral/Conservative views |

---

## 📡 Complete API Reference

### 1. Portfolio Risk Management APIs

#### `GET /api/risk/portfolio/{account_id}`
**Continuously assess risk, capital, and potential returns for all open positions**

Response:
```json
{
  "account_id": "acc_123",
  "total_value": 100000,
  "cash_available": 20000,
  "invested_value": 80000,
  "overall_risk_level": "moderate",
  "diversification_score": 70,
  "concentration_warning": false,
  "capital_at_risk": 5000,
  "rebalance_needed": true,
  "positions": [...],
  "suggested_actions": [
    {"priority": 1, "symbol": "TSLA", "action": "reduce", "reason": "Position too concentrated"}
  ]
}
```

#### `GET /api/risk/position/{account_id}/{symbol}`
**Get detailed risk assessment for a specific position**

#### `POST /api/risk/reallocation/{account_id}`
**Get capital reallocation suggestions**

Request:
```json
{
  "opportunities": [
    {"symbol": "NVDA", "reason": "AI sector growth", "expected_return": "20%", "risk_level": "moderate"}
  ]
}
```

---

### 2. AI Position Advisor APIs (3-Way Debate System)

#### `POST /api/ai/position-debate/{symbol}`
**Analyze position using 3-way AI risk debate**

Request:
```json
{
  "entry_price": 150.0,
  "current_price": 165.0,
  "quantity": 100,
  "days_held": 30,
  "concentration": 15.0,
  "market_context": {
    "trend": "bullish",
    "volatility": "high",
    "sector_performance": "positive"
  }
}
```

Response:
```json
{
  "symbol": "AAPL",
  "final_decision": "hold",
  "risk_score": 35,
  "arguments": [
    {
      "stance": "aggressive",
      "position_action": "add",
      "confidence": 0.8,
      "key_points": ["Strong momentum", "Sector tailwinds", "Earnings catalyst"]
    },
    {
      "stance": "conservative",
      "position_action": "reduce",
      "confidence": 0.6,
      "key_points": ["Valuation stretched", "Concentration risk", "Lock in profits"]
    },
    {
      "stance": "neutral",
      "position_action": "hold",
      "confidence": 0.75,
      "key_points": ["Balanced risk/reward", "Wait for confirmation", "Maintain position"]
    }
  ],
  "debate_summary": "After weighing aggressive growth potential against conservative risk concerns, the balanced approach recommends holding the position..."
}
```

#### `POST /api/ai/portfolio-recommendations/{account_id}`
**Get AI-powered recommendations for entire portfolio**

Response:
```json
{
  "portfolio_risk_score": 45,
  "portfolio_risk_level": "moderate",
  "positions_to_exit": [...],
  "positions_to_reduce": [...],
  "positions_to_hold": [...],
  "positions_to_add": [...],
  "all_recommendations": [...]
}
```

---

### 3. TradingAgents Multi-Agent APIs

#### `GET /api/trading-agents/strategies`
**List all 28 AI-powered strategy configurations**

#### `POST /api/trading-agents/analyze`
**Analyze stock using multi-agent AI system**

Request:
```json
{
  "symbol": "AAPL",
  "strategy_type": "value_investing"
}
```

#### `POST /api/trading-agents/signal`
**Get BUY/SELL/HOLD signal**

#### `POST /api/trading-agents/batch-analyze`
**Analyze multiple stocks (max 10)**

---

### 4. System Info

#### `GET /api/risk/summary`
**Get risk system capabilities summary**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Vue 3)                        │
├─────────────────────────────────────────────────────────────────┤
│                         API Layer (FastAPI)                     │
├──────────────────┬────────────────────┬─────────────────────────┤
│  Risk Management │  AI Position       │  TradingAgents          │
│  Service         │  Advisor           │  Integration            │
├──────────────────┼────────────────────┼─────────────────────────┤
│ • Portfolio Risk │ • 3-Way Debate     │ • Market Analyst        │
│ • Position Risk  │ • Aggressive View  │ • Fundamentals Analyst  │
│ • Reallocation   │ • Neutral View     │ • News Analyst          │
│ • Capital Mgmt   │ • Conservative View│ • Social Analyst        │
│                  │ • Judge Decision   │ • Bull/Bear Researchers │
│                  │                    │ • Trader Agent          │
│                  │                    │ • Risk Manager          │
└──────────────────┴────────────────────┴─────────────────────────┘
```

---

## 🔧 Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_key

# Optional (for enhanced data)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

---

## 📂 New Files Created

| File | Purpose |
|------|---------|
| `services/portfolio_risk_service.py` | Continuous portfolio risk assessment |
| `services/ai_position_advisor.py` | 3-way AI debate system for positions |
| `octopus/ai_platforms/trading_agents.py` | TradingAgents integration |
| `octopus/ai_platforms/strategy_agents.py` | 28 strategy agent configurations |
| `jobs/trading_bot_ai.py` | AI-enhanced trading bot |

---

## ✅ Hackathon Checklist

- [x] Continuously assess risk, capital, potential returns for open positions
- [x] Recommend actions: hold, reduce, exit, reallocate capital
- [x] Manage multiple positions together to balance risk
- [x] Focus on reasoning and adaptability (3-way debate system)
- [x] Track open positions and estimate current risk
- [x] New opportunities trigger reallocation suggestions
- [x] Not fixed strategies - AI-powered dynamic decision making

---

## 🚀 Quick Start

```bash
# 1. Set environment variables
$env:OPENAI_API_KEY = "your_key"

# 2. Start the API server
cd backend/app
python main.py

# 3. Test the risk API
curl http://localhost:5000/api/risk/summary
```
