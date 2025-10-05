"""
Portfolio Analyzer - Main Analysis Logic
"""
from src.sentiment_analyzer import SentimentAnalyzer
from src.technical_analyzer import TechnicalAnalyzer
from src.data_fetcher import DataFetcher
from src.chart_generator import ChartGenerator

class PortfolioAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.data_fetcher = DataFetcher()
        self.chart_generator = ChartGenerator()
    
    def analyze_stock(self, ticker, max_news=5, chart_type='candlestick'):
        """Comprehensive analysis of a single stock
        
        Args:
            ticker: Stock ticker symbol
            max_news: Maximum number of news articles to fetch
            chart_type: Type of chart ('candlestick', 'line', 'ohlc', 'area')
        """
        print(f"\nAnalyzing {ticker}...")
        
        result = {
            'ticker': ticker,
            'success': False
        }
        
        try:
            # Fetch historical data
            df = self.data_fetcher.fetch_historical_data(ticker)
            if df is None or df.empty:
                result['error'] = 'No historical data available'
                return result
            
            # Get stock info
            stock_info = self.data_fetcher.get_stock_info(ticker)
            result['name'] = stock_info['name']
            result['sector'] = stock_info['sector']
            result['industry'] = stock_info['industry']
            
            # Sentiment Analysis
            news_titles = self.data_fetcher.fetch_news(ticker, max_news)
            sentiment_results = []
            
            if news_titles:
                for title in news_titles:
                    sentiment = self.sentiment_analyzer.analyze(title)
                    sentiment['title'] = title
                    sentiment_results.append(sentiment)
            
            avg_sentiment_score = (
                sum(s['score'] for s in sentiment_results) / len(sentiment_results)
                if sentiment_results else 0.5
            )
            
            # Technical Analysis
            indicators = self.technical_analyzer.calculate_indicators(df)
            technical_signals = self.technical_analyzer.generate_signals(df, indicators)
            
            # Combined Recommendation
            combined_score = (avg_sentiment_score * 0.4 + technical_signals['score'] * 0.6)
            
            if combined_score > 0.65:
                recommendation = 'STRONG BUY'
                color = '#27ae60'
            elif combined_score > 0.55:
                recommendation = 'BUY'
                color = '#2ecc71'
            elif combined_score > 0.45:
                recommendation = 'HOLD'
                color = '#f39c12'
            elif combined_score > 0.35:
                recommendation = 'SELL'
                color = '#e67e22'
            else:
                recommendation = 'STRONG SELL'
                color = '#c0392b'
            
            # Price info
            current_price = df['Close'].iloc[-1]
            price_change = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
            
            # Generate chart data (JSON format for client-side rendering)
            chart_fig = self.chart_generator.create_candlestick_chart(ticker, df, indicators, chart_type)
            
            # Store data for later chart regeneration
            result.update({
                'success': True,
                'recommendation': recommendation,
                'color': color,
                'combined_score': combined_score,
                'sentiment_score': avg_sentiment_score,
                'technical_score': technical_signals['score'],
                'technical_signal': technical_signals['signal'],
                'technical_reasons': technical_signals['reasons'],
                'current_price': current_price,
                'price_change': price_change,
                'news_count': len(news_titles),
                'sentiment_results': sentiment_results,
                'chart_data': chart_fig.to_json() if chart_fig else None,
                'chart_type_used': chart_type  # Track what chart type was used
            })
            
        except Exception as e:
            result['error'] = str(e)
            print(f"Error analyzing {ticker}: {e}")
        
        return result
    
    def analyze_portfolio(self, tickers, chart_type='candlestick'):
        """Analyze multiple stocks
        
        Args:
            tickers: List of ticker symbols
            chart_type: Type of chart to generate
        """
        results = []
        for ticker in tickers:
            result = self.analyze_stock(ticker.strip().upper(), chart_type=chart_type)
            if result['success']:
                results.append(result)
        return results
