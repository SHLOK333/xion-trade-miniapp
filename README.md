# 🚀 XION Trade Strategies

> **AI-Powered Risk-Aware Trading Platform** | Newton Hackathon 2026

[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/Paper_profit_bot)
[![API Docs](https://img.shields.io/badge/API-Docs-green?logo=swagger)](https://your-railway-url.up.railway.app/docs)
[![Mini App](https://img.shields.io/badge/Mini%20App-Live-purple)](https://shlok333.github.io/xion-trade-miniapp/)

---

## 🎯 What is XION Trade Strategies?

A **Telegram Mini App + AI-powered API** that brings institutional-grade trading analysis to everyone. Practice trading with real market data, get AI-driven signals, and learn risk management—all without risking real money.

```
┌─────────────────────────────────────────────────────────────┐
│                    XION Trade Platform                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   📱 Telegram Bot          🌐 Mini App           🔌 API     │
│   ┌──────────────┐        ┌──────────────┐    ┌──────────┐  │
│   │ /price AAPL  │        │  Dark UI     │    │ REST API │  │
│   │ /analyze TSLA│   ←→   │  Portfolio   │ ←→ │ FastAPI  │  │
│   │ /risk        │        │  Charts      │    │ OpenAPI  │  │
│   └──────────────┘        └──────────────┘    └──────────┘  │
│            │                     │                  │        │
│            └─────────────────────┴──────────────────┘        │
│                              │                               │
│                    ┌─────────▼─────────┐                    │
│                    │   🤖 AI Engine    │                    │
│                    │  GPT-4 / Claude   │                    │
│                    │  DeepSeek         │                    │
│                    └─────────┬─────────┘                    │
│                              │                               │
│                    ┌─────────▼─────────┐                    │
│                    │  📊 Market Data   │                    │
│                    │  Yahoo Finance    │                    │
│                    │  Alpha Vantage    │                    │
│                    └───────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔥 Key Features

### 📱 Telegram Mini App
Access the full trading terminal directly in Telegram:

| Feature | Description |
|---------|-------------|
| 💼 **Portfolio View** | Track positions, P&L, and performance |
| 📈 **Live Charts** | Real-time candlestick charts |
| 🛒 **Trade Execution** | Buy/Sell with one tap |
| 🎨 **Dark Terminal UI** | Professional trading interface |

### 🤖 AI Trading Analysis

```
┌─────────────────────────────────────────────┐
│              AI Analysis Flow               │
├─────────────────────────────────────────────┤
│                                             │
│   User: /analyze TSLA value_investing       │
│              │                              │
│              ▼                              │
│   ┌─────────────────────┐                  │
│   │ 1. Fetch Live Data  │                  │
│   │    - Price: $430    │                  │
│   │    - P/E: 398       │                  │
│   │    - 52W Range      │                  │
│   └──────────┬──────────┘                  │
│              ▼                              │
│   ┌─────────────────────┐                  │
│   │ 2. Apply Strategy   │                  │
│   │    - Entry Rules    │                  │
│   │    - Risk Params    │                  │
│   │    - Position Size  │                  │
│   └──────────┬──────────┘                  │
│              ▼                              │
│   ┌─────────────────────┐                  │
│   │ 3. AI Analysis      │                  │
│   │    - GPT-4 Prompt   │                  │
│   │    - Signal Gen     │                  │
│   └──────────┬──────────┘                  │
│              ▼                              │
│   🟢 BUY Signal | 85% Confidence           │
│   Entry: $430 | Stop: $408 | Target: $515  │
│                                             │
└─────────────────────────────────────────────┘
```

### 📊 30+ Trading Strategies

```
┌────────────────────────────────────────────────────────────┐
│                   Strategy Categories                       │
├──────────────────┬──────────────────┬─────────────────────┤
│   🏦 Long Term   │  📊 Swing Trade  │   ⚡ Day Trading    │
├──────────────────┼──────────────────┼─────────────────────┤
│ • Value Invest   │ • Trend Follow   │ • Scalping          │
│ • Buy & Hold     │ • Breakout       │ • VWAP Strategy     │
│ • DCA            │ • Momentum       │ • Opening Range     │
│ • Dividend       │ • Mean Revert    │ • News Trading      │
│ • Index Fund     │ • RSI Strategy   │ • Intraday Trends   │
├──────────────────┴──────────────────┴─────────────────────┤
│                 🏆 Legendary Investors                      │
├───────────────────────────────────────────────────────────┤
│ Warren Buffett • Ben Graham • Peter Lynch • Ray Dalio     │
│ Jesse Livermore • John Bogle • Stanley Druckenmiller      │
└───────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Option 1: Telegram Bot (Easiest!)

1. Open [@Paper_profit_bot](https://t.me/Paper_profit_bot) in Telegram
2. Send `/start` to begin
3. Click **"📊 Open Mini App"** for the full trading terminal

### Option 2: API Access

```bash
# Get stock price
curl https://your-api.railway.app/api/instruments/get/AAPL

# AI Stock Analysis
curl -X POST https://your-api.railway.app/api/ai/analyze-stock \
  -H "Content-Type: application/json" \
  -d '{"symbol": "TSLA", "ai": "openai"}'

# Get all strategies
curl https://your-api.railway.app/api/strategies
```

---

## 📡 API Reference

### Base URL
```
https://your-railway-url.up.railway.app
```

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/accounts` | GET | List all trading accounts |
| `/api/accounts/{id}/portfolio` | GET | Get portfolio positions |
| `/api/instruments/get/{symbol}` | GET | Get real-time stock data |
| `/api/ai/analyze-stock` | POST | AI-powered stock analysis |
| `/api/ai/generate-strategy` | POST | Generate trading strategy |
| `/api/ai/market-insights` | GET | Market sector insights |
| `/api/strategies` | GET | List trading strategies |

### AI Analysis Request

```json
POST /api/ai/analyze-stock
{
  "symbol": "AAPL",
  "analysis_type": "comprehensive",
  "ai": "openai"
}
```

### Response

```json
{
  "symbol": "AAPL",
  "signal": "BUY",
  "confidence": 85,
  "entry_price": 185.50,
  "stop_loss": 176.22,
  "target_price": 210.00,
  "position_size": "5%",
  "reasons": [
    "Strong technical breakout above resistance",
    "Positive earnings momentum",
    "Healthy cash flow generation"
  ]
}
```

📚 **Full API Docs**: [/docs](https://your-railway-url.up.railway.app/docs)

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      Architecture                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Frontend (Mini App)          Backend (API)                 │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │ Vue 3 + Vite    │         │ FastAPI         │           │
│  │ Tailwind CSS    │   ──▶   │ SQLAlchemy      │           │
│  │ Chart.js        │         │ yfinance        │           │
│  └─────────────────┘         └─────────────────┘           │
│                                      │                      │
│  Telegram Bot                        ▼                      │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │ python-telegram │         │ AI Services     │           │
│  │ -bot v22        │         │ • OpenAI GPT-4  │           │
│  │                 │   ──▶   │ • Claude        │           │
│  └─────────────────┘         │ • DeepSeek      │           │
│                              └─────────────────┘           │
│                                                              │
│  Hosting                                                    │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ GitHub Pages    │  │ Railway         │                  │
│  │ (Mini App)      │  │ (Bot + API)     │                  │
│  └─────────────────┘  └─────────────────┘                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏃 Running Locally

### Prerequisites
- Python 3.10+
- Node.js 20+
- OpenAI API Key (for AI features)

### Backend

```bash
cd backend/app
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_token
export OPENAI_API_KEY=your_key

# Run API server
uvicorn api:app --host 0.0.0.0 --port 5000 --reload

# Or run Telegram bot
python telegram_bot_enhanced.py
```

### Frontend (Mini App)

```bash
cd miniapp
npm install
npm run dev
# Opens at http://localhost:3000
```

### Main Dashboard

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

---

## 📱 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot, open Mini App |
| `/price AAPL` | Get real-time stock price |
| `/analyze TSLA momentum` | AI analysis with strategy |
| `/strategies` | List all trading strategies |
| `/risk` | Portfolio risk assessment |
| `/help` | Show all commands |

---

## 🔐 Environment Variables

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
OPENAI_API_KEY=your_openai_key

# Optional
ALPHA_VANTAGE_API_KEY=your_key
MINI_APP_URL=https://shlok333.github.io/xion-trade-miniapp/
```

---

## 📊 Risk Management

```
┌──────────────────────────────────────────────────────────┐
│                  Risk Assessment                          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│   Portfolio Value: $100,000                              │
│                                                           │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│   │ Beta: 1.2   │  │ VaR: 2.5%   │  │ Sharpe: 1.8 │     │
│   │ ⚠️ Moderate │  │ 📉 $2,500   │  │ ✅ Good     │     │
│   └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                           │
│   Position Limits:                                       │
│   ├── Max Single Position: 10%                          │
│   ├── Max Sector Exposure: 30%                          │
│   └── Stop Loss Required: ✅                            │
│                                                           │
│   AI Recommendation:                                     │
│   "Reduce tech exposure by 5%, add defensive stocks"    │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 🏆 Team XION

Built with ❤️ for **Newton Hackathon 2026**

| Member | Role |
|--------|------|
| SHLOK | Lead Developer |

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>🚀 Trade Smarter with AI • Practice Without Risk 📈</b>
</p>
