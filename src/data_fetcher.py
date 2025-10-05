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
                
                # Extract title
                if 'title' in article:
                    article_data['title'] = article['title']
                elif 'headline' in article:
                    article_data['title'] = article['headline']
                elif 'content' in article and isinstance(article['content'], dict):
                    article_data['title'] = article['content'].get('title', 'Untitled')
                else:
                    continue
                
                # Extract link
                article_data['link'] = article.get('link', '') or article.get('url', '')
                
                # Extract publisher
                article_data['publisher'] = article.get('publisher', 'Unknown')
                
                # Extract publish date
                article_data['published'] = article.get('providerPublishTime', '')
                
                # Extract thumbnail if available
                article_data['thumbnail'] = None
                if 'thumbnail' in article and article['thumbnail']:
                    if isinstance(article['thumbnail'], dict):
                        article_data['thumbnail'] = article['thumbnail'].get('resolutions', [{}])[0].get('url', '')
                    elif isinstance(article['thumbnail'], str):
                        article_data['thumbnail'] = article['thumbnail']
                
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
