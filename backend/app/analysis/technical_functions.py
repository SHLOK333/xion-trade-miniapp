#!/usr/bin/env python3

"""
Technical Functions Module

This module provides functions for calculating technical indicators and parameters
using data from various third-party services via the octopus data providers.

Each function takes a stock symbol as input and returns the calculated technical indicator value.
"""

import logging
from typing import Optional, Union, Dict, Any, List
from sqlalchemy.orm import Session
from octopus.data_providers.alpha_vantage import AlphaVantageService
from octopus.data_providers.financialmodelingprep import FinancialModelingPrepService
from octopus.data_providers.yahoo_finance import YahooFinanceService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TechnicalFunctions:
    """Class containing functions for calculating technical indicators"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.alpha_vantage = AlphaVantageService(db_session)
        self.fmp = FinancialModelingPrepService(db_session)
        self.yahoo = YahooFinanceService(db_session)
    
    def _get_best_data_provider(self, symbol: str, data_type: str = "technical") -> Dict[str, Any]:
        """
        Try multiple data providers to get the best available data for a symbol
        
        Args:
            symbol: Stock symbol
            data_type: Type of data needed ("technical", "price", "historical")
            
        Returns:
            Dictionary with the best available data
        """
        data = None
        
        # Try Alpha Vantage first for technical data
        if data_type == "technical":
            try:
                data = self.alpha_vantage.get_technical_indicators(symbol)
                if data and data.get('rsi') is not None:
                    logger.info(f"Using Alpha Vantage technical data for {symbol}")
                    return data
            except Exception as e:
                logger.debug(f"Alpha Vantage technical indicators failed for {symbol}: {e}")
        
        # Try Yahoo Finance for price/historical data
        try:
            if data_type == "price":
                data = self.yahoo.fetch_current_price(symbol)
            elif data_type == "historical":
                data = self.yahoo.fetch_historical_data(symbol, "6mo")
            else:
                data = self.yahoo.get_stock_analysis(symbol)
                
            if data:
                logger.info(f"Using Yahoo Finance data for {symbol}")
                return data
        except Exception as e:
            logger.debug(f"Yahoo Finance failed for {symbol}: {e}")
        
        # Try Financial Modeling Prep
        try:
            data = self.fmp.get_stock_analysis(symbol)
            if data:
                logger.info(f"Using Financial Modeling Prep data for {symbol}")
                return data
        except Exception as e:
            logger.debug(f"Financial Modeling Prep failed for {symbol}: {e}")
        
        logger.warning(f"No technical data available for {symbol} from any provider")
        return {}
    
    def _get_historical_prices(self, symbol: str, period: str = "6mo") -> Optional[List[float]]:
        """Get historical closing prices for a symbol"""
        try:
            # Try Yahoo Finance first
            historical_data = self.yahoo.fetch_historical_data(symbol, period)
            if historical_data:
                close_prices = [data['close_price'] for data in historical_data]
                return close_prices
            
            # Try Alpha Vantage
            historical_data = self.alpha_vantage.fetch_historical_data(symbol, period)
            if historical_data:
                close_prices = [data['close_price'] for data in historical_data]
                return close_prices
            
            # Try Financial Modeling Prep
            historical_data = self.fmp.fetch_historical_data(symbol, period)
            if historical_data:
