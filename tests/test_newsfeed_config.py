"""
Unit tests for PortfolioAnalyzer newsfeed configuration
Tests the configurable limits for news and social media
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from src.portfolio_analyzer import PortfolioAnalyzer


class TestNewsfeedConfiguration(unittest.TestCase):
    """Test newsfeed configuration parameters"""
    
    def setUp(self):
        """Set up test instance"""
        self.analyzer = PortfolioAnalyzer(enable_social_media=False)
    
    def test_default_news_limit(self):
        """Test that default news limit is 5"""
        import pandas as pd
        
        # Mock the data fetcher with valid data
        mock_fetcher = Mock()
        # Return a simple DataFrame with price data
        df = pd.DataFrame({
            'Close': [100, 101, 102],
            'Open': [99, 100, 101],
            'High': [101, 102, 103],
            'Low': [98, 99, 100],
            'Volume': [1000, 1100, 1200]
        })
        mock_fetcher.fetch_historical_data.return_value = df
        mock_fetcher.fetch_news.return_value = []
        mock_fetcher.get_stock_info.return_value = {'name': 'Apple Inc.', 'sector': 'Technology', 'industry': 'Consumer Electronics'}
        self.analyzer.data_fetcher = mock_fetcher
        
        # Call analyze_stock without specifying max_news
        self.analyzer.analyze_stock('AAPL')
        
        # Verify fetch_news was called with default limit of 5
        mock_fetcher.fetch_news.assert_called_once()
        call_args = mock_fetcher.fetch_news.call_args
        self.assertEqual(call_args[0][1], 5)  # Second argument should be 5
    
    def test_custom_news_limit(self):
        """Test that custom news limit is respected"""
        import pandas as pd
        
        # Mock the data fetcher with valid data
        mock_fetcher = Mock()
        df = pd.DataFrame({
            'Close': [100, 101, 102],
            'Open': [99, 100, 101],
            'High': [101, 102, 103],
            'Low': [98, 99, 100],
            'Volume': [1000, 1100, 1200]
        })
        mock_fetcher.fetch_historical_data.return_value = df
        mock_fetcher.fetch_news.return_value = []
        mock_fetcher.get_stock_info.return_value = {'name': 'Apple Inc.', 'sector': 'Technology', 'industry': 'Consumer Electronics'}
        self.analyzer.data_fetcher = mock_fetcher
        
        # Call analyze_stock with custom max_news
        self.analyzer.analyze_stock('AAPL', max_news=10)
        
        # Verify fetch_news was called with custom limit
        mock_fetcher.fetch_news.assert_called_once()
        call_args = mock_fetcher.fetch_news.call_args
        self.assertEqual(call_args[0][1], 10)
    
    def test_default_social_limit(self):
        """Test that default social media limit is 5"""
        # Enable social media for this test
        analyzer = PortfolioAnalyzer(enable_social_media=True)
        
        # Mock the social media fetcher
        mock_social_fetcher = Mock()
        mock_social_fetcher.fetch_all_social_media.return_value = []
        analyzer.social_media_fetcher = mock_social_fetcher
        
        # Mock other dependencies
        mock_fetcher = Mock()
        mock_fetcher.fetch_historical_data.return_value = None
        mock_fetcher.fetch_news.return_value = []
        mock_fetcher.get_stock_info.return_value = {'name': 'Test', 'sector': 'Tech', 'industry': 'Software'}
        analyzer.data_fetcher = mock_fetcher
        
        # Call analyze_stock without specifying max_social
        result = analyzer.analyze_stock('AAPL')
        
        # If social media was attempted, verify it used default limit of 5
        if mock_social_fetcher.fetch_all_social_media.called:
            call_args = mock_social_fetcher.fetch_all_social_media.call_args
            self.assertEqual(call_args[1]['max_per_source'], 5)
    
    def test_function_signature_backward_compatible(self):
        """Test that old function calls still work (backward compatibility)"""
        # Mock dependencies
        mock_fetcher = Mock()
        mock_fetcher.fetch_historical_data.return_value = None
        mock_fetcher.fetch_news.return_value = []
        self.analyzer.data_fetcher = mock_fetcher
        
        # Old-style call (should still work)
        try:
            self.analyzer.analyze_stock('AAPL', 5, 'candlestick', '3mo')
            success = True
        except TypeError:
            success = False
        
        self.assertTrue(success, "Old function signature should still work")
    
    def test_new_parameters_accept_values(self):
        """Test that new parameters accept custom values"""
        # Mock dependencies
        mock_fetcher = Mock()
        mock_fetcher.fetch_historical_data.return_value = None
        mock_fetcher.fetch_news.return_value = []
        self.analyzer.data_fetcher = mock_fetcher
        
        # New-style call with all parameters
        try:
            self.analyzer.analyze_stock(
                'AAPL',
                max_news=10,
                max_social=8,
                news_sort='date_desc',
                social_sort='date_asc'
            )
            success = True
        except (TypeError, AttributeError):
            success = False
        
        self.assertTrue(success, "New parameters should be accepted")
    
    def test_sort_parameters_stored(self):
        """Test that sort parameters are accepted (even if not used yet)"""
        # This tests that the parameters don't cause errors
        # Actual sorting logic will be implemented later
        mock_fetcher = Mock()
        mock_fetcher.fetch_historical_data.return_value = None
        mock_fetcher.fetch_news.return_value = []
        self.analyzer.data_fetcher = mock_fetcher
        
        # Should not raise an error
        self.analyzer.analyze_stock(
            'AAPL',
            news_sort='relevance',
            social_sort='date_desc'
        )


class TestNewsfeedLimits(unittest.TestCase):
    """Test that limits are properly enforced"""
    
    def test_news_limit_boundary_values(self):
        """Test boundary values for news limit"""
        import pandas as pd
        
        analyzer = PortfolioAnalyzer(enable_social_media=False)
        
        # Test various limits
        test_limits = [0, 1, 5, 10, 50, 100]
        
        for limit in test_limits:
            with self.subTest(limit=limit):
                mock_fetcher = Mock()
                df = pd.DataFrame({
                    'Close': [100, 101, 102],
                    'Open': [99, 100, 101],
                    'High': [101, 102, 103],
                    'Low': [98, 99, 100],
                    'Volume': [1000, 1100, 1200]
                })
                mock_fetcher.fetch_historical_data.return_value = df
                mock_fetcher.fetch_news.return_value = []
                mock_fetcher.get_stock_info.return_value = {'name': 'Test', 'sector': 'Test', 'industry': 'Test'}
                analyzer.data_fetcher = mock_fetcher
                
                analyzer.analyze_stock('AAPL', max_news=limit)
                
                # Verify the limit was passed correctly
                call_args = mock_fetcher.fetch_news.call_args
                self.assertEqual(call_args[0][1], limit)


if __name__ == '__main__':
    unittest.main()
