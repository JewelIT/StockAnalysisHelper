"""
Analysis Service - Handles stock and portfolio analysis business logic
"""
from src.core.portfolio_analyzer import PortfolioAnalyzer
from src.data.data_fetcher import DataFetcher
from src.technical_analyzer import TechnicalAnalyzer
from src.chart_generator import ChartGenerator


class AnalysisService:
    """Service for managing stock analysis operations"""
    
    def __init__(self):
        self.analyzer = None
        self.cache = {}  # Store analysis data for chart regeneration
    
    def _get_analyzer(self):
        """Lazy load analyzer"""
        if self.analyzer is None:
            self.analyzer = PortfolioAnalyzer()
        return self.analyzer
    
    def analyze(self, tickers, chart_type='candlestick', timeframe='3mo', theme='dark', use_cache=False,
                max_news=5, max_social=5, news_sort='relevance', social_sort='relevance',
                news_days=3, social_days=7):
        """
        Analyze stocks/portfolio
        
        Args:
            tickers: List of ticker symbols
            chart_type: Type of chart to generate
            timeframe: Historical data timeframe
            theme: Chart theme ('dark' or 'light')
            use_cache: Use cached data for chart regeneration only
            max_news: Maximum news articles to fetch
            max_social: Maximum social media posts to fetch
            news_sort: How to sort news
            social_sort: How to sort social media
            news_days: How many days back to fetch news
            social_days: How many days back to fetch social media
            
        Returns:
            List of analysis results
        """
        # Handle cache-based chart regeneration
        if use_cache and len(tickers) == 1 and tickers[0] in self.cache:
            return self._regenerate_chart(tickers[0], chart_type, theme)
        
        # Fresh analysis
        analyzer = self._get_analyzer()
        results = analyzer.analyze_portfolio(
            tickers, 
            chart_type=chart_type, 
            timeframe=timeframe,
            theme=theme,
            max_news=max_news,
            max_social=max_social,
            news_sort=news_sort,
            social_sort=social_sort,
            news_days=news_days,
            social_days=social_days
        )
        
        # Cache results for later use
        self._cache_results(results, timeframe)
        
        return results
    
    def _regenerate_chart(self, ticker, chart_type, theme='dark'):
        """Regenerate chart from cached data"""
        cached = self.cache[ticker]
        chart_gen = ChartGenerator()
        
        chart_fig = chart_gen.create_candlestick_chart(
            ticker,
            cached['df'],
            cached['indicators'],
            chart_type,
            cached.get('timeframe', '3mo'),
            theme
        )
        
        result = cached['result'].copy()
        result['chart_data'] = chart_fig.to_json() if chart_fig else None
        result['chart_type_used'] = chart_type
        
        return [result]
    
    def _cache_results(self, results, timeframe='3mo'):
        """Cache analysis data for each ticker"""
        fetcher = DataFetcher()
        tech_analyzer = TechnicalAnalyzer()
        
        for result in results:
            if result.get('success'):
                ticker = result['ticker']
                df = fetcher.fetch_historical_data(ticker, timeframe)
                
                if df is not None and not df.empty:
                    indicators = tech_analyzer.calculate_indicators(df)
                    self.cache[ticker] = {
                        'df': df,
                        'indicators': indicators,
                        'result': result
                    }
    
    def get_cached_analysis(self, ticker):
        """Get cached analysis for a ticker"""
        return self.cache.get(ticker)
    
    def clear_cache(self, ticker=None):
        """Clear cache for specific ticker or all"""
        if ticker:
            self.cache.pop(ticker, None)
        else:
            self.cache.clear()
