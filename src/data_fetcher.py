"""
Data Fetcher Module
"""
import yfinance as yf

class DataFetcher:
    @staticmethod
    def fetch_news(ticker, max_articles=5):
        """Fetch latest news from Yahoo Finance"""
        stock = yf.Ticker(ticker)
        try:
            news_list = stock.news[:max_articles] if hasattr(stock, 'news') and stock.news else []
        except:
            return []
        
        titles = []
        for article in news_list:
            if isinstance(article, dict):
                if 'content' in article and isinstance(article['content'], dict):
                    if 'title' in article['content']:
                        titles.append(article['content']['title'])
                elif 'title' in article:
                    titles.append(article['title'])
                elif 'headline' in article:
                    titles.append(article['headline'])
        
        return titles
    
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
