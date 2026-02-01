# Paper Profit Mini App 📱

A stunning Telegram Mini App for the Paper Profit AI Trading System.

## ✨ Features

- **Real-time Portfolio View** - Beautiful cards showing all positions with P&L
- **Interactive Charts** - Portfolio performance and allocation charts using Chart.js
- **AI Advisor** - 3-way AI debate (Bull/Neutral/Bear) for trading decisions
- **Risk Alerts** - Real-time alerts with urgency indicators
- **Auto Rebalancing** - Configure automatic portfolio rebalancing
- **Glass Morphism UI** - Modern design with smooth animations

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd miniapp
npm install
```

### 2. Configure Environment

Create `.env` file:

```env
VITE_API_URL=http://localhost:5000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

## 📱 Telegram Integration

### Setting Up the Mini App

1. **Create a Web App** in BotFather:
   - Open [@BotFather](https://t.me/botfather)
   - Send `/mybots`
   - Select your bot
   - Click "Bot Settings" → "Menu Button" → "Configure menu button"
   - Set the URL to your deployed Mini App

2. **Deploy the Mini App** (HTTPS required):
   - **Vercel**: `npx vercel --prod`
   - **Netlify**: Connect to GitHub and deploy
   - **GitHub Pages**: `npm run build` and deploy `dist/`

3. **Update Environment Variables**:
   - Set `MINI_APP_URL` in your Telegram bot environment
   - Ensure `VITE_API_URL` points to your deployed backend

### Development with ngrok (Local Testing)

```bash
# Install ngrok
npm install -g ngrok

# Expose your local server
ngrok http 5173
```

Use the ngrok HTTPS URL in BotFather for testing.

## 🎨 Design System

### Colors

- **Accent**: `#00D4AA` (Teal green)
- **Profit**: `#10B981` (Green)
- **Loss**: `#EF4444` (Red)
- **Dark Card**: `#1E293B`
- **Dark Border**: `#334155`

### Components

| Component | Description |
|-----------|-------------|
| `PortfolioSummary` | Portfolio value with sparkline and risk gauge |
| `QuickActions` | Horizontal scrollable action buttons |
| `PositionCard` | Individual position with mini chart |
| `PortfolioChart` | Full portfolio performance chart |
| `AllocationChart` | Donut chart for asset allocation |
| `AIAdvisor` | 3-way AI debate interface |
| `AlertCard` | Alert cards with urgency indicators |
| `BottomNav` | Tab navigation |
| `PositionModal` | Position detail modal with chart |
| `SettingsModal` | Settings panel |

## 📁 Project Structure

```
miniapp/
├── index.html          # Entry point with Telegram SDK
├── package.json        # Dependencies
├── vite.config.js      # Vite configuration
├── tailwind.config.js  # Tailwind with custom theme
├── postcss.config.js   # PostCSS configuration
└── src/
    ├── main.js         # Vue initialization
    ├── App.vue         # Main app component
    ├── style.css       # Global styles & animations
    ├── services/
    │   └── api.js      # API service for backend
    └── components/
        ├── PortfolioSummary.vue
        ├── QuickActions.vue
        ├── PositionCard.vue
        ├── PortfolioChart.vue
        ├── AllocationChart.vue
        ├── AIAdvisor.vue
        ├── AlertCard.vue
        ├── BottomNav.vue
        ├── PositionModal.vue
        └── SettingsModal.vue
```

## 🔧 Tech Stack

- **Vue 3** - Composition API with `<script setup>`
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **Chart.js** - Interactive charts
- **GSAP** - Smooth animations
- **Telegram WebApp SDK** - Native Telegram integration

## 🌟 Killer Features

1. **AI 3-Way Debate** - See Bull, Neutral, and Bear perspectives before making decisions
2. **Risk Gauge** - Visual indicator of portfolio risk level
3. **Haptic Feedback** - Native Telegram haptic responses
4. **Auto-refresh** - Portfolio data refreshes every 60 seconds
5. **Glass Morphism** - Modern, sleek design with blur effects
6. **Responsive** - Optimized for mobile Telegram

## 📝 License

MIT License - Part of the Paper Profit project.
