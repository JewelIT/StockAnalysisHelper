"""
Portfolio Analyzer - Main Analysis Logic
"""
from src.sentiment_analyzer import SentimentAnalyzer
from src.multi_model_sentiment import MultiModelSentimentAnalyzer
from src.technical_analyzer import TechnicalAnalyzer
from src.data_fetcher import DataFetcher
from src.social_media_fetcher import SocialMediaFetcher
from src.chart_generator import ChartGenerator
from src.analyst_consensus import AnalystConsensusFetcher

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
        self.analyst_fetcher = AnalystConsensusFetcher()
    
    def analyze_stock(self, ticker, max_news=5, chart_type='candlestick', timeframe='3mo',
                     max_social=5, news_sort='relevance', social_sort='relevance',
                     news_days=3, social_days=7):
        """Comprehensive analysis of a single stock
        
        Args:
            ticker: Stock ticker symbol
            max_news: Maximum number of news articles to fetch (default: 5)
            chart_type: Type of chart ('candlestick', 'line', 'ohlc', 'area')
            timeframe: Chart timeframe (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            max_social: Maximum number of social media posts to fetch (default: 5)
            news_sort: How to sort news ('relevance', 'date_desc', 'date_asc')
            social_sort: How to sort social media ('relevance', 'date_desc', 'date_asc')
            news_days: Maximum age of news articles in days (default: 3)
            social_days: Maximum age of social media posts in days (default: 7)
        """
        # Input validation for security
        max_news = max(0, min(int(max_news), 100))
        max_social = max(0, min(int(max_social), 100))
        news_days = max(1, min(int(news_days), 30))
        social_days = max(1, min(int(social_days), 30))
        valid_sort_options = {'relevance', 'date_desc', 'date_asc'}
        if news_sort not in valid_sort_options:
            news_sort = 'relevance'
        if social_sort not in valid_sort_options:
            social_sort = 'relevance'
        
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
            news_articles = self.data_fetcher.fetch_news(ticker, max_news, days=news_days)
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
                    social_posts = self.social_media_fetcher.fetch_all_social_media(ticker, max_per_source=max_social, days=social_days)
                    
                    if social_posts:
                        print(f"  🧠 Analyzing {len(social_posts)} social media posts...")
                        for post in social_posts:
                            sentiment = self.social_sentiment_analyzer.analyze(post['text'])
                            sentiment['text'] = post['text'][:200] + '...' if len(post['text']) > 200 else post['text']
                            sentiment['source'] = post.get('source', 'Unknown')
                            sentiment['created_at'] = post.get('created_at', '')
                            sentiment['link'] = post.get('link', '')
                            sentiment['source_type'] = 'social_media'
                            social_sentiment_results.append(sentiment)
                        
                        social_sentiment_score = (
                            sum(s['score'] for s in social_sentiment_results) / len(social_sentiment_results)
                            if social_sentiment_results else 0.5
                        )
                except Exception as e:
                    print(f"  ⚠️  Error fetching social media: {e}")
            
            # Combined sentiment (weighted average of news and social media)
            # If we have both news and social, weight them appropriately
            # If we only have one source, use that
            # If we have neither, we'll rely purely on technical analysis
            if news_sentiment_results and social_sentiment_results:
                # Both available: news 60%, social 40%
                avg_sentiment_score = (news_sentiment_score * 0.6 + social_sentiment_score * 0.4)
            elif news_sentiment_results:
                # Only news available
                avg_sentiment_score = news_sentiment_score
            elif social_sentiment_results:
                # Only social available
                avg_sentiment_score = social_sentiment_score
            else:
                # No sentiment data available - use neutral
                avg_sentiment_score = 0.5
            
            # Combine all sentiment results
            sentiment_results = news_sentiment_results + social_sentiment_results
            
            # Technical Analysis
            indicators = self.technical_analyzer.calculate_indicators(df)
            technical_signals = self.technical_analyzer.generate_signals(df, indicators)
            
            # Analyst Consensus Analysis
            print(f"  📊 Fetching analyst consensus...")
            analyst_data = self.analyst_fetcher.fetch_analyst_data(ticker)
            analyst_score = None
            analyst_consensus = None
            analyst_weight_used = '0%'
            analyst_coverage_level = 'none'  # none, limited, standard, strong
            
            if analyst_data.get('has_data', False) and analyst_data.get('number_of_analysts', 0) >= 2:
                # Calculate analyst scores (now accepts 2+ analysts, was 3+)
                recommendation_score = self.analyst_fetcher.calculate_analyst_score(analyst_data)
                target_score = self.analyst_fetcher.calculate_price_target_score(analyst_data)
                
                # Combine analyst recommendation and price target
                # Weight recommendation more heavily (70%) than price target (30%)
                if recommendation_score is not None and target_score is not None:
                    analyst_score = recommendation_score * 0.7 + target_score * 0.3
                elif recommendation_score is not None:
                    analyst_score = recommendation_score
                elif target_score is not None:
                    analyst_score = target_score
                
                # Get human-readable consensus
                analyst_consensus = self.analyst_fetcher.get_analyst_consensus_signal(analyst_data)
                
                # Determine coverage level
                num_analysts = analyst_data.get('number_of_analysts', 0)
                if num_analysts >= 10:
                    analyst_coverage_level = 'strong'
                    print(f"  ✓ Analyst Consensus: {analyst_consensus['signal']} ({num_analysts} analysts - Strong Coverage)")
                elif num_analysts >= 5:
                    analyst_coverage_level = 'standard'
                    print(f"  ✓ Analyst Consensus: {analyst_consensus['signal']} ({num_analysts} analysts)")
                else:
                    analyst_coverage_level = 'limited'
                    print(f"  ⚠️  Analyst Consensus: {analyst_consensus['signal']} ({num_analysts} analysts - Limited Coverage)")
            else:
                print(f"  ⚠️  No analyst coverage available")
            
            # Combined Recommendation
            # Three-way weighting when analyst data is available
            if analyst_score is not None:
                # With analyst data: Professional analysts get priority
                # 20% sentiment, 30% technical, 50% analyst consensus
                # Rationale: Professional analysts have done deep research and have significant upside/downside targets
                combined_score = (
                    avg_sentiment_score * 0.20 + 
                    technical_signals['score'] * 0.30 + 
                    analyst_score * 0.50
                )
                sentiment_weight_used = '20%'
                technical_weight_used = '30%'
                analyst_weight_used = '50%'
                
                formula = f'Combined Score = (Sentiment × {sentiment_weight_used}) + (Technical × {technical_weight_used}) + (Analyst Consensus × {analyst_weight_used})'
            elif not sentiment_results:
                # No sentiment data: 100% technical analysis
                combined_score = technical_signals['score']
                sentiment_weight_used = '0%'
                technical_weight_used = '100%'
                formula = 'Combined Score = Technical Score (No sentiment or analyst data available)'
            else:
                # No analyst data: 40% sentiment, 60% technical (original formula)
                combined_score = (avg_sentiment_score * 0.4 + technical_signals['score'] * 0.6)
                sentiment_weight_used = '40%'
                technical_weight_used = '60%'
                formula = f'Combined Score = (Sentiment Score × {sentiment_weight_used}) + (Technical Score × {technical_weight_used})'
            
            # Build explanation of how recommendation was calculated
            recommendation_explanation = {
                'formula': formula,
                'sentiment_weight': sentiment_weight_used,
                'technical_weight': technical_weight_used,
                'analyst_weight': analyst_weight_used,
                'sentiment_components': {
                    'news_sentiment': f'{news_sentiment_score:.2f}' if news_sentiment_results else 'N/A',
                    'social_sentiment': f'{social_sentiment_score:.2f}' if social_sentiment_results else 'N/A',
                    'news_weight': '60% of sentiment',
                    'social_weight': '40% of sentiment'
                },
                'technical_components': technical_signals.get('reasons', []),
                'analyst_components': None,
                'final_score': f'{combined_score:.2f}',
                'thresholds': {
                    'STRONG BUY': '> 0.65',
                    'BUY': '0.55 - 0.65',
                    'HOLD': '0.45 - 0.55',
                    'SELL': '0.35 - 0.45',
                    'STRONG SELL': '< 0.35'
                }
            }
            
            # Add analyst components to explanation if available
            if analyst_score is not None and analyst_consensus:
                target_mean = analyst_data.get('target_mean_price')
                current = analyst_data.get('current_price')
                upside_pct = None
                if target_mean and current and current > 0:
                    upside_pct = ((target_mean - current) / current) * 100
                
                recommendation_explanation['analyst_components'] = {
                    'consensus': analyst_consensus['signal'],
                    'num_analysts': analyst_consensus['num_analysts'],
                    'recommendation_mean': f"{analyst_consensus['recommendation_mean']:.2f}",
                    'analyst_score': f'{analyst_score:.2f}',
                    'target_price': f'${target_mean:.2f}' if target_mean else 'N/A',
                    'current_price': f'${current:.2f}' if current else 'N/A',
                    'upside': f'{upside_pct:+.1f}%' if upside_pct is not None else 'N/A',
                    'recommendation_weight': '70% of analyst score',
                    'target_weight': '30% of analyst score'
                }
            
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
                'recommendation_explanation': recommendation_explanation,
                'color': color,
                'combined_score': combined_score,
                'sentiment_score': avg_sentiment_score,
                'news_sentiment_score': news_sentiment_score,
                'social_sentiment_score': social_sentiment_score,
                'technical_score': technical_signals['score'],
                'technical_signal': technical_signals['signal'],
                'technical_reasons': technical_signals['reasons'],
                'analyst_score': analyst_score,
                'analyst_consensus': analyst_consensus,
                'analyst_data': analyst_data if analyst_data.get('has_data', False) else None,
                'analyst_coverage_level': analyst_coverage_level,
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
    
    def analyze_portfolio(self, tickers, chart_type='candlestick', timeframe='3mo',
                         max_news=5, max_social=5, news_sort='relevance', social_sort='relevance',
                         news_days=3, social_days=7):
        """Analyze multiple stocks
        
        Args:
            tickers: List of ticker symbols
            chart_type: Type of chart to generate
            timeframe: Chart timeframe
            max_news: Maximum news articles to fetch
            max_social: Maximum social media posts to fetch
            news_sort: How to sort news
            social_sort: How to sort social media
            news_days: How many days back to fetch news
            social_days: How many days back to fetch social media
        """
        results = []
        for ticker in tickers:
            result = self.analyze_stock(ticker.strip().upper(), chart_type=chart_type, timeframe=timeframe,
                                       max_news=max_news, max_social=max_social, 
                                       news_sort=news_sort, social_sort=social_sort,
                                       news_days=news_days, social_days=social_days)
            if result['success']:
                results.append(result)
        return results
