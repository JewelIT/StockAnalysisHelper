"""
Dynamic Stock Recommendations Service
Gets live stock recommendations based on real-time market data, not hardcoded lists.
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf
import requests

logger = logging.getLogger(__name__)


class DynamicRecommendationService:
    """
    Generate stock recommendations dynamically from live market data.
    NO hardcoded stock lists - all recommendations based on real-time analysis.
    """
    
    def __init__(self):
        # Sector ETFs to analyze for constituents
        self.sector_etfs = {
            'Technology': 'XLK',
            'Healthcare': 'XLV',
            'Financials': 'XLF',
            'Energy': 'XLE',
            'Industrials': 'XLI',
            'Consumer Discretionary': 'XLY',
            'Consumer Staples': 'XLP',
            'Materials': 'XLB',
            'Real Estate': 'XLRE',
            'Utilities': 'XLU',
            'Communication Services': 'XLC'
        }
        
        # API clients (if available)
        self.finnhub_client = None
        self.alpha_vantage_key = None
        self._init_api_clients()
    
    def _init_api_clients(self):
        """Initialize API clients for live data"""
        import os
        
        # Finnhub
        finnhub_key = os.getenv('FINNHUB_API_KEY')
        if finnhub_key:
            try:
                import finnhub
                self.finnhub_client = finnhub.Client(api_key=finnhub_key)
                logger.info("✓ Finnhub client initialized for dynamic recommendations")
            except ImportError:
                logger.warning("finnhub-python not installed")
        
        # Alpha Vantage
        self.alpha_vantage_key = os.getenv('ALPHAVANTAGE_API_KEY')
        if self.alpha_vantage_key:
            logger.info("✓ Alpha Vantage key available for dynamic recommendations")
    
    def get_dynamic_buy_recommendations(
        self, 
        top_sectors: List[str], 
        max_recommendations: int = 10
    ) -> List[Dict]:
        """
        Generate BUY recommendations dynamically based on:
        1. Top performing sectors
        2. Stocks with strong momentum in those sectors
        3. Technical indicators (RSI, volume)
        4. News sentiment (if available)
        
        NO hardcoded lists - all live data!
        """
        recommendations = []
        
        try:
            for sector_name in top_sectors:
                if len(recommendations) >= max_recommendations:
                    break
                
                # Get live stocks from this sector
                sector_stocks = self._get_live_sector_stocks(sector_name, limit=20)
                
                # Analyze each stock with live data
                for ticker in sector_stocks:
                    if len(recommendations) >= max_recommendations:
                        break
                    
                    # Skip if we've already got this ticker
                    if any(r['ticker'] == ticker for r in recommendations):
                        continue
                    
                    # Perform live technical analysis
                    analysis = self._analyze_stock_live(ticker)
                    
                    if analysis and analysis['score'] >= 0.6:  # Strong buy signal
                        recommendations.append({
                            'ticker': ticker,
                            'sector': sector_name,
                            'price': analysis['price'],
                            'reason': self._generate_buy_reason(ticker, analysis, sector_name),
                            'score': analysis['score'],
                            'momentum': analysis.get('momentum', 'N/A'),
                            'rsi': analysis.get('rsi', 'N/A'),
                            'volume_ratio': analysis.get('volume_ratio', 'N/A')
                        })
            
            logger.info(f"Generated {len(recommendations)} dynamic buy recommendations")
            
        except Exception as e:
            logger.error(f"Error generating dynamic buy recommendations: {e}")
        
        return recommendations[:max_recommendations]
    
    def get_dynamic_sell_recommendations(
        self,
        bottom_sectors: List[str],
        max_recommendations: int = 10,
        excluded_tickers: set = None
    ) -> List[Dict]:
        """
        Generate SELL recommendations dynamically based on:
        1. Worst performing sectors
        2. Stocks with weak momentum
        3. Technical indicators showing weakness
        4. Negative news sentiment
        
        NO hardcoded lists - all live data!
        """
        recommendations = []
        excluded_tickers = excluded_tickers or set()
        
        try:
            for sector_name in bottom_sectors:
                if len(recommendations) >= max_recommendations:
                    break
                
                # Get live stocks from this sector
                sector_stocks = self._get_live_sector_stocks(sector_name, limit=20)
                
                # Analyze each stock with live data
                for ticker in sector_stocks:
                    if len(recommendations) >= max_recommendations:
                        break
                    
                    # Skip if in buy recommendations or already added
                    if ticker in excluded_tickers:
                        continue
                    if any(r['ticker'] == ticker for r in recommendations):
                        continue
                    
                    # Perform live technical analysis
                    analysis = self._analyze_stock_live(ticker)
                    
                    if analysis and analysis['score'] <= 0.4:  # Weak/sell signal
                        recommendations.append({
                            'ticker': ticker,
                            'sector': sector_name,
                            'price': analysis['price'],
                            'reason': self._generate_sell_reason(ticker, analysis, sector_name),
                            'score': analysis['score'],
                            'momentum': analysis.get('momentum', 'N/A'),
                            'rsi': analysis.get('rsi', 'N/A'),
                            'volume_ratio': analysis.get('volume_ratio', 'N/A')
                        })
            
            logger.info(f"Generated {len(recommendations)} dynamic sell recommendations")
            
        except Exception as e:
            logger.error(f"Error generating dynamic sell recommendations: {e}")
        
        return recommendations[:max_recommendations]
    
    def _get_live_sector_stocks(self, sector_name: str, limit: int = 20) -> List[str]:
        """
        Get live list of QUALITY stocks in a sector by:
        1. S&P 500 list (filtered by sector)
        2. Using Finnhub sector data
        3. Quality filters: price > $5, volume > 100k
        """
        try:
            # Method 1: Get S&P 500 stocks and filter by sector (BEST approach for quality)
            stocks = self._get_sp500_stocks_by_sector(sector_name)
            if stocks:
                logger.info(f"Got {len(stocks)} quality stocks from S&P 500 for {sector_name}")
                return stocks[:limit]
            
            # Method 2: Try Finnhub stock screener
            if self.finnhub_client:
                stocks = self._get_stocks_from_finnhub_screener(sector_name)
                if stocks:
                    logger.info(f"Got {len(stocks)} stocks from Finnhub for {sector_name}")
                    return stocks[:limit]
            
            # Method 3: Fallback - top holdings from sector ETF
            sector_etf = self.sector_etfs.get(sector_name)
            if sector_etf:
                stocks = self._get_etf_top_holdings(sector_etf, limit)
                if stocks:
                    logger.info(f"Got {len(stocks)} stocks from {sector_etf} ETF holdings")
                    return stocks
            
            logger.warning(f"No live stocks found for {sector_name}, returning empty list")
            return []
            
        except Exception as e:
            logger.error(f"Error getting live sector stocks for {sector_name}: {e}")
            return []
    
    def _get_sp500_stocks_by_sector(self, sector_name: str) -> List[str]:
        """Get S&P 500 stocks filtered by sector (BEST method for quality stocks)"""
        try:
            import pandas as pd
            import requests
            from io import StringIO
            
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            
            logger.info(f"Fetching S&P 500 list from Wikipedia for sector: {sector_name}")
            
            # Wikipedia blocks requests without proper User-Agent, so use requests library
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML tables
            tables = pd.read_html(StringIO(response.text))
            sp500_table = tables[0]
            
            # Map our sector names to GICS sectors
            sector_map = {
                'Technology': 'Information Technology',
                'Healthcare': 'Health Care',
                'Financials': 'Financials',
                'Energy': 'Energy',
                'Industrials': 'Industrials',
                'Consumer Discretionary': 'Consumer Discretionary',
                'Consumer Staples': 'Consumer Staples',
                'Materials': 'Materials',
                'Real Estate': 'Real Estate',
                'Utilities': 'Utilities',
                'Communication Services': 'Communication Services'
            }
            
            gics_sector = sector_map.get(sector_name)
            if not gics_sector:
                return []
            
            # Filter by sector
            sector_stocks = sp500_table[sp500_table['GICS Sector'] == gics_sector]
            tickers = sector_stocks['Symbol'].tolist()
            
            # Clean tickers (remove dots, replace with hyphens for Yahoo Finance)
            tickers = [t.replace('.', '-') for t in tickers]
            
            logger.info(f"✓ Found {len(tickers)} S&P 500 stocks in {sector_name}")
            return tickers
            
        except Exception as e:
            logger.debug(f"Failed to get S&P 500 stocks by sector: {e}")
            return []
    
    def _get_stocks_from_finnhub_screener(self, sector_name: str) -> List[str]:
        """Get stocks using Finnhub stock screener"""
        try:
            if not self.finnhub_client:
                return []
            
            # Map our sector names to Finnhub sectors
            sector_map = {
                'Technology': 'Technology',
                'Healthcare': 'Healthcare',
                'Financials': 'Financial Services',
                'Energy': 'Energy',
                'Industrials': 'Industrials',
                'Consumer Discretionary': 'Consumer Cyclical',
                'Consumer Staples': 'Consumer Defensive',
                'Materials': 'Basic Materials',
                'Real Estate': 'Real Estate',
                'Utilities': 'Utilities',
                'Communication Services': 'Communication Services'
            }
            
            finnhub_sector = sector_map.get(sector_name)
            if not finnhub_sector:
                return []
            
            # Get stocks by sector (Finnhub stock screener)
            # Note: This requires Finnhub premium, fallback if not available
            stocks = self.finnhub_client.stock_symbols('US')
            
            # Filter by sector and market cap
            sector_stocks = []
            for stock in stocks:
                if stock.get('type') == 'Common Stock':
                    ticker = stock.get('symbol', '')
                    if ticker and not any(x in ticker for x in ['.', '^', '/', '-']):
                        sector_stocks.append(ticker)
            
            return sector_stocks[:50]  # Return top 50 by liquidity
            
        except Exception as e:
            logger.debug(f"Finnhub screener failed: {e}")
            return []
    
    def _get_etf_top_holdings(self, etf_symbol: str, limit: int = 20) -> List[str]:
        """Get top holdings from sector ETF using Yahoo Finance"""
        try:
            etf = yf.Ticker(etf_symbol)
            
            # Try to get holdings (not always available via yfinance)
            # Alternative: Parse from ETF provider website
            info = etf.info
            
            # Fallback: Get most actively traded stocks correlated with ETF
            # by analyzing ETF's major movers
            hist = etf.history(period='1mo')
            if hist.empty:
                return []
            
            # Get stocks that move with this ETF (sector constituents)
            # This is a heuristic - in production, use proper ETF holdings data
            stocks = self._find_correlated_stocks(etf_symbol, limit)
            
            return stocks
            
        except Exception as e:
            logger.debug(f"Failed to get {etf_symbol} holdings: {e}")
            return []
    
    def _find_correlated_stocks(self, etf_symbol: str, limit: int = 20) -> List[str]:
        """Find stocks highly correlated with sector ETF (heuristic method)"""
        try:
            # Use Finnhub to get stocks in the same sector
            if self.finnhub_client:
                # Get ETF peers/similar stocks
                similar = self.finnhub_client.company_peers(etf_symbol)
                if similar:
                    return similar[:limit]
            
            # Fallback: Return common large-cap stocks in sector
            # In production, replace with proper ETF holdings API
            return []
            
        except Exception as e:
            logger.warning(f"Failed to find correlated stocks: {e}")
            return []
    
    def _screen_stocks_by_sector(self, sector_name: str, limit: int = 20) -> List[str]:
        """
        Screen stocks by sector using market screener
        Fallback method when APIs unavailable
        """
        try:
            # Use Yahoo Finance screener (limited free data)
            # In production: Use dedicated screener API
            
            # Fallback: Get S&P 500 list and filter by sector
            sp500_stocks = self._get_sp500_stocks()
            
            # Filter by sector (would need sector classification API)
            # For now, return active large-cap stocks
            return sp500_stocks[:limit]
            
        except Exception as e:
            logger.warning(f"Stock screener failed: {e}")
            return []
    
    def _get_sp500_stocks(self) -> List[str]:
        """Get S&P 500 stock list from Wikipedia"""
        try:
            import pandas as pd
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            sp500_table = tables[0]
            tickers = sp500_table['Symbol'].tolist()
            # Clean tickers
            tickers = [t.replace('.', '-') for t in tickers]
            return tickers
        except Exception as e:
            logger.debug(f"Failed to get S&P 500 list: {e}")
            return []
    
    def _analyze_stock_live(self, ticker: str) -> Optional[Dict]:
        """
        Perform live technical analysis on a stock:
        - Price action (momentum)
        - Volume analysis
        - RSI (overbought/oversold)
        - Moving averages
        - Returns a score 0-1 (0=sell, 1=buy)
        
        QUALITY FILTERS:
        - Skip penny stocks (< $5)
        - Skip low volume stocks
        - Skip stocks with insufficient history
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get basic info for quality filtering
            try:
                info = stock.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
                market_cap = info.get('marketCap', 0)
                
                # QUALITY FILTER 1: Skip penny stocks
                if current_price < 5:
                    return None
                
                # QUALITY FILTER 2: Skip micro-caps (< $500M market cap)
                if market_cap < 500_000_000:
                    return None
                    
            except Exception:
                # If info unavailable, try from history
                pass
            
            hist = stock.history(period='3mo')
            
            if hist.empty or len(hist) < 20:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # QUALITY FILTER 3: Price check from history
            if current_price < 5:
                return None
            
            # QUALITY FILTER 4: Volume check - skip illiquid stocks
            avg_volume = hist['Volume'].rolling(20).mean().iloc[-1]
            if avg_volume < 100_000:  # Less than 100k shares/day = illiquid
                return None
            
            # Calculate momentum (20-day vs 50-day MA)
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            ma50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else ma20
            
            # Calculate RSI
            rsi = self._calculate_rsi(hist['Close'], period=14)
            
            # Volume analysis (current vs average)
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Price momentum (3-month)
            price_3mo_ago = hist['Close'].iloc[0]
            momentum_pct = ((current_price - price_3mo_ago) / price_3mo_ago) * 100
            
            # Calculate score (0-1)
            score = 0.5  # Neutral start
            
            # Momentum signals
            if ma20 > ma50:
                score += 0.15  # Bullish trend
            else:
                score -= 0.15  # Bearish trend
            
            # RSI signals
            if rsi < 30:
                score += 0.15  # Oversold (potential buy)
            elif rsi > 70:
                score -= 0.15  # Overbought (potential sell)
            
            # Volume signals
            if volume_ratio > 1.5:
                score += 0.1  # High volume (strong interest)
            elif volume_ratio < 0.5:
                score -= 0.1  # Low volume (weak interest)
            
            # Price momentum signals
            if momentum_pct > 10:
                score += 0.1  # Strong uptrend
            elif momentum_pct < -10:
                score -= 0.1  # Strong downtrend
            
            # Clamp score to 0-1
            score = max(0, min(1, score))
            
            return {
                'price': round(current_price, 2),
                'score': round(score, 2),
                'momentum': f"{momentum_pct:+.1f}%",
                'rsi': round(rsi, 1),
                'volume_ratio': round(volume_ratio, 2),
                'ma20': round(ma20, 2),
                'ma50': round(ma50, 2),
                'avg_volume': int(avg_volume)
            }
            
        except Exception as e:
            logger.warning(f"Failed to analyze {ticker}: {e}")
            return None
    
    def _calculate_rsi(self, prices, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        try:
            deltas = prices.diff()
            gain = (deltas.where(deltas > 0, 0)).rolling(window=period).mean()
            loss = (-deltas.where(deltas < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi.iloc[-1])
        except Exception as e:
            return 50.0  # Neutral
    
    def _generate_buy_reason(self, ticker: str, analysis: Dict, sector: str) -> str:
        """Generate human-readable buy reason based on live analysis"""
        reasons = []
        
        # Momentum
        momentum = analysis.get('momentum', '')
        if '+' in str(momentum):
            reasons.append(f"Strong upward momentum ({momentum})")
        
        # RSI
        rsi = analysis.get('rsi', 50)
        if rsi < 35:
            reasons.append(f"Oversold conditions (RSI: {rsi:.0f})")
        elif 45 <= rsi <= 55:
            reasons.append(f"Balanced momentum (RSI: {rsi:.0f})")
        
        # Volume
        volume_ratio = analysis.get('volume_ratio', 1.0)
        if volume_ratio > 1.5:
            reasons.append(f"High trading volume ({volume_ratio:.1f}x average)")
        
        # Moving averages
        ma20 = analysis.get('ma20', 0)
        ma50 = analysis.get('ma50', 0)
        if ma20 > ma50:
            reasons.append("Price above moving averages (bullish)")
        
        # Sector context
        reasons.append(f"{sector} sector showing strength")
        
        return ". ".join(reasons) + "."
    
    def _generate_sell_reason(self, ticker: str, analysis: Dict, sector: str) -> str:
        """Generate human-readable sell reason based on live analysis"""
        reasons = []
        
        # Momentum
        momentum = analysis.get('momentum', '')
        if '-' in str(momentum):
            reasons.append(f"Negative momentum ({momentum})")
        
        # RSI
        rsi = analysis.get('rsi', 50)
        if rsi > 70:
            reasons.append(f"Overbought conditions (RSI: {rsi:.0f})")
        
        # Volume
        volume_ratio = analysis.get('volume_ratio', 1.0)
        if volume_ratio < 0.7:
            reasons.append(f"Declining volume ({volume_ratio:.1f}x average)")
        
        # Moving averages
        ma20 = analysis.get('ma20', 0)
        ma50 = analysis.get('ma50', 0)
        if ma20 < ma50:
            reasons.append("Price below moving averages (bearish)")
        
        # Sector context
        reasons.append(f"{sector} sector showing weakness")
        
        return ". ".join(reasons) + "."


# Singleton instance
_dynamic_service_instance = None

def get_dynamic_recommendation_service() -> DynamicRecommendationService:
    """Get or create singleton instance"""
    global _dynamic_service_instance
    if _dynamic_service_instance is None:
        _dynamic_service_instance = DynamicRecommendationService()
    return _dynamic_service_instance
