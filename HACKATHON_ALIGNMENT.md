# 🏆 Hackathon Requirements Alignment

## Problem Statement
> **"Continuous Decision-Making for Risk-Aware Trading"**
> 
> Build an AI-powered system that continuously assesses risk, capital, and potential returns for a set of open trading positions, then recommends whether to hold, reduce, exit, or reallocate capital as new opportunities arise — managing multiple positions together rather than just one trade at a time.

---

## ✅ Requirement Checklist

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| **Continuously assess risk** | ✅ DONE | `ContinuousPortfolioMonitor` runs in background loop |
| **Track open positions** | ✅ DONE | `PositionService` with SQLite database |
| **Estimate current risk** | ✅ DONE | Risk scoring: LOW → MODERATE → HIGH → CRITICAL |
| **Estimate potential returns** | ✅ DONE | P&L calculation with entry price vs current price |
| **Recommend: HOLD** | ✅ DONE | `PositionAction.HOLD` when within parameters |
| **Recommend: REDUCE** | ✅ DONE | `PositionAction.REDUCE` for concentration/profit taking |
| **Recommend: EXIT** | ✅ DONE | `PositionAction.EXIT` for critical losses |
| **Recommend: REALLOCATE** | ✅ DONE | `get_reallocation_suggestions()` API |
| **New opportunities detection** | ✅ DONE | `AlertType.OPPORTUNITY` + idle capital detection |
| **Manage multiple positions together** | ✅ DONE | Portfolio-level assessment, not individual |
| **Reasoning (not fixed rules)** | ✅ DONE | 3-way AI debate with GPT-4o-mini |
| **Adaptability** | ✅ DONE | 28 strategy-specific configurations |
| **🆕 Auto-execute trades** | ✅ DONE | `AutoPortfolioRebalancer` executes on alerts |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT INTERFACE                        │
│  /price /analyze /portfolio /monitor /alerts /rebalance /trades │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│               CONTINUOUS PORTFOLIO MONITOR                       │
│                                                                  │
│  • Background monitoring loop (60s intervals)                    │
│  • Real-time price updates (Yahoo Finance)                       │
│  • Alert generation (stop-loss, take-profit, risk)              │
│  • Action recommendations (hold, reduce, exit, add)             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              🆕 AUTO PORTFOLIO REBALANCER                        │
│                                                                  │
│  • Listens to alerts from monitor                                │
│  • Automatically executes trades (or simulates in dry-run)      │
│  • Safety limits: max trades/day, cooldowns, position limits    │
│  • Telegram notifications for all actions                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AI POSITION ADVISOR                             │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                   │
│  │AGGRESSIVE│    │ NEUTRAL  │    │CONSERV.  │                   │
│  │ ANALYST  │    │ ANALYST  │    │ ANALYST  │                   │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘                   │
│       │               │               │                          │
│       └───────────────┼───────────────┘                          │
│                       ▼                                          │
│              ┌─────────────┐                                     │
│              │    JUDGE    │  → Final Decision                   │
│              └─────────────┘                                     │
└─────────────────────────────────────────────────────────────────┘
```
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 STRATEGY CONFIGURATIONS                          │
│                                                                  │
│  Long Term: Value, Growth, Dividend, Quality, Index             │
│  Swing: Momentum, Mean Reversion, Breakout, Sector Rotation     │
│  Day Trading: Scalping, Gap Trading, VWAP                       │
│  Options: Covered Calls, Protective Puts, Iron Condors          │
│  Greatest Investors: Buffett, Lynch, Soros, Dalio, Livermore    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                    │
│                                                                  │
│  Yahoo Finance → Real-time prices, historical data              │
│  Alpha Vantage → Fundamental data                               │
│  SQLite DB → Positions, accounts, transactions                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Components

### 1. Continuous Portfolio Monitor
**File:** `services/continuous_monitor.py`

```python
# Runs continuously in background
monitor = ContinuousPortfolioMonitor(
    account_id="user123",
    check_interval_seconds=60,
    on_alert=handle_alert,      # Called when alert generated
    on_update=handle_update     # Called on every check
)
monitor.start()  # Background thread
```

**Features:**
- Real-time price fetching with caching
- Risk level assessment (LOW → CRITICAL)
- Action recommendations with urgency
- Alert generation for threshold breaches
- Capital efficiency tracking

### 2. AI Position Advisor (3-Way Debate)
**File:** `services/ai_position_advisor.py`

```python
advisor = AIPositionAdvisor()
result = await advisor.analyze_position_with_debate(
    symbol="AAPL",
    entry_price=150.0,
    current_price=142.0,
    quantity=100,
    strategy="value_investing"
)
# Result: {"recommendation": "HOLD", "risk_score": 45, "reasoning": "..."}
```

**Debate Process:**
1. **Aggressive Analyst**: Looks for opportunity, recommends holding through dips
2. **Neutral Analyst**: Weighs evidence objectively
3. **Conservative Analyst**: Prioritizes capital preservation
4. **Judge**: Makes final decision based on debate

### 3. Strategy-Specific Analysis
**File:** `telegram_bot_enhanced.py`

Each of 28 strategies has unique:
- Risk tolerance (low/moderate/high)
- Time horizon (short/medium/long)
- Entry/exit criteria
- Position sizing rules
- Analysis prompts for AI

### 4. Portfolio Risk Service
**File:** `services/portfolio_risk_service.py`

Provides:
- Portfolio-wide risk assessment
- Position-level risk scoring
- Reallocation suggestions
- Concentration analysis

---

## 📱 Telegram Bot Commands

| Command | Purpose |
|---------|---------|
| `/start` | Welcome menu |
| `/price AAPL` | Get real-time price |
| `/analyze AAPL value_investing` | Strategy-specific AI analysis |
| `/strategies` | List all 28 strategies |
| `/portfolio` | View portfolio with risk assessment |
| `/monitor` | Start continuous monitoring info |
| `/alerts` | View current alerts |
| `/actions` | View recommended actions |

---

## 🎯 Hackathon Focus Areas

### ✅ "Continuously assess risk"
```python
class ContinuousPortfolioMonitor:
    def _monitoring_loop(self):
        while self._running:
            snapshot = self._check_portfolio()  # Every 60 seconds
            for alert in snapshot.alerts:
                self.on_alert(alert)  # Proactive alerts
            time.sleep(self.check_interval)
```

### ✅ "Recommend hold, reduce, exit, or reallocate"
```python
class PositionAction(Enum):
    HOLD = "hold"
    REDUCE = "reduce"
    EXIT = "exit"
    ADD = "add"
    REALLOCATE = "reallocate"
```

### ✅ "Capital reallocation as new opportunities arise"
```python
def get_reallocation_suggestions(self, account_id: str) -> List[ReallocationSuggestion]:
    # Analyze positions and suggest moves
    # E.g., "Reduce AAPL by 20%, add to MSFT"
```

### ✅ "Manage multiple positions together"
```python
class PortfolioRiskAssessment:
    positions: List[PositionRiskAssessment]  # All positions
    overall_risk_level: RiskLevel
    concentration_issues: List[str]
    correlation_warnings: List[str]
```

### ✅ "Focus on reasoning and adaptability"
- **Not fixed rules**: AI debate system with 3 perspectives
- **Adaptability**: 28 strategies with different risk profiles
- **Reasoning**: Each decision includes detailed rationale

---

## 🚀 Running the System

```bash
# Terminal 1: Backend API
cd backend/app
python main.py

# Terminal 2: Telegram Bot
cd backend/app
python telegram_bot_enhanced.py

# Terminal 3: Continuous Monitor (optional standalone)
cd backend/app
python -m services.continuous_monitor
```

---

## 📊 Sample Output

### Portfolio Assessment
```
📊 Portfolio Risk: MODERATE
💵 Capital Efficiency: 72.3%

🚪 AAPL: EXIT (NOW!)
   P&L: -18.5% | Risk: CRITICAL
   Critical loss: -18.5%

📉 NVDA: REDUCE (Consider)
   P&L: +32.1% | Risk: MODERATE
   Large gain at risk: +32.1%

⏸️ MSFT: HOLD
   P&L: +5.2% | Risk: LOW
   Position within acceptable parameters
```

### AI Debate Result
```
🤖 AI POSITION ANALYSIS: AAPL

📌 RECOMMENDATION: REDUCE
📊 Risk Score: 68/100
⚡ Urgency: HIGH

💭 DEBATE SUMMARY:
- Aggressive: Hold for recovery, fundamentals intact
- Neutral: Technical damage requires caution
- Conservative: Cut losses now, preserve capital
- Judge: Reduce 50% to limit risk while maintaining exposure

✅ ACTION: Sell 50 shares of AAPL
```

---

## 🎓 Conclusion

This implementation fully addresses the hackathon problem statement:

1. ✅ **Continuous** - Background monitoring loop
2. ✅ **Risk-aware** - Multi-level risk scoring with alerts
3. ✅ **Decision-making** - AI-powered recommendations
4. ✅ **Portfolio-level** - Manages all positions together
5. ✅ **Adaptive** - 28 strategies with different rules
6. ✅ **Reasoning** - 3-way AI debate, not fixed thresholds
7. ✅ **Actionable** - Clear hold/reduce/exit/reallocate recommendations
8. ✅ **Real data** - Yahoo Finance integration
9. ✅ **User-friendly** - Telegram bot interface
