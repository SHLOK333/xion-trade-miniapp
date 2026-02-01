"""
XION Trade Telegram Bot with Real Data

Features:
- Real-time stock prices from Yahoo Finance
- Real portfolio positions from database
- Strategy-specific AI analysis
- Position management recommendations
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Mini App URL (GitHub Pages)
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://shlok333.github.io/xion-trade-miniapp/?v=2")

import yfinance as yf

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


# ==================== STRATEGY CONFIGURATIONS ====================

@dataclass
class StrategyConfig:
    """Configuration for each strategy type"""
    name: str
    category: str
    risk_tolerance: str  # low, moderate, high
    time_horizon: str    # short, medium, long
    key_metrics: List[str]
    entry_criteria: str
    exit_criteria: str
    position_sizing: str
    analysis_prompt: str


STRATEGY_CONFIGS = {
    # LONG TERM STRATEGIES
    "value_investing": StrategyConfig(
        name="Value Investing",
        category="Long Term",
        risk_tolerance="moderate",
        time_horizon="long",
        key_metrics=["P/E Ratio", "P/B Ratio", "Debt/Equity", "Free Cash Flow"],
        entry_criteria="Buy when stock trades below intrinsic value (margin of safety > 30%)",
        exit_criteria="Sell when price reaches fair value or fundamentals deteriorate",
        position_sizing="Max 5% per position, diversify across 15-20 stocks",
        analysis_prompt="Analyze as a value investor. Focus on P/E ratio, book value, debt levels, and margin of safety."
    ),
    "growth_investing": StrategyConfig(
        name="Growth Investing",
        category="Long Term",
        risk_tolerance="high",
        time_horizon="long",
        key_metrics=["Revenue Growth", "EPS Growth", "ROE", "Market Share"],
        entry_criteria="Buy high-growth companies with >20% revenue growth",
        exit_criteria="Sell if growth slows significantly or valuation becomes extreme",
        position_sizing="Max 8% per position, concentrate in 10-15 best ideas",
        analysis_prompt="Analyze as a growth investor. Focus on revenue growth rate, market expansion, and competitive moat."
    ),
    "dividend_growth": StrategyConfig(
        name="Dividend Growth",
        category="Long Term",
        risk_tolerance="low",
        time_horizon="long",
        key_metrics=["Dividend Yield", "Payout Ratio", "Dividend Growth Rate", "Years of Increases"],
        entry_criteria="Buy dividend aristocrats with >10 years of increases",
        exit_criteria="Sell if dividend is cut or payout ratio exceeds 80%",
        position_sizing="Max 4% per position, build 25+ stock portfolio",
        analysis_prompt="Analyze as a dividend investor. Focus on dividend safety, growth history, and payout ratio sustainability."
    ),
    "momentum_trading": StrategyConfig(
        name="Momentum Trading",
        category="Swing Trading",
        risk_tolerance="high",
        time_horizon="short",
        key_metrics=["RSI", "MACD", "Price vs 50/200 MA", "Volume"],
        entry_criteria="Buy when RSI > 50 and price breaks above 20-day high with volume",
        exit_criteria="Sell when RSI > 70 or price closes below 10-day MA",
        position_sizing="Max 10% per position, use tight stop losses",
        analysis_prompt="Analyze as a momentum trader. Focus on RSI, MACD, moving averages, and volume patterns."
    ),
    "mean_reversion": StrategyConfig(
        name="Mean Reversion",
        category="Swing Trading",
        risk_tolerance="moderate",
        time_horizon="short",
        key_metrics=["RSI", "Bollinger Bands", "Standard Deviation", "Z-Score"],
        entry_criteria="Buy when RSI < 30 and price at lower Bollinger Band",
        exit_criteria="Sell when RSI > 50 or price returns to 20-day MA",
        position_sizing="Max 5% per position, scale in on further drops",
        analysis_prompt="Analyze for mean reversion. Focus on oversold conditions, Bollinger Bands, and historical price deviation."
    ),
    "scalping": StrategyConfig(
        name="Scalping",
        category="Day Trading",
        risk_tolerance="high",
        time_horizon="short",
        key_metrics=["Bid-Ask Spread", "Volume", "Volatility", "Level 2 Data"],
        entry_criteria="Enter on micro price movements with tight spreads",
        exit_criteria="Exit immediately on small profit or stop loss",
        position_sizing="Large position sizes with very tight stops",
        analysis_prompt="Analyze for scalping. Focus on bid-ask spreads, volume, and intraday volatility."
    ),
    "warren_buffett": StrategyConfig(
        name="Warren Buffett Style",
        category="Greatest Investors",
        risk_tolerance="low",
        time_horizon="long",
        key_metrics=["ROE", "Profit Margins", "Competitive Moat", "Management Quality"],
        entry_criteria="Buy wonderful companies at fair prices with durable competitive advantage",
        exit_criteria="Hold forever unless thesis breaks or better opportunities arise",
        position_sizing="Concentrate in 10-15 best ideas, large positions in high conviction",
        analysis_prompt="Analyze like Warren Buffett. Look for economic moat, honest management, consistent earnings, and reasonable valuation."
    ),
    "peter_lynch": StrategyConfig(
        name="Peter Lynch Style",
        category="Greatest Investors",
        risk_tolerance="moderate",
        time_horizon="medium",
        key_metrics=["PEG Ratio", "Earnings Growth", "Debt Levels", "Insider Buying"],
        entry_criteria="Buy growth at reasonable price (PEG < 1), look for 10-baggers",
        exit_criteria="Sell when story changes or PEG > 2",
        position_sizing="Diversify across many small positions, let winners run",
        analysis_prompt="Analyze like Peter Lynch. Focus on PEG ratio, growth potential, and look for hidden gems."
    ),
}


# ==================== REAL DATA FUNCTIONS ====================

def get_real_stock_data(symbol: str) -> Dict[str, Any]:
    """Fetch real-time stock data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1mo")
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
        prev_close = info.get('previousClose') or info.get('regularMarketPreviousClose') or current_price
        
        # Calculate metrics
        day_change = current_price - prev_close
        day_change_pct = (day_change / prev_close * 100) if prev_close > 0 else 0
        
        # Get 52-week data
        week_52_high = info.get('fiftyTwoWeekHigh', 0)
        week_52_low = info.get('fiftyTwoWeekLow', 0)
        
        # Calculate technical indicators from history
        if len(hist) > 0:
            ma_20 = hist['Close'].tail(20).mean()
            ma_50 = hist['Close'].tail(50).mean() if len(hist) >= 50 else ma_20
            volatility = hist['Close'].pct_change().std() * 100
        else:
            ma_20 = ma_50 = current_price
            volatility = 0
        
        return {
            "symbol": symbol.upper(),
            "name": info.get('shortName', symbol),
            "current_price": current_price,
            "prev_close": prev_close,
            "day_change": day_change,
            "day_change_pct": day_change_pct,
            "week_52_high": week_52_high,
            "week_52_low": week_52_low,
            "market_cap": info.get('marketCap', 0),
            "pe_ratio": info.get('trailingPE', 0),
            "forward_pe": info.get('forwardPE', 0),
            "dividend_yield": info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            "volume": info.get('volume', 0),
            "avg_volume": info.get('averageVolume', 0),
            "ma_20": ma_20,
            "ma_50": ma_50,
            "volatility": volatility,
            "beta": info.get('beta', 1),
            "sector": info.get('sector', 'Unknown'),
            "industry": info.get('industry', 'Unknown'),
        }
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate RSI from price list"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# ==================== XION TRADE BOT ====================

class XionTradeBot:
    """XION Trade Telegram bot with real data and strategy-specific analysis"""
    
    def __init__(self):
        self.application = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Welcome message with all commands"""
        keyboard = [
            [InlineKeyboardButton("📊 Open Trading Dashboard", web_app=WebAppInfo(url=MINI_APP_URL))],
            [InlineKeyboardButton("📈 Analyze Stock", callback_data="menu_analyze")],
            [InlineKeyboardButton("💼 My Portfolio", callback_data="menu_portfolio")],
            [InlineKeyboardButton("🔄 Auto Rebalance", callback_data="menu_rebalance")],
            [InlineKeyboardButton("🎯 Strategies", callback_data="menu_strategies")],
            [InlineKeyboardButton("📋 All Commands", callback_data="menu_commands")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🚀 **Welcome to XION Trade Bot!**\n\n"
            "AI-powered risk-aware trading system.\n\n"
            "**📋 AVAILABLE COMMANDS:**\n\n"
            "**📊 Market Data:**\n"
            "`/price AAPL` - Real-time stock price\n\n"
            "**🤖 AI Analysis:**\n"
            "`/analyze AAPL momentum` - Strategy-specific AI analysis\n"
            "`/strategies` - List all trading strategies\n\n"
            "**📈 Portfolio:**\n"
            "`/portfolio` - View portfolio with risk assessment\n"
            "`/alerts` - View current risk alerts\n"
            "`/actions` - View recommended actions\n\n"
            "**🔄 Auto Rebalancing:**\n"
            "`/monitor` - Start continuous monitoring\n"
            "`/rebalance` - Trigger portfolio rebalance\n"
            "`/autotrade ON/OFF/DRY` - Toggle auto-trading\n"
            "`/trades` - View trade history\n\n"
            "`/help` - Show this help message\n\n"
            "Choose an option below:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def get_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Get real-time stock price"""
        args = context.args
        if not args:
            await update.message.reply_text("❌ Usage: `/price AAPL`", parse_mode='Markdown')
            return
        
        symbol = args[0].upper()
        msg = await update.message.reply_text(f"🔄 Fetching {symbol} data...")
        
        data = get_real_stock_data(symbol)
        
        if "error" in data:
            await msg.edit_text(f"❌ Error fetching {symbol}: {data['error']}")
            return
        
        # Price direction emoji
        change_emoji = "🟢" if data['day_change'] >= 0 else "🔴"
        
        text = f"""
📊 **{data['name']}** ({data['symbol']})

💰 **Price:** ${data['current_price']:.2f}
{change_emoji} **Change:** ${data['day_change']:+.2f} ({data['day_change_pct']:+.2f}%)

📈 **52-Week Range:**
   Low: ${data['week_52_low']:.2f} | High: ${data['week_52_high']:.2f}

📊 **Key Metrics:**
• P/E Ratio: {data['pe_ratio']:.2f}
• Dividend Yield: {data['dividend_yield']:.2f}%
• Beta: {data['beta']:.2f}
• Volume: {data['volume']:,}

📉 **Technical:**
• MA(20): ${data['ma_20']:.2f}
• MA(50): ${data['ma_50']:.2f}
• Volatility: {data['volatility']:.2f}%

🏢 **Sector:** {data['sector']}

_Last updated: {datetime.now().strftime('%H:%M:%S')}_
        """
        await msg.edit_text(text.strip(), parse_mode='Markdown')

    async def analyze_with_strategy(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Analyze stock with specific strategy"""
        args = context.args
        
        if not args:
            strategies_list = "\n".join([f"• `{k}`" for k in STRATEGY_CONFIGS.keys()])
            await update.message.reply_text(
                "❌ **Usage:** `/analyze AAPL [strategy]`\n\n"
                f"**Available Strategies:**\n{strategies_list}\n\n"
                "**Example:** `/analyze AAPL value_investing`",
                parse_mode='Markdown'
            )
            return
        
        symbol = args[0].upper()
        strategy_type = args[1].lower() if len(args) > 1 else "value_investing"
        
        # Get strategy config
        strategy = STRATEGY_CONFIGS.get(strategy_type)
        if not strategy:
            await update.message.reply_text(
                f"❌ Unknown strategy: `{strategy_type}`\n"
                f"Use `/analyze` to see available strategies.",
                parse_mode='Markdown'
            )
            return
        
        msg = await update.message.reply_text(
            f"🔄 Analyzing **{symbol}** with **{strategy.name}** strategy...\n\n"
            f"📊 Fetching real market data...",
            parse_mode='Markdown'
        )
        
        # Get real stock data
        stock_data = get_real_stock_data(symbol)
        
        if "error" in stock_data:
            await msg.edit_text(f"❌ Error: {stock_data['error']}")
            return
        
        await msg.edit_text(
            f"🔄 Analyzing **{symbol}** with **{strategy.name}** strategy...\n\n"
            f"💰 Current Price: ${stock_data['current_price']:.2f}\n"
            f"📈 Day Change: {stock_data['day_change_pct']:+.2f}%\n\n"
            f"🤖 Running AI analysis...",
            parse_mode='Markdown'
        )
        
        # Run AI analysis with strategy context
        try:
            result = await self._run_strategy_analysis(symbol, stock_data, strategy)
            response = self._format_strategy_analysis(symbol, stock_data, strategy, result)
            await msg.edit_text(response, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            await msg.edit_text(f"❌ Analysis error: {str(e)}")

    async def _run_strategy_analysis(
        self, 
        symbol: str, 
        stock_data: Dict[str, Any], 
        strategy: StrategyConfig
    ) -> Dict[str, Any]:
        """Run AI analysis with strategy-specific prompts"""
        try:
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
            
            # Build strategy-specific prompt
            prompt = f"""You are an expert trader using the {strategy.name} strategy.

**Strategy Details:**
- Category: {strategy.category}
- Risk Tolerance: {strategy.risk_tolerance}
- Time Horizon: {strategy.time_horizon}
- Key Metrics: {', '.join(strategy.key_metrics)}
- Entry Criteria: {strategy.entry_criteria}
- Exit Criteria: {strategy.exit_criteria}
- Position Sizing: {strategy.position_sizing}

**Stock Data for {symbol}:**
- Current Price: ${stock_data['current_price']:.2f}
- Day Change: {stock_data['day_change_pct']:+.2f}%
- P/E Ratio: {stock_data['pe_ratio']:.2f}
- 52-Week Range: ${stock_data['week_52_low']:.2f} - ${stock_data['week_52_high']:.2f}
- MA(20): ${stock_data['ma_20']:.2f}
- MA(50): ${stock_data['ma_50']:.2f}
- Volatility: {stock_data['volatility']:.2f}%
- Beta: {stock_data['beta']:.2f}
- Dividend Yield: {stock_data['dividend_yield']:.2f}%
- Sector: {stock_data['sector']}

{strategy.analysis_prompt}

Based on this strategy, provide:
1. SIGNAL: BUY, SELL, or HOLD
2. CONFIDENCE: 0-100%
3. POSITION SIZE: Recommended % of portfolio
4. ENTRY PRICE: If buying, at what price
5. STOP LOSS: Protective stop level
6. TARGET PRICE: Price target
7. KEY REASONS: 3 bullet points explaining your decision

Format your response as:
SIGNAL: [BUY/SELL/HOLD]
CONFIDENCE: [0-100]
POSITION_SIZE: [percentage]
ENTRY_PRICE: [price]
STOP_LOSS: [price]
TARGET_PRICE: [price]
REASONS:
- Reason 1
- Reason 2
- Reason 3"""

            response = llm.invoke(prompt)
            return self._parse_strategy_response(response.content)
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {
                "signal": "HOLD",
                "confidence": 50,
                "position_size": 0,
                "entry_price": stock_data['current_price'],
                "stop_loss": stock_data['current_price'] * 0.95,
                "target_price": stock_data['current_price'] * 1.1,
                "reasons": [f"Analysis error: {str(e)}"]
            }

    def _parse_strategy_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        result = {
            "signal": "HOLD",
            "confidence": 50,
            "position_size": 5,
            "entry_price": 0,
            "stop_loss": 0,
            "target_price": 0,
            "reasons": []
        }
        
        lines = content.split('\n')
        in_reasons = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            upper = line.upper()
            
            if 'SIGNAL:' in upper:
                val = line.split(':', 1)[1].strip().upper()
                if 'BUY' in val:
                    result['signal'] = 'BUY'
                elif 'SELL' in val:
                    result['signal'] = 'SELL'
                else:
                    result['signal'] = 'HOLD'
            elif 'CONFIDENCE:' in upper:
                try:
                    result['confidence'] = float(line.split(':', 1)[1].strip().replace('%', ''))
                except:
                    pass
            elif 'POSITION_SIZE:' in upper:
                try:
                    result['position_size'] = float(line.split(':', 1)[1].strip().replace('%', ''))
                except:
                    pass
            elif 'ENTRY_PRICE:' in upper:
                try:
                    result['entry_price'] = float(line.split(':', 1)[1].strip().replace('$', ''))
                except:
                    pass
            elif 'STOP_LOSS:' in upper:
                try:
                    result['stop_loss'] = float(line.split(':', 1)[1].strip().replace('$', ''))
                except:
                    pass
            elif 'TARGET_PRICE:' in upper:
                try:
                    result['target_price'] = float(line.split(':', 1)[1].strip().replace('$', ''))
                except:
                    pass
            elif 'REASONS:' in upper:
                in_reasons = True
            elif in_reasons and line.startswith('-'):
                result['reasons'].append(line[1:].strip())
        
        return result

    def _format_strategy_analysis(
        self, 
        symbol: str, 
        stock_data: Dict[str, Any], 
        strategy: StrategyConfig,
        result: Dict[str, Any]
    ) -> str:
        """Format the analysis result for Telegram"""
        signal = result['signal']
        signal_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal, "⚪")
        
        risk_emoji = {"low": "🟢", "moderate": "🟡", "high": "🔴"}.get(strategy.risk_tolerance, "⚪")
        
        reasons_text = "\n".join([f"  • {r}" for r in result['reasons'][:3]])
        
        return f"""
🤖 **Strategy Analysis: {symbol}**

**📊 Strategy:** {strategy.name}
**📁 Category:** {strategy.category}
{risk_emoji} **Risk Level:** {strategy.risk_tolerance.title()}
**⏱ Time Horizon:** {strategy.time_horizon.title()}

━━━━━━━━━━━━━━━━━━━━━

**💰 Real-Time Data:**
• Price: **${stock_data['current_price']:.2f}**
• Day: {stock_data['day_change_pct']:+.2f}%
• P/E: {stock_data['pe_ratio']:.2f}
• 52W Range: ${stock_data['week_52_low']:.2f} - ${stock_data['week_52_high']:.2f}

━━━━━━━━━━━━━━━━━━━━━

{signal_emoji} **SIGNAL: {signal}**
📊 Confidence: **{result['confidence']:.0f}%**

**📍 Trade Setup:**
• Entry: ${result['entry_price']:.2f}
• Stop Loss: ${result['stop_loss']:.2f}
• Target: ${result['target_price']:.2f}
• Position: {result['position_size']:.1f}% of portfolio

**💡 Key Reasons:**
{reasons_text}

━━━━━━━━━━━━━━━━━━━━━

**📋 Strategy Rules:**
_Entry:_ {strategy.entry_criteria[:100]}...
_Exit:_ {strategy.exit_criteria[:100]}...

_Analysis: {datetime.now().strftime('%H:%M:%S')}_
        """.strip()

    async def list_strategies(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List available strategies with details"""
        text = "🎯 **Trading Strategies**\n\n"
        
        # Group by category
        categories = {}
        for key, config in STRATEGY_CONFIGS.items():
            if config.category not in categories:
                categories[config.category] = []
            categories[config.category].append((key, config))
        
        for cat, strategies in categories.items():
            risk_emoji = {"Long Term": "🏦", "Swing Trading": "📊", "Day Trading": "⚡", "Greatest Investors": "🏆"}.get(cat, "📈")
            text += f"\n{risk_emoji} **{cat}:**\n"
            for key, config in strategies:
                risk = {"low": "🟢", "moderate": "🟡", "high": "🔴"}.get(config.risk_tolerance, "⚪")
                text += f"  {risk} `{key}`\n"
        
        text += "\n**Usage:** `/analyze AAPL value_investing`"
        
        await update.message.reply_text(text, parse_mode='Markdown')

    async def portfolio_risk(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Get real portfolio risk assessment"""
        args = context.args
        account_id = args[0] if args else "namo"
        
        msg = await update.message.reply_text(f"🔄 Analyzing portfolio `{account_id}`...")
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(f"{API_BASE_URL}/api/risk/portfolio/{account_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    risk_level = data.get('overall_risk_level', 'unknown').upper()
                    risk_emoji = {"LOW": "🟢", "MODERATE": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(risk_level, "⚪")
                    
                    text = f"""
📊 **Portfolio Risk Assessment**
Account: `{account_id}`

{risk_emoji} **Risk Level: {risk_level}**

💰 **Value:** ${data.get('total_value', 0):,.2f}
💵 **Cash:** ${data.get('cash_available', 0):,.2f}
📈 **Invested:** ${data.get('invested_value', 0):,.2f}
📊 **P&L:** ${data.get('total_unrealized_pnl', 0):+,.2f}

**Metrics:**
• Diversification: {data.get('diversification_score', 0):.0f}/100
• Positions: {len(data.get('positions', []))}
• Rebalance: {'⚠️ Needed' if data.get('rebalance_needed') else '✅ OK'}

**Actions:**"""
                    
                    actions = data.get('suggested_actions', [])
                    if actions:
                        for a in actions[:5]:
                            action_emoji = {"exit": "🚪", "reduce": "📉", "hold": "⏸️", "add": "➕"}.get(a.get('action', ''), "•")
                            text += f"\n{action_emoji} {a.get('symbol', 'N/A')}: {a.get('action', '').upper()}"
                    else:
                        text += "\n✅ No actions needed"
                    
                    await msg.edit_text(text, parse_mode='Markdown')
                else:
                    await msg.edit_text(f"❌ Error: {response.text}")
        except Exception as e:
            await msg.edit_text(f"❌ Error: {str(e)}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Help message with all commands"""
        text = """
📖 **Paper Profit Bot - All Commands**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📊 MARKET DATA**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`/price AAPL` - Get real-time stock price
`/price TSLA` - Works with any stock symbol

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🤖 AI ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`/analyze AAPL` - AI analysis (default strategy)
`/analyze AAPL momentum` - Momentum strategy
`/analyze NVDA growth_investing` - Growth strategy
`/analyze MSFT warren_buffett` - Buffett style
`/strategies` - List all 28 strategies

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📈 PORTFOLIO MANAGEMENT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`/portfolio` - View portfolio with risk
`/alerts` - View current risk alerts
`/actions` - View recommended actions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🔄 AUTO REBALANCING**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`/monitor` - Start continuous monitoring
`/rebalance` - Trigger portfolio rebalance
`/autotrade ON` - Enable auto-trading
`/autotrade OFF` - Disable auto-trading
`/autotrade DRY` - Simulate only (safe)
`/trades` - View trade history

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🎯 STRATEGY EXAMPLES**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• `value_investing` - Buy undervalued
• `growth_investing` - High growth
• `momentum_trading` - Ride trends
• `warren_buffett` - Quality at fair price
• `peter_lynch` - Growth at reasonable price

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`/start` - Back to main menu
        """
        # Check if this came from a button callback
        if update.callback_query:
            await update.callback_query.edit_message_text(text, parse_mode='Markdown')
        else:
            await update.message.reply_text(text, parse_mode='Markdown')

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "menu_analyze":
            await query.edit_message_text(
                "📊 **Stock Analysis**\n\n"
                "**Commands:**\n"
                "`/price AAPL` - Get real-time price\n"
                "`/analyze AAPL` - AI analysis\n"
                "`/analyze AAPL momentum` - With strategy\n\n"
                "**Example strategies:**\n"
                "• `value_investing`\n"
                "• `growth_investing`\n"
                "• `momentum_trading`\n"
                "• `warren_buffett`\n\n"
                "Use `/strategies` to see all 28 strategies",
                parse_mode='Markdown'
            )
        elif query.data == "menu_portfolio":
            await query.edit_message_text(
                "📈 **Portfolio Management**\n\n"
                "**Commands:**\n"
                "`/portfolio` - View portfolio with risk\n"
                "`/alerts` - View current alerts\n"
                "`/actions` - View recommended actions\n\n"
                "**Risk Levels:**\n"
                "🟢 LOW - All good\n"
                "🟡 MODERATE - Monitor closely\n"
                "🟠 HIGH - Action recommended\n"
                "🔴 CRITICAL - Immediate action needed",
                parse_mode='Markdown'
            )
        elif query.data == "menu_rebalance":
            await query.edit_message_text(
                "🔄 **Auto Rebalancing**\n\n"
                "**Commands:**\n"
                "`/monitor` - Start monitoring\n"
                "`/rebalance` - Trigger rebalance\n"
                "`/autotrade ON` - Enable auto-trading\n"
                "`/autotrade OFF` - Disable\n"
                "`/autotrade DRY` - Simulate only\n"
                "`/trades` - View trade history\n\n"
                "**Auto Actions:**\n"
                "• Exit if loss > 15%\n"
                "• Take profit if gain > 30%\n"
                "• Reduce if concentration > 30%",
                parse_mode='Markdown'
            )
        elif query.data == "menu_strategies":
            await query.edit_message_text(
                "🎯 **Trading Strategies**\n\n"
                "Use `/strategies` to see all 28 strategies.\n\n"
                "**Categories:**\n"
                "• 📈 Long Term (5 strategies)\n"
                "• 🔄 Swing Trading (4 strategies)\n"
                "• ⚡ Day Trading (4 strategies)\n"
                "• 📊 Options (4 strategies)\n"
                "• 👑 Greatest Investors (5 strategies)\n\n"
                "**Usage:**\n"
                "`/analyze AAPL value_investing`",
                parse_mode='Markdown'
            )
        elif query.data == "menu_commands":
            await self.help_command(update, context)

    def run(self):
        """Run the bot"""
        if not BOT_TOKEN:
            print("❌ Error: TELEGRAM_BOT_TOKEN not set!")
            print("   Please set it in your .env file")
            return
        
        print("🤖 Starting XION Trade Bot...")
        print(f"📡 API URL: {API_BASE_URL}")
        print(f"📱 Mini App URL: {MINI_APP_URL}")
        print("✅ Features: Real prices, Strategy-specific AI analysis")
        
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("price", self.get_price))
        self.application.add_handler(CommandHandler("analyze", self.analyze_with_strategy))
        self.application.add_handler(CommandHandler("strategies", self.list_strategies))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_risk))
        self.application.add_handler(CommandHandler("monitor", self.start_monitoring))
        self.application.add_handler(CommandHandler("alerts", self.get_alerts))
        self.application.add_handler(CommandHandler("actions", self.get_actions))
        self.application.add_handler(CommandHandler("rebalance", self.trigger_rebalance))
        self.application.add_handler(CommandHandler("autotrade", self.toggle_autotrade))
        self.application.add_handler(CommandHandler("trades", self.get_trades))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        print("✅ Bot is running!")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def start_monitoring(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start continuous portfolio monitoring"""
        await update.message.reply_text(
            "📡 **Continuous Monitoring Active**\n\n"
            "I'm continuously monitoring your portfolio for:\n"
            "• ⚠️ Stop-loss alerts\n"
            "• 💰 Take-profit opportunities\n"
            "• 🔴 Critical risk thresholds\n"
            "• 📊 Concentration warnings\n"
            "• 💤 Idle capital detection\n\n"
            "Use /alerts to see current alerts\n"
            "Use /actions to see recommended actions",
            parse_mode='Markdown'
        )

    async def get_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Get current portfolio alerts"""
        try:
            from services.continuous_monitor import create_monitor_for_account
            
            monitor = create_monitor_for_account("demo", interval=60)
            snapshot = monitor.get_current_state()
            
            if not snapshot or not snapshot.alerts:
                await update.message.reply_text(
                    "✅ **No Active Alerts**\n\n"
                    "Your portfolio is within acceptable parameters.",
                    parse_mode='Markdown'
                )
                return
            
            text = "🚨 **Active Alerts**\n\n"
            for alert in snapshot.alerts[:5]:  # Show top 5
                urgency_emoji = {"immediate": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(alert.urgency.value, "⚪")
                text += f"{urgency_emoji} **{alert.title}**\n"
                text += f"   {alert.message}\n\n"
            
            await update.message.reply_text(text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def get_actions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Get recommended portfolio actions"""
        try:
            from services.continuous_monitor import create_monitor_for_account
            
            monitor = create_monitor_for_account("demo", interval=60)
            snapshot = monitor.get_current_state()
            
            if not snapshot:
                await update.message.reply_text("❌ Could not assess portfolio")
                return
            
            text = "📋 **Recommended Actions**\n\n"
            text += f"📊 Portfolio Risk: {snapshot.risk_level.value.upper()}\n"
            text += f"💵 Capital Efficiency: {snapshot.capital_efficiency:.1f}%\n\n"
            
            actions = {"exit": "🚪", "reduce": "📉", "hold": "⏸️", "add": "➕"}
            
            for pos in snapshot.positions:
                emoji = actions.get(pos.recommended_action.value, "•")
                urgency = {"immediate": "NOW!", "high": "Soon", "medium": "Consider", "low": ""}.get(pos.action_urgency.value, "")
                text += f"{emoji} **{pos.symbol}**: {pos.recommended_action.value.upper()}"
                if urgency:
                    text += f" ({urgency})"
                text += f"\n   P&L: {pos.unrealized_pnl_pct:+.1f}% | Risk: {pos.risk_level.value}\n"
                if pos.reasons:
                    text += f"   _{pos.reasons[0]}_\n"
                text += "\n"
            
            await update.message.reply_text(text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def trigger_rebalance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Trigger manual portfolio rebalance"""
        try:
            from services.auto_rebalancer import ContinuousRebalancingSystem
            
            await update.message.reply_text(
                "🔄 **Triggering Portfolio Rebalance...**\n\n"
                "Analyzing positions and executing trades based on alerts.",
                parse_mode='Markdown'
            )
            
            # Create system in dry-run mode for safety
            system = ContinuousRebalancingSystem(
                account_id="demo",
                monitor_interval=60,
                dry_run=True  # Safe mode
            )
            
            # Get current state and process alerts
            from services.continuous_monitor import create_monitor_for_account
            monitor = create_monitor_for_account("demo", interval=60)
            snapshot = monitor.get_current_state()
            
            if not snapshot:
                await update.message.reply_text("❌ Could not assess portfolio")
                return
            
            # Build response
            text = "🔄 **Rebalance Analysis Complete**\n\n"
            text += f"📊 Risk Level: {snapshot.risk_level.value.upper()}\n"
            text += f"📈 Positions: {snapshot.position_count}\n"
            text += f"🚨 Alerts: {len(snapshot.alerts)}\n\n"
            
            if snapshot.alerts:
                text += "**Recommended Trades (Dry Run):**\n\n"
                for alert in snapshot.alerts[:5]:
                    if alert.symbol:
                        action = "SELL" if "loss" in alert.message.lower() or "risk" in alert.message.lower() else "REDUCE"
                        text += f"• {action} {alert.symbol}: {alert.message[:50]}...\n"
            else:
                text += "✅ No rebalancing needed - portfolio is balanced!"
            
            text += "\n\n_Use /autotrade ON to enable automatic execution_"
            
            await update.message.reply_text(text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Rebalance error: {e}")
            await update.message.reply_text(f"❌ Error: {e}")

    async def toggle_autotrade(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Toggle automatic trading on/off"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "⚙️ **Auto-Trading Settings**\n\n"
                "Auto-trading automatically executes trades when:\n"
                "• 🔴 Stop-loss is hit (loss > 15%)\n"
                "• 💰 Take-profit triggered (gain > 30%)\n"
                "• ⚠️ Position too concentrated (> 30%)\n"
                "• 🚨 Critical risk threshold exceeded\n\n"
                "**Commands:**\n"
                "`/autotrade ON` - Enable auto-trading\n"
                "`/autotrade OFF` - Disable (safe mode)\n"
                "`/autotrade DRY` - Dry run (simulate only)\n\n"
                "⚠️ _Currently in DRY RUN mode (safe)_",
                parse_mode='Markdown'
            )
            return
        
        mode = args[0].upper()
        
        if mode == "ON":
            text = (
                "🟢 **Auto-Trading ENABLED**\n\n"
                "⚠️ **WARNING**: Real trades will be executed!\n\n"
                "The system will automatically:\n"
                "• Exit positions with >15% loss\n"
                "• Take profits on >30% gains\n"
                "• Reduce over-concentrated positions\n\n"
                "_Use /autotrade OFF to disable_"
            )
        elif mode == "OFF":
            text = (
                "🔴 **Auto-Trading DISABLED**\n\n"
                "The system will only monitor and alert.\n"
                "No trades will be executed automatically.\n\n"
                "_Use /autotrade ON to enable_"
            )
        elif mode == "DRY":
            text = (
                "🟡 **Dry Run Mode ENABLED**\n\n"
                "Trades will be simulated but NOT executed.\n"
                "You'll see what WOULD happen without risk.\n\n"
                "_Use /autotrade ON for live trading_"
            )
        else:
            text = "❌ Unknown mode. Use: ON, OFF, or DRY"
        
        await update.message.reply_text(text, parse_mode='Markdown')

    async def get_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Get recent trade history"""
        try:
            from services.auto_rebalancer import create_auto_rebalancer
            
            rebalancer = create_auto_rebalancer("demo", dry_run=True)
            trades = rebalancer.get_trade_history(10)
            stats = rebalancer.get_daily_stats()
            
            text = "📜 **Trade History**\n\n"
            text += f"📊 Today's Stats:\n"
            text += f"   Trades: {stats['trades_today']}\n"
            text += f"   Volume: ${stats['total_volume']:,.2f}\n"
            text += f"   Mode: {'🟡 Dry Run' if stats['dry_run_mode'] else '🟢 Live'}\n\n"
            
            if trades:
                text += "**Recent Trades:**\n"
                for trade in trades[-5:]:
                    emoji = "✅" if trade.success else "❌"
                    text += f"{emoji} {trade.action.value.upper()} {trade.quantity:.1f} {trade.symbol}\n"
                    text += f"   @ ${trade.price:.2f} = ${trade.total_value:,.2f}\n"
            else:
                text += "_No trades executed yet_"
            
            await update.message.reply_text(text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")


def main():
    bot = XionTradeBot()
    bot.run()


if __name__ == "__main__":
    main()
