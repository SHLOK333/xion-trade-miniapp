"""
Paper Profit Telegram Bot

A Telegram bot for interacting with the Paper Profit trading system.
Features:
- Portfolio risk assessment
- AI position debate (aggressive/neutral/conservative)
- Trading signals
- Strategy recommendations

Setup:
1. Create a bot via @BotFather on Telegram
2. Get your bot token
3. Set TELEGRAM_BOT_TOKEN environment variable
4. Run this script
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

# Import services (when running with database context)
try:
    from storage.database import SessionLocal
    from services.portfolio_risk_service import PortfolioRiskService
    from services.ai_position_advisor import AIPositionAdvisor
    HAS_SERVICES = True
except ImportError:
    HAS_SERVICES = False
    logger.warning("Services not available - bot will use HTTP API")


class PaperProfitBot:
    """Telegram bot for Paper Profit trading system"""
    
    def __init__(self):
        self.application = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send welcome message when /start is issued"""
        welcome_message = """
🚀 **Welcome to Paper Profit Bot!**

I'm your AI-powered trading assistant for risk-aware portfolio management.

**Available Commands:**

📊 **Portfolio & Risk**
/portfolio - View your portfolio risk assessment
/risk - Get overall risk summary

🤖 **AI Analysis**
/analyze AAPL - AI debate on a position (3 perspectives)
/signal AAPL - Get trading signal for a stock

📈 **Strategies**
/strategies - List available trading strategies

💰 **Account**
/accounts - View your trading accounts
/balance - Check account balance

**Example Usage:**
```
/analyze AAPL 150 175 100
```
(Analyze AAPL: entry $150, current $175, 100 shares)

Let's make smarter trading decisions together! 💪
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message"""
        help_text = """
**📖 Paper Profit Bot Help**

**Commands:**
• `/start` - Welcome message
• `/help` - This help message
• `/portfolio [account_id]` - Portfolio risk assessment
• `/analyze SYMBOL [entry] [current] [qty]` - AI position debate
• `/signal SYMBOL` - Get BUY/SELL/HOLD signal
• `/strategies` - List trading strategies
• `/accounts` - List your accounts
• `/risk` - Risk system overview

**AI Position Debate:**
The `/analyze` command runs a 3-way AI debate:
🔴 **Aggressive** - High risk, high reward view
🟡 **Neutral** - Balanced perspective
🟢 **Conservative** - Risk-averse view

**Example:**
`/analyze TSLA 200 250 50`
Analyzes 50 shares of TSLA bought at $200, now at $250
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def risk_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show risk system summary"""
        summary = """
🎯 **Continuous Risk-Aware Trading System**

**Risk Levels:**
🟢 Low - Position is safe
🟡 Moderate - Monitor closely  
🟠 High - Consider reducing
🔴 Critical - Action needed

**Position Actions:**
• **HOLD** - Keep current position
• **REDUCE** - Partial exit recommended
• **EXIT** - Full exit recommended
• **ADD** - Increase position
• **REALLOCATE** - Move capital elsewhere

**AI Debate System:**
Each analysis includes 3 perspectives:
• 🔴 Aggressive (risk-seeking)
• 🟡 Neutral (balanced)
• 🟢 Conservative (risk-averse)

Use `/analyze SYMBOL` to get AI recommendations!
        """
        await update.message.reply_text(summary, parse_mode='Markdown')

    async def analyze_position(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Run AI position debate"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "❌ Please provide a symbol!\n\n"
                "**Usage:** `/analyze SYMBOL [entry_price] [current_price] [quantity]`\n\n"
                "**Examples:**\n"
                "`/analyze AAPL` - Quick analysis\n"
                "`/analyze AAPL 150 175 100` - Full analysis",
                parse_mode='Markdown'
            )
            return
        
        symbol = args[0].upper()
        
        # Parse optional parameters
        entry_price = float(args[1]) if len(args) > 1 else 100.0
        current_price = float(args[2]) if len(args) > 2 else 110.0
        quantity = float(args[3]) if len(args) > 3 else 100
        
        # Calculate derived values
        market_value = quantity * current_price
        unrealized_pnl = (current_price - entry_price) * quantity
        pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
        
        # Send "analyzing" message
        msg = await update.message.reply_text(
            f"🔄 Analyzing {symbol}...\n\n"
            f"📊 Entry: ${entry_price:.2f}\n"
            f"💰 Current: ${current_price:.2f}\n"
            f"📈 P&L: {pnl_pct:+.1f}%\n\n"
            "Running AI debate (aggressive vs neutral vs conservative)...",
            parse_mode='Markdown'
        )
        
        try:
            # Run AI analysis
            if HAS_SERVICES:
                result = await self._analyze_with_services(
                    symbol, entry_price, current_price, quantity
                )
            else:
                result = await self._analyze_with_api(
                    symbol, entry_price, current_price, quantity
                )
            
            # Format response
            response = self._format_debate_result(symbol, result, entry_price, current_price, pnl_pct)
            
            await msg.edit_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            await msg.edit_text(
                f"❌ Error analyzing {symbol}: {str(e)}\n\n"
                "Make sure the API server is running!",
                parse_mode='Markdown'
            )

    async def _analyze_with_services(
        self, symbol: str, entry_price: float, current_price: float, quantity: float
    ) -> Dict[str, Any]:
        """Run analysis using direct service calls"""
        db = SessionLocal()
        try:
            advisor = AIPositionAdvisor(db_session=db)
            
            position_data = {
                "entry_price": entry_price,
                "current_price": current_price,
                "quantity": quantity,
                "market_value": quantity * current_price,
                "unrealized_pnl": (current_price - entry_price) * quantity,
                "unrealized_pnl_pct": ((current_price - entry_price) / entry_price * 100),
                "days_held": 30,
                "concentration": 10.0
            }
            
            result = advisor.analyze_position_with_debate(symbol, position_data)
            
            return {
                "final_decision": result.final_decision,
                "final_reasoning": result.final_reasoning,
                "risk_score": result.risk_score,
                "arguments": [
                    {
                        "stance": arg.stance.value,
                        "position_action": arg.position_action,
                        "confidence": arg.confidence,
                        "key_points": arg.key_points
                    }
                    for arg in result.arguments
                ]
            }
        finally:
            db.close()

    async def _analyze_with_api(
        self, symbol: str, entry_price: float, current_price: float, quantity: float
    ) -> Dict[str, Any]:
        """Run analysis using HTTP API"""
        import httpx
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/ai/position-debate/{symbol}",
                json={
                    "entry_price": entry_price,
                    "current_price": current_price,
                    "quantity": quantity,
                    "days_held": 30,
                    "concentration": 10.0
                }
            )
            response.raise_for_status()
            return response.json()

    def _format_debate_result(
        self, symbol: str, result: Dict[str, Any], 
        entry_price: float, current_price: float, pnl_pct: float
    ) -> str:
        """Format debate result for Telegram"""
        decision = result.get("final_decision", "hold").upper()
        risk_score = result.get("risk_score", 50)
        reasoning = result.get("final_reasoning", "")[:500]  # Truncate for Telegram
        
        # Decision emoji
        decision_emoji = {
            "HOLD": "⏸️",
            "REDUCE": "📉",
            "EXIT": "🚪",
            "ADD": "➕"
        }.get(decision, "❓")
        
        # Risk level emoji
        if risk_score >= 75:
            risk_emoji = "🔴"
            risk_level = "CRITICAL"
        elif risk_score >= 50:
            risk_emoji = "🟠"
            risk_level = "HIGH"
        elif risk_score >= 25:
            risk_emoji = "🟡"
            risk_level = "MODERATE"
        else:
            risk_emoji = "🟢"
            risk_level = "LOW"
        
        # Format arguments
        args_text = ""
        for arg in result.get("arguments", []):
            stance = arg.get("stance", "").upper()
            action = arg.get("position_action", "").upper()
            confidence = arg.get("confidence", 0) * 100
            
            stance_emoji = {"AGGRESSIVE": "🔴", "NEUTRAL": "🟡", "CONSERVATIVE": "🟢"}.get(stance, "⚪")
            args_text += f"\n{stance_emoji} **{stance}**: {action} ({confidence:.0f}%)"
        
        response = f"""
🤖 **AI Position Analysis: {symbol}**

📊 **Position Summary:**
• Entry: ${entry_price:.2f}
• Current: ${current_price:.2f}
• P&L: {pnl_pct:+.1f}%

{decision_emoji} **DECISION: {decision}**
{risk_emoji} **Risk Score: {risk_score:.0f}/100 ({risk_level})**

📣 **Debate Results:**{args_text}

💡 **Reasoning:**
{reasoning}

_Analysis generated at {datetime.now().strftime('%H:%M:%S')}_
        """
        return response.strip()

    async def get_signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Get trading signal for a symbol"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "❌ Please provide a symbol!\n"
                "**Usage:** `/signal AAPL`",
                parse_mode='Markdown'
            )
            return
        
        symbol = args[0].upper()
        
        await update.message.reply_text(
            f"🔄 Getting signal for {symbol}...",
            parse_mode='Markdown'
        )
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{API_BASE_URL}/api/trading-agents/signal",
                    json={"symbol": symbol, "strategy_type": "value_investing"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    signal = data.get("signal", "HOLD")
                    confidence = data.get("confidence", 0) * 100
                    
                    signal_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal, "⚪")
                    
                    await update.message.reply_text(
                        f"{signal_emoji} **{symbol}: {signal}**\n"
                        f"Confidence: {confidence:.0f}%",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        f"❌ Error getting signal: {response.text}",
                        parse_mode='Markdown'
                    )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {str(e)}",
                parse_mode='Markdown'
            )

    async def list_strategies(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List available trading strategies"""
        strategies_text = """
📈 **Available Trading Strategies**

**🏦 Long Term (8 strategies)**
• Value Investing
• Growth Investing  
• Dividend Growth
• Index Investing
• GARP (Growth at Reasonable Price)
• Quality Investing
• Buy and Hold
• Sector Rotation

**📊 Swing Trading (5 strategies)**
• Momentum Trading
• Mean Reversion
• Breakout Trading
• Trend Following
• Gap Trading

**⚡ Day Trading (4 strategies)**
• Scalping
• Range Trading
• News Trading
• VWAP Trading

**🎯 Options (3 strategies)**
• Covered Calls
• Protective Puts
• Iron Condor

**🏆 Greatest Investors (8 strategies)**
• Warren Buffett Style
• Peter Lynch Style
• Benjamin Graham Style
• George Soros Style
• Ray Dalio Style
• Carl Icahn Style
• Jim Simons Style
• Cathie Wood Style

Use `/analyze SYMBOL` to get AI recommendations!
        """
        await update.message.reply_text(strategies_text, parse_mode='Markdown')

    async def list_accounts(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List trading accounts"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{API_BASE_URL}/api/accounts")
                
                if response.status_code == 200:
                    accounts = response.json()
                    
                    if not accounts:
                        await update.message.reply_text(
                            "📭 No accounts found. Create one in the web UI!",
                            parse_mode='Markdown'
                        )
                        return
                    
                    text = "💼 **Your Trading Accounts**\n\n"
                    for acc in accounts:
                        balance = acc.get('cash_balance', 0)
                        equity = acc.get('total_equity', 0)
                        name = acc.get('account_name', acc.get('account_id', 'Unknown'))
                        status = "🟢" if acc.get('is_active') else "🔴"
                        
                        text += f"{status} **{name}**\n"
                        text += f"   💵 Cash: ${balance:,.2f}\n"
                        text += f"   📊 Equity: ${equity:,.2f}\n\n"
                    
                    await update.message.reply_text(text, parse_mode='Markdown')
                else:
                    await update.message.reply_text(
                        f"❌ Error fetching accounts: {response.status_code}",
                        parse_mode='Markdown'
                    )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {str(e)}\nMake sure the API server is running!",
                parse_mode='Markdown'
            )

    async def portfolio_risk(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Get portfolio risk assessment"""
        args = context.args
        account_id = args[0] if args else "namo"  # Default account
        
        await update.message.reply_text(
            f"🔄 Analyzing portfolio risk for `{account_id}`...",
            parse_mode='Markdown'
        )
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/risk/portfolio/{account_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    risk_level = data.get('overall_risk_level', 'unknown').upper()
                    risk_emoji = {
                        "LOW": "🟢",
                        "MODERATE": "🟡", 
                        "HIGH": "🟠",
                        "CRITICAL": "🔴"
                    }.get(risk_level, "⚪")
                    
                    total_value = data.get('total_value', 0)
                    cash = data.get('cash_available', 0)
                    invested = data.get('invested_value', 0)
                    pnl = data.get('total_unrealized_pnl', 0)
                    
                    text = f"""
📊 **Portfolio Risk Assessment**
Account: `{account_id}`

{risk_emoji} **Risk Level: {risk_level}**

💰 **Portfolio Value:** ${total_value:,.2f}
💵 **Cash:** ${cash:,.2f}
📈 **Invested:** ${invested:,.2f}
📊 **Unrealized P&L:** ${pnl:+,.2f}

**Metrics:**
• Diversification: {data.get('diversification_score', 0):.0f}/100
• Positions: {len(data.get('positions', []))}
• Rebalance Needed: {'Yes ⚠️' if data.get('rebalance_needed') else 'No ✅'}
                    """
                    
                    # Add suggested actions if any
                    actions = data.get('suggested_actions', [])
                    if actions:
                        text += "\n\n**📋 Suggested Actions:**"
                        for action in actions[:3]:  # Top 3
                            text += f"\n• {action.get('symbol', 'N/A')}: {action.get('action', '').upper()}"
                    
                    await update.message.reply_text(text.strip(), parse_mode='Markdown')
                else:
                    await update.message.reply_text(
                        f"❌ Error: {response.text}",
                        parse_mode='Markdown'
                    )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {str(e)}",
                parse_mode='Markdown'
            )

    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unknown commands"""
        await update.message.reply_text(
            "❓ Unknown command. Use /help to see available commands.",
            parse_mode='Markdown'
        )

    def run(self):
        """Run the bot"""
        if not BOT_TOKEN:
            print("❌ Error: TELEGRAM_BOT_TOKEN not set!")
            print("\nTo set up the bot:")
            print("1. Message @BotFather on Telegram")
            print("2. Create a new bot with /newbot")
            print("3. Copy the token")
            print("4. Set the environment variable:")
            print('   $env:TELEGRAM_BOT_TOKEN = "your_token_here"')
            return
        
        print("🤖 Starting Paper Profit Telegram Bot...")
        print(f"📡 API URL: {API_BASE_URL}")
        
        # Create application
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("risk", self.risk_summary))
        self.application.add_handler(CommandHandler("analyze", self.analyze_position))
        self.application.add_handler(CommandHandler("signal", self.get_signal))
        self.application.add_handler(CommandHandler("strategies", self.list_strategies))
        self.application.add_handler(CommandHandler("accounts", self.list_accounts))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_risk))
        
        # Handle unknown commands
        self.application.add_handler(
            MessageHandler(filters.COMMAND, self.unknown_command)
        )
        
        print("✅ Bot is running! Press Ctrl+C to stop.")
        print("\n📱 Open Telegram and message your bot to get started!")
        
        # Run the bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    bot = PaperProfitBot()
    bot.run()


if __name__ == "__main__":
    main()
