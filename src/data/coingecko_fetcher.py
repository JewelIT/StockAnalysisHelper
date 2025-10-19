"""
CoinGecko Data Fetcher Module
Handles cryptocurrency price data and news from CoinGecko API
"""
import requests
from datetime import datetime, timedelta
import pandas as pd
import time

class CoinGeckoFetcher:
    """
    Fetches cryptocurrency data from CoinGecko API
    Free tier: Unlimited requests with rate limiting (50 calls/minute)
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    # Common crypto ticker mappings (e.g., BTC -> bitcoin, ETH -> ethereum)
    TICKER_MAP = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'BNB': 'binancecoin',
        'ADA': 'cardano',
        'SOL': 'solana',
        'XRP': 'ripple',
        'DOT': 'polkadot',
        'DOGE': 'dogecoin',
        'AVAX': 'avalanche-2',
        'SHIB': 'shiba-inu',
        'MATIC': 'matic-network',
        'LINK': 'chainlink',
        'UNI': 'uniswap',
        'LTC': 'litecoin',
        'ATOM': 'cosmos',
        'ETC': 'ethereum-classic',
        'XLM': 'stellar',
        'BCH': 'bitcoin-cash',
        'ALGO': 'algorand',
        'VET': 'vechain',
        'FIL': 'filecoin',
        'TRX': 'tron',
        'APT': 'aptos',
        'ARB': 'arbitrum',
        'OP': 'optimism',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'FinBertPortfolioAnalyzer/1.0'
        })
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Safer: 30 calls/minute = 2s between calls (avoid 429)
    
    def _rate_limit(self):
        """Enforce rate limiting to stay within free tier limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _normalize_ticker(self, ticker):
        """
        Convert ticker to CoinGecko ID
        Examples: BTC-USD -> bitcoin, ETH -> ethereum, bitcoin -> bitcoin
        """
        # Remove currency suffix if present (BTC-USD -> BTC)
        base_ticker = ticker.split('-')[0].upper()
        
        # Check if it's in our mapping
        if base_ticker in self.TICKER_MAP:
            return self.TICKER_MAP[base_ticker]
        
        # Try searching CoinGecko
        return self._search_coin_id(ticker)
    
    def _search_coin_id(self, query):
        """Search for coin ID by symbol or name"""
        try:
            self._rate_limit()
            response = self.session.get(
                f"{self.BASE_URL}/search",
                params={'query': query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('coins') and len(data['coins']) > 0:
                    # Return the first match's ID
                    return data['coins'][0]['id']
            
            return None
        except Exception as e:
            print(f"⚠️  Error searching for coin: {e}")
            return None
    
    @staticmethod
    def is_crypto_ticker(ticker):
        """
        Detect if a ticker is likely a cryptocurrency
        Examples: BTC-USD, ETH-EUR, BTC, bitcoin
        """
        ticker_upper = ticker.upper()
        
        # Check for crypto currency pairs
        if '-' in ticker_upper:
            base = ticker_upper.split('-')[0]
            quote = ticker_upper.split('-')[1]
            if quote in ['USD', 'EUR', 'GBP', 'USDT', 'BTC', 'ETH']:
                return True
        
        # Check if it's a known crypto symbol
        if ticker_upper in CoinGeckoFetcher.TICKER_MAP:
            return True
        
        # Check if it's already a CoinGecko ID format (lowercase with hyphens)
        if ticker == ticker.lower() and '-' in ticker:
            return True
        
        return False
    
    def fetch_historical_data(self, ticker, period="3mo"):
        """
        Fetch historical crypto price data
        
        Args:
            ticker: Crypto symbol (BTC, ETH) or pair (BTC-USD)
            period: Time period (1d, 1mo, 3mo, 6mo, 1y, 5y)
        
        Returns:
            pandas DataFrame with OHLCV data, or None if failed
        """
        coin_id = self._normalize_ticker(ticker)
        
        if not coin_id:
            print(f"⚠️  Could not find CoinGecko ID for {ticker}")
            return None
        
        # Convert period to days
        period_map = {
            '1d': 1,
            '1wk': 7,
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '5y': 1825,
            'max': 'max'
        }
        days = period_map.get(period, 90)
        
        try:
            self._rate_limit()
            
            # Fetch OHLC data (Open, High, Low, Close)
            response = self.session.get(
                f"{self.BASE_URL}/coins/{coin_id}/ohlc",
                params={'vs_currency': 'usd', 'days': days},
                timeout=15
            )
            
            if response.status_code == 429:
                print(f"⚠️  CoinGecko rate limit reached for {ticker}")
                print(f"   Waiting 10 seconds before retry...")
                time.sleep(10)
                # Retry once
                response = self.session.get(
                    f"{self.BASE_URL}/coins/{coin_id}/ohlc",
                    params={'vs_currency': 'usd', 'days': days},
                    timeout=15
                )
            
            if response.status_code != 200:
                print(f"⚠️  CoinGecko API error {response.status_code} for {ticker}")
                if response.status_code == 429:
                    print(f"   Try again in a few minutes or reduce the number of crypto tickers")
                return None
            
            data = response.json()
            
            if not data or len(data) == 0:
                print(f"⚠️  No OHLC data returned for {ticker}")
                return None
            
            # Convert to DataFrame
            # Data format: [[timestamp_ms, open, high, low, close], ...]
            df = pd.DataFrame(data, columns=['timestamp', 'Open', 'High', 'Low', 'Close'])
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df.index.name = 'Date'
            
            # Add volume (fetch separately as it's not in OHLC endpoint)
            df['Volume'] = 0  # Placeholder, can fetch from market_chart if needed
            
            print(f"  📊 Fetched {len(df)} data points for {ticker} (CoinGecko: {coin_id})")
            
            return df
            
        except Exception as e:
            print(f"⚠️  Error fetching CoinGecko data for {ticker}: {e}")
            return None
    
    def get_coin_info(self, ticker):
        """
        Get basic cryptocurrency information
        
        Returns:
            dict with name, symbol, market_cap, current_price, etc.
        """
        coin_id = self._normalize_ticker(ticker)
        
        if not coin_id:
            return {'name': ticker, 'sector': 'Cryptocurrency', 'industry': 'Crypto'}
        
        try:
            self._rate_limit()
            
            response = self.session.get(
                f"{self.BASE_URL}/coins/{coin_id}",
                params={
                    'localization': 'false',
                    'tickers': 'false',
                    'community_data': 'false',
                    'developer_data': 'false'
                },
                timeout=10
            )
            
            if response.status_code != 200:
                return {'name': ticker, 'sector': 'Cryptocurrency', 'industry': 'Crypto'}
            
            data = response.json()
            
            return {
                'name': data.get('name', ticker),
                'symbol': data.get('symbol', '').upper(),
                'sector': 'Cryptocurrency',
                'industry': data.get('categories', ['Crypto'])[0] if data.get('categories') else 'Crypto',
                'market_cap_rank': data.get('market_cap_rank', 'N/A'),
                'current_price': data.get('market_data', {}).get('current_price', {}).get('usd', 'N/A')
            }
            
        except Exception as e:
            print(f"⚠️  Error fetching coin info for {ticker}: {e}")
            return {'name': ticker, 'sector': 'Cryptocurrency', 'industry': 'Crypto'}
    
    def fetch_news(self, ticker, max_articles=5):
        """
        Fetch cryptocurrency news
        CoinGecko doesn't have a news API, but we can use status updates
        
        Returns:
            List of dicts with 'title', 'link', 'publisher', 'published'
        """
        coin_id = self._normalize_ticker(ticker)
        
        if not coin_id:
            return []
        
        try:
            self._rate_limit()
            
            # Fetch status updates (closest thing to news in free API)
            response = self.session.get(
                f"{self.BASE_URL}/coins/{coin_id}",
                params={'localization': 'false'},
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            
            # Try to get description and links
            articles = []
            
            # Add coin description as first "article"
            if data.get('description', {}).get('en'):
                description = data['description']['en']
                # Truncate to first paragraph
                first_para = description.split('\n')[0][:300] + '...'
                
                articles.append({
                    'title': f"{data.get('name', ticker)} Overview",
                    'link': data.get('links', {}).get('homepage', [''])[0],
                    'publisher': 'CoinGecko',
                    'published': ''
                })
            
            # Add links to official resources
            links = data.get('links', {})
            if links.get('homepage') and links['homepage'][0]:
                articles.append({
                    'title': f"Official {data.get('name', ticker)} Website",
                    'link': links['homepage'][0],
                    'publisher': 'Official',
                    'published': ''
                })
            
            # Note: For real news, consider integrating CryptoPanic API or NewsAPI
            
            return articles[:max_articles]
            
        except Exception as e:
            print(f"⚠️  Error fetching crypto news for {ticker}: {e}")
            return []
