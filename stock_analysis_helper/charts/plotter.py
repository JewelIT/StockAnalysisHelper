"""Chart Plotter for creating financial charts with technical indicators"""

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from typing import Dict, List, Optional, Tuple
import os


class ChartPlotter:
    """Creates charts for stock price data with technical indicators"""
    
    def __init__(self, output_dir: str = "charts"):
        """
        Initialize chart plotter
        
        Args:
            output_dir: Directory to save charts
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def calculate_sma(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Calculate Simple Moving Average
        
        Args:
            data: Price data
            window: Window size for SMA
            
        Returns:
            SMA series
        """
        return data['Close'].rolling(window=window).mean()
    
    def calculate_ema(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Args:
            data: Price data
            window: Window size for EMA
            
        Returns:
            EMA series
        """
        return data['Close'].ewm(span=window, adjust=False).mean()
    
    def calculate_rsi(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index
        
        Args:
            data: Price data
            window: Window size for RSI
            
        Returns:
            RSI series
        """
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data: Price data
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
        
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def plot_price_with_indicators(self, data: pd.DataFrame, symbol: str, 
                                   indicators: List[str] = ['SMA20', 'SMA50']) -> str:
        """
        Plot price chart with technical indicators
        
        Args:
            data: Price data (OHLCV format)
            symbol: Stock symbol
            indicators: List of indicators to plot
            
        Returns:
            Path to saved chart
        """
        if data.empty:
            raise ValueError("No data to plot")
        
        # Prepare additional plots
        apds = []
        
        # Add moving averages
        if 'SMA20' in indicators:
            sma20 = self.calculate_sma(data, 20)
            apds.append(mpf.make_addplot(sma20, color='blue', width=1.5))
        
        if 'SMA50' in indicators:
            sma50 = self.calculate_sma(data, 50)
            apds.append(mpf.make_addplot(sma50, color='red', width=1.5))
        
        if 'EMA20' in indicators:
            ema20 = self.calculate_ema(data, 20)
            apds.append(mpf.make_addplot(ema20, color='green', width=1.5))
        
        # Create the plot
        output_path = os.path.join(self.output_dir, f"{symbol}_chart.png")
        
        mpf.plot(data, type='candle', style='charles', 
                 title=f'{symbol} Price Chart',
                 ylabel='Price ($)',
                 volume=True,
                 addplot=apds if apds else None,
                 savefig=output_path)
        
        return output_path
    
    def plot_rsi(self, data: pd.DataFrame, symbol: str) -> str:
        """
        Plot RSI indicator
        
        Args:
            data: Price data
            symbol: Stock symbol
            
        Returns:
            Path to saved chart
        """
        rsi = self.calculate_rsi(data)
        
        plt.figure(figsize=(12, 6))
        plt.plot(rsi.index, rsi, label='RSI', color='purple')
        plt.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
        plt.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
        plt.title(f'{symbol} - Relative Strength Index (RSI)')
        plt.xlabel('Date')
        plt.ylabel('RSI')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_path = os.path.join(self.output_dir, f"{symbol}_rsi.png")
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def plot_macd(self, data: pd.DataFrame, symbol: str) -> str:
        """
        Plot MACD indicator
        
        Args:
            data: Price data
            symbol: Stock symbol
            
        Returns:
            Path to saved chart
        """
        macd_line, signal_line, histogram = self.calculate_macd(data)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # Price chart
        ax1.plot(data.index, data['Close'], label='Close Price', color='blue')
        ax1.set_title(f'{symbol} - Price and MACD')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # MACD chart
        ax2.plot(macd_line.index, macd_line, label='MACD', color='blue')
        ax2.plot(signal_line.index, signal_line, label='Signal', color='red')
        ax2.bar(histogram.index, histogram, label='Histogram', color='gray', alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('MACD')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_path = os.path.join(self.output_dir, f"{symbol}_macd.png")
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def create_portfolio_overview(self, portfolio_data: Dict, output_name: str = "portfolio_overview") -> str:
        """
        Create overview chart for entire portfolio
        
        Args:
            portfolio_data: Dictionary with portfolio performance data
            output_name: Name for output file
            
        Returns:
            Path to saved chart
        """
        if not portfolio_data:
            raise ValueError("No portfolio data to plot")
        
        symbols = list(portfolio_data.keys())
        values = [portfolio_data[symbol].get('value', 0) for symbol in symbols]
        
        plt.figure(figsize=(10, 6))
        plt.bar(symbols, values, color='steelblue')
        plt.title('Portfolio Overview')
        plt.xlabel('Symbol')
        plt.ylabel('Value ($)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        output_path = os.path.join(self.output_dir, f"{output_name}.png")
        plt.savefig(output_path)
        plt.close()
        
        return output_path
