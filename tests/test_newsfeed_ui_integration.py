"""
Integration tests for Newsfeed Configuration UI
Tests that the frontend configuration properly connects to backend parameters
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import pandas as pd


class TestNewsfeedUIIntegration(unittest.TestCase):
    """Test that newsfeed UI configuration reaches the backend correctly"""
    
    def setUp(self):
        """Set up test client"""
        from app import create_app
        self.app = create_app()
        self.client = self.app.test_client()
    
    @patch('app.services.analysis_service.AnalysisService._get_analyzer')
    def test_analyze_endpoint_accepts_newsfeed_params(self, mock_get_analyzer):
        """Test that /analyze endpoint accepts max_news and max_social parameters"""
        # Mock analyzer
        mock_analyzer = Mock()
        mock_analyzer.analyze_portfolio.return_value = [{
            'ticker': 'AAPL',
            'success': True,
            'chart': '<div>Chart</div>'
        }]
        mock_get_analyzer.return_value = mock_analyzer
        
        # Make request with newsfeed parameters
        response = self.client.post('/analyze',
                                   json={
                                       'tickers': ['AAPL'],
                                       'chart_type': 'candlestick',
                                       'max_news': 10,
                                       'max_social': 8,
                                       'news_sort': 'date_desc',
                                       'social_sort': 'relevance'
                                   })
        
        self.assertEqual(response.status_code, 200)
        
        # Verify parameters were passed to analyzer
        mock_analyzer.analyze_portfolio.assert_called_once()
        call_args = mock_analyzer.analyze_portfolio.call_args
        
        self.assertEqual(call_args.kwargs['max_news'], 10)
        self.assertEqual(call_args.kwargs['max_social'], 8)
        self.assertEqual(call_args.kwargs['news_sort'], 'date_desc')
        self.assertEqual(call_args.kwargs['social_sort'], 'relevance')
    
    @patch('app.services.analysis_service.AnalysisService._get_analyzer')
    def test_analyze_endpoint_defaults_newsfeed_params(self, mock_get_analyzer):
        """Test that /analyze endpoint uses default values when params not provided"""
        mock_analyzer = Mock()
        mock_analyzer.analyze_portfolio.return_value = [{
            'ticker': 'MSFT',
            'success': True,
            'chart': '<div>Chart</div>'
        }]
        mock_get_analyzer.return_value = mock_analyzer
        
        # Make request without newsfeed parameters
        response = self.client.post('/analyze',
                                   json={
                                       'tickers': ['MSFT'],
                                       'chart_type': 'line'
                                   })
        
        self.assertEqual(response.status_code, 200)
        
        # Verify default parameters were used
        call_args = mock_analyzer.analyze_portfolio.call_args
        self.assertEqual(call_args.kwargs['max_news'], 5)
        self.assertEqual(call_args.kwargs['max_social'], 5)
        self.assertEqual(call_args.kwargs['news_sort'], 'relevance')
        self.assertEqual(call_args.kwargs['social_sort'], 'relevance')
    
    @patch('app.services.analysis_service.AnalysisService._get_analyzer')
    def test_zero_limits_accepted(self, mock_get_analyzer):
        """Test that max_news=0 and max_social=0 are properly handled"""
        mock_analyzer = Mock()
        mock_analyzer.analyze_portfolio.return_value = [{
            'ticker': 'GOOGL',
            'success': True,
            'chart': '<div>Chart</div>'
        }]
        mock_get_analyzer.return_value = mock_analyzer
        
        # Request with zero limits (disable news and social)
        response = self.client.post('/analyze',
                                   json={
                                       'tickers': ['GOOGL'],
                                       'max_news': 0,
                                       'max_social': 0
                                   })
        
        self.assertEqual(response.status_code, 200)
        
        call_args = mock_analyzer.analyze_portfolio.call_args
        self.assertEqual(call_args.kwargs['max_news'], 0)
        self.assertEqual(call_args.kwargs['max_social'], 0)


class TestNewsfeedConfigInAnalysisService(unittest.TestCase):
    """Test that AnalysisService properly forwards newsfeed parameters"""
    
    @patch('app.services.analysis_service.PortfolioAnalyzer')
    def test_analysis_service_forwards_params(self, mock_analyzer_class):
        """Test that analysis service forwards all parameters to portfolio analyzer"""
        from app.services.analysis_service import AnalysisService
        
        # Mock the analyzer instance
        mock_analyzer = Mock()
        mock_analyzer.analyze_portfolio.return_value = []
        mock_analyzer_class.return_value = mock_analyzer
        
        service = AnalysisService()
        
        # Call analyze with all parameters
        service.analyze(
            tickers=['AAPL'],
            chart_type='candlestick',
            timeframe='3mo',
            max_news=15,
            max_social=12,
            news_sort='date_asc',
            social_sort='date_desc',
            news_days=7,
            social_days=14
        )
        
        # Verify all parameters were forwarded
        mock_analyzer.analyze_portfolio.assert_called_once_with(
            ['AAPL'],
            chart_type='candlestick',
            timeframe='3mo',
            max_news=15,
            max_social=12,
            news_sort='date_asc',
            social_sort='date_desc',
            news_days=7,
            social_days=14
        )


class TestNewsfeedConfigInPortfolioAnalyzer(unittest.TestCase):
    """Test that PortfolioAnalyzer properly uses newsfeed parameters"""
    
    @patch('src.portfolio_analyzer.DataFetcher')
    @patch('src.portfolio_analyzer.SentimentAnalyzer')
    @patch('src.portfolio_analyzer.TechnicalAnalyzer')
    @patch('src.portfolio_analyzer.ChartGenerator')
    @patch('src.portfolio_analyzer.SocialMediaFetcher')
    def test_portfolio_analyzer_forwards_to_individual_stock(self, 
                                                            mock_social, 
                                                            mock_chart,
                                                            mock_tech,
                                                            mock_sent,
                                                            mock_fetcher_class):
        """Test that analyze_portfolio forwards params to analyze_stock"""
        from src.portfolio_analyzer import PortfolioAnalyzer
        
        # Mock data fetcher to return valid DataFrame
        mock_fetcher = Mock()
        df = pd.DataFrame({
            'Close': [100, 101, 102],
            'Open': [99, 100, 101],
            'High': [101, 102, 103],
            'Low': [98, 99, 100],
            'Volume': [1000, 1100, 1200]
        })
        mock_fetcher.fetch_historical_data.return_value = df
        mock_fetcher.get_stock_info.return_value = {
            'name': 'Test Company',
            'sector': 'Technology',
            'industry': 'Software'
        }
        mock_fetcher.fetch_news.return_value = []
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock social media fetcher
        mock_social_instance = Mock()
        mock_social_instance.fetch_all_social_media.return_value = []
        mock_social.return_value = mock_social_instance
        
        # Mock other components
        mock_sent.return_value = Mock()
        mock_tech.return_value = Mock()
        mock_chart_instance = Mock()
        mock_chart_instance.create_candlestick_chart.return_value = Mock(to_html=Mock(return_value='<div>Chart</div>'))
        mock_chart.return_value = mock_chart_instance
        
        analyzer = PortfolioAnalyzer(enable_social_media=True)
        
        # Call analyze_portfolio with custom limits
        results = analyzer.analyze_portfolio(
            tickers=['AAPL'],
            chart_type='candlestick',
            timeframe='3mo',
            max_news=20,
            max_social=18,
            news_sort='date_desc',
            social_sort='date_asc'
        )
        
        # Verify social media fetcher was called with max_social
        mock_social_instance.fetch_all_social_media.assert_called_once()
        call_args = mock_social_instance.fetch_all_social_media.call_args
        self.assertEqual(call_args.kwargs['max_per_source'], 18)


if __name__ == '__main__':
    unittest.main()
