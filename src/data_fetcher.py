"""
Data Fetcher Module
"""
import yfinance as yf

class DataFetcher:
    @staticmethod
    def fetch_news(ticker, max_articles=5):
        """
        Fetch latest news from Yahoo Finance with links
        
        Returns:
            List of dicts with 'title', 'link', 'publisher', 'published'
        """
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
    
    @staticmethod
    def fetch_historical_data(ticker, period="3mo"):
        """Fetch historical stock price data"""
        stock = yf.Ticker(ticker)
        try:
            hist = stock.history(period=period)
            return hist if not hist.empty else None
        except:
            return None
    
    @staticmethod
    def get_stock_info(ticker):
        """Get basic stock information"""
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
