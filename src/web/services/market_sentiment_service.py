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

# Import multi-source service
try:
    from .multi_source_market_data import get_multi_source_service
    MULTI_SOURCE_AVAILABLE = True
    logger.info("✓ Multi-source market data service available")
except ImportError as e:
    MULTI_SOURCE_AVAILABLE = False
    logger.warning(f"Multi-source service not available, using Yahoo Finance only: {e}")

# Import dynamic recommendations service
try:
    from .dynamic_recommendations import get_dynamic_recommendation_service
    DYNAMIC_RECS_AVAILABLE = True
    logger.info("✓ Dynamic recommendations service available")
except ImportError as e:
    DYNAMIC_RECS_AVAILABLE = False
    logger.warning(f"Dynamic recommendations not available: {e}")

class MarketSentimentService:
    """Service for generating market sentiment and recommendations"""
    
    def __init__(self):
        self.cache_file = 'cache/market_sentiment_cache.json'
        self.cache_duration_hours = 0.25  # Refresh every 15 minutes (markets are volatile!)
        
        # Exchange rates (fallback values, should fetch live)
        self.exchange_rates = {
            'USD': 1.0,
            'EUR': 0.92,
            'GBP': 0.79
        }
        
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
        """Fetch current data for major market indices using MULTI-SOURCE or intraday data"""
        try:
            # Try multi-source consensus first
            if MULTI_SOURCE_AVAILABLE:
                try:
                    multi_source = get_multi_source_service()
                    consensus_data = multi_source.get_consensus_market_data()
                    
                    if consensus_data:
                        logger.info(f"✓ Using multi-source consensus from {len(consensus_data)} indices")
                        
                        # Convert to our format
                        result = {}
                        for index_name, consensus in consensus_data.items():
                            result[index_name] = {
                                'symbol': consensus.get('index_name', index_name),
                                'current': consensus['consensus_price'],
                                'change_pct': consensus['consensus_change_pct'],
                                'trend': consensus['trend'],
                                'sources': consensus['sources_used'],
                                'confidence': consensus['confidence'],
                                'multi_source': True
                            }
                            
                            # Log discrepancies
                            if consensus.get('has_discrepancy'):
                                logger.warning(
                                    f"⚠️ {index_name}: Sources disagree by {consensus['spread']:.2f}% "
                                    f"(Severity: {consensus['severity']})"
                                )
                        
                        return result
                except Exception as e:
                    logger.warning(f"Multi-source fetch failed, falling back to Yahoo: {e}")
            
            # Fallback: Use Yahoo Finance intraday data
            logger.info("Using Yahoo Finance fallback")
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
                    # USE INTRADAY DATA instead of 5-day history
                    # Get 1 day of 5-minute bars to capture today's moves
                    hist = ticker.history(period='1d', interval='5m')
                    
                    # Fallback to daily data if intraday fails (market closed/pre-market)
                    if hist.empty or len(hist) < 2:
                        hist = ticker.history(period='5d')
                    
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        # Compare to TODAY'S OPEN, not yesterday's close
                        day_open = hist['Open'].iloc[0] if len(hist) > 0 else current
                        change_pct = ((current - day_open) / day_open) * 100
                        
                        data[name] = {
                            'symbol': symbol,
                            'current': round(current, 2),
                            'change_pct': round(change_pct, 2),
                            'trend': 'up' if change_pct > 0 else 'down',
                            'intraday': len(hist) > 10,  # Flag if we got intraday data
                            'multi_source': False
                        }
                except Exception as e:
                    logger.warning(f"Failed to fetch {name}: {e}")
                    continue
                    
            return data
        except Exception as e:
            logger.error(f"Error fetching market indices: {e}")
            return {}
    
    def get_fear_greed_index(self) -> Optional[Dict]:
        """
        Fetch CNN Fear & Greed Index (0-100 scale)
        0-25 = Extreme Fear → Force BEARISH
        25-45 = Fear → BEARISH/NEUTRAL
        45-55 = Neutral
        55-75 = Greed → BULLISH
        75-100 = Extreme Greed → Caution
        """
        try:
            import requests
            # Try CNN's Fear & Greed Index API
            url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                # Extract current fear & greed value
                if 'fear_and_greed' in data:
                    current_value = data['fear_and_greed'].get('score', None)
                    rating = data['fear_and_greed'].get('rating', 'Unknown')
                    
                    if current_value is not None:
                        logger.info(f"Fear & Greed Index: {current_value} ({rating})")
                        return {
                            'value': current_value,
                            'rating': rating,
                            'timestamp': datetime.now().isoformat()
                        }
        except Exception as e:
            logger.warning(f"Could not fetch Fear & Greed Index: {e}")
        
        return None
    
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
            
            # NEW: Check Fear & Greed Index FIRST (highest priority)
            fear_greed = self.get_fear_greed_index()
            fear_greed_override = None
            fg_reason = None
            
            if fear_greed and 'value' in fear_greed:
                fg_value = fear_greed['value']
                fg_rating = fear_greed['rating']
                
                if fg_value < 25:
                    # Extreme Fear - force BEARISH
                    fear_greed_override = "BEARISH"
                    fg_reason = f"CNN Fear & Greed Index at {fg_value} (Extreme Fear) - market sentiment very negative. High risk of further declines."
                elif fg_value < 45:
                    # Fear - force BEARISH (not just lean, FORCE it)
                    fear_greed_override = "BEARISH"
                    fg_reason = f"CNN Fear & Greed Index at {fg_value} (Fear) - investor sentiment cautious. Markets unstable, defensive positioning recommended."
                elif fg_value < 55:
                    # Neutral zone - don't override but note the uncertainty
                    fg_reason = f"CNN Fear & Greed Index at {fg_value} (Neutral) - mixed signals in market"
                elif fg_value > 75:
                    # Extreme Greed - force NEUTRAL (never BULLISH in greed zone)
                    fear_greed_override = "NEUTRAL"
                    fg_reason = f"CNN Fear & Greed Index at {fg_value} (Extreme Greed) - market potentially overheated. Risk of correction."
                elif fg_value > 65:
                    # Greed - cap at NEUTRAL max
                    fear_greed_override = "NEUTRAL"
                    fg_reason = f"CNN Fear & Greed Index at {fg_value} (Greed) - market exuberance may be excessive. Caution advised."
                
                logger.info(f"Fear & Greed: {fg_value} ({fg_rating}) - Override: {fear_greed_override}")
            
            # Check VIX (Fear Index) second - it also overrides other signals
            vix_current = market_data.get('VIX (Volatility)', {}).get('current', 0)
            vix_change = market_data.get('VIX (Volatility)', {}).get('change_pct', 0)
            vix_override = None
            vix_reason = None
            
            # MORE SENSITIVE VIX THRESHOLDS - VIX >20 is NOT normal, it's elevated fear
            if vix_current > 30:
                # High fear - force BEARISH
                vix_override = "BEARISH"
                vix_reason = f"High market fear (VIX {vix_current:.1f}) indicates significant risk and uncertainty"
            elif vix_current > 25:
                # Elevated fear - force BEARISH unless Fear & Greed already handled it
                vix_override = "BEARISH"
                vix_reason = f"Elevated market fear (VIX {vix_current:.1f}) signals heightened risk environment"
            elif vix_current > 20:
                # Moderate fear - cap at NEUTRAL (no BULLISH allowed)
                vix_override = "NEUTRAL"
                vix_reason = f"Volatility elevated (VIX {vix_current:.1f}) above normal, caution warranted"
            elif vix_change > 15:
                # VIX spiking rapidly (15%+ increase) - fear is increasing
                vix_override = "BEARISH"
                vix_reason = f"VIX spiking {vix_change:.1f}% - fear escalating, volatility rising"
            
            # Determine final sentiment with priority: Fear & Greed > VIX > Index moves
            # CRITICAL: Be pragmatic, not overly optimistic. When fear is present, acknowledge it.
            risk_warnings = []
            
            if fear_greed_override:
                # Fear & Greed Index has highest priority
                sentiment = fear_greed_override
                confidence = min(75 + abs(int((fear_greed['value'] - 50) / 2)), 95)
                summary = fg_reason
                
                # Add explicit risk warning when Fear & Greed shows fear
                if fear_greed['value'] < 45:
                    risk_warnings.append(f"Market Fear Index at {fear_greed['value']} - expect volatility and potential continued declines")
                elif fear_greed['value'] > 65:
                    risk_warnings.append(f"Market Greed Index at {fear_greed['value']} - risk of correction when sentiment is this bullish")
                    
            elif vix_override:
                # VIX second priority
                sentiment = vix_override
                confidence = min(70 + int(vix_current - 20) * 2, 90)
                summary = vix_reason
                risk_warnings.append(f"Elevated volatility (VIX {vix_current:.1f}) suggests uncertain market conditions")
                
            elif avg_change > 0.5 and market_trend_pct >= 75:
                # HIGHER threshold for BULLISH (was 0.3 and 65%, now 0.5 and 75%)
                sentiment = "BULLISH"
                confidence = min(65 + int(avg_change * 8), 90)  # Lower max confidence
                summary = "Markets showing positive momentum across major indices"
                # Even in bullish, acknowledge any fear signals
                if vix_current > 18:
                    risk_warnings.append(f"VIX at {vix_current:.1f} suggests some underlying caution despite gains")
                    
            elif avg_change < -0.3 and market_trend_pct <= 35:
                sentiment = "BEARISH"
                confidence = min(70 + int(abs(avg_change) * 8), 95)
                summary = "Markets experiencing downward pressure with widespread declines"
                risk_warnings.append("Broad market weakness - defensive positioning recommended")
                
            else:
                # Default to NEUTRAL with lower confidence - be conservative
                sentiment = "NEUTRAL"
                confidence = 50 + int(abs(avg_change) * 5)  # Lower confidence calculation
                summary = "Markets showing mixed signals with no clear directional trend"
                if vix_current > 18:
                    risk_warnings.append(f"VIX at {vix_current:.1f} above normal baseline, suggesting caution")
            
            # ALWAYS add risk context when fear signals present
            if fg_reason and fear_greed_override in ["BEARISH", "NEUTRAL"]:
                summary = f"{summary}. {fg_reason}"
            elif vix_reason and vix_override in ["BEARISH", "NEUTRAL"]:
                summary = f"{summary}. {vix_reason}"
            
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
            
            # Extract key factors - include risk warnings prominently
            key_factors = []
            
            # PRIORITIZE risk warnings at the top
            if risk_warnings:
                key_factors.extend(risk_warnings)
            
            # Add Fear & Greed context
            if fear_greed and 'value' in fear_greed:
                key_factors.append(f"CNN Fear & Greed Index: {fear_greed['value']}/100 ({fear_greed['rating']})")
            
            # Add VIX context
            if 'VIX (Volatility)' in market_data:
                vix_data = market_data['VIX (Volatility)']
                if vix_data['current'] > 25:
                    key_factors.append(f"High volatility - VIX at {vix_data['current']:.1f} (elevated fear)")
                elif vix_data['current'] > 20:
                    key_factors.append(f"Elevated volatility - VIX at {vix_data['current']:.1f} (above normal)")
                elif vix_data['current'] < 15:
                    key_factors.append(f"Low volatility - VIX at {vix_data['current']:.1f} (market calm)")
            
            # Add sector performance
            if sector_data:
                top_sector = list(sector_data.keys())[0]
                key_factors.append(f"{top_sector} sector leading market")
                
                worst_performing = list(sector_data.items())[-1]
                key_factors.append(f"{worst_performing[0]} sector underperforming")
            
            # Generate recommendations based on top sectors
            # CRITICAL FIX: Generate buy first, then pass excluded tickers to sell generation
            buy_recommendations = self._generate_buy_recommendations(sector_data, sentiment)
            buy_tickers = {r['ticker'] for r in buy_recommendations}
            
            # Pass excluded tickers to avoid duplicates
            sell_recommendations = self._generate_sell_recommendations(
                sector_data, 
                sentiment, 
                excluded_tickers=buy_tickers
            )
            
            # Double-check for any remaining duplicates (shouldn't happen now)
            sell_tickers = {r['ticker'] for r in sell_recommendations}
            duplicates = buy_tickers & sell_tickers
            
            if duplicates:
                logger.error(f"CRITICAL: Still found duplicates after exclusion: {duplicates}")
                # Remove duplicates from sell list as fallback
                sell_recommendations = [r for r in sell_recommendations if r['ticker'] not in duplicates]
            
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
        """Get current stock price in USD"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d')
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
        except Exception as e:
            logger.warning(f"Failed to get price for {ticker}: {e}")
        return None
    
    def _convert_price(self, price_usd: float, target_currency: str) -> float:
        """Convert price from USD to target currency"""
        if target_currency == 'USD' or target_currency == 'NATIVE':
            return price_usd
        
        rate = self.exchange_rates.get(target_currency, 1.0)
        return price_usd * rate
    
    def _fetch_live_exchange_rates(self) -> Dict[str, float]:
        """Fetch live exchange rates (optional enhancement)"""
        try:
            # Could implement live fetching from API here
            # For now, return fallback rates
            return self.exchange_rates
        except Exception as e:
            logger.warning(f"Failed to fetch live exchange rates: {e}")
            return self.exchange_rates
    
    def _get_stock_specific_buy_reason(self, ticker: str, sector_name: str, sector_change: float, sentiment: str) -> str:
        """Generate stock-specific buy recommendation reason"""
        stock_characteristics = {
            # Technology
            'AAPL': 'Strong brand loyalty and ecosystem, consistent revenue growth from services',
            'MSFT': 'Leading cloud computing position with Azure, enterprise software dominance',
            'GOOGL': 'Dominant search market share, diversified revenue streams including cloud',
            'NVDA': 'AI chip market leader, strong data center demand',
            'META': 'Social media dominance, growing AI investments and advertising platform',
            'TSLA': 'Electric vehicle market leader, autonomous driving technology advancement',
            'AMD': 'Competitive CPU/GPU offerings, gaining server market share',
            'INTC': 'Manufacturing investments, AI chip development potential',
            'CRM': 'Leading CRM platform, strong enterprise customer retention',
            'ORCL': 'Database market leader, growing cloud infrastructure business',
            
            # Healthcare
            'JNJ': 'Diversified healthcare portfolio, stable dividend history',
            'UNH': 'Healthcare services leader, consistent earnings growth',
            'PFE': 'Strong pharmaceutical pipeline, dividend reliability',
            'ABBV': 'Immunology drugs market leader, attractive dividend yield',
            'TMO': 'Life sciences equipment leader, essential research tools provider',
            'LLY': 'Diabetes and obesity drug success, strong pipeline',
            'MRK': 'Cancer drug portfolio strength, solid R&D investments',
            'ABT': 'Medical devices leader, diverse product portfolio',
            'DHR': 'Healthcare technology innovator, consistent acquisition strategy',
            'BMY': 'Oncology focus, attractive valuation',
            
            # Financials
            'JPM': 'Strongest balance sheet among major banks, diversified revenue',
            'BAC': 'Large deposit base, improving net interest margins',
            'WFC': 'Branch network advantage, cost reduction progress',
            'GS': 'Investment banking leader, strong trading operations',
            'MS': 'Wealth management growth, diversified revenue streams',
            'C': 'Global presence, turnaround potential',
            'BLK': 'Asset management leader, ETF market dominance',
            'SCHW': 'Retail trading platform strength, banking services growth',
            'V': 'Payment processing leader, global transaction growth',
            'MA': 'Strong network effects, digital payment trend beneficiary',
            
            # Consumer Discretionary
            'AMZN': 'E-commerce dominance, AWS cloud leadership',
            'HD': 'Home improvement leader, housing market beneficiary',
            'MCD': 'Global brand strength, consistent same-store sales growth',
            'NKE': 'Athletic wear brand leader, direct-to-consumer strategy',
            'SBUX': 'Coffee chain dominance, international expansion',
            'TGT': 'Retail innovation, omnichannel execution',
            'LOW': 'Home improvement growth, professional customer focus',
            'TJX': 'Off-price retail leader, inventory management excellence',
            'CMG': 'Fast-casual dining success, digital ordering growth',
            'BKNG': 'Travel booking platform leader, post-pandemic recovery',
            
            # Consumer Staples
            'WMT': 'Retail giant with strong e-commerce growth, recession-resistant',
            'PG': 'Consumer products leader, premium brand portfolio',
            'KO': 'Beverage industry icon, global distribution network',
            'PEP': 'Diversified food and beverage portfolio, snacks division strength',
            'COST': 'Membership model strength, customer loyalty',
            'MDLZ': 'Global snacks portfolio, emerging markets growth',
            'PM': 'International tobacco presence, smoke-free product transition',
            'CL': 'Oral care leadership, emerging markets presence',
            'KMB': 'Essential products portfolio, stable demand',
            'GIS': 'Cereal and snacks brands, e-commerce adaptation',
            
            # Energy
            'XOM': 'Integrated energy major, strong balance sheet',
            'CVX': 'Energy diversification, reliable dividend',
            'COP': 'Low-cost production, strong cash flow',
            'SLB': 'Oilfield services leader, technology advantage',
            'EOG': 'Shale production efficiency, strong returns',
            'MPC': 'Refining capacity leader, downstream integration',
            'PSX': 'Refining and midstream assets, stable cash flow',
            'VLO': 'Refining operations strength, renewable diesel growth',
            'OXY': 'Permian Basin focus, debt reduction progress',
            'PXD': 'Permian pure-play, capital discipline',
            
            # Industrials
            'BA': 'Aviation duopoly, commercial aircraft backlog',
            'CAT': 'Construction equipment leader, infrastructure spending beneficiary',
            'UNP': 'Railroad network advantage, pricing power',
            'HON': 'Diversified technology and manufacturing, aerospace exposure',
            'UPS': 'Logistics leader, e-commerce delivery growth',
            'LMT': 'Defense contractor leader, consistent government contracts',
            'RTX': 'Aerospace and defense diversification, commercial recovery',
            'DE': 'Agricultural equipment dominance, precision farming technology',
            'MMM': 'Diversified industrial conglomerate, innovation culture',
            'GE': 'Industrial transformation, aviation recovery',
            
            # Materials
            'LIN': 'Industrial gases leader, essential manufacturing inputs',
            'APD': 'Gases and chemicals diversification, hydrogen potential',
            'ECL': 'Cleaning and sanitation leader, recurring revenue',
            'SHW': 'Paint and coatings dominance, retail and contractor presence',
            'NEM': 'Gold mining leader, inflation hedge',
            'FCX': 'Copper production scale, EV demand beneficiary',
            'NUE': 'Steel minimill efficiency, construction demand',
            'DOW': 'Chemicals and materials diversification, essential products',
            'DD': 'Specialty chemicals focus, electronics materials',
            'PPG': 'Coatings technology leader, automotive and industrial exposure',
            
            # Real Estate
            'AMT': 'Cell tower REIT leader, 5G infrastructure beneficiary',
            'PLD': 'Logistics real estate focus, e-commerce tailwind',
            'CCI': 'Telecom infrastructure provider, recurring revenues',
            'EQIX': 'Data center REIT leader, cloud infrastructure growth',
            'PSA': 'Self-storage market leader, stable occupancy',
            'WELL': 'Healthcare real estate focus, aging demographics',
            'DLR': 'Data center presence, digital transformation trend',
            'O': 'Monthly dividend REIT, retail diversification',
            'SPG': 'Premium mall operator, retail evolution',
            'AVB': 'Apartment REIT, urban housing demand',
            
            # Utilities
            'NEE': 'Renewable energy leader, regulated utility base',
            'DUK': 'Regulated utility operations, clean energy transition',
            'SO': 'Southeast utilities presence, customer growth',
            'D': 'Mid-Atlantic service area, infrastructure investments',
            'AEP': 'Transmission network strength, renewable investments',
            'EXC': 'Nuclear fleet operator, carbon-free generation',
            'SRE': 'California utilities presence, renewable focus',
            'XEL': 'Upper Midwest operations, clean energy leadership',
            'WEC': 'Midwest utilities, customer satisfaction ratings',
            'ES': 'Nuclear operations, clean energy transition',
            
            # Communication Services
            'GOOGL': 'Digital advertising duopoly, YouTube dominance',
            'META': 'Social media platforms leadership, engagement metrics',
            'NFLX': 'Streaming entertainment leader, content library',
            'DIS': 'Entertainment empire, streaming growth',
            'CMCSA': 'Cable and broadband provider, content ownership',
            'T': 'Telecom infrastructure, 5G deployment',
            'VZ': 'Network quality reputation, enterprise services',
            'TMUS': 'Un-carrier strategy, 5G network leadership',
            'CHTR': 'Cable provider, broadband expansion',
            'EA': 'Gaming franchises strength, live services revenue'
        }
        
        base_reason = stock_characteristics.get(ticker, f'Strong presence in {sector_name} sector')
        
        # Add context based on sector performance and market sentiment
        if sector_change > 1.0:
            context = f' Sector leading with {sector_change:+.1f}% performance'
        elif sentiment == 'BULLISH':
            context = f' Bullish market conditions favor {sector_name} exposure'
        else:
            context = f' Sector showing {sector_change:+.1f}% momentum'
            
        return f'{base_reason}.{context}'
    
    def _generate_buy_recommendations(self, sector_data: Dict, sentiment: str, max_recommendations: int = 10) -> List[Dict]:
        """
        Generate buy recommendations DYNAMICALLY from live market data.
        NO hardcoded stocks - uses real-time analysis!
        """
        try:
            # Try dynamic recommendations first (NEW - LIVE DATA!)
            if DYNAMIC_RECS_AVAILABLE:
                dynamic_service = get_dynamic_recommendation_service()
                top_sectors = [name for name, _ in list(sector_data.items())[:5]]
                
                recommendations = dynamic_service.get_dynamic_buy_recommendations(
                    top_sectors=top_sectors,
                    max_recommendations=max_recommendations
                )
                
                if recommendations:
                    logger.info(f"✓ Using {len(recommendations)} DYNAMIC buy recommendations (live data!)")
                    return recommendations
            
            # Fallback: Hardcoded approach (DEPRECATED - only if dynamic fails)
            logger.warning("⚠️ Falling back to hardcoded stocks (dynamic service unavailable)")
            return self._generate_buy_recommendations_fallback(sector_data, sentiment, max_recommendations)
            
        except Exception as e:
            logger.error(f"Error generating buy recommendations: {e}")
            return self._generate_buy_recommendations_fallback(sector_data, sentiment, max_recommendations)
    
    def _generate_buy_recommendations_fallback(self, sector_data: Dict, sentiment: str, max_recommendations: int = 10) -> List[Dict]:
        """FALLBACK: Generate buy recommendations from hardcoded lists (DEPRECATED)"""
        recommendations = []
        
        try:
            # Get top performing sectors
            top_sectors = list(sector_data.items())[:5]  # Get top 5 sectors
            
            # Round-robin approach: take 1 stock from each sector to diversify
            sector_stock_iterators = {}
            for sector_name, sector_info in top_sectors:
                if sector_name in self.sector_stocks:
                    sector_stock_iterators[sector_name] = {
                        'stocks': iter(self.sector_stocks[sector_name]),
                        'info': sector_info
                    }
            
            # Keep cycling through sectors until we have enough recommendations
            while len(recommendations) < max_recommendations and sector_stock_iterators:
                sectors_to_remove = []
                
                for sector_name, data in list(sector_stock_iterators.items()):
                    if len(recommendations) >= max_recommendations:
                        break
                    
                    try:
                        ticker = next(data['stocks'])
                        price = self._get_stock_price(ticker)
                        
                        if price is not None:
                            # Generate stock-specific reason
                            reason = self._get_stock_specific_buy_reason(
                                ticker, 
                                sector_name, 
                                data['info']['change_pct'],
                                sentiment
                            )
                            
                            recommendations.append({
                                "ticker": ticker,
                                "reason": reason,
                                "sector": sector_name,
                                "price": round(price, 2)
                            })
                    except StopIteration:
                        # No more stocks in this sector
                        sectors_to_remove.append(sector_name)
                
                # Remove exhausted sectors
                for sector_name in sectors_to_remove:
                    del sector_stock_iterators[sector_name]
            
        except Exception as e:
            logger.warning(f"Error in fallback buy recommendations: {e}")
        
        return recommendations[:max_recommendations]
    
    def _get_stock_specific_sell_reason(self, ticker: str, sector_name: str, sector_change: float, sentiment: str) -> str:
        """Generate stock-specific sell/avoid recommendation reason"""
        stock_risks = {
            # Technology
            'AAPL': 'High valuation relative to growth rates, regulatory scrutiny risks',
            'MSFT': 'Premium valuation, cybersecurity concerns',
            'GOOGL': 'Antitrust challenges, advertising market uncertainty',
            'NVDA': 'Extreme valuation, AI hype cycle concerns',
            'META': 'Privacy regulations impact, user engagement challenges',
            'TSLA': 'Valuation disconnect from fundamentals, competition intensifying',
            'AMD': 'Competitive pressures, cyclical semiconductor exposure',
            'INTC': 'Market share losses, manufacturing delays',
            'CRM': 'Slowing growth, high valuation multiples',
            'ORCL': 'Cloud market share challenges, licensing model pressures',
            
            # Healthcare
            'JNJ': 'Litigation risks, patent expirations',
            'UNH': 'Regulatory scrutiny, political healthcare policy risks',
            'PFE': 'Post-COVID revenue normalization, pipeline uncertainties',
            'ABBV': 'Key drug patent expiration risks, pricing pressures',
            'TMO': 'High acquisition debt levels, integration risks',
            'LLY': 'Valuation stretched, drug pricing scrutiny',
            'MRK': 'Patent cliff concerns, R&D execution risks',
            'ABT': 'Medical device competition, reimbursement pressures',
            'DHR': 'Rich valuation, acquisition integration challenges',
            'BMY': 'Pipeline development delays, competitive threats',
            
            # Financials
            'JPM': 'Interest rate sensitivity, credit cycle concerns',
            'BAC': 'Economic slowdown exposure, credit quality risks',
            'WFC': 'Regulatory constraints, operational risk legacy',
            'GS': 'Trading volatility, deal flow uncertainty',
            'MS': 'Market downturn vulnerability, wealth management fee pressures',
            'C': 'Turnaround execution risks, emerging market exposures',
            'BLK': 'Fee compression, passive investing shift',
            'SCHW': 'Interest rate dependency, competitive pressures',
            'V': 'Regulatory pressures on interchange fees, competitive threats',
            'MA': 'Similar payment network challenges, fintech disruption',
            
            # Consumer Discretionary
            'AMZN': 'Antitrust concerns, margin compression from investments',
            'HD': 'Housing market slowdown sensitivity, high valuation',
            'MCD': 'Labor cost inflation, franchise operational issues',
            'NKE': 'Inventory management challenges, China market weakness',
            'SBUX': 'Labor union pressures, competition intensifying',
            'TGT': 'Retail margin pressures, e-commerce competition',
            'LOW': 'Housing market dependency, DIY demand normalization',
            'TJX': 'Inventory sourcing challenges, retail traffic concerns',
            'CMG': 'Food safety reputation risks, high valuation',
            'BKNG': 'Travel demand uncertainty, competition from alternatives',
            
            # Consumer Staples
            'WMT': 'Wage inflation pressures, e-commerce investment costs',
            'PG': 'Commodity cost inflation, market share losses',
            'KO': 'Health trend headwinds, volume growth challenges',
            'PEP': 'Input cost inflation, health-conscious consumer shifts',
            'COST': 'Competition from online retail, membership growth slowing',
            'MDLZ': 'Commodity price volatility, portfolio optimization delays',
            'PM': 'Tobacco consumption declining, ESG investor concerns',
            'CL': 'Emerging market volatility, competitive pricing',
            'KMB': 'Raw material inflation, private label competition',
            'GIS': 'Changing consumer preferences, brand relevance challenges',
            
            # Energy
            'XOM': 'Energy transition risks, carbon emission pressures',
            'CVX': 'Oil price volatility, renewable energy transition',
            'COP': 'Commodity price exposure, production decline risks',
            'SLB': 'Oil capex cycle dependency, technology disruption',
            'EOG': 'Shale production economics, ESG concerns',
            'MPC': 'Refining margin volatility, EV adoption impact',
            'PSX': 'Crack spread uncertainty, environmental regulations',
            'VLO': 'Refining capacity oversupply, demand destruction risks',
            'OXY': 'High debt levels, oil price sensitivity',
            'PXD': 'Permian competition, water disposal challenges',
            
            # Industrials
            'BA': 'Manufacturing quality issues, delivery delays',
            'CAT': 'Economic cycle sensitivity, China exposure',
            'UNP': 'Service quality concerns, regulatory headwinds',
            'HON': 'Cyclical aerospace exposure, restructuring costs',
            'UPS': 'Labor cost inflation, volume growth challenges',
            'LMT': 'Defense budget uncertainties, program delays',
            'RTX': 'Supply chain challenges, commercial recovery delays',
            'DE': 'Agricultural market cyclicality, farmer income pressures',
            'MMM': 'Legacy liability issues, organic growth challenges',
            'GE': 'Execution risks on turnaround, debt reduction needs',
            
            # Materials
            # 'LIN': 'Energy cost sensitivity, demand cyclicality',  # REMOVED - LIN already in BUY list
            'APD': 'Capital intensity, hydrogen economics uncertainty',
            'ECL': 'Hospitality demand dependency, input cost pressures',
            'SHW': 'Raw material inflation, housing market sensitivity',
            'NEM': 'Gold price volatility, operational cost inflation',
            'FCX': 'Copper price dependency, geopolitical mining risks',
            'NUE': 'Steel cycle vulnerability, import competition',
            'DOW': 'Chemical demand cyclicality, margin compression',
            'DD': 'End market weakness, semiconductor cycle exposure',
            'PPG': 'Raw material inflation, automotive production delays',
            
            # Real Estate
            'AMT': 'Interest rate sensitivity, tenant consolidation',
            'PLD': 'Industrial real estate oversupply, e-commerce normalization',
            'CCI': 'Carrier capex uncertainty, tower lease dynamics',
            'EQIX': 'Data center competition, power cost inflation',
            'PSA': 'Self-storage demand normalization, new supply',
            'WELL': 'Healthcare tenant credit risks, regulatory changes',
            'DLR': 'Valuation premium, competitive market dynamics',
            'O': 'Retail tenant challenges, lease renewal risks',
            'SPG': 'Mall traffic decline, tenant bankruptcies',
            'AVB': 'Apartment supply increases, rent growth deceleration',
            
            # Utilities
            'NEE': 'Interest rate sensitivity, regulatory recovery lags',
            'DUK': 'Regulatory review risks, coal plant retirement costs',
            'SO': 'Rate case outcomes, weather normalization',
            'D': 'Regulatory challenges, offshore wind costs',
            'AEP': 'Transmission investment recovery, coal transition',
            'EXC': 'Nuclear operational risks, power price exposure',
            'SRE': 'California wildfire liabilities, regulatory constraints',
            'XEL': 'Renewable integration costs, weather impacts',
            'WEC': 'Rate base growth limits, coal retirement costs',
            'ES': 'Nuclear plant operational costs, wholesale power prices',
            
            # Communication Services
            'GOOGL': 'Advertising market maturity, regulatory breakup risk',
            'META': 'Metaverse investment drag, advertising weakness',
            'NFLX': 'Streaming competition, subscriber growth saturation',
            'DIS': 'Streaming profitability challenges, parks attendance',
            'CMCSA': 'Cord-cutting acceleration, broadband competition',
            'T': 'Wireless competition, fiber buildout costs',
            'VZ': 'Market share losses, capital spending burden',
            'TMUS': 'Integration risks, network investment needs',
            'CHTR': 'Cable subscriber losses, fixed wireless competition',
            'EA': 'Gaming cycle maturity, live service monetization risks'
        }
        
        base_reason = stock_risks.get(ticker, f'Facing headwinds in {sector_name} sector')
        
        # Add context based on sector performance and market sentiment
        if sector_change < -1.0:
            context = f' Sector underperforming with {sector_change:.1f}% decline'
        elif sentiment == 'BEARISH':
            context = f' Bearish market conditions amplify {sector_name} risks'
        else:
            context = f' Sector showing {sector_change:.1f}% weakness'
            
        return f'{base_reason}.{context}'
    
    def _generate_sell_recommendations(self, sector_data: Dict, sentiment: str, max_recommendations: int = 10, excluded_tickers: set = None) -> List[Dict]:
        """
        Generate sell recommendations DYNAMICALLY from live market data.
        NO hardcoded stocks - uses real-time analysis!
        """
        excluded_tickers = excluded_tickers or set()  # Avoid duplicates with buy list
        
        try:
            # Try dynamic recommendations first (NEW - LIVE DATA!)
            if DYNAMIC_RECS_AVAILABLE:
                dynamic_service = get_dynamic_recommendation_service()
                bottom_sectors = [name for name, _ in list(sector_data.items())[-5:]]
                bottom_sectors.reverse()  # Worst first
                
                recommendations = dynamic_service.get_dynamic_sell_recommendations(
                    bottom_sectors=bottom_sectors,
                    max_recommendations=max_recommendations,
                    excluded_tickers=excluded_tickers
                )
                
                if recommendations:
                    logger.info(f"✓ Using {len(recommendations)} DYNAMIC sell recommendations (live data!)")
                    return recommendations
            
            # Fallback: Hardcoded approach (DEPRECATED - only if dynamic fails)
            logger.warning("⚠️ Falling back to hardcoded stocks (dynamic service unavailable)")
            return self._generate_sell_recommendations_fallback(sector_data, sentiment, max_recommendations, excluded_tickers)
            
        except Exception as e:
            logger.error(f"Error generating sell recommendations: {e}")
            return self._generate_sell_recommendations_fallback(sector_data, sentiment, max_recommendations, excluded_tickers)
    
    def _generate_sell_recommendations_fallback(self, sector_data: Dict, sentiment: str, max_recommendations: int = 10, excluded_tickers: set = None) -> List[Dict]:
        """FALLBACK: Generate sell recommendations from hardcoded lists (DEPRECATED)"""
        recommendations = []
        excluded_tickers = excluded_tickers or set()
        
        try:
            # Get bottom performing sectors
            bottom_sectors = list(sector_data.items())[-5:]  # Get bottom 5 sectors
            bottom_sectors.reverse()  # Worst first
            
            # Round-robin approach: take 1 stock from each sector to diversify
            sector_stock_iterators = {}
            for sector_name, sector_info in bottom_sectors:
                if sector_name in self.sector_stocks:
                    sector_stock_iterators[sector_name] = {
                        'stocks': iter(self.sector_stocks[sector_name]),
                        'info': sector_info
                    }
            
            # Keep cycling through sectors until we have enough recommendations
            while len(recommendations) < max_recommendations and sector_stock_iterators:
                sectors_to_remove = []
                
                for sector_name, data in list(sector_stock_iterators.items()):
                    if len(recommendations) >= max_recommendations:
                        break
                    
                    try:
                        ticker = next(data['stocks'])
                        
                        # CRITICAL: Skip if ticker is in buy recommendations
                        if ticker in excluded_tickers:
                            continue
                        
                        price = self._get_stock_price(ticker)
                        
                        if price is not None:
                            # Generate stock-specific reason
                            reason = self._get_stock_specific_sell_reason(
                                ticker,
                                sector_name,
                                data['info']['change_pct'],
                                sentiment
                            )
                            
                            recommendations.append({
                                "ticker": ticker,
                                "reason": reason,
                                "sector": sector_name,
                                "price": round(price, 2)
                            })
                    except StopIteration:
                        # No more stocks in this sector
                        sectors_to_remove.append(sector_name)
                
                # Remove exhausted sectors
                for sector_name in sectors_to_remove:
                    del sector_stock_iterators[sector_name]
            
        except Exception as e:
            logger.warning(f"Error in fallback sell recommendations: {e}")
        
        return recommendations[:max_recommendations]
    
    def load_cache(self) -> Optional[Dict]:
        """Load cached sentiment if still valid (expires daily or after set hours)"""
        try:
            if not os.path.exists(self.cache_file):
                return None
                
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            
            cached_time = datetime.fromisoformat(cache.get('timestamp', ''))
            now = datetime.now()
            
            # CRITICAL FIX: Expire cache if it's from a different day
            if cached_time.date() != now.date():
                logger.info(f"Cache expired: from {cached_time.date()}, today is {now.date()}")
                return None
            
            # Within same day: check hourly expiration
            if now - cached_time < timedelta(hours=self.cache_duration_hours):
                age_minutes = (now - cached_time).total_seconds() / 60
                logger.info(f"Using cached market sentiment from {age_minutes:.1f} minutes ago")
                return cache.get('data')
            else:
                logger.info("Cache expired (hourly limit reached), refreshing market sentiment")
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
    
    def _filter_by_price_range(self, recommendations: List[Dict], price_range: str) -> List[Dict]:
        """Filter recommendations by price range"""
        if price_range == 'all' or not recommendations:
            return recommendations
        
        ranges = {
            '1-5': (1, 5),
            '5-10': (5, 10),
            '10-25': (10, 25),
            '25-100': (25, 100),
            '100+': (100, float('inf'))
        }
        
        if price_range not in ranges:
            return recommendations
        
        min_price, max_price = ranges[price_range]
        return [r for r in recommendations if r.get('price') and min_price <= r['price'] < max_price]
    
    def get_daily_sentiment(self, force_refresh: bool = False, currency: str = 'USD') -> Dict:
        """
        Get daily market sentiment with caching
        
        Args:
            force_refresh: Force refresh even if cache is valid
            currency: Target currency for price display (USD, EUR, GBP, NATIVE)
            
        Returns:
            Dictionary containing market sentiment analysis with prices in requested currency
        """
        try:
            # Check cache first unless force refresh
            if not force_refresh:
                cached = self.load_cache()
                if cached:
                    # Convert cached prices to requested currency
                    return self._convert_sentiment_currency(cached, currency)
            
            logger.info("Generating market sentiment")
            
            # Fetch market data
            market_data = self.get_market_indices_data()
            sector_data = self.get_sector_performance()
            
            # Generate sentiment analysis with all recommendations
            ai_sentiment = self.generate_sentiment_analysis(market_data, sector_data)
            
            # Get all recommendations (up to 10 each) - prices in USD
            buy_recs = ai_sentiment.get('buy_recommendations', [])[:3]
            sell_recs = ai_sentiment.get('sell_recommendations', [])[:3]
            
            # Combine all data (prices in USD for caching)
            result = {
                'timestamp': datetime.now().isoformat(),
                'market_indices': market_data,
                'top_sectors': sector_data,
                'sentiment': ai_sentiment.get('sentiment', 'NEUTRAL'),
                'confidence': ai_sentiment.get('confidence', 50),
                'summary': ai_sentiment.get('summary', ''),
                'reasoning': ai_sentiment.get('reasoning', ''),
                'key_factors': ai_sentiment.get('key_factors', []),
                'buy_recommendations': buy_recs,
                'sell_recommendations': sell_recs,
                'currency': 'USD'  # Cache is always in USD
            }
            
            # Save to cache (in USD)
            self.save_cache(result)
            
            # Convert to requested currency before returning
            return self._convert_sentiment_currency(result, currency)
            
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
                'sell_recommendations': [],
                'currency': currency
            }
    
    def _convert_sentiment_currency(self, data: Dict, target_currency: str) -> Dict:
        """Convert all prices in sentiment data to target currency"""
        if not data or target_currency == 'USD':
            # Already in USD or no data
            result = data.copy()
            result['currency'] = target_currency
            return result
        
        result = data.copy()
        
        # Convert buy recommendations
        if 'buy_recommendations' in result:
            result['buy_recommendations'] = [
                {
                    **rec,
                    'price': round(self._convert_price(rec['price'], target_currency), 2)
                    if rec.get('price') else None
                }
                for rec in result['buy_recommendations']
            ]
        
        # Convert sell recommendations
        if 'sell_recommendations' in result:
            result['sell_recommendations'] = [
                {
                    **rec,
                    'price': round(self._convert_price(rec['price'], target_currency), 2)
                    if rec.get('price') else None
                }
                for rec in result['sell_recommendations']
            ]
        
        result['currency'] = target_currency
        return result


# Singleton instance
_market_sentiment_service = None

def get_market_sentiment_service() -> MarketSentimentService:
    """Get or create market sentiment service singleton"""
    global _market_sentiment_service
    if _market_sentiment_service is None:
        _market_sentiment_service = MarketSentimentService()
    return _market_sentiment_service
