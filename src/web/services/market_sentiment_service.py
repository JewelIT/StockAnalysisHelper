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
    """Service for generating market sentiment and recommendations"""
    
    def __init__(self):
        self.cache_file = 'cache/market_sentiment_cache.json'
        self.cache_duration_hours = 4  # Refresh every 4 hours
        
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
        """Generate buy recommendations based on top performing sectors with prices"""
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
            logger.warning(f"Error generating buy recommendations: {e}")
        
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
            'LIN': 'Energy cost sensitivity, demand cyclicality',
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
    
    def _generate_sell_recommendations(self, sector_data: Dict, sentiment: str, max_recommendations: int = 10) -> List[Dict]:
        """Generate sell/avoid recommendations based on underperforming sectors with prices"""
        recommendations = []
        
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
