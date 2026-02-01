"""
TradingAgents Integration for Paper Profit
Integrates the TradingAgents multi-agent LLM framework with Paper Profit strategies.

This module creates AI-powered trading agents that can analyze stocks using multiple
specialized agents (analysts, researchers, traders, risk managers) to make trading decisions.
"""

import sys
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add TradingAgents to path
TRADING_AGENTS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'TradingAgents')
)
if TRADING_AGENTS_PATH not in sys.path:
    sys.path.insert(0, TRADING_AGENTS_PATH)

logger = logging.getLogger(__name__)


class TradingAgentsService:
    """
    Service that integrates TradingAgents framework with Paper Profit strategies.
    
    Maps Paper Profit's 28 trading strategies to appropriate AI agent configurations.
    """
    
    # Strategy to analyst configuration mapping
    STRATEGY_ANALYST_MAP = {
        # Long Term Strategies - Focus on fundamentals
        'buy_and_hold': ['fundamentals', 'news'],
        'index_fund_investing': ['fundamentals', 'market'],
        'dollar_cost_averaging': ['fundamentals', 'market'],
        'dividend_growth_investing': ['fundamentals', 'news'],
        'value_investing': ['fundamentals', 'news', 'market'],
        'growth_investing': ['fundamentals', 'news', 'market'],
        'sector_rotation': ['fundamentals', 'market', 'news'],
        'asset_allocation_rebalancing': ['fundamentals', 'market'],
        
        # Swing Trading - Technical + Sentiment
        'trend_following': ['market', 'social', 'news'],
        'breakout_trading': ['market', 'social', 'news'],
        'momentum_trading': ['market', 'social', 'news'],
        'mean_reversion': ['market', 'fundamentals'],
        'rsi_strategy': ['market'],
        
        # Day Trading - All signals needed quickly
        'scalping': ['market', 'social'],
        'vwap_strategy': ['market'],
        'opening_range_breakout': ['market', 'news'],
        'news_trading': ['news', 'social', 'market'],
        
        # Options - Need all perspectives
        'covered_calls': ['market', 'fundamentals'],
        'cash_secured_puts': ['market', 'fundamentals'],
        'iron_condor': ['market'],
        
        # Greatest Investors - Strategy-specific combinations
        'warren_buffett_strategy': ['fundamentals', 'news'],
        'ben_graham_strategy': ['fundamentals'],
        'peter_lynch_strategy': ['fundamentals', 'news', 'market'],
        'ray_dalio_strategy': ['fundamentals', 'market', 'news'],
        'jesse_livermore_strategy': ['market', 'news'],
        'john_bogle_strategy': ['fundamentals'],
        'stanley_druckenmiller_strategy': ['fundamentals', 'market', 'news', 'social'],
        'jim_simons_strategy': ['market', 'fundamentals', 'social', 'news'],
    }
    
    # Strategy-specific prompts for enhanced analysis
    STRATEGY_PROMPTS = {
        'value_investing': "Focus on intrinsic value, margin of safety, P/E ratios below 15, P/B below 1.5",
        'growth_investing': "Prioritize revenue growth >15%, EPS growth >10%, strong market position",
        'dividend_growth_investing': "Look for dividend aristocrats, payout ratio <70%, consistent dividend increases",
        'momentum_trading': "Focus on RSI signals, volume confirmation, trend strength indicators",
        'warren_buffett_strategy': "Look for durable competitive advantages (moats), strong ROE >15%, undervalued with margin of safety",
        'ben_graham_strategy': "Apply strict valuation metrics: P/E <15, P/B <1.5, seek net-net opportunities",
        'peter_lynch_strategy': "Find GARP opportunities: PEG <1, strong earnings growth with reasonable valuation",
        'ray_dalio_strategy': "Consider macroeconomic environment, asset allocation across stocks/bonds/gold/commodities",
        'jim_simons_strategy': "Apply quantitative analysis, statistical patterns, mean reversion signals",
    }
    
    def __init__(self, db_session=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the TradingAgents service.
        
        Args:
            db_session: Database session for logging
            config: Custom configuration for the trading agents
        """
        self.db = db_session
        self.config = config or self._get_default_config()
        self._trading_graph = None
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for TradingAgents."""
        try:
            from tradingagents.default_config import DEFAULT_CONFIG
            config = DEFAULT_CONFIG.copy()
            
            # Use cost-effective models for testing
            config["llm_provider"] = "openai"
            config["deep_think_llm"] = "gpt-4o-mini"
            config["quick_think_llm"] = "gpt-4o-mini"
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
            
            # Data vendors
            config["data_vendors"] = {
                "core_stock_apis": "yfinance",
                "technical_indicators": "yfinance", 
                "fundamental_data": "alpha_vantage",
                "news_data": "alpha_vantage",
            }
            
            return config
        except ImportError:
            logger.warning("TradingAgents not installed, using minimal config")
            return {}
    
    def _get_trading_graph(self, strategy_type: str):
        """
        Get or create a TradingAgentsGraph configured for the given strategy.
        
        Args:
            strategy_type: The Paper Profit strategy type
            
        Returns:
            Configured TradingAgentsGraph instance
        """
        try:
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            
            # Get analysts for this strategy
            selected_analysts = self.STRATEGY_ANALYST_MAP.get(
                strategy_type, 
                ['market', 'fundamentals', 'news', 'social']  # Default: all
            )
            
            logger.info(f"Creating TradingAgentsGraph for {strategy_type} with analysts: {selected_analysts}")
            
            return TradingAgentsGraph(
                selected_analysts=selected_analysts,
                debug=False,
                config=self.config
            )
        except ImportError as e:
            logger.error(f"Failed to import TradingAgentsGraph: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create TradingAgentsGraph: {e}")
            raise
    
    def analyze_stock(
        self, 
        symbol: str, 
        strategy_type: str,
        trade_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a stock using TradingAgents for a specific strategy.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            strategy_type: Paper Profit strategy type (e.g., 'value_investing')
            trade_date: Date for analysis (default: today)
            
        Returns:
            Analysis result with decision (BUY/SELL/HOLD) and reasoning
        """
        if trade_date is None:
            trade_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Get configured trading graph for this strategy
            trading_graph = self._get_trading_graph(strategy_type)
            
            logger.info(f"Analyzing {symbol} with strategy {strategy_type} for date {trade_date}")
            
            # Run the multi-agent analysis
            final_state, decision = trading_graph.propagate(symbol, trade_date)
            
            # Extract relevant reports from the analysis
            result = {
                "symbol": symbol,
                "strategy_type": strategy_type,
                "trade_date": trade_date,
                "decision": decision,  # BUY, SELL, or HOLD
                "reports": {
                    "market_report": final_state.get("market_report", ""),
                    "sentiment_report": final_state.get("sentiment_report", ""),
                    "news_report": final_state.get("news_report", ""),
                    "fundamentals_report": final_state.get("fundamentals_report", ""),
                },
                "investment_plan": final_state.get("investment_plan", ""),
                "trader_plan": final_state.get("trader_investment_plan", ""),
                "final_trade_decision": final_state.get("final_trade_decision", ""),
                "success": True
            }
            
            logger.info(f"Analysis complete for {symbol}: {decision}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "strategy_type": strategy_type,
                "trade_date": trade_date,
                "decision": "HOLD",
                "error": str(e),
                "success": False
            }
    
    def batch_analyze(
        self, 
        symbols: List[str], 
        strategy_type: str,
        trade_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple stocks for a strategy.
        
        Args:
            symbols: List of stock ticker symbols
            strategy_type: Paper Profit strategy type
            trade_date: Date for analysis
            
        Returns:
            List of analysis results
        """
        results = []
        for symbol in symbols:
            result = self.analyze_stock(symbol, strategy_type, trade_date)
            results.append(result)
        return results
    
    def get_trading_signal(
        self, 
        symbol: str, 
        strategy_type: str,
        strategy_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get a trading signal for a stock based on strategy parameters.
        
        This is the main integration point with Paper Profit's trading bot.
        
        Args:
            symbol: Stock ticker symbol
            strategy_type: Paper Profit strategy type
            strategy_params: Strategy parameters from Paper Profit
            
        Returns:
            Trading signal with action, confidence, and reasoning
        """
        try:
            analysis = self.analyze_stock(symbol, strategy_type)
            
            if not analysis.get("success"):
                return {
                    "symbol": symbol,
                    "action": "HOLD",
                    "confidence": 0.0,
                    "reason": f"Analysis failed: {analysis.get('error', 'Unknown error')}",
                    "source": "trading_agents"
                }
            
            decision = analysis.get("decision", "HOLD").upper()
            
            # Map decision to action
            action_map = {
                "BUY": "BUY",
                "SELL": "SELL",
                "HOLD": "HOLD",
                "STRONG BUY": "BUY",
                "STRONG SELL": "SELL"
            }
            action = action_map.get(decision, "HOLD")
            
            # Calculate confidence based on analyst consensus
            reports = analysis.get("reports", {})
            confidence = 0.75 if all(reports.values()) else 0.5
            
            return {
                "symbol": symbol,
                "action": action,
                "confidence": confidence,
                "reason": analysis.get("investment_plan", "AI agent analysis"),
                "trader_reasoning": analysis.get("trader_plan", ""),
                "market_report": reports.get("market_report", ""),
                "fundamentals_report": reports.get("fundamentals_report", ""),
                "source": "trading_agents",
                "strategy_type": strategy_type
            }
            
        except Exception as e:
            logger.error(f"Error getting trading signal for {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "action": "HOLD",
                "confidence": 0.0,
                "reason": f"Error: {str(e)}",
                "source": "trading_agents"
            }


def get_strategy_agents_config(strategy_type: str) -> Dict[str, Any]:
    """
    Get the recommended TradingAgents configuration for a Paper Profit strategy.
    
    Args:
        strategy_type: The strategy index from strategy-list.yaml
        
    Returns:
        Configuration dict with analysts and settings
    """
    analysts = TradingAgentsService.STRATEGY_ANALYST_MAP.get(
        strategy_type,
        ['market', 'fundamentals', 'news', 'social']
    )
    
    prompt = TradingAgentsService.STRATEGY_PROMPTS.get(strategy_type, "")
    
    return {
        "strategy_type": strategy_type,
        "selected_analysts": analysts,
        "strategy_prompt": prompt,
        "recommended_debate_rounds": 1 if strategy_type in ['scalping', 'vwap_strategy'] else 2
    }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test the service
    service = TradingAgentsService()
    
    # Analyze AAPL with value investing strategy
    result = service.analyze_stock("AAPL", "value_investing")
    print(f"Decision for AAPL: {result.get('decision')}")
    print(f"Investment Plan: {result.get('investment_plan')}")
