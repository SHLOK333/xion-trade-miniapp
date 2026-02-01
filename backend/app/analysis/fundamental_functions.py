#!/usr/bin/env python3

"""
Parameter Functions Module

This module provides functions for calculating strategy parameters using data
from various third-party services via the octopus data providers.

Each function takes a stock symbol as input and returns the calculated parameter value.
"""

import logging
from typing import Optional, Union, Dict, Any
from sqlalchemy.orm import Session
from octopus.data_providers.alpha_vantage import AlphaVantageService
from octopus.data_providers.financialmodelingprep import FinancialModelingPrepService
from octopus.data_providers.yahoo_finance import YahooFinanceService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FundamentalFunctions:
    """Class containing functions for calculating strategy parameters"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.alpha_vantage = AlphaVantageService(db_session)
        self.fmp = FinancialModelingPrepService(db_session)
        self.yahoo = YahooFinanceService(db_session)
    
    def _get_best_data_provider(self, symbol: str, data_type: str = "fundamental") -> Dict[str, Any]:
        """
        Try multiple data providers to get the best available data for a symbol
        
        Args:
            symbol: Stock symbol
            data_type: Type of data needed ("fundamental", "price", "technical")
            
        Returns:
            Dictionary with the best available data
        """
        data = None
        
        # Try Financial Modeling Prep first for fundamental data
        if data_type == "fundamental":
            try:
                data = self.fmp.fetch_stock_info(symbol)
                if data and data.get('pe_ratio') is not None:
                    logger.info(f"Using Financial Modeling Prep data for {symbol}")
                    return data
            except Exception as e:
                logger.debug(f"Financial Modeling Prep failed for {symbol}: {e}")
        
        # Try Alpha Vantage
        try:
            data = self.alpha_vantage.fetch_stock_info(symbol)
            if data and data.get('pe_ratio') is not None:
                logger.info(f"Using Alpha Vantage data for {symbol}")
                return data
        except Exception as e:
            logger.debug(f"Alpha Vantage failed for {symbol}: {e}")
        
        # Try Yahoo Finance as fallback
        try:
            data = self.yahoo.fetch_stock_info(symbol)
            if data:
                logger.info(f"Using Yahoo Finance data for {symbol}")
                return data
        except Exception as e:
            logger.debug(f"Yahoo Finance failed for {symbol}: {e}")
        
        logger.warning(f"No data available for {symbol} from any provider")
        return {}
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price from the best available provider"""
        try:
            # Try Yahoo Finance first for price data
            price_data = self.yahoo.fetch_current_price(symbol)
            if price_data and price_data.get('price'):
                return price_data['price']
            
            # Try Alpha Vantage
            price_data = self.alpha_vantage.fetch_current_price(symbol)
            if price_data and price_data.get('price'):
                return price_data['price']
            
            # Try Financial Modeling Prep
            price_data = self.fmp.fetch_current_price(symbol)
            if price_data and price_data.get('price'):
                return price_data['price']
                
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
        
        return None
    
    def _get_key_metrics(self, symbol: str) -> Optional[Dict[str, Any]]:
