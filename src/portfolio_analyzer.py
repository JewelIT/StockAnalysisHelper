"""
Portfolio Analyzer - Main Analysis Logic
"""
from src.sentiment_analyzer import SentimentAnalyzer
from src.multi_model_sentiment import MultiModelSentimentAnalyzer
from src.technical_analyzer import TechnicalAnalyzer
from src.data_fetcher import DataFetcher
from src.social_media_fetcher import SocialMediaFetcher
from src.chart_generator import ChartGenerator

class PortfolioAnalyzer:
    def __init__(self, enable_social_media=True):
        """
        Initialize portfolio analyzer
        
        Args:
            enable_social_media: Whether to fetch and analyze social media sentiment
        """
        self.sentiment_analyzer = SentimentAnalyzer()  # Keep original for news
        self.social_sentiment_analyzer = None
        self.enable_social_media = enable_social_media
        
        if enable_social_media:
            # Load Twitter-optimized model for social media
            try:
                self.social_sentiment_analyzer = MultiModelSentimentAnalyzer('twitter-financial')
                self.social_media_fetcher = SocialMediaFetcher()
            except Exception as e:
                print(f"⚠️  Could not load social media features: {e}")
                self.enable_social_media = False
        
        self.technical_analyzer = TechnicalAnalyzer()
        self.data_fetcher = DataFetcher()
        self.chart_generator = ChartGenerator()
    
    def analyze_stock(self, ticker, max_news=5, chart_type='candlestick', timeframe='3mo'):
        """Comprehensive analysis of a single stock
        
        Args:
            ticker: Stock ticker symbol
            max_news: Maximum number of news articles to fetch
            chart_type: Type of chart ('candlestick', 'line', 'ohlc', 'area')
            timeframe: Chart timeframe (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
        """
        print(f"\nAnalyzing {ticker} ({timeframe})...")
        
        result = {
            'ticker': ticker,
            'success': False
        }
        
        try:
            # Fetch historical data with specified timeframe
            df = self.data_fetcher.fetch_historical_data(ticker, period=timeframe)
            if df is None or df.empty:
                result['error'] = 'No historical data available'
                return result
            
            # Get stock info
            stock_info = self.data_fetcher.get_stock_info(ticker)
            result['name'] = stock_info['name']
            result['sector'] = stock_info['sector']
            result['industry'] = stock_info['industry']
            
            # News Sentiment Analysis (using FinBERT)
            news_articles = self.data_fetcher.fetch_news(ticker, max_news)
            news_sentiment_results = []
            
            if news_articles:
                print(f"  📰 Analyzing {len(news_articles)} news articles...")
                for article in news_articles:
                    sentiment = self.sentiment_analyzer.analyze(article['title'])
                    sentiment['title'] = article['title']
                    sentiment['link'] = article.get('link', '')
                    sentiment['publisher'] = article.get('publisher', 'Unknown')
                    sentiment['published'] = article.get('published', '')
                    sentiment['thumbnail'] = article.get('thumbnail', '')
                    sentiment['source_type'] = 'news'
                    news_sentiment_results.append(sentiment)
            
            news_sentiment_score = (
                sum(s['score'] for s in news_sentiment_results) / len(news_sentiment_results)
                if news_sentiment_results else 0.5
            )
            
            # Social Media Sentiment Analysis (using Twitter-RoBERTa)
            social_sentiment_results = []
            social_sentiment_score = 0.5
            
            if self.enable_social_media and self.social_sentiment_analyzer:
                try:
                    print(f"  💬 Fetching social media sentiment...")
                    social_posts = self.social_media_fetcher.fetch_all_social_media(ticker, max_per_source=15)
                    
                    if social_posts:
                        print(f"  🧠 Analyzing {len(social_posts)} social media posts...")
                        for post in social_posts:
                            sentiment = self.social_sentiment_analyzer.analyze(post['text'])
                            sentiment['text'] = post['text'][:200] + '...' if len(post['text']) > 200 else post['text']
                            sentiment['source'] = post.get('source', 'Unknown')
                            sentiment['created_at'] = post.get('created_at', '')
                            sentiment['source_type'] = 'social_media'
                            social_sentiment_results.append(sentiment)
                        
                        social_sentiment_score = (
                            sum(s['score'] for s in social_sentiment_results) / len(social_sentiment_results)
                            if social_sentiment_results else 0.5
                        )
                except Exception as e:
                    print(f"  ⚠️  Error fetching social media: {e}")
            
            # Combined sentiment (weighted average of news and social media)
            if social_sentiment_results:
                # Give more weight to news (60%) vs social media (40%)
                avg_sentiment_score = (news_sentiment_score * 0.6 + social_sentiment_score * 0.4)
            else:
                avg_sentiment_score = news_sentiment_score
            
            # Combine all sentiment results
            sentiment_results = news_sentiment_results + social_sentiment_results
            
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
                'news_sentiment_score': news_sentiment_score,
                'social_sentiment_score': social_sentiment_score,
                'technical_score': technical_signals['score'],
                'technical_signal': technical_signals['signal'],
                'technical_reasons': technical_signals['reasons'],
                'current_price': current_price,
                'price_change': price_change,
                'news_count': len(news_sentiment_results),
                'social_count': len(social_sentiment_results),
                'sentiment_results': sentiment_results,
                'chart_data': chart_fig.to_json() if chart_fig else None,
                'chart_type_used': chart_type  # Track what chart type was used
            })
            
        except Exception as e:
            result['error'] = str(e)
            print(f"Error analyzing {ticker}: {e}")
        
        return result
    
    def analyze_portfolio(self, tickers, chart_type='candlestick', timeframe='3mo'):
        """Analyze multiple stocks
        
        Args:
            tickers: List of ticker symbols
            chart_type: Type of chart to generate
            timeframe: Chart timeframe
        """
        results = []
        for ticker in tickers:
            result = self.analyze_stock(ticker.strip().upper(), chart_type=chart_type, timeframe=timeframe)
            if result['success']:
                results.append(result)
        return results
