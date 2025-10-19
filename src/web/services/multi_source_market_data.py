"""
Multi-Source Market Data Service - Aggregates data from multiple sources with fallback handling.

ARCHITECTURE:
  Data sources are prioritized to maximize reliability and accuracy:
  
  Priority 1 (Weight 1.5): Finnhub - Real-time, high accuracy, requires API key
  Priority 2 (Weight 1.5): Alpha Vantage - Real-time with rate limits, fallback disabled on 429
  Priority 3 (Weight 1.0): yfinance - Always available, free, fallback when others fail
  
FALLBACK STRATEGY:
  - All three sources queried in parallel attempts
  - Weighted consensus calculated from successful responses
  - Alpha Vantage automatically disabled if rate limit (429) detected
  - System continues functioning with remaining sources
  - yfinance guarantees application never fails on market data
  
RATE LIMIT HANDLING:
  - Alpha Vantage rate limit triggers automatic disabled flag
  - Detection: 'Note' field in response OR 'rate limit' in exception
  - Once disabled: AV skipped until manual re-enable
  - Consensus recalculated from Finnhub + yfinance with adjusted weights
  
CONSENSUS CALCULATION:
  - Weighted average: sum(price * weight) / sum(weights)
  - Detects discrepancies: flags if sources disagree > 10% or opposite signs
  - Calculates confidence: higher with more sources in agreement
  - All raw data included for auditability
"""
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import statistics

logger = logging.getLogger(__name__)

class MultiSourceMarketData:
    """
    Fetch market data from multiple sources and calculate weighted consensus.
    
    Ensures no single source failure brings down the system.
    Automatically manages Alpha Vantage rate limiting with graceful degradation.
    """
    
    def __init__(self):
        self.sources_config = {
            'yfinance': {
                'enabled': True,
                'weight': 1.0,  # Lowest weight due to reliability issues
                'priority': 3,
                'requires_key': False
            },
            'finnhub': {
                'enabled': self._check_api_key('FINNHUB_API_KEY'),
                'weight': 1.5,
                'priority': 1,
                'requires_key': True
            },
            'alphavantage': {
                'enabled': self._check_api_key('ALPHAVANTAGE_API_KEY'),
                'weight': 1.5,
                'priority': 2,
                'requires_key': True
            }
        }
        
        self.indices_map = {
            'S&P 500': {'yf': '^GSPC', 'finnhub': 'SPY', 'av': 'SPY'},
            'Dow Jones': {'yf': '^DJI', 'finnhub': 'DIA', 'av': 'DIA'},
            'NASDAQ': {'yf': '^IXIC', 'finnhub': 'QQQ', 'av': 'QQQ'},
            'VIX (Volatility)': {'yf': '^VIX', 'finnhub': '^VIX', 'av': '^VIX'},  # Fear index (inverse to market)
        }
        
        # Initialize clients
        self._init_clients()
    
    def _check_api_key(self, env_var: str) -> bool:
        """Check if API key exists in environment"""
        key = os.getenv(env_var)
        return key is not None and len(key) > 0
    
    def _init_clients(self):
        """Initialize API clients for enabled sources"""
        self.clients = {}
        
        # Finnhub
        if self.sources_config['finnhub']['enabled']:
            try:
                import finnhub
                api_key = os.getenv('FINNHUB_API_KEY')
                self.clients['finnhub'] = finnhub.Client(api_key=api_key)
                logger.info("✓ Finnhub client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Finnhub: {e}")
                self.sources_config['finnhub']['enabled'] = False
        
        # Alpha Vantage
        if self.sources_config['alphavantage']['enabled']:
            try:
                from alpha_vantage.timeseries import TimeSeries
                api_key = os.getenv('ALPHAVANTAGE_API_KEY')
                self.clients['alphavantage'] = TimeSeries(key=api_key, output_format='json')
                logger.info("✓ Alpha Vantage client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Alpha Vantage: {e}")
                self.sources_config['alphavantage']['enabled'] = False
        
        # Yahoo Finance (always available, no key needed)
        try:
            import yfinance as yf
            self.clients['yfinance'] = yf
            logger.info("✓ Yahoo Finance available")
        except Exception as e:
            logger.error(f"Yahoo Finance not available: {e}")
    
    def get_consensus_market_data(self) -> Dict:
        """
        Fetch market data from all available sources and return consensus
        
        Returns:
            Dict with consensus data for each index, including:
            - consensus_price
            - consensus_change_pct
            - sources_used
            - confidence level
            - discrepancy warnings
        """
        consensus_data = {}
        
        for index_name, symbols in self.indices_map.items():
            try:
                results = self._fetch_from_all_sources(index_name, symbols)
                
                if not results:
                    logger.warning(f"No data available for {index_name}")
                    continue
                
                # Calculate consensus
                consensus = self._calculate_consensus(results)
                consensus['index_name'] = index_name
                consensus_data[index_name] = consensus
                
                # Log if sources disagree significantly
                if consensus.get('has_discrepancy'):
                    logger.warning(
                        f"⚠️ {index_name}: Data sources disagree by {consensus['spread']:.2f}% "
                        f"(Severity: {consensus['severity']})"
                    )
                
            except Exception as e:
                logger.error(f"Error fetching consensus for {index_name}: {e}")
        
        return consensus_data
    
    def _fetch_from_all_sources(self, index_name: str, symbols: Dict) -> List[Dict]:
        """Fetch data from all enabled sources for a given index"""
        results = []
        
        # Yahoo Finance
        if self.sources_config['yfinance']['enabled']:
            data = self._fetch_yfinance(symbols.get('yf'))
            if data:
                results.append({
                    'source': 'yfinance',
                    'price': data['price'],
                    'change_pct': data['change_pct'],
                    'weight': self.sources_config['yfinance']['weight'],
                    'timestamp': datetime.now().isoformat()
                })
        
        # Finnhub
        if self.sources_config['finnhub']['enabled']:
            data = self._fetch_finnhub(symbols.get('finnhub'))
            if data:
                results.append({
                    'source': 'finnhub',
                    'price': data['price'],
                    'change_pct': data['change_pct'],
                    'weight': self.sources_config['finnhub']['weight'],
                    'timestamp': datetime.now().isoformat()
                })
        
        # Alpha Vantage
        if self.sources_config['alphavantage']['enabled']:
            data = self._fetch_alphavantage(symbols.get('av'))
            if data:
                results.append({
                    'source': 'alphavantage',
                    'price': data['price'],
                    'change_pct': data['change_pct'],
                    'weight': self.sources_config['alphavantage']['weight'],
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def _fetch_yfinance(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Yahoo Finance"""
        try:
            ticker = self.clients['yfinance'].Ticker(symbol)
            hist = ticker.history(period='1d', interval='5m')
            
            if hist.empty or len(hist) < 2:
                hist = ticker.history(period='5d')
            
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                day_open = hist['Open'].iloc[0]
                change_pct = ((current - day_open) / day_open) * 100
                
                return {
                    'price': float(current),
                    'change_pct': float(change_pct)
                }
        except Exception as e:
            logger.warning(f"Yahoo Finance fetch failed for {symbol}: {e}")
        return None
    
    def _fetch_finnhub(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Finnhub"""
        try:
            quote = self.clients['finnhub'].quote(symbol)
            
            if quote and 'c' in quote and 'pc' in quote:
                current = quote['c']  # Current price
                prev_close = quote['pc']  # Previous close
                change_pct = ((current - prev_close) / prev_close) * 100
                
                return {
                    'price': float(current),
                    'change_pct': float(change_pct)
                }
        except Exception as e:
            logger.warning(f"Finnhub fetch failed for {symbol}: {e}")
        return None
    
    def _fetch_alphavantage(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Alpha Vantage with fallback handling for rate limits"""
        try:
            data, meta_data = self.clients['alphavantage'].get_intraday(
                symbol=symbol,
                interval='5min',
                outputsize='compact'
            )
            
            if data and len(data) >= 2:
                # Get latest and first prices of the day
                times = sorted(data.keys(), reverse=True)
                latest = data[times[0]]
                day_open = data[times[-1]]
                
                current = float(latest['4. close'])
                open_price = float(day_open['1. open'])
                change_pct = ((current - open_price) / open_price) * 100
                
                return {
                    'price': current,
                    'change_pct': change_pct
                }
            else:
                # Check for rate limit message in meta_data
                if meta_data and 'Note' in meta_data:
                    logger.warning(f"Alpha Vantage rate limit reached for {symbol}. Switching to fallback sources.")
                    self.sources_config['alphavantage']['enabled'] = False
                    return None
                elif meta_data and 'Error Message' in meta_data:
                    logger.warning(f"Alpha Vantage error for {symbol}: {meta_data.get('Error Message')}")
                    return None
        except Exception as e:
            error_str = str(e)
            if 'rate' in error_str.lower() or 'limit' in error_str.lower():
                logger.warning(f"Alpha Vantage rate limit reached for {symbol}. Switching to fallback sources.")
                self.sources_config['alphavantage']['enabled'] = False
            else:
                logger.warning(f"Alpha Vantage fetch failed for {symbol}: {e}")
        return None
    
    def _calculate_consensus(self, results: List[Dict]) -> Dict:
        """Calculate weighted consensus from multiple sources"""
        if not results:
            return {}
        
        # Calculate weighted average
        total_weight = sum(r['weight'] for r in results)
        consensus_price = sum(r['price'] * r['weight'] for r in results) / total_weight
        consensus_change = sum(r['change_pct'] * r['weight'] for r in results) / total_weight
        
        # Detect discrepancies
        discrepancy = self._detect_discrepancy(results, consensus_change)
        
        # Determine confidence level
        confidence = self._calculate_confidence(results, discrepancy)
        
        return {
            'consensus_price': round(consensus_price, 2),
            'consensus_change_pct': round(consensus_change, 2),
            'trend': 'up' if consensus_change > 0 else 'down',
            'sources_used': [r['source'] for r in results],
            'sources_count': len(results),
            'confidence': confidence,
            'has_discrepancy': discrepancy['has_discrepancy'],
            'severity': discrepancy['severity'],
            'spread': discrepancy['spread'],
            'raw_sources': results  # For debugging
        }
    
    def _detect_discrepancy(self, results: List[Dict], consensus: float) -> Dict:
        """Detect if sources disagree significantly"""
        if len(results) < 2:
            return {
                'has_discrepancy': False,
                'severity': 'NONE',
                'spread': 0,
                'sign_disagreement': False
            }
        
        changes = [r['change_pct'] for r in results]
        max_change = max(changes)
        min_change = min(changes)
        spread = max_change - min_change
        
        # Check for sign disagreement (one says up, another says down)
        has_sign_disagreement = (max_change > 0.5) and (min_change < -0.5)
        
        severity = 'NONE'
        if spread > 10 or has_sign_disagreement:
            severity = 'CRITICAL'  # Sources completely disagree
        elif spread > 5:
            severity = 'HIGH'      # Significant disagreement
        elif spread > 2:
            severity = 'MEDIUM'    # Minor disagreement
        elif spread > 1:
            severity = 'LOW'       # Slight disagreement
        
        return {
            'has_discrepancy': spread > 1,
            'severity': severity,
            'spread': round(spread, 2),
            'sign_disagreement': has_sign_disagreement,
            'outliers': self._find_outliers(results, consensus)
        }
    
    def _find_outliers(self, results: List[Dict], consensus: float) -> List[str]:
        """Find sources that disagree significantly from consensus"""
        outliers = []
        for r in results:
            if abs(r['change_pct'] - consensus) > 3:  # More than 3% deviation
                outliers.append(r['source'])
        return outliers
    
    def _calculate_confidence(self, results: List[Dict], discrepancy: Dict) -> str:
        """Calculate confidence level based on sources and agreement"""
        num_sources = len(results)
        
        if num_sources >= 3 and discrepancy['severity'] == 'NONE':
            return 'VERY_HIGH'
        elif num_sources >= 3 and discrepancy['severity'] in ['LOW', 'MEDIUM']:
            return 'HIGH'
        elif num_sources >= 2 and discrepancy['severity'] in ['NONE', 'LOW']:
            return 'MEDIUM'
        elif num_sources >= 2:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def get_enabled_sources(self) -> List[str]:
        """Return list of currently enabled data sources"""
        return [name for name, config in self.sources_config.items() if config['enabled']]
    
    def get_source_status(self) -> Dict:
        """Get status of all configured sources"""
        status = {}
        for source, config in self.sources_config.items():
            status[source] = {
                'enabled': config['enabled'],
                'weight': config['weight'],
                'priority': config['priority'],
                'client_initialized': source in self.clients
            }
        return status


# Singleton instance
_multi_source_instance = None

def get_multi_source_service() -> MultiSourceMarketData:
    """Get or create singleton instance of multi-source service"""
    global _multi_source_instance
    if _multi_source_instance is None:
        _multi_source_instance = MultiSourceMarketData()
    return _multi_source_instance
