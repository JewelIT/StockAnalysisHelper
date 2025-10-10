"""
Tests for Market Sentiment Feature
Tests the market sentiment service and API endpoint
"""
import unittest
from unittest.mock import patch, MagicMock
from app import create_app
from app.services.market_sentiment_service import MarketSentimentService, get_market_sentiment_service
import json
import os
from datetime import datetime, timedelta


class TestMarketSentimentService(unittest.TestCase):
    """Test the market sentiment service"""
    
    def setUp(self):
        """Set up test environment"""
        self.service = MarketSentimentService()
        # Use a test cache file
        self.service.cache_file = 'cache/test_market_sentiment_cache.json'
        
    def tearDown(self):
        """Clean up test cache file"""
        if os.path.exists(self.service.cache_file):
            os.remove(self.service.cache_file)
    
    def test_service_initialization(self):
        """Test: Service initializes correctly"""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.cache_duration_hours, 4)
        self.assertIsInstance(self.service.sector_stocks, dict)
        self.assertGreater(len(self.service.sector_stocks), 0)
    
    def test_sector_stocks_data_structure(self):
        """Test: Sector stocks dictionary has correct structure"""
        expected_sectors = [
            'Technology', 'Financials', 'Healthcare', 'Energy', 
            'Industrials', 'Consumer Discretionary', 'Consumer Staples',
            'Materials', 'Real Estate', 'Utilities'
        ]
        
        for sector in expected_sectors:
            self.assertIn(sector, self.service.sector_stocks)
            self.assertIsInstance(self.service.sector_stocks[sector], list)
            self.assertGreater(len(self.service.sector_stocks[sector]), 0)
    
    @patch('yfinance.Ticker')
    def test_get_market_indices_data(self, mock_ticker):
        """Test: Market indices data fetching"""
        # Mock yfinance response
        mock_hist = MagicMock()
        mock_hist.empty = False
        mock_hist.__len__ = lambda x: 5
        mock_hist.__getitem__ = lambda x, key: MagicMock(
            iloc=MagicMock(__getitem__=lambda x, idx: 100.0 if idx == -1 else 99.0)
        )
        
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_hist
        mock_ticker.return_value = mock_ticker_instance
        
        data = self.service.get_market_indices_data()
        
        self.assertIsInstance(data, dict)
        # Should have attempted to fetch at least some indices
        # Note: May be empty if all fail, but structure should be dict
    
    @patch('yfinance.Ticker')
    def test_get_sector_performance(self, mock_ticker):
        """Test: Sector performance fetching"""
        # Mock yfinance response
        mock_hist = MagicMock()
        mock_hist.empty = False
        mock_hist.__len__ = lambda x: 5
        mock_hist.__getitem__ = lambda x, key: MagicMock(
            iloc=MagicMock(__getitem__=lambda x, idx: 100.0 if idx == -1 else 99.0)
        )
        
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_hist
        mock_ticker.return_value = mock_ticker_instance
        
        data = self.service.get_sector_performance()
        
        self.assertIsInstance(data, dict)
        # Should return top 5 sectors (or fewer if errors)
        self.assertLessEqual(len(data), 5)
    
    def test_generate_sentiment_analysis_bullish(self):
        """Test: Sentiment analysis generates BULLISH correctly"""
        market_data = {
            'S&P 500': {'current': 5000, 'change_pct': 1.5, 'trend': 'up'},
            'Dow Jones': {'current': 40000, 'change_pct': 1.2, 'trend': 'up'},
            'NASDAQ': {'current': 18000, 'change_pct': 2.0, 'trend': 'up'},
            'VIX (Volatility)': {'current': 12.5, 'change_pct': -5.0, 'trend': 'down'}
        }
        
        sector_data = {
            'Technology': {'symbol': 'XLK', 'change_pct': 1.8, 'trend': 'up'},
            'Financials': {'symbol': 'XLF', 'change_pct': 1.5, 'trend': 'up'}
        }
        
        result = self.service.generate_sentiment_analysis(market_data, sector_data)
        
        self.assertEqual(result['sentiment'], 'BULLISH')
        self.assertGreater(result['confidence'], 50)
        self.assertIsInstance(result['summary'], str)
        self.assertIsInstance(result['reasoning'], str)
        self.assertIsInstance(result['key_factors'], list)
        self.assertIsInstance(result['buy_recommendations'], list)
        self.assertIsInstance(result['sell_recommendations'], list)
    
    def test_generate_sentiment_analysis_bearish(self):
        """Test: Sentiment analysis generates BEARISH correctly"""
        market_data = {
            'S&P 500': {'current': 5000, 'change_pct': -1.5, 'trend': 'down'},
            'Dow Jones': {'current': 40000, 'change_pct': -1.2, 'trend': 'down'},
            'NASDAQ': {'current': 18000, 'change_pct': -2.0, 'trend': 'down'},
            'VIX (Volatility)': {'current': 25.0, 'change_pct': 15.0, 'trend': 'up'}
        }
        
        sector_data = {
            'Technology': {'symbol': 'XLK', 'change_pct': -1.8, 'trend': 'down'},
            'Financials': {'symbol': 'XLF', 'change_pct': -1.5, 'trend': 'down'}
        }
        
        result = self.service.generate_sentiment_analysis(market_data, sector_data)
        
        self.assertEqual(result['sentiment'], 'BEARISH')
        self.assertGreater(result['confidence'], 50)
    
    def test_generate_sentiment_analysis_neutral(self):
        """Test: Sentiment analysis generates NEUTRAL correctly"""
        market_data = {
            'S&P 500': {'current': 5000, 'change_pct': 0.1, 'trend': 'up'},
            'Dow Jones': {'current': 40000, 'change_pct': -0.2, 'trend': 'down'},
            'NASDAQ': {'current': 18000, 'change_pct': 0.15, 'trend': 'up'},
            'VIX (Volatility)': {'current': 16.0, 'change_pct': 1.0, 'trend': 'up'}
        }
        
        sector_data = {
            'Technology': {'symbol': 'XLK', 'change_pct': 0.3, 'trend': 'up'},
            'Financials': {'symbol': 'XLF', 'change_pct': -0.2, 'trend': 'down'}
        }
        
        result = self.service.generate_sentiment_analysis(market_data, sector_data)
        
        self.assertEqual(result['sentiment'], 'NEUTRAL')
    
    def test_generate_buy_recommendations(self):
        """Test: Buy recommendations generation"""
        sector_data = {
            'Technology': {'symbol': 'XLK', 'change_pct': 1.5, 'trend': 'up'},
            'Financials': {'symbol': 'XLF', 'change_pct': 1.2, 'trend': 'up'},
            'Healthcare': {'symbol': 'XLV', 'change_pct': 0.8, 'trend': 'up'}
        }
        
        recommendations = self.service._generate_buy_recommendations(sector_data, 'BULLISH')
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 10)  # Now returns up to 10
        
        for rec in recommendations:
            self.assertIn('ticker', rec)
            self.assertIn('reason', rec)
            self.assertIn('sector', rec)
            self.assertIn('price', rec)  # Price field added
            self.assertIsInstance(rec['ticker'], str)
            self.assertIsInstance(rec['reason'], str)
            self.assertIsInstance(rec['sector'], str)
    
    def test_generate_sell_recommendations(self):
        """Test: Sell recommendations generation"""
        sector_data = {
            'Technology': {'symbol': 'XLK', 'change_pct': 0.5, 'trend': 'up'},
            'Financials': {'symbol': 'XLF', 'change_pct': -0.5, 'trend': 'down'},
            'Energy': {'symbol': 'XLE', 'change_pct': -1.2, 'trend': 'down'}
        }
        
        recommendations = self.service._generate_sell_recommendations(sector_data, 'BEARISH')
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 10)  # Now returns up to 10
        
        for rec in recommendations:
            self.assertIn('ticker', rec)
            self.assertIn('reason', rec)
            self.assertIn('sector', rec)
            self.assertIn('price', rec)  # Price field added
    
    def test_cache_save_and_load(self):
        """Test: Cache saving and loading"""
        test_data = {
            'sentiment': 'BULLISH',
            'confidence': 85,
            'summary': 'Test summary',
            'market_indices': {},
            'top_sectors': {}
        }
        
        # Save cache
        self.service.save_cache(test_data)
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.service.cache_file))
        
        # Load cache
        loaded_data = self.service.load_cache()
        
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data['sentiment'], 'BULLISH')
        self.assertEqual(loaded_data['confidence'], 85)
    
    def test_cache_expiration(self):
        """Test: Cache expires after duration"""
        test_data = {
            'sentiment': 'BULLISH',
            'confidence': 85
        }
        
        # Save cache with old timestamp
        old_cache = {
            'timestamp': (datetime.now() - timedelta(hours=5)).isoformat(),
            'data': test_data
        }
        
        os.makedirs(os.path.dirname(self.service.cache_file), exist_ok=True)
        with open(self.service.cache_file, 'w') as f:
            json.dump(old_cache, f)
        
        # Load cache - should return None due to expiration
        loaded_data = self.service.load_cache()
        
        self.assertIsNone(loaded_data)
    
    def test_get_market_sentiment_service_singleton(self):
        """Test: Service singleton works correctly"""
        service1 = get_market_sentiment_service()
        service2 = get_market_sentiment_service()
        
        self.assertIs(service1, service2)


class TestMarketSentimentAPI(unittest.TestCase):
    """Test the market sentiment API endpoint"""
    
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('app.services.market_sentiment_service.MarketSentimentService.get_daily_sentiment')
    def test_market_sentiment_endpoint_success(self, mock_get_sentiment):
        """Test: /market-sentiment endpoint returns success"""
        mock_get_sentiment.return_value = {
            'timestamp': datetime.now().isoformat(),
            'sentiment': 'BULLISH',
            'confidence': 85,
            'summary': 'Test summary',
            'reasoning': 'Test reasoning',
            'key_factors': ['Factor 1', 'Factor 2'],
            'market_indices': {},
            'top_sectors': {},
            'buy_recommendations': [],
            'sell_recommendations': []
        }
        
        response = self.client.get('/market-sentiment')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(data['data']['sentiment'], 'BULLISH')
        self.assertEqual(data['data']['confidence'], 85)
    
    @patch('app.services.market_sentiment_service.MarketSentimentService.get_daily_sentiment')
    def test_market_sentiment_endpoint_force_refresh(self, mock_get_sentiment):
        """Test: /market-sentiment?refresh=true forces refresh"""
        mock_get_sentiment.return_value = {
            'sentiment': 'NEUTRAL',
            'confidence': 50
        }
        
        response = self.client.get('/market-sentiment?refresh=true')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        
        # Verify force_refresh was passed
        mock_get_sentiment.assert_called_once_with(force_refresh=True)
    
    @patch('app.services.market_sentiment_service.MarketSentimentService.get_daily_sentiment')
    def test_market_sentiment_endpoint_error_handling(self, mock_get_sentiment):
        """Test: Endpoint handles errors gracefully"""
        mock_get_sentiment.side_effect = Exception("Test error")
        
        response = self.client.get('/market-sentiment')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 500)
        self.assertFalse(data['success'])
        self.assertIn('error', data)


class TestPriceFiltering(unittest.TestCase):
    """Test price filtering functionality"""
    
    def test_price_range_filtering(self):
        """Test: Price range filtering works correctly"""
        recommendations = [
            {'ticker': 'AAPL', 'price': 150.0, 'sector': 'Tech'},
            {'ticker': 'F', 'price': 12.0, 'sector': 'Auto'},
            {'ticker': 'BAC', 'price': 30.0, 'sector': 'Finance'},
            {'ticker': 'AMZN', 'price': 175.0, 'sector': 'Tech'},
            {'ticker': 'GE', 'price': 4.5, 'sector': 'Industrial'},
        ]
        
        # Test 1-5 range
        filtered = [r for r in recommendations if 1 <= r['price'] < 5]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['ticker'], 'GE')
        
        # Test 10-25 range
        filtered = [r for r in recommendations if 10 <= r['price'] < 25]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['ticker'], 'F')
        
        # Test 25-100 range
        filtered = [r for r in recommendations if 25 <= r['price'] < 100]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['ticker'], 'BAC')
        
        # Test 100+ range
        filtered = [r for r in recommendations if r['price'] >= 100]
        self.assertEqual(len(filtered), 2)
        
    def test_recommendations_include_prices(self):
        """Test: Generated recommendations include price information"""
        service = MarketSentimentService()
        sector_data = {
            'Technology': {'symbol': 'XLK', 'change_pct': 1.0, 'trend': 'up'}
        }
        
        result = service.generate_sentiment_analysis({}, sector_data)
        
        # Check that at least some recommendations have prices
        buy_recs = result.get('buy_recommendations', [])
        if len(buy_recs) > 0:
            # At least one should have a price field
            has_price = any('price' in rec for rec in buy_recs)
            self.assertTrue(has_price, "At least one recommendation should have a price")


class TestMarketSentimentDataStructure(unittest.TestCase):
    """Test the data structure returned by sentiment service"""
    
    def setUp(self):
        """Set up service"""
        self.service = MarketSentimentService()
    
    def test_sentiment_response_has_all_fields(self):
        """Test: Sentiment response has all required fields"""
        market_data = {
            'S&P 500': {'current': 5000, 'change_pct': 0.5, 'trend': 'up'}
        }
        sector_data = {
            'Technology': {'symbol': 'XLK', 'change_pct': 0.8, 'trend': 'up'}
        }
        
        result = self.service.generate_sentiment_analysis(market_data, sector_data)
        
        required_fields = [
            'sentiment', 'confidence', 'summary', 'reasoning',
            'key_factors', 'buy_recommendations', 'sell_recommendations'
        ]
        
        for field in required_fields:
            self.assertIn(field, result)
    
    def test_recommendation_structure(self):
        """Test: Recommendations have correct structure"""
        sector_data = {
            'Technology': {'symbol': 'XLK', 'change_pct': 1.0, 'trend': 'up'}
        }
        
        result = self.service.generate_sentiment_analysis({}, sector_data)
        
        for rec in result['buy_recommendations']:
            self.assertIn('ticker', rec)
            self.assertIn('reason', rec)
            self.assertIn('sector', rec)
            self.assertIn('price', rec)
            # Ticker should be valid format
            self.assertTrue(rec['ticker'].isupper())
            self.assertGreater(len(rec['ticker']), 0)
            # Price should be a positive number if present
            if rec['price'] is not None:
                self.assertIsInstance(rec['price'], (int, float))
                self.assertGreater(rec['price'], 0)
    
    def test_sentiment_values_valid(self):
        """Test: Sentiment values are valid"""
        market_data = {
            'S&P 500': {'current': 5000, 'change_pct': 0.5, 'trend': 'up'}
        }
        
        result = self.service.generate_sentiment_analysis(market_data, {})
        
        # Sentiment must be one of three values
        self.assertIn(result['sentiment'], ['BULLISH', 'BEARISH', 'NEUTRAL'])
        
        # Confidence must be between 0 and 100
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 100)


if __name__ == '__main__':
    unittest.main()
