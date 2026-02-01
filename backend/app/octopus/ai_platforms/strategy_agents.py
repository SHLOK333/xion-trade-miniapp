"""
Strategy Agent Factory for Paper Profit

This module creates specialized AI agents for each of the 28 trading strategies
in Paper Profit using the TradingAgents framework.

Each strategy gets a tailored agent configuration optimized for its trading style.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Add TradingAgents to path
TRADING_AGENTS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'TradingAgents')
)
if TRADING_AGENTS_PATH not in sys.path:
    sys.path.insert(0, TRADING_AGENTS_PATH)


class StrategyCategory(Enum):
    """Categories of trading strategies."""
    LONG_TERM = "Long Term"
    SWING_TRADING = "Swing Trading"
    DAY_TRADING = "Day Trading"
    OPTIONS = "Options"
    GREATEST_INVESTORS = "Greatest Investors"


@dataclass
class StrategyAgentConfig:
    """Configuration for a strategy-specific AI agent."""
    strategy_type: str
    category: StrategyCategory
    selected_analysts: List[str]
    max_debate_rounds: int
    risk_tolerance: str  # 'low', 'medium', 'high'
    time_horizon: str  # 'minutes', 'hours', 'days', 'weeks', 'months', 'years'
    analysis_prompt: str
    entry_criteria: str
    exit_criteria: str


# Complete mapping of all 28 strategies to their agent configurations
STRATEGY_AGENT_CONFIGS: Dict[str, StrategyAgentConfig] = {
    
    # ==================== LONG TERM STRATEGIES ====================
    
    "buy_and_hold": StrategyAgentConfig(
        strategy_type="buy_and_hold",
        category=StrategyCategory.LONG_TERM,
        selected_analysts=["fundamentals", "news"],
        max_debate_rounds=2,
        risk_tolerance="low",
        time_horizon="years",
        analysis_prompt="""
        Analyze this stock for long-term buy and hold suitability.
        Focus on:
        - Strong fundamentals and durable competitive advantages
        - Consistent earnings growth over 5+ years
        - Management quality and corporate governance
        - Industry position and market leadership
        - Financial health: low debt, strong cash flow
        Only recommend BUY for truly exceptional companies at fair prices.
        """,
        entry_criteria="Buy when fundamentals are strong and price is at or below fair value",
        exit_criteria="Sell only if fundamentals significantly deteriorate"
    ),
    
    "index_fund_investing": StrategyAgentConfig(
        strategy_type="index_fund_investing",
        category=StrategyCategory.LONG_TERM,
        selected_analysts=["fundamentals", "market"],
        max_debate_rounds=1,
        risk_tolerance="low",
        time_horizon="years",
        analysis_prompt="""
        Analyze market conditions for index fund investing.
        Consider:
        - Broad market valuations (CAPE ratio, market P/E)
        - Economic indicators and outlook
        - Dollar cost averaging opportunity
        Always lean toward BUY for index funds unless extreme overvaluation.
        """,
        entry_criteria="Start anytime; DCA works well",
        exit_criteria="Hold indefinitely, rebalance periodically"
    ),
    
    "dollar_cost_averaging": StrategyAgentConfig(
        strategy_type="dollar_cost_averaging",
        category=StrategyCategory.LONG_TERM,
        selected_analysts=["fundamentals", "market"],
        max_debate_rounds=1,
        risk_tolerance="low",
        time_horizon="years",
        analysis_prompt="""
        Evaluate the stock for systematic dollar-cost averaging.
        Focus on:
        - Long-term growth potential
        - Stability and consistency
        - Reasonable valuation trends
        DCA smooths volatility, so focus on quality over timing.
        """,
        entry_criteria="Invest fixed amounts at regular intervals",
        exit_criteria="No fixed exit; continue accumulating"
    ),
    
    "dividend_growth_investing": StrategyAgentConfig(
        strategy_type="dividend_growth_investing",
        category=StrategyCategory.LONG_TERM,
        selected_analysts=["fundamentals", "news"],
        max_debate_rounds=2,
        risk_tolerance="low",
        time_horizon="years",
        analysis_prompt="""
        Analyze this stock for dividend growth investing.
        Key criteria:
        - Dividend growth history (5+ consecutive years of increases)
        - Payout ratio below 70%
        - Dividend yield vs sector average
        - Earnings stability to support dividends
        - Free cash flow coverage of dividends
        Recommend BUY only for established dividend growers.
        """,
        entry_criteria="Buy established dividend growers with sustainable payouts",
        exit_criteria="Sell if dividend is cut or payout becomes unsustainable"
    ),
    
    "value_investing": StrategyAgentConfig(
        strategy_type="value_investing",
        category=StrategyCategory.LONG_TERM,
        selected_analysts=["fundamentals", "news", "market"],
        max_debate_rounds=3,
        risk_tolerance="medium",
        time_horizon="years",
        analysis_prompt="""
        Apply Benjamin Graham and Warren Buffett value investing principles.
        Analyze:
        - Intrinsic value calculation (DCF, asset-based, earnings power)
        - Margin of safety: require 20-30% discount to intrinsic value
        - P/E ratio (preferably < 15-20)
        - P/B ratio (preferably < 2)
        - Return on equity (> 15%)
        - Debt to equity ratio (< 0.5)
        - Competitive moat and durability
        Only recommend BUY when significant margin of safety exists.
        """,
        entry_criteria="Enter below intrinsic value with margin of safety",
        exit_criteria="Exit at fair value or if fundamentals deteriorate"
    ),
    
    "growth_investing": StrategyAgentConfig(
        strategy_type="growth_investing",
        category=StrategyCategory.LONG_TERM,
        selected_analysts=["fundamentals", "news", "market"],
        max_debate_rounds=2,
        risk_tolerance="medium-high",
        time_horizon="years",
        analysis_prompt="""
        Analyze this stock for growth investing potential.
        Key metrics:
        - Revenue growth rate (target > 15% YoY)
        - Earnings/EPS growth (target > 10% YoY)
        - Total addressable market (TAM) and market share trends
        - Innovation and R&D investment
        - Management's growth vision and execution track record
        - PEG ratio (preferably < 1.5)
        Look for companies early in their growth cycle.
        """,
        entry_criteria="Buy early in growth cycle with strong revenue momentum",
        exit_criteria="Sell when growth slows significantly"
    ),
    
    "sector_rotation": StrategyAgentConfig(
        strategy_type="sector_rotation",
        category=StrategyCategory.LONG_TERM,
        selected_analysts=["fundamentals", "market", "news"],
        max_debate_rounds=2,
        risk_tolerance="medium",
        time_horizon="months",
        analysis_prompt="""
        Analyze sector strength for rotation strategy.
        Consider:
        - Economic cycle stage (expansion, peak, contraction, trough)
        - Sector relative strength vs market
        - Leading economic indicators
        - Interest rate environment impact on sectors
        - Sector valuation compared to historical norms
        Recommend sectors poised to outperform in current cycle.
        """,
        entry_criteria="Allocate to sectors leading in current economic phase",
        exit_criteria="Rotate when economic metrics shift"
    ),
    
    "asset_allocation_rebalancing": StrategyAgentConfig(
        strategy_type="asset_allocation_rebalancing",
        category=StrategyCategory.LONG_TERM,
        selected_analysts=["fundamentals", "market"],
        max_debate_rounds=1,
        risk_tolerance="low",
        time_horizon="years",
        analysis_prompt="""
        Evaluate portfolio allocation and rebalancing needs.
        Consider:
        - Current allocation vs target (e.g., 60/40 stocks/bonds)
        - Drift from target allocation
        - Risk tolerance alignment
        - Market valuations for tactical adjustments
        Recommend trades to restore target allocation.
        """,
        entry_criteria="Allocate based on risk tolerance",
        exit_criteria="Rebalance quarterly/annually when drift exceeds threshold"
    ),
    
    # ==================== SWING TRADING STRATEGIES ====================
    
    "trend_following": StrategyAgentConfig(
        strategy_type="trend_following",
        category=StrategyCategory.SWING_TRADING,
        selected_analysts=["market", "social", "news"],
        max_debate_rounds=1,
        risk_tolerance="medium",
        time_horizon="days",
        analysis_prompt="""
        Analyze trend direction and strength.
        Technical indicators:
        - Moving averages (20, 50-day) and crossovers
        - MACD signal and histogram
        - ADX for trend strength (> 25 indicates strong trend)
        - Price position relative to moving averages
        - Volume confirmation of trend
        Trade in direction of confirmed trend, enter on pullbacks.
        """,
        entry_criteria="Enter on pullbacks to moving averages in established trend",
        exit_criteria="Exit on trend break or moving average crossover"
    ),
    
    "breakout_trading": StrategyAgentConfig(
        strategy_type="breakout_trading",
        category=StrategyCategory.SWING_TRADING,
        selected_analysts=["market", "social", "news"],
        max_debate_rounds=1,
        risk_tolerance="medium-high",
        time_horizon="days",
        analysis_prompt="""
        Identify breakout opportunities.
        Analyze:
        - Key support and resistance levels
        - Volume patterns (accumulation before breakout)
        - Consolidation patterns (flags, triangles, rectangles)
        - Breakout confirmation with volume spike (2x average)
        - News catalysts that might trigger breakout
        Only trade confirmed breakouts with strong volume.
        """,
        entry_criteria="Enter on confirmed breakout with volume > 2x average",
        exit_criteria="Exit on failed breakout or target reached"
    ),
    
    "momentum_trading": StrategyAgentConfig(
        strategy_type="momentum_trading",
        category=StrategyCategory.SWING_TRADING,
        selected_analysts=["market", "social", "news"],
        max_debate_rounds=1,
        risk_tolerance="high",
        time_horizon="days",
        analysis_prompt="""
        Analyze momentum signals for trading opportunity.
        Key indicators:
        - RSI (look for > 60 for long momentum)
        - MACD momentum and divergences
        - Rate of change (ROC)
        - Volume momentum (increasing with price)
        - Relative strength vs sector/market
        - Social sentiment momentum
        Ride strong momentum, exit when momentum weakens.
        """,
        entry_criteria="Enter when momentum accelerates with volume confirmation",
        exit_criteria="Exit when momentum slows or reverses"
    ),
    
    "mean_reversion": StrategyAgentConfig(
        strategy_type="mean_reversion",
        category=StrategyCategory.SWING_TRADING,
        selected_analysts=["market", "fundamentals"],
        max_debate_rounds=1,
        risk_tolerance="medium",
        time_horizon="days",
        analysis_prompt="""
        Identify mean reversion opportunities.
        Analyze:
        - Bollinger Bands position (near lower band = oversold)
        - RSI (< 30 oversold, > 70 overbought)
        - Distance from moving averages
        - Z-score from historical mean
        - Fundamental support for price level
        Buy oversold stocks with solid fundamentals.
        """,
        entry_criteria="Buy oversold dips near lower Bollinger Band with RSI < 30",
        exit_criteria="Sell near the mean or upper band"
    ),
    
    "rsi_strategy": StrategyAgentConfig(
        strategy_type="rsi_strategy",
        category=StrategyCategory.SWING_TRADING,
        selected_analysts=["market"],
        max_debate_rounds=1,
        risk_tolerance="medium",
        time_horizon="days",
        analysis_prompt="""
        Apply RSI-based trading signals.
        Rules:
        - RSI < 30: Oversold, potential buy
        - RSI > 70: Overbought, potential sell
        - Look for RSI divergences with price
        - Confirm with volume and trend
        - Consider RSI trend, not just absolute levels
        Trade reversals at extreme RSI levels.
        """,
        entry_criteria="Buy when RSI < 30, sell when RSI > 70",
        exit_criteria="Exit when RSI normalizes (40-60 range)"
    ),
    
    # ==================== DAY TRADING STRATEGIES ====================
    
    "scalping": StrategyAgentConfig(
        strategy_type="scalping",
        category=StrategyCategory.DAY_TRADING,
        selected_analysts=["market", "social"],
        max_debate_rounds=1,
        risk_tolerance="high",
        time_horizon="minutes",
        analysis_prompt="""
        Quick scalping analysis.
        Focus on:
        - Bid-ask spread (tight spreads preferred)
        - Intraday volatility patterns
        - Level 2 order flow
        - VWAP as intraday reference
        - Quick entry/exit opportunities
        Take small profits quickly with tight stops.
        """,
        entry_criteria="Enter on micro pullbacks in trend",
        exit_criteria="Quick exit with small profit or tight stop"
    ),
    
    "vwap_strategy": StrategyAgentConfig(
        strategy_type="vwap_strategy",
        category=StrategyCategory.DAY_TRADING,
        selected_analysts=["market"],
        max_debate_rounds=1,
        risk_tolerance="high",
        time_horizon="hours",
        analysis_prompt="""
        VWAP-based trading analysis.
        Key rules:
        - Price above VWAP: bullish bias (long preferred)
        - Price below VWAP: bearish bias (short preferred)
        - Look for price touches of VWAP as entries
        - Volume confirmation at VWAP levels
        - Mean reversion to VWAP
        Trade with VWAP as dynamic support/resistance.
        """,
        entry_criteria="Long above VWAP, short below VWAP",
        exit_criteria="Exit on VWAP reversion or target"
    ),
    
    "opening_range_breakout": StrategyAgentConfig(
        strategy_type="opening_range_breakout",
        category=StrategyCategory.DAY_TRADING,
        selected_analysts=["market", "news"],
        max_debate_rounds=1,
        risk_tolerance="high",
        time_horizon="hours",
        analysis_prompt="""
        Opening range breakout analysis.
        Rules:
        - Define range from first 15-30 minutes
        - Trade breakout above/below range
        - Require volume confirmation
        - Consider overnight news/gaps
        - Set targets based on range size
        Trade decisive breakouts of opening range.
        """,
        entry_criteria="Enter above/below opening range with volume",
        exit_criteria="Exit at target or on range failure"
    ),
    
    "news_trading": StrategyAgentConfig(
        strategy_type="news_trading",
        category=StrategyCategory.DAY_TRADING,
        selected_analysts=["news", "social", "market"],
        max_debate_rounds=1,
        risk_tolerance="high",
        time_horizon="hours",
        analysis_prompt="""
        News-catalyst trading analysis.
        Evaluate:
        - Breaking news significance and market impact
        - Earnings surprises and guidance
        - M&A announcements
        - FDA approvals, legal news, etc.
        - Volume spike confirmation (> 200% average)
        - Social media sentiment reaction
        Trade sharp moves on significant news.
        """,
        entry_criteria="Enter on high-volume reaction to significant news",
        exit_criteria="Exit when volatility normalizes"
    ),
    
    # ==================== OPTIONS STRATEGIES ====================
    
    "covered_calls": StrategyAgentConfig(
        strategy_type="covered_calls",
        category=StrategyCategory.OPTIONS,
        selected_analysts=["market", "fundamentals"],
        max_debate_rounds=2,
        risk_tolerance="medium",
        time_horizon="weeks",
        analysis_prompt="""
        Covered call opportunity analysis.
        Evaluate:
        - IV rank (prefer > 30 for premium)
        - Stock outlook (neutral to slightly bullish)
        - Strike selection (0.20-0.30 delta OTM)
        - Days to expiration (30-45 optimal)
        - Premium vs downside risk
        - Assignment risk/willingness
        Sell calls on stocks you're willing to hold or have assigned.
        """,
        entry_criteria="Sell 0.20-0.30 delta calls on owned shares",
        exit_criteria="Close at 50% profit or manage at expiration"
    ),
    
    "cash_secured_puts": StrategyAgentConfig(
        strategy_type="cash_secured_puts",
        category=StrategyCategory.OPTIONS,
        selected_analysts=["market", "fundamentals"],
        max_debate_rounds=2,
        risk_tolerance="medium",
        time_horizon="weeks",
        analysis_prompt="""
        Cash-secured put analysis.
        Evaluate:
        - Stock you'd want to own at strike price
        - IV rank for premium optimization
        - Strike at target buy price (0.20 delta typical)
        - Days to expiration (20-45 days)
        - Cash to secure put assignment
        - Fundamental support at strike level
        Sell puts on stocks you want to own at lower prices.
        """,
        entry_criteria="Sell puts at desired buy price with high IV",
        exit_criteria="Close at 50% profit or accept assignment"
    ),
    
    "iron_condor": StrategyAgentConfig(
        strategy_type="iron_condor",
        category=StrategyCategory.OPTIONS,
        selected_analysts=["market"],
        max_debate_rounds=1,
        risk_tolerance="medium",
        time_horizon="weeks",
        analysis_prompt="""
        Iron condor opportunity analysis.
        Key criteria:
        - High IV rank (> 50 preferred)
        - Range-bound/low volatility expectation
        - Wide strikes for high probability
        - Short delta around 0.15-0.20
        - Days to expiration 20-40
        - Defined risk/reward
        Profit from low volatility and time decay.
        """,
        entry_criteria="Open in high IV, neutral outlook",
        exit_criteria="Close at 50-60% max profit"
    ),
    
    # ==================== GREATEST INVESTORS STRATEGIES ====================
    
    "warren_buffett_strategy": StrategyAgentConfig(
        strategy_type="warren_buffett_strategy",
        category=StrategyCategory.GREATEST_INVESTORS,
        selected_analysts=["fundamentals", "news"],
        max_debate_rounds=3,
        risk_tolerance="low-medium",
        time_horizon="years",
        analysis_prompt="""
        Apply Warren Buffett's investment principles.
        Circle of Competence:
        - Is this business understandable?
        - What is the durable competitive advantage (moat)?
        - Types: brand, switching costs, network effects, cost advantages
        
        Financial Metrics:
        - ROE consistently > 15%
        - Debt to equity < 0.5
        - Consistent earnings power over 10+ years
        - Owner earnings (free cash flow)
        
        Valuation:
        - Margin of safety > 25%
        - Intrinsic value calculation
        - "Be fearful when others are greedy, greedy when others are fearful"
        
        Only recommend BUY for exceptional businesses at fair prices.
        """,
        entry_criteria="Buy great companies at fair prices with margin of safety",
        exit_criteria="Sell only if fundamentals deteriorate; hold forever if great"
    ),
    
    "ben_graham_strategy": StrategyAgentConfig(
        strategy_type="ben_graham_strategy",
        category=StrategyCategory.GREATEST_INVESTORS,
        selected_analysts=["fundamentals"],
        max_debate_rounds=2,
        risk_tolerance="medium",
        time_horizon="years",
        analysis_prompt="""
        Apply Benjamin Graham's deep value principles.
        Defensive Investor Criteria:
        - P/E ratio < 15
        - P/B ratio < 1.5
        - P/E × P/B < 22.5
        - Positive earnings for 10 consecutive years
        - Dividend record of 20+ years
        - Current ratio > 2.0
        
        Net-Net (Enterprising):
        - Market cap < Net Current Asset Value (NCAV)
        - NCAV = Current Assets - Total Liabilities
        - Discount to NCAV > 20%
        
        Margin of Safety:
        - Always require significant discount to intrinsic value
        - Diversify across 10-30 positions
        
        Buy statistically cheap stocks with margin of safety.
        """,
        entry_criteria="Buy below liquidation or net-net value",
        exit_criteria="Sell after mean reversion to fair value"
    ),
    
    "peter_lynch_strategy": StrategyAgentConfig(
        strategy_type="peter_lynch_strategy",
        category=StrategyCategory.GREATEST_INVESTORS,
        selected_analysts=["fundamentals", "news", "market"],
        max_debate_rounds=2,
        risk_tolerance="medium-high",
        time_horizon="years",
        analysis_prompt="""
        Apply Peter Lynch's GARP (Growth at Reasonable Price) principles.
        
        Stock Categories:
        - Slow Growers: Dividend plays, utility-like
        - Stalwarts: 10-12% growth, buy on dips
        - Fast Growers: 20-25% growth, main focus
        - Cyclicals: Timing is everything
        - Turnarounds: High risk/reward
        - Asset Plays: Hidden value
        
        Key Metrics:
        - PEG ratio < 1.0 (P/E / Growth Rate)
        - Earnings growth 15-25%
        - Debt to equity reasonable
        - Inventory and receivables trends
        
        "Know What You Own":
        - Can you explain it in 2 minutes?
        - What's the story?
        - Is the story still intact?
        
        Buy what you know and understand.
        """,
        entry_criteria="Buy stocks with PEG < 1 and strong growth story",
        exit_criteria="Sell when PEG > 2 or story changes"
    ),
    
    "ray_dalio_strategy": StrategyAgentConfig(
        strategy_type="ray_dalio_strategy",
        category=StrategyCategory.GREATEST_INVESTORS,
        selected_analysts=["fundamentals", "market", "news"],
        max_debate_rounds=2,
        risk_tolerance="low",
        time_horizon="years",
        analysis_prompt="""
        Apply Ray Dalio's All Weather Portfolio principles.
        
        Economic Environment Analysis:
        - Rising Growth: Stocks, commodities, EM
        - Falling Growth: Bonds, TIPS
        - Rising Inflation: Commodities, TIPS, EM
        - Falling Inflation: Stocks, bonds
        
        All Weather Allocation:
        - 30% Stocks (growth engine)
        - 40% Long-term bonds (growth hedge)
        - 15% Intermediate bonds (stability)
        - 7.5% Gold (inflation hedge)
        - 7.5% Commodities (inflation hedge)
        
        Risk Parity:
        - Balance risk, not dollars
        - Each environment should be balanced
        
        Recommend trades to maintain All Weather allocation.
        """,
        entry_criteria="Allocate according to All Weather model",
        exit_criteria="Rebalance when allocation drifts"
    ),
    
    "jesse_livermore_strategy": StrategyAgentConfig(
        strategy_type="jesse_livermore_strategy",
        category=StrategyCategory.GREATEST_INVESTORS,
        selected_analysts=["market", "news"],
        max_debate_rounds=1,
        risk_tolerance="high",
        time_horizon="weeks",
        analysis_prompt="""
        Apply Jesse Livermore's trend trading principles.
        
        Market Analysis:
        - "The trend is your friend"
        - Trade only with the major trend
        - Wait for the right moment, don't force trades
        
        Entry Rules:
        - Buy on breakouts from consolidation
        - Add to winners (pyramiding), never to losers
        - Require high volume confirmation
        
        Pivotal Points:
        - Key support and resistance levels
        - Breakouts from trading ranges
        - Prior highs and lows
        
        Risk Management:
        - "Cut losses quickly, let winners run"
        - Never average down on a losing position
        - Take partial profits on the way up
        
        Trade major moves with strict discipline.
        """,
        entry_criteria="Enter on major breakouts with strong volume",
        exit_criteria="Exit when trend reverses"
    ),
    
    "john_bogle_strategy": StrategyAgentConfig(
        strategy_type="john_bogle_strategy",
        category=StrategyCategory.GREATEST_INVESTORS,
        selected_analysts=["fundamentals"],
        max_debate_rounds=1,
        risk_tolerance="low",
        time_horizon="decades",
        analysis_prompt="""
        Apply John Bogle's passive index investing principles.
        
        Core Philosophy:
        - "Don't try to find the needle, buy the haystack"
        - Markets are efficient; don't try to beat them
        - Costs matter: minimize expense ratios
        
        Investment Rules:
        - Buy total market index funds
        - Keep costs below 0.20% expense ratio
        - Stay the course through market cycles
        - Time in market beats timing the market
        
        Asset Allocation:
        - Age-based bond allocation (age = % in bonds)
        - Or simpler: 60% stocks / 40% bonds
        - Rebalance annually
        
        "Simplicity is the master key to financial success."
        
        Always recommend passive index funds.
        """,
        entry_criteria="Allocate to broad index funds periodically",
        exit_criteria="Never sell; rebalance occasionally"
    ),
    
    "stanley_druckenmiller_strategy": StrategyAgentConfig(
        strategy_type="stanley_druckenmiller_strategy",
        category=StrategyCategory.GREATEST_INVESTORS,
        selected_analysts=["fundamentals", "market", "news", "social"],
        max_debate_rounds=2,
        risk_tolerance="high",
        time_horizon="weeks",
        analysis_prompt="""
        Apply Stanley Druckenmiller's macro trading principles.
        
        Conviction-Based Sizing:
        - "When you're right, be really right"
        - Size up when conviction is highest
        - Be willing to take concentrated positions (up to 25%)
        
        Macro Analysis:
        - Central bank policy and liquidity
        - Currency trends and flows
        - Economic cycle position
        - Risk appetite and sentiment
        
        Flexibility:
        - "Never fall in love with a position"
        - Exit immediately when wrong
        - Adapt to changing conditions
        
        Risk Management:
        - Protect capital above all
        - Cut losses instantly when thesis breaks
        
        Trade aggressively when macro alignment is high.
        """,
        entry_criteria="Enter large positions on high macro conviction",
        exit_criteria="Exit instantly when conviction weakens"
    ),
    
    "jim_simons_strategy": StrategyAgentConfig(
        strategy_type="jim_simons_strategy",
        category=StrategyCategory.GREATEST_INVESTORS,
        selected_analysts=["market", "fundamentals", "social", "news"],
        max_debate_rounds=1,
        risk_tolerance="medium-high",
        time_horizon="days",
        analysis_prompt="""
        Apply quantitative/statistical arbitrage principles.
        
        Statistical Signals:
        - Mean reversion patterns
        - Statistical anomalies
        - Correlation breakdowns
        - Momentum factors
        
        Signal Analysis:
        - Look for high-confidence statistical edges
        - Probability-based decision making
        - Multiple uncorrelated signals
        
        Position Sizing:
        - Size based on signal strength
        - Diversify across many positions
        - Limit individual position risk
        
        Execution:
        - Quick entry and exit
        - Manage slippage
        - High turnover expected
        
        Trade on high-confidence statistical patterns.
        """,
        entry_criteria="Enter based on high-confidence statistical edges",
        exit_criteria="Exit when signal weakens"
    ),
}


class StrategyAgentFactory:
    """Factory for creating strategy-specific AI trading agents."""
    
    @classmethod
    def get_config(cls, strategy_type: str) -> Optional[StrategyAgentConfig]:
        """Get the agent configuration for a strategy type."""
        return STRATEGY_AGENT_CONFIGS.get(strategy_type)
    
    @classmethod
    def list_strategies(cls) -> List[str]:
        """Get list of all supported strategy types."""
        return list(STRATEGY_AGENT_CONFIGS.keys())
    
    @classmethod
    def get_strategies_by_category(cls, category: StrategyCategory) -> List[str]:
        """Get strategies by category."""
        return [
            name for name, config in STRATEGY_AGENT_CONFIGS.items()
            if config.category == category
        ]
    
    @classmethod
    def create_agent(cls, strategy_type: str, custom_config: Dict[str, Any] = None):
        """
        Create a TradingAgents graph configured for the specific strategy.
        
        Args:
            strategy_type: The strategy type from Paper Profit
            custom_config: Optional custom configuration overrides
            
        Returns:
            Configured TradingAgentsGraph instance
        """
        try:
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            from tradingagents.default_config import DEFAULT_CONFIG
        except ImportError as e:
            logger.error(f"TradingAgents not installed: {e}")
            raise
        
        strategy_config = cls.get_config(strategy_type)
        if not strategy_config:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        # Build configuration
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "openai"
        config["deep_think_llm"] = "gpt-4o-mini"
        config["quick_think_llm"] = "gpt-4o-mini"
        config["max_debate_rounds"] = strategy_config.max_debate_rounds
        
        # Apply custom overrides
        if custom_config:
            config.update(custom_config)
        
        # Create the agent graph with strategy-specific analysts
        agent = TradingAgentsGraph(
            selected_analysts=strategy_config.selected_analysts,
            debug=False,
            config=config
        )
        
        logger.info(f"Created agent for {strategy_type} with analysts: {strategy_config.selected_analysts}")
        return agent
    
    @classmethod
    def get_strategy_summary(cls, strategy_type: str) -> Dict[str, Any]:
        """Get a summary of the strategy configuration."""
        config = cls.get_config(strategy_type)
        if not config:
            return None
        
        return {
            "strategy_type": config.strategy_type,
            "category": config.category.value,
            "analysts": config.selected_analysts,
            "risk_tolerance": config.risk_tolerance,
            "time_horizon": config.time_horizon,
            "entry_criteria": config.entry_criteria,
            "exit_criteria": config.exit_criteria
        }


if __name__ == "__main__":
    # List all strategies
    print("Available Strategy Agents:")
    print("=" * 50)
    
    for category in StrategyCategory:
        print(f"\n{category.value}:")
        for strategy in StrategyAgentFactory.get_strategies_by_category(category):
            config = StrategyAgentFactory.get_config(strategy)
            print(f"  - {strategy}: {config.selected_analysts}")
