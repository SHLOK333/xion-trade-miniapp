"""
AI-Enhanced Trading Bot Integration

This module enhances the Paper Profit trading bot with AI-powered trading agents
from the TradingAgents framework.

Usage:
    from jobs.trading_bot_ai import AITradingBot
    
    bot = AITradingBot(db_session, use_ai_agents=True)
    bot.run()
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.database import get_session
from storage.repositories import RepositoryFactory
from storage.models import Account, Strategy, TradingSignal

logger = logging.getLogger(__name__)


class AITradingBot:
    """
    Trading bot enhanced with TradingAgents AI multi-agent system.
    
    This bot can use traditional technical/fundamental analysis OR
    leverage the TradingAgents framework for AI-powered decision making.
    """
    
    def __init__(self, db, use_ai_agents: bool = True, ai_config: Dict[str, Any] = None):
        """
        Initialize the AI-enhanced trading bot.
        
        Args:
            db: Database session
            use_ai_agents: Whether to use TradingAgents AI agents
            ai_config: Configuration for the AI agents
        """
        self.db = db
        self.repo_factory = RepositoryFactory(db)
        self.use_ai_agents = use_ai_agents
        self.ai_config = ai_config or {}
        
        # Initialize AI services if enabled
        self._trading_agents_service = None
        self._strategy_factory = None
        
        if use_ai_agents:
            self._init_ai_services()
    
    def _init_ai_services(self):
        """Initialize TradingAgents AI services."""
        try:
            from octopus.ai_platforms.trading_agents import TradingAgentsService
            from octopus.ai_platforms.strategy_agents import StrategyAgentFactory
            
            self._trading_agents_service = TradingAgentsService(
                db_session=self.db,
                config=self.ai_config
            )
            self._strategy_factory = StrategyAgentFactory
            
            logger.info("AI Trading Agents initialized successfully")
            
        except ImportError as e:
            logger.warning(f"TradingAgents not available: {e}")
            self.use_ai_agents = False
        except Exception as e:
            logger.error(f"Failed to initialize AI services: {e}")
            self.use_ai_agents = False
    
    def run(self):
        """Main trading bot execution."""
        logger.info("Starting AI-Enhanced Trading Bot...")
        
        try:
            # Get all active accounts with strategies
            active_accounts = self._get_active_accounts()
            
            if not active_accounts:
                logger.info("No active accounts with strategies found.")
                return
            
            logger.info(f"Processing {len(active_accounts)} active accounts")
            
            for account in active_accounts:
                try:
                    self._process_account(account)
                except Exception as e:
                    logger.error(f"Error processing account {account.account_id}: {e}")
            
            logger.info("AI Trading Bot cycle completed.")
            
        except Exception as e:
            logger.error(f"Error in AI trading bot: {e}")
            raise
    
    def _get_active_accounts(self) -> List[Account]:
        """Get all active accounts with assigned strategies."""
        accounts = self.repo_factory.accounts.get_all()
        return [acc for acc in accounts if acc.is_active and acc.strategy_id and acc.status == 'active']
    
    def _process_account(self, account: Account):
        """Process trading for a single account."""
        logger.info(f"Processing account: {account.account_id}")
        
        strategy = self.repo_factory.strategies.get_by_id(account.strategy_id)
        if not strategy or not strategy.is_active:
            logger.warning(f"Strategy not found or inactive for account {account.account_id}")
            return
        
        # Get stock list for the strategy
        stock_list = self._get_stock_list(strategy)
        if not stock_list:
            logger.warning(f"No stock list for strategy {strategy.name}")
            return
        
        logger.info(f"Strategy: {strategy.name}, Stocks: {len(stock_list)}")
        
        # Process each stock
        for symbol in stock_list:
            try:
                self._analyze_and_trade(account, strategy, symbol)
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
    
    def _get_stock_list(self, strategy: Strategy) -> List[str]:
        """Get the stock list for a strategy."""
        if not strategy.stock_list:
            return []
        
        # Parse stock list
        try:
            stocks = json.loads(strategy.stock_list)
            if isinstance(stocks, list):
                return [s.strip().upper() for s in stocks if s]
        except json.JSONDecodeError:
            pass
        
        # Try comma-separated
        if ',' in strategy.stock_list:
            return [s.strip().upper() for s in strategy.stock_list.split(',') if s.strip()]
        
        # Try newline-separated
        return [s.strip().upper() for s in strategy.stock_list.split('\n') if s.strip()]
    
    def _analyze_and_trade(self, account: Account, strategy: Strategy, symbol: str):
        """
        Analyze a stock and generate trading signals.
        
        Uses AI agents if enabled, otherwise falls back to traditional analysis.
        """
        if self.use_ai_agents and self._trading_agents_service:
            signal = self._get_ai_trading_signal(symbol, strategy)
        else:
            signal = self._get_traditional_signal(symbol, strategy)
        
        if signal:
            self._process_trading_signal(account, strategy, symbol, signal)
    
    def _get_ai_trading_signal(self, symbol: str, strategy: Strategy) -> Dict[str, Any]:
        """
        Get trading signal using TradingAgents AI.
        
        Args:
            symbol: Stock ticker symbol
            strategy: The trading strategy
            
        Returns:
            Trading signal with action and reasoning
        """
        try:
            # Get strategy type
            strategy_type = strategy.strategy_type or 'value_investing'
            
            logger.info(f"Getting AI signal for {symbol} using {strategy_type} strategy")
            
            # Use TradingAgents service
            signal = self._trading_agents_service.get_trading_signal(
                symbol=symbol,
                strategy_type=strategy_type,
                strategy_params=strategy.parameters if isinstance(strategy.parameters, dict) else {}
            )
            
            logger.info(f"AI Signal for {symbol}: {signal.get('action')} (confidence: {signal.get('confidence', 0):.2f})")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error getting AI signal for {symbol}: {e}")
            return {
                "symbol": symbol,
                "action": "HOLD",
                "confidence": 0.0,
                "reason": f"AI analysis failed: {str(e)}",
                "source": "fallback"
            }
    
    def _get_traditional_signal(self, symbol: str, strategy: Strategy) -> Dict[str, Any]:
        """
        Get trading signal using traditional technical/fundamental analysis.
        
        This is the fallback when AI agents are not available.
        """
        # Import the original trading bot for traditional analysis
        try:
            from jobs.trading_bot import TradingBot
            traditional_bot = TradingBot(self.db)
            
            # Get instrument
            instrument = self.repo_factory.instruments.get_by_symbol(symbol)
            if not instrument:
                return None
            
            # Get market data and indicators
            market_data = traditional_bot._get_market_data(symbol)
            if not market_data:
                return None
            
            indicators = traditional_bot._get_technical_indicators(instrument.instrument_id)
            strategy_params = traditional_bot._parse_strategy_parameters(strategy)
            
            # Generate signal
            signal_result = traditional_bot._generate_trading_signal(
                None, strategy, instrument, market_data, indicators, strategy_params
            )
            
            if signal_result:
                return {
                    "symbol": symbol,
                    "action": signal_result.get('action', 'HOLD'),
                    "confidence": 0.6,
                    "reason": signal_result.get('reason', 'Traditional analysis'),
                    "source": "traditional"
                }
            
        except Exception as e:
            logger.error(f"Error in traditional analysis for {symbol}: {e}")
        
        return {
            "symbol": symbol,
            "action": "HOLD",
            "confidence": 0.0,
            "reason": "No signal generated",
            "source": "none"
        }
    
    def _process_trading_signal(
        self, 
        account: Account, 
        strategy: Strategy, 
        symbol: str, 
        signal: Dict[str, Any]
    ):
        """Process a trading signal and create orders if appropriate."""
        action = signal.get('action', 'HOLD').upper()
        confidence = signal.get('confidence', 0.0)
        reason = signal.get('reason', '')
        
        # Store the trading signal
        self._save_trading_signal(account, strategy, symbol, signal)
        
        # Check confidence threshold
        min_confidence = 0.6
        if confidence < min_confidence:
            logger.info(f"Signal confidence {confidence:.2f} below threshold for {symbol}")
            return
        
        # For now, just log the signal - full order creation would go here
        logger.info(f"Trading Signal: {symbol} - {action} (confidence: {confidence:.2f})")
        logger.info(f"Reason: {reason}")
        
        # TODO: Implement actual order creation based on signal
        # This would involve:
        # 1. Check current positions
        # 2. Calculate position size
        # 3. Create buy/sell orders
        # 4. Apply risk management
    
    def _save_trading_signal(
        self, 
        account: Account, 
        strategy: Strategy, 
        symbol: str, 
        signal: Dict[str, Any]
    ):
        """Save a trading signal to the database."""
        try:
            # Get or create instrument
            instrument = self.repo_factory.instruments.get_by_symbol(symbol)
            if not instrument:
                # Try to fetch and create the instrument
                from octopus.data_providers.yahoo_finance import YahooFinanceService
                yahoo = YahooFinanceService(self.db)
                instrument = yahoo.get_or_create_instrument(symbol)
            
            if not instrument:
                logger.warning(f"Could not find or create instrument for {symbol}")
                return
            
            # Create trading signal record
            trading_signal = TradingSignal(
                account_id=account.account_id,
                strategy_id=strategy.id,
                symbol_id=instrument.instrument_id,
                signal=signal.get('action', 'HOLD'),
                strength=signal.get('confidence', 0.0),
                reason=signal.get('reason', '')[:500],  # Truncate if too long
                timestamp=datetime.utcnow()
            )
            
            self.db.add(trading_signal)
            self.db.commit()
            
            logger.debug(f"Saved trading signal for {symbol}: {signal.get('action')}")
            
        except Exception as e:
            logger.error(f"Error saving trading signal: {e}")
            self.db.rollback()


def run_ai_trading_bot(use_ai: bool = True):
    """
    Run the AI-enhanced trading bot.
    
    Args:
        use_ai: Whether to use AI agents (True) or traditional analysis (False)
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    with get_session() as db:
        bot = AITradingBot(db, use_ai_agents=use_ai)
        bot.run()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-Enhanced Trading Bot')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI agents')
    args = parser.parse_args()
    
    run_ai_trading_bot(use_ai=not args.no_ai)
