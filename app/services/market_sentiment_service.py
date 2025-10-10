"""
Market Sentiment Service - Daily market analysis and recommendations
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
import random

logger = logging.getLogger(__name__)

class MarketSentimentService:
    """Service for generating daily market sentiment and recommendations"""
    
    def __init__(self):
        self.cache_file = 'cache/market_sentiment_cache.json'
        self.cache_duration_hours = 4  # Refresh every 4 hours
        
        # Stock recommendations by sector
        self.sector_stocks = {
            'Technology': ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META', 'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE'],
            'Financials': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA', 'AXP', 'BLK'],
            'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'DHR', 'MRK', 'BMY', 'AMGN'],
            'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL'],
            'Industrials': ['BA', 'HON', 'UNP', 'UPS', 'CAT', 'LMT', 'RTX', 'GE', 'MMM', 'DE'],
            'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX', 'BKNG'],
            'Consumer Staples': ['WMT', 'PG', 'KO', 'PEP', 'COST', 'PM', 'MDLZ', 'CL', 'MO', 'KMB'],
            'Materials': ['LIN', 'APD', 'SHW', 'FCX', 'NEM', 'ECL', 'DD', 'DOW', 'NUE', 'VMC'],
            'Real Estate': ['AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'O', 'WELL', 'DLR', 'SPG', 'AVB'],
            'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'PEG', 'XEL', 'ED']
        }
        
    def get_market_indices_data(self) -> Dict:
        """Fetch current data for major market indices"""
        try:
            indices = {
                '^GSPC': 'S&P 500',
                '^DJI': 'Dow Jones',
                '^IXIC': 'NASDAQ',
                '^VIX': 'VIX (Volatility)',
            }
            
            data = {}
            for symbol, name in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='5d')
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
                        change_pct = ((current - previous) / previous) * 100
                        
                        data[name] = {
                            'symbol': symbol,
                            'current': round(current, 2),
                            'change_pct': round(change_pct, 2),
                            'trend': 'up' if change_pct > 0 else 'down'
                        }
                except Exception as e:
                    logger.warning(f"Failed to fetch {name}: {e}")
                    continue
                    
            return data
        except Exception as e:
            logger.error(f"Error fetching market indices: {e}")
            return {}
    
    def get_sector_performance(self) -> Dict:
        """Fetch sector ETF performance"""
        try:
            sectors = {
                'XLK': 'Technology',
                'XLF': 'Financials',
                'XLV': 'Healthcare',
                'XLE': 'Energy',
                'XLI': 'Industrials',
                'XLY': 'Consumer Discretionary',
                'XLP': 'Consumer Staples',
                'XLB': 'Materials',
                'XLRE': 'Real Estate',
                'XLU': 'Utilities',
            }
            
            data = {}
            for symbol, name in sectors.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='5d')
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
                        change_pct = ((current - previous) / previous) * 100
                        
                        data[name] = {
                            'symbol': symbol,
                            'change_pct': round(change_pct, 2),
                            'trend': 'up' if change_pct > 0 else 'down'
                        }
                except Exception as e:
                    logger.warning(f"Failed to fetch sector {name}: {e}")
                    continue
            
            # Sort by performance
            sorted_sectors = sorted(data.items(), key=lambda x: x[1]['change_pct'], reverse=True)
            return dict(sorted_sectors[:5])  # Top 5 performing sectors
            
        except Exception as e:
            logger.error(f"Error fetching sector performance: {e}")
            return {}
    
    def generate_sentiment_analysis(self, market_data: Dict, sector_data: Dict) -> Dict:
        """Generate market sentiment based on market data and sector performance"""
        try:
            # Filter out VIX from trend calculation (it's inverse to market)
            market_indices = {k: v for k, v in market_data.items() if 'VIX' not in k}
            
            # Calculate overall market trend (excluding VIX)
            positive_indices = sum(1 for idx in market_indices.values() if idx['change_pct'] > 0)
            total_indices = len(market_indices)
            market_trend_pct = (positive_indices / total_indices * 100) if total_indices > 0 else 50
            
            # Calculate average market change (excluding VIX)
            avg_change = sum(idx['change_pct'] for idx in market_indices.values()) / total_indices if total_indices > 0 else 0
            
            # Determine sentiment - More sensitive thresholds
            if avg_change > 0.3 and market_trend_pct >= 65:
                sentiment = "BULLISH"
                confidence = min(70 + int(avg_change * 8), 95)
                summary = "Markets showing strong positive momentum across major indices"
            elif avg_change < -0.3 and market_trend_pct <= 35:
                sentiment = "BEARISH"
                confidence = min(70 + int(abs(avg_change) * 8), 95)
                summary = "Markets experiencing downward pressure with widespread declines"
            else:
                sentiment = "NEUTRAL"
                confidence = 50 + int(abs(avg_change) * 10)
                summary = "Markets showing mixed signals with no clear directional trend"
            
            # Generate reasoning
            reasoning_parts = []
            if market_data:
                up_indices = [name for name, data in market_data.items() if data['change_pct'] > 0]
                down_indices = [name for name, data in market_data.items() if data['change_pct'] < 0]
                
                if up_indices:
                    reasoning_parts.append(f"{', '.join(up_indices[:2])} leading gains")
                if down_indices:
                    reasoning_parts.append(f"{', '.join(down_indices[:2])} showing weakness")
            
            if sector_data:
                top_sectors = list(sector_data.keys())[:2]
                reasoning_parts.append(f"{', '.join(top_sectors)} sectors outperforming")
            
            reasoning = ". ".join(reasoning_parts) + "." if reasoning_parts else "Market data analysis in progress."
            
            # Extract key factors
            key_factors = []
            if 'VIX (Volatility)' in market_data:
                vix_data = market_data['VIX (Volatility)']
                if vix_data['current'] > 20:
                    key_factors.append(f"Elevated volatility (VIX: {vix_data['current']})")
                elif vix_data['current'] < 15:
                    key_factors.append(f"Low volatility environment (VIX: {vix_data['current']})")
            
            if sector_data:
                top_sector = list(sector_data.keys())[0]
                key_factors.append(f"{top_sector} sector leading market")
                
                worst_performing = list(sector_data.items())[-1]
                key_factors.append(f"{worst_performing[0]} sector underperforming")
            
            # Generate recommendations based on top sectors
            buy_recommendations = self._generate_buy_recommendations(sector_data, sentiment)
            sell_recommendations = self._generate_sell_recommendations(sector_data, sentiment)
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "summary": summary,
                "reasoning": reasoning,
                "key_factors": key_factors,
                "buy_recommendations": buy_recommendations,
                "sell_recommendations": sell_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating sentiment analysis: {e}")
            return {
                "sentiment": "NEUTRAL",
                "confidence": 50,
                "summary": "Market analysis temporarily unavailable",
                "reasoning": "Unable to generate market sentiment at this time. Please check back later.",
                "key_factors": ["Data unavailable"],
                "buy_recommendations": [],
                "sell_recommendations": []
            }
    
    def _get_stock_price(self, ticker: str) -> Optional[float]:
        """Get current stock price"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d')
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
        except Exception as e:
            logger.warning(f"Failed to get price for {ticker}: {e}")
        return None
    
    def _generate_buy_recommendations(self, sector_data: Dict, sentiment: str, max_recommendations: int = 10) -> List[Dict]:
        """Generate buy recommendations based on top performing sectors with prices"""
        recommendations = []
        
        try:
            # Get top performing sectors
            top_sectors = list(sector_data.items())[:5]  # Get more sectors for better selection
            
            for sector_name, sector_info in top_sectors:
                if sector_name in self.sector_stocks:
                    stocks = self.sector_stocks[sector_name]
                    
                    # Try to get multiple stocks from this sector
                    for ticker in stocks:
                        if len(recommendations) >= max_recommendations:
                            break
                        
                        # Get stock price
                        price = self._get_stock_price(ticker)
                        
                        if price is not None:
                            reason = f"Strong sector performance ({sector_info['change_pct']:+.2f}%) suggests momentum in {sector_name}"
                            
                            recommendations.append({
                                "ticker": ticker,
                                "reason": reason,
                                "sector": sector_name,
                                "price": round(price, 2)
                            })
                        
                        # Stop if we have enough
                        if len(recommendations) >= max_recommendations:
                            break
            
        except Exception as e:
            logger.warning(f"Error generating buy recommendations: {e}")
        
        return recommendations[:max_recommendations]
    
    def _generate_sell_recommendations(self, sector_data: Dict, sentiment: str, max_recommendations: int = 10) -> List[Dict]:
        """Generate sell/avoid recommendations based on underperforming sectors with prices"""
        recommendations = []
        
        try:
            # Get bottom performing sectors
            bottom_sectors = list(sector_data.items())[-5:]  # Get more sectors for better selection
            bottom_sectors.reverse()  # Worst first
            
            for sector_name, sector_info in bottom_sectors:
                if sector_name in self.sector_stocks:
                    stocks = self.sector_stocks[sector_name]
                    
                    # Try to get multiple stocks from this sector
                    for ticker in stocks:
                        if len(recommendations) >= max_recommendations:
                            break
                        
                        # Get stock price
                        price = self._get_stock_price(ticker)
                        
                        if price is not None:
                            reason = f"Sector weakness ({sector_info['change_pct']:+.2f}%) indicates potential headwinds for {sector_name}"
                            
                            recommendations.append({
                                "ticker": ticker,
                                "reason": reason,
                                "sector": sector_name,
                                "price": round(price, 2)
                            })
                        
                        # Stop if we have enough
                        if len(recommendations) >= max_recommendations:
                            break
            
        except Exception as e:
            logger.warning(f"Error generating sell recommendations: {e}")
        
        return recommendations[:max_recommendations]
    
    def load_cache(self) -> Optional[Dict]:
        """Load cached sentiment if still valid"""
        try:
            if not os.path.exists(self.cache_file):
                return None
                
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            
            cached_time = datetime.fromisoformat(cache.get('timestamp', ''))
            if datetime.now() - cached_time < timedelta(hours=self.cache_duration_hours):
                logger.info("Using cached market sentiment")
                return cache.get('data')
            else:
                logger.info("Cache expired, refreshing market sentiment")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None
    
    def save_cache(self, data: Dict):
        """Save sentiment to cache"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            cache = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
            logger.info("Market sentiment cached successfully")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def get_daily_sentiment(self, force_refresh: bool = False) -> Dict:
        """
        Get daily market sentiment with caching
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            Dictionary containing market sentiment analysis
        """
        try:
            # Check cache first unless force refresh
            if not force_refresh:
                cached = self.load_cache()
                if cached:
                    return cached
            
            logger.info("Generating fresh market sentiment")
            
            # Fetch market data
            market_data = self.get_market_indices_data()
            sector_data = self.get_sector_performance()
            
            # Generate sentiment analysis
            ai_sentiment = self.generate_sentiment_analysis(market_data, sector_data)
            
            # Combine all data
            result = {
                'timestamp': datetime.now().isoformat(),
                'market_indices': market_data,
                'top_sectors': sector_data,
                'sentiment': ai_sentiment.get('sentiment', 'NEUTRAL'),
                'confidence': ai_sentiment.get('confidence', 50),
                'summary': ai_sentiment.get('summary', ''),
                'reasoning': ai_sentiment.get('reasoning', ''),
                'key_factors': ai_sentiment.get('key_factors', []),
                'buy_recommendations': ai_sentiment.get('buy_recommendations', []),
                'sell_recommendations': ai_sentiment.get('sell_recommendations', [])
            }
            
            # Cache the result
            self.save_cache(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting daily sentiment: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'market_indices': {},
                'top_sectors': {},
                'sentiment': 'NEUTRAL',
                'confidence': 0,
                'summary': 'Unable to fetch market sentiment',
                'reasoning': 'An error occurred while fetching market data.',
                'key_factors': [],
                'buy_recommendations': [],
                'sell_recommendations': []
            }


# Singleton instance
_market_sentiment_service = None

def get_market_sentiment_service() -> MarketSentimentService:
    """Get or create market sentiment service singleton"""
    global _market_sentiment_service
    if _market_sentiment_service is None:
        _market_sentiment_service = MarketSentimentService()
    return _market_sentiment_service
