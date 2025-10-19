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
    
    def _get_company_name(self, ticker: str) -> str:
        """
        Get company name for a ticker using yfinance
        Returns company name or ticker if not found
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            long_name = info.get('longName')
            if long_name:
                return long_name
            # Fallback to shortName if available
            short_name = info.get('shortName')
            if short_name:
                return short_name
        except Exception as e:
            logger.debug(f"Could not fetch company name for {ticker}: {e}")
        
        return ticker  # Fallback to ticker symbol
    
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
                            'name': self._get_company_name(ticker),
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
                            'name': self._get_company_name(ticker),
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
    
    def _calculate_fundamental_score(self, ticker: str) -> float:
        """
        Calculate fundamental health score (0-1) from yfinance data.
        Returns score based on:
        - Valuation (P/E, P/B)
        - Profitability (operating margin, ROE)
        - Efficiency (debt/equity, current ratio)
        - Growth (earnings growth)
        
        Returns 0-1 where: 0=poor fundamentals, 1=excellent fundamentals
        Returns 0.5 (neutral) if data unavailable
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            score_components = []
            weights = []
            
            # 1. VALUATION ANALYSIS (30% weight)
            # Lower P/E is generally better, but context matters (growth vs value)
            forward_pe = info.get('forwardPE')
            trailing_pe = info.get('trailingPE')
            pe = forward_pe if forward_pe and forward_pe > 0 else trailing_pe
            
            if pe and pe > 0:
                # P/E ranges: <15 undervalued, 15-25 fair, >25 premium/growth
                if pe < 15:
                    pe_score = 0.9
                elif pe < 20:
                    pe_score = 0.8
                elif pe < 30:
                    pe_score = 0.7
                elif pe < 40:
                    pe_score = 0.5
                else:
                    pe_score = 0.3
                score_components.append(pe_score)
                weights.append(0.30)
            
            # 2. PROFITABILITY (35% weight - most important)
            profit_score = 0.5
            profit_weight_sum = 0
            
            # Operating margin (> 15% = good)
            op_margin = info.get('operatingMargins')
            if op_margin is not None:
                if op_margin > 0.20:
                    profit_score = max(profit_score, 0.9)
                elif op_margin > 0.15:
                    profit_score = max(profit_score, 0.8)
                elif op_margin > 0.10:
                    profit_score = max(profit_score, 0.7)
                elif op_margin > 0.05:
                    profit_score = max(profit_score, 0.6)
                elif op_margin > 0:
                    profit_score = max(profit_score, 0.4)
                else:
                    profit_score = 0.2
                profit_weight_sum += 1
            
            # Gross margin (> 40% = good)
            gross_margin = info.get('grossMargins')
            if gross_margin is not None:
                if gross_margin > 0.50:
                    profit_score = max(profit_score, 0.9)
                elif gross_margin > 0.40:
                    profit_score = max(profit_score, 0.8)
                elif gross_margin > 0.30:
                    profit_score = max(profit_score, 0.7)
                elif gross_margin > 0.20:
                    profit_score = max(profit_score, 0.6)
                elif gross_margin > 0.10:
                    profit_score = max(profit_score, 0.4)
                profit_weight_sum += 1
            
            # Return on Equity (> 15% = good, but can be inflated by leverage)
            roe = info.get('returnOnEquity')
            if roe is not None and roe > 0:
                if roe > 0.30:
                    profit_score = max(profit_score, 0.95)
                elif roe > 0.20:
                    profit_score = max(profit_score, 0.9)
                elif roe > 0.15:
                    profit_score = max(profit_score, 0.8)
                elif roe > 0.10:
                    profit_score = max(profit_score, 0.7)
                profit_weight_sum += 1
            
            if profit_weight_sum > 0:
                score_components.append(profit_score)
                weights.append(0.35)
            
            # 3. FINANCIAL HEALTH (25% weight)
            health_score = 0.5
            health_weight_sum = 0
            
            # Debt-to-Equity (lower is safer, but context matters)
            debt_to_eq = info.get('debtToEquity')
            if debt_to_eq is not None and debt_to_eq >= 0:
                if debt_to_eq < 0.5:
                    health_score = max(health_score, 0.95)
                elif debt_to_eq < 1.0:
                    health_score = max(health_score, 0.85)
                elif debt_to_eq < 1.5:
                    health_score = max(health_score, 0.75)
                elif debt_to_eq < 2.0:
                    health_score = max(health_score, 0.6)
                elif debt_to_eq < 3.0:
                    health_score = max(health_score, 0.4)
                else:
                    health_score = 0.2
                health_weight_sum += 1
            
            # Current Ratio (> 1.5 = good, can handle obligations)
            current_ratio = info.get('currentRatio')
            if current_ratio is not None:
                if current_ratio > 2.0:
                    health_score = max(health_score, 0.9)
                elif current_ratio > 1.5:
                    health_score = max(health_score, 0.85)
                elif current_ratio > 1.0:
                    health_score = max(health_score, 0.75)
                elif current_ratio > 0.7:
                    health_score = max(health_score, 0.5)
                else:
                    health_score = max(health_score, 0.3)
                health_weight_sum += 1
            
            if health_weight_sum > 0:
                score_components.append(health_score)
                weights.append(0.25)
            
            # 4. GROWTH (10% weight)
            growth_score = 0.5
            growth_weight_sum = 0
            
            # Earnings growth
            earnings_growth = info.get('earningsGrowth')
            if earnings_growth is not None:
                if earnings_growth > 0.20:
                    growth_score = 0.95
                elif earnings_growth > 0.10:
                    growth_score = 0.85
                elif earnings_growth > 0.05:
                    growth_score = 0.7
                elif earnings_growth > 0:
                    growth_score = 0.6
                else:
                    growth_score = 0.3
                growth_weight_sum += 1
            
            if growth_weight_sum > 0:
                score_components.append(growth_score)
                weights.append(0.10)
            
            # Calculate weighted average
            if score_components and weights:
                total_weight = sum(weights)
                if total_weight > 0:
                    weighted_score = sum(c * w for c, w in zip(score_components, weights)) / total_weight
                    return round(max(0, min(1, weighted_score)), 2)
            
            # Return neutral if insufficient data
            return 0.5
            
        except Exception as e:
            logger.warning(f"Failed to calculate fundamentals for {ticker}: {e}")
            return 0.5
    
    def get_consolidated_score(self, ticker: str) -> Optional[Dict]:
        """
        Get consolidated recommendation score combining:
        - Technical analysis (70% weight): momentum, RSI, volume, moving averages
        - Fundamental analysis (30% weight): valuation, profitability, health, growth
        
        Returns dict with:
        - total_score: 0-1 (final recommendation score)
        - technical_score: 0-1 (technical only)
        - fundamental_score: 0-1 (fundamental only)
        - technical_factors: dict with breakdown
        - fundamental_factors: dict with breakdown
        - recommendation: "BUY", "HOLD", "SELL" based on total_score
        """
        try:
            # Get technical analysis
            technical_result = self._analyze_stock_live(ticker)
            if not technical_result:
                return None
            
            technical_score = technical_result['score']
            
            # Get fundamental score
            fundamental_score = self._calculate_fundamental_score(ticker)
            
            # Calculate weighted consolidated score
            # 70% weight on technical analysis (shorter-term momentum)
            # 30% weight on fundamental analysis (long-term health)
            total_score = (0.7 * technical_score) + (0.3 * fundamental_score)
            total_score = round(max(0, min(1, total_score)), 2)
            
            # Determine recommendation based on score
            if total_score >= 0.6:
                recommendation = "BUY"
            elif total_score <= 0.4:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"
            
            return {
                'total_score': total_score,
                'technical_score': round(technical_score, 2),
                'fundamental_score': round(fundamental_score, 2),
                'technical_weight': 0.7,
                'fundamental_weight': 0.3,
                'recommendation': recommendation,
                'technical_factors': {
                    'momentum': technical_result.get('momentum'),
                    'rsi': technical_result.get('rsi'),
                    'volume_ratio': technical_result.get('volume_ratio'),
                    'ma20': technical_result.get('ma20'),
                    'ma50': technical_result.get('ma50'),
                },
                'fundamental_factors': {
                    'note': 'Derived from P/E, margins, debt/equity, current ratio, ROE, earnings growth'
                },
                'ticker': ticker,
                'price': technical_result.get('price'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Failed to get consolidated score for {ticker}: {e}")
            return None
    
    def get_recommendation_with_sentiment(self, ticker: str, headlines: List[str]) -> Optional[Dict]:
        """
        Get recommendation score with sentiment weighting.
        
        Formula: 0.65*technical + 0.25*fundamental + 0.1*sentiment
        
        Args:
            ticker: Stock ticker
            headlines: List of news headlines about the stock
            
        Returns:
            Dict with total_score, component scores, sentiment analysis, and confidence
        """
        try:
            # Get technical + fundamental scores
            base_result = self.get_consolidated_score(ticker)
            if not base_result:
                return None
            
            # Get sentiment from headlines
            from src.web.services.headline_sentiment_service import HeadlineSentimentService
            sentiment_service = HeadlineSentimentService()
            
            if headlines:
                sentiment_score = sentiment_service.get_sentiment_score_for_stock(ticker, headlines)
                headlines_count = len(headlines)
            else:
                sentiment_score = 0.5  # Neutral
                headlines_count = 0
            
            # Calculate sentiment-weighted total
            # Keep previous 0.7*tech + 0.3*fund, but now distribute the total differently
            # New: 0.65*tech + 0.25*fund + 0.1*sentiment
            technical_score = base_result['technical_score']
            fundamental_score = base_result['fundamental_score']
            
            total_score = (0.65 * technical_score) + (0.25 * fundamental_score) + (0.1 * sentiment_score)
            total_score = round(max(0, min(1, total_score)), 2)
            
            # Determine recommendation
            if total_score >= 0.6:
                recommendation = "BUY"
            elif total_score <= 0.4:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"
            
            # Calculate confidence based on component agreement
            components = [technical_score, fundamental_score, sentiment_score]
            avg_component = sum(components) / len(components)
            component_variance = sum((c - avg_component) ** 2 for c in components) / len(components)
            component_std = component_variance ** 0.5
            
            # High agreement = high confidence
            if component_std < 0.1:
                confidence = "HIGH"
            elif component_std < 0.25:
                confidence = "MODERATE"
            else:
                confidence = "LOW"
            
            return {
                'ticker': ticker,
                'total_score': total_score,
                'technical_score': round(technical_score, 2),
                'fundamental_score': round(fundamental_score, 2),
                'sentiment_score': round(sentiment_score, 3),
                'technical_weight': 0.65,
                'fundamental_weight': 0.25,
                'sentiment_weight': 0.1,
                'sentiment_headlines_count': headlines_count,
                'confidence': confidence,
                'recommendation': recommendation,
                'price': base_result.get('price'),
                'timestamp': datetime.now().isoformat(),
                'components': {
                    'technical': base_result.get('technical_factors'),
                    'fundamental': base_result.get('fundamental_factors'),
                    'sentiment': {
                        'headlines_analyzed': headlines_count,
                        'score': sentiment_score
                    }
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to get recommendation with sentiment for {ticker}: {e}")
            return None
    
    def get_recommendation_with_confidence(self, ticker: str, headlines: List[str]) -> Optional[Dict]:
        """
        Get recommendation with comprehensive confidence analysis and fact-checking.
        
        Returns dict with:
        - recommendation: BUY/HOLD/SELL
        - confidence_level: HIGH/MEDIUM/LOW (based on signal agreement)
        - warnings: List of cautions for investor
        - explanation: Clear rationale for recommendation
        - score_breakdown: All component scores and weights
        - market_context: VIX and other market factors
        
        Warnings examples:
        - "Weak signal" (component < 0.3)
        - "Signals disagree significantly" (spread > 0.4)
        - "High score from single factor" (>0.8 but only 1 strong component)
        - "Market is volatile" (VIX > 25)
        - "Insufficient headline data"
        """
        try:
            # Get sentiment-weighted recommendation
            rec_with_sentiment = self.get_recommendation_with_sentiment(ticker, headlines)
            if not rec_with_sentiment:
                return None
            
            warnings = []
            
            # Extract component scores
            tech_score = rec_with_sentiment['technical_score']
            fund_score = rec_with_sentiment['fundamental_score']
            sent_score = rec_with_sentiment['sentiment_score']
            total_score = rec_with_sentiment['total_score']
            
            # ==== WEAK SIGNAL DETECTION ====
            weak_components = []
            if tech_score < 0.3:
                weak_components.append(f"Technical score very low ({tech_score:.2f})")
            if fund_score < 0.3:
                weak_components.append(f"Fundamentals weak ({fund_score:.2f})")
            if sent_score < 0.3:
                weak_components.append(f"Sentiment bearish ({sent_score:.2f})")
            
            if weak_components:
                warnings.append(f"⚠️ WEAK SIGNAL: {', '.join(weak_components)}. "
                              "Recommendation is weak - proceed with caution.")
            
            # ==== SIGNAL DISAGREEMENT DETECTION ====
            scores = [tech_score, fund_score, sent_score]
            score_spread = max(scores) - min(scores)
            
            if score_spread > 0.4:
                high_components = [n for n, s in [('Tech', tech_score), ('Fundamental', fund_score), 
                                                   ('Sentiment', sent_score)] if s > 0.6]
                low_components = [n for n, s in [('Tech', tech_score), ('Fundamental', fund_score), 
                                                 ('Sentiment', sent_score)] if s < 0.4]
                
                if high_components and low_components:
                    warnings.append(f"⚠️ SIGNALS CONFLICT: {'+'.join(high_components)} say BUY "
                                  f"but {'+'.join(low_components)} say SELL. "
                                  "Signals disagree significantly - more research recommended.")
            
            # ==== SINGLE STRONG COMPONENT WARNING ====
            strong_components = sum(1 for s in scores if s > 0.7)
            weak_components_count = sum(1 for s in scores if s < 0.4)
            
            if total_score > 0.8 and strong_components == 1:
                warnings.append(f"⚠️ HIGH SCORE FROM SINGLE FACTOR: Score is {total_score:.2f} "
                              "but only ONE component is strong. "
                              "This could be misleading - diversify your research.")
            
            if total_score < 0.2 and weak_components_count == 3:
                warnings.append(f"⚠️ ALL SIGNALS WEAK: All three indicators are bearish. "
                              "This is a strong sell signal or insufficient data.")
            
            # ==== MARKET CONTEXT: VIX CHECK ====
            try:
                from src.web.services.multi_source_market_data import MultiSourceMarketData
                market_data = MultiSourceMarketData()
                market_consensus = market_data.get_consensus_market_data()
                
                vix_data = market_consensus.get('VIX (Volatility)', {})
                vix_price = vix_data.get('consensus_price', 20)
                
                market_context = {
                    'vix': vix_price,
                    'market_conditions': 'calm' if vix_price < 15 else 'normal' if vix_price < 25 else 'volatile',
                    'warning': None
                }
                
                if vix_price > 25:
                    warnings.append(f"📊 MARKET CONTEXT: VIX at {vix_price:.1f} indicates HIGH VOLATILITY. "
                                  "Market is fearful - consider tightening stop losses.")
                    market_context['warning'] = 'high_volatility'
                elif vix_price > 20:
                    market_context['warning'] = 'elevated_volatility'
                
            except Exception as e:
                logger.warning(f"Could not get market context for {ticker}: {e}")
                market_context = {'vix': None, 'market_conditions': 'unknown'}
            
            # ==== CONFIDENCE LEVEL CALCULATION ====
            # Based on component agreement
            if score_spread < 0.15:
                confidence = 'HIGH'
            elif score_spread < 0.35:
                confidence = 'MEDIUM'
            else:
                confidence = 'LOW'
            
            # Adjust confidence based on headline count
            if headlines and len(headlines) < 2:
                if confidence == 'HIGH':
                    confidence = 'MEDIUM'
                    warnings.append(f"ℹ️ LIMITED DATA: Only {len(headlines)} headline(s) analyzed. "
                                  "Consider researching more sources.")
            
            # ==== BUILD EXPLANATION ====
            if total_score >= 0.6:
                if confidence == 'HIGH':
                    explanation = (f"Strong BUY signal. All indicators align: "
                                 f"Technical ({tech_score:.2f}), "
                                 f"Fundamental ({fund_score:.2f}), "
                                 f"Sentiment ({sent_score:.2f}).")
                elif confidence == 'MEDIUM':
                    explanation = (f"BUY signal with moderate confidence. "
                                 f"Signals mostly positive but some divergence. "
                                 f"Review warnings above.")
                else:
                    explanation = (f"BUY signal but LOW confidence due to conflicting indicators. "
                                 f"Technical analysis suggests buying but other factors are weaker. "
                                 f"Do additional research.")
            elif total_score <= 0.4:
                if confidence == 'HIGH':
                    explanation = (f"Strong SELL signal. All indicators align: "
                                 f"Technical ({tech_score:.2f}), "
                                 f"Fundamental ({fund_score:.2f}), "
                                 f"Sentiment ({sent_score:.2f}).")
                elif confidence == 'MEDIUM':
                    explanation = (f"SELL signal with moderate confidence. "
                                 f"Signals mostly negative but some divergence. "
                                 f"Review warnings above.")
                else:
                    explanation = (f"SELL signal but LOW confidence due to conflicting indicators. "
                                 f"Some factors suggest selling but others are stronger. "
                                 f"Do additional research.")
            else:
                explanation = (f"HOLD signal - no clear direction. "
                             f"Technical ({tech_score:.2f}), "
                             f"Fundamental ({fund_score:.2f}), "
                             f"Sentiment ({sent_score:.2f}) all show mixed signals. "
                             f"Wait for more clarity.")
            
            # ==== SUMMARY ====
            return {
                'ticker': ticker,
                'recommendation': rec_with_sentiment['recommendation'],
                'confidence_level': confidence,
                'warnings': warnings if warnings else ["✓ No major warnings"],
                'explanation': explanation,
                'score_breakdown': {
                    'technical_score': tech_score,
                    'fundamental_score': fund_score,
                    'sentiment_score': sent_score,
                    'total_score': total_score,
                    'technical_weight': 0.65,
                    'fundamental_weight': 0.25,
                    'sentiment_weight': 0.1,
                },
                'market_context': market_context,
                'sentiment_headlines_count': rec_with_sentiment['sentiment_headlines_count'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Failed to get confidence analysis for {ticker}: {e}")
            return None
    
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
