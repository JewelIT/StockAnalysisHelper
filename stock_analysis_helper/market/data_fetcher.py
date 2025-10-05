"""Market Data Fetcher for retrieving stock and crypto data"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class MarketDataFetcher:
    """Fetches market data for stocks and cryptocurrencies"""
    
    def __init__(self):
        """Initialize market data fetcher"""
        self.cache = {}
    
    def get_stock_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """
        Get stock price data
        
        Args:
            symbol: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with OHLCV data
        """
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        return data
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            Current price
        """
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('currentPrice', info.get('regularMarketPrice', 0))
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        Get detailed stock information
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with stock information
        """
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "name": info.get("longName", symbol),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
            "previous_close": info.get("previousClose", 0),
            "open": info.get("open", 0),
            "day_high": info.get("dayHigh", 0),
            "day_low": info.get("dayLow", 0),
            "volume": info.get("volume", 0),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "dividend_yield": info.get("dividendYield", 0),
            "52_week_high": info.get("fiftyTwoWeekHigh", 0),
            "52_week_low": info.get("fiftyTwoWeekLow", 0),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
        }
    
    def get_multiple_stocks_data(self, symbols: List[str], period: str = "1mo") -> Dict[str, pd.DataFrame]:
        """
        Get data for multiple stocks
        
        Args:
            symbols: List of ticker symbols
            period: Data period
            
        Returns:
            Dictionary mapping symbols to their data
        """
        result = {}
        for symbol in symbols:
            try:
                result[symbol] = self.get_stock_data(symbol, period)
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                result[symbol] = pd.DataFrame()
        
        return result
    
    def calculate_returns(self, symbol: str, period: str = "1mo") -> Dict:
        """
        Calculate returns for a symbol
        
        Args:
            symbol: Ticker symbol
            period: Period for calculation
            
        Returns:
            Dictionary with return metrics
        """
        data = self.get_stock_data(symbol, period)
        
        if data.empty:
            return {"error": "No data available"}
        
        start_price = data['Close'].iloc[0]
        end_price = data['Close'].iloc[-1]
        
        total_return = ((end_price - start_price) / start_price) * 100
        
        return {
            "symbol": symbol,
            "start_price": start_price,
            "end_price": end_price,
            "total_return_pct": total_return,
            "period": period
        }
    
    def get_market_summary(self, symbols: List[str]) -> List[Dict]:
        """
        Get market summary for multiple symbols
        
        Args:
            symbols: List of symbols
            
        Returns:
            List of dictionaries with summary data
        """
        summary = []
        
        for symbol in symbols:
            try:
                info = self.get_stock_info(symbol)
                returns = self.calculate_returns(symbol, "1mo")
                
                summary.append({
                    "symbol": symbol,
                    "name": info.get("name", symbol),
                    "current_price": info.get("current_price", 0),
                    "change_pct": returns.get("total_return_pct", 0),
                    "volume": info.get("volume", 0),
                    "market_cap": info.get("market_cap", 0)
                })
            except Exception as e:
                print(f"Error getting summary for {symbol}: {e}")
                summary.append({
                    "symbol": symbol,
                    "error": str(e)
                })
        
        return summary
