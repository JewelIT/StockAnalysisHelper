"""
Data Fetcher Module
Handles both traditional stocks (yfinance) and cryptocurrencies (CoinGecko)
"""
import yfinance as yf
from .coingecko_fetcher import CoinGeckoFetcher

class DataFetcher:
    def __init__(self):
        self.coingecko = CoinGeckoFetcher()
    def fetch_news(self, ticker, max_articles=5):
        """
        Fetch latest news from Yahoo Finance or CoinGecko (for crypto)
        
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
            news_list = stock.news[:max_articles] if hasattr(stock, 'news') and stock.news else []
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
        
        return articles
    
    def fetch_historical_data(self, ticker, period="3mo"):
        """Fetch historical stock/crypto price data"""
        # Check if it's a cryptocurrency
        if CoinGeckoFetcher.is_crypto_ticker(ticker):
            print(f"  💰 Using CoinGecko for crypto: {ticker}")
            return self.coingecko.fetch_historical_data(ticker, period)
        
        # Otherwise use Yahoo Finance
        stock = yf.Ticker(ticker)
        try:
            hist = stock.history(period=period)
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
