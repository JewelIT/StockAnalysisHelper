"""
Data Fetcher Module
Handles both traditional stocks (yfinance) and cryptocurrencies (CoinGecko)
"""
import yfinance as yf
from .coingecko_fetcher import CoinGeckoFetcher
from .config import Config

class DataFetcher:
    def __init__(self):
        self.coingecko = CoinGeckoFetcher()
    def fetch_news(self, ticker, max_articles=5, days=3):
        """
        Fetch latest news from Yahoo Finance or CoinGecko (for crypto)
        
        Args:
            ticker: Stock ticker symbol
            max_articles: Maximum number of articles to return
            days: Maximum age of articles in days (default: 3)
        
        Returns:
            List of dicts with 'title', 'link', 'publisher', 'published'
        """
        # Check if it's a cryptocurrency
        if CoinGeckoFetcher.is_crypto_ticker(ticker):
            print(f"  📰 Fetching crypto news from CoinGecko for {ticker}...")
            return self.coingecko.fetch_news(ticker, max_articles)
        
        # Otherwise use Yahoo Finance
        stock = yf.Ticker(ticker)
        try:
            # Fetch more articles than needed to allow for filtering
            news_list = stock.news if hasattr(stock, 'news') and stock.news else []
        except:
            return []
        
        articles = []
        for article in news_list:
            if isinstance(article, dict):
                article_data = {}
                
                # Check if article has nested 'content' structure (newer Yahoo Finance format)
                content = article.get('content', {}) if isinstance(article.get('content'), dict) else {}
                
                # Extract title
                if 'title' in article:
                    article_data['title'] = article['title']
                elif 'headline' in article:
                    article_data['title'] = article['headline']
                elif content.get('title'):
                    article_data['title'] = content['title']
                else:
                    continue
                
                # Extract link (multiple possible locations)
                link = (
                    article.get('link') or 
                    article.get('url') or 
                    content.get('canonicalUrl', {}).get('url') or
                    content.get('clickThroughUrl', {}).get('url') or
                    ''
                )
                article_data['link'] = link
                
                # Extract publisher (check nested structure first)
                publisher = 'Unknown'
                if content.get('provider', {}).get('displayName'):
                    publisher = content['provider']['displayName']
                elif article.get('publisher'):
                    publisher = article['publisher']
                elif article.get('source'):
                    publisher = article['source']
                article_data['publisher'] = publisher
                
                # Extract publish date
                pub_date = (
                    article.get('providerPublishTime') or 
                    content.get('pubDate') or
                    content.get('displayTime') or
                    ''
                )
                article_data['published'] = pub_date
                
                # Extract thumbnail if available
                article_data['thumbnail'] = None
                thumbnail = content.get('thumbnail') or article.get('thumbnail')
                if thumbnail:
                    if isinstance(thumbnail, dict):
                        # Get highest quality resolution or original
                        resolutions = thumbnail.get('resolutions', [])
                        if resolutions and len(resolutions) > 0:
                            article_data['thumbnail'] = resolutions[0].get('url', '')
                        elif thumbnail.get('originalUrl'):
                            article_data['thumbnail'] = thumbnail['originalUrl']
                    elif isinstance(thumbnail, str):
                        article_data['thumbnail'] = thumbnail
                
                articles.append(article_data)
        
        # Filter articles by age
        from datetime import datetime, timedelta, timezone
        import logging
        logger = logging.getLogger(__name__)
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        filtered_articles = []
        for article in articles:
            pub_time = article.get('published', '')
            if pub_time:
                try:
                    # Handle multiple timestamp formats
                    if isinstance(pub_time, (int, float)):
                        # Unix timestamp (seconds since epoch)
                        article_date = datetime.fromtimestamp(pub_time, tz=timezone.utc)
                    elif isinstance(pub_time, str):
                        # Try ISO format first (most common)
                        if 'T' in pub_time or '+' in pub_time or pub_time.endswith('Z'):
                            article_date = datetime.fromisoformat(pub_time.replace('Z', '+00:00'))
                            # Ensure timezone-aware
                            if article_date.tzinfo is None:
                                article_date = article_date.replace(tzinfo=timezone.utc)
                        else:
                            # Try other common formats
                            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                                try:
                                    article_date = datetime.strptime(pub_time, fmt).replace(tzinfo=timezone.utc)
                                    break
                                except ValueError:
                                    continue
                            else:
                                # No format worked, log it
                                logger.warning(f"Unrecognized date format for news article: '{pub_time}' (type: {type(pub_time).__name__})")
                                filtered_articles.append(article)
                                continue
                    else:
                        logger.warning(f"Unexpected timestamp type for news article: {type(pub_time).__name__} = {pub_time}")
                        filtered_articles.append(article)
                        continue
                    
                    if article_date >= cutoff_date:
                        filtered_articles.append(article)
                except (ValueError, TypeError, OSError) as e:
                    # If date parsing fails, log and include the article
                    logger.warning(f"Failed to parse news date '{pub_time}': {str(e)}")
                    filtered_articles.append(article)
            else:
                # Include articles without timestamp
                filtered_articles.append(article)
        
        # Return up to max_articles after filtering
        return filtered_articles[:max_articles]
    
    def fetch_historical_data(self, ticker, period="3mo"):
        """Fetch historical stock/crypto price data with appropriate interval"""
        # Check if it's a cryptocurrency
        if CoinGeckoFetcher.is_crypto_ticker(ticker):
            print(f"  💰 Using CoinGecko for crypto: {ticker}")
            return self.coingecko.fetch_historical_data(ticker, period)
        
        # Determine appropriate interval based on period (from config)
        interval = Config.get_interval_for_period(period)
        
        # Otherwise use Yahoo Finance
        stock = yf.Ticker(ticker)
        try:
            hist = stock.history(period=period, interval=interval)
            return hist if not hist.empty else None
        except:
            return None
    
    def get_stock_info(self, ticker):
        """Get basic stock/crypto information"""
        # Check if it's a cryptocurrency
        if CoinGeckoFetcher.is_crypto_ticker(ticker):
            return self.coingecko.get_coin_info(ticker)
        
        # Otherwise use Yahoo Finance
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A')
            }
        except:
            return {'name': ticker, 'sector': 'N/A', 'industry': 'N/A'}
    
    def get_pre_market_data(self, ticker):
        """Get pre-market trading data if available"""
        # Cryptos trade 24/7, no pre-market
        if CoinGeckoFetcher.is_crypto_ticker(ticker):
            return {'has_data': False, 'reason': '24/7 trading'}
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if pre/post market data is available
            if not info.get('hasPrePostMarketData', False):
                return {'has_data': False, 'reason': 'Not available'}
            
            # Get pre-market data
            pre_market_price = info.get('preMarketPrice')
            if pre_market_price is None:
                return {'has_data': False, 'reason': 'Market hours or no activity'}
            
            return {
                'has_data': True,
                'price': pre_market_price,
                'change': info.get('preMarketChange', 0),
                'change_percent': info.get('preMarketChangePercent', 0),
                'time': info.get('preMarketTime', 0),
                'market_state': info.get('marketState', 'UNKNOWN')
            }
        except Exception as e:
            return {'has_data': False, 'reason': f'Error: {str(e)}'}
