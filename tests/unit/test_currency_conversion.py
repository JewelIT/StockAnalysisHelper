"""
Unit tests for currency conversion functionality
"""
import pytest
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.web.services.market_sentiment_service import MarketSentimentService


class TestCurrencyConversion:
    """Test currency conversion in market sentiment service"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = MarketSentimentService()
    
    def test_convert_price_usd_to_usd(self):
        """Test USD to USD conversion (no change)"""
        price = 100.0
        result = self.service._convert_price(price, 'USD')
        assert result == 100.0
    
    def test_convert_price_usd_to_eur(self):
        """Test USD to EUR conversion"""
        price = 100.0
        result = self.service._convert_price(price, 'EUR')
        # Should use exchange rate (default 0.92)
        assert result == 92.0
    
    def test_convert_price_usd_to_gbp(self):
        """Test USD to GBP conversion"""
        price = 100.0
        result = self.service._convert_price(price, 'GBP')
        # Should use exchange rate (default 0.79)
        assert result == 79.0
    
    def test_convert_price_native_no_conversion(self):
        """Test native currency (no conversion)"""
        price = 100.0
        result = self.service._convert_price(price, 'NATIVE')
        assert result == 100.0
    
    def test_convert_price_invalid_currency(self):
        """Test invalid currency defaults to USD"""
        price = 100.0
        result = self.service._convert_price(price, 'INVALID')
        # Should default to 1.0 rate
        assert result == 100.0
    
    def test_convert_sentiment_currency_usd(self):
        """Test sentiment data conversion to USD (no change)"""
        data = {
            'buy_recommendations': [
                {'ticker': 'AAPL', 'price': 175.50, 'reason': 'Test'},
                {'ticker': 'MSFT', 'price': 380.25, 'reason': 'Test'}
            ],
            'sell_recommendations': [
                {'ticker': 'TSLA', 'price': 250.00, 'reason': 'Test'}
            ]
        }
        
        result = self.service._convert_sentiment_currency(data, 'USD')
        
        assert result['currency'] == 'USD'
        assert result['buy_recommendations'][0]['price'] == 175.50
        assert result['buy_recommendations'][1]['price'] == 380.25
        assert result['sell_recommendations'][0]['price'] == 250.00
    
    def test_convert_sentiment_currency_eur(self):
        """Test sentiment data conversion to EUR"""
        data = {
            'buy_recommendations': [
                {'ticker': 'AAPL', 'price': 100.00, 'reason': 'Test'},
            ],
            'sell_recommendations': [
                {'ticker': 'TSLA', 'price': 100.00, 'reason': 'Test'}
            ]
        }
        
        result = self.service._convert_sentiment_currency(data, 'EUR')
        
        assert result['currency'] == 'EUR'
        # 100 * 0.92 = 92.0
        assert result['buy_recommendations'][0]['price'] == 92.0
        assert result['sell_recommendations'][0]['price'] == 92.0
    
    def test_convert_sentiment_currency_gbp(self):
        """Test sentiment data conversion to GBP"""
        data = {
            'buy_recommendations': [
                {'ticker': 'AAPL', 'price': 100.00, 'reason': 'Test'},
            ],
            'sell_recommendations': []
        }
        
        result = self.service._convert_sentiment_currency(data, 'GBP')
        
        assert result['currency'] == 'GBP'
        # 100 * 0.79 = 79.0
        assert result['buy_recommendations'][0]['price'] == 79.0
    
    def test_convert_sentiment_currency_preserves_other_fields(self):
        """Test that conversion preserves all other fields"""
        data = {
            'timestamp': '2024-01-01T00:00:00',
            'sentiment': 'BULLISH',
            'confidence': 85,
            'buy_recommendations': [
                {'ticker': 'AAPL', 'price': 100.00, 'reason': 'Strong growth', 'sector': 'Technology'},
            ],
            'sell_recommendations': []
        }
        
        result = self.service._convert_sentiment_currency(data, 'EUR')
        
        # Check other fields preserved
        assert result['timestamp'] == '2024-01-01T00:00:00'
        assert result['sentiment'] == 'BULLISH'
        assert result['confidence'] == 85
        assert result['buy_recommendations'][0]['ticker'] == 'AAPL'
        assert result['buy_recommendations'][0]['reason'] == 'Strong growth'
        assert result['buy_recommendations'][0]['sector'] == 'Technology'
        # But price should be converted
        assert result['buy_recommendations'][0]['price'] == 92.0
    
    def test_convert_sentiment_currency_handles_missing_price(self):
        """Test conversion handles recommendations without price"""
        data = {
            'buy_recommendations': [
                {'ticker': 'AAPL', 'reason': 'Test'},  # No price field
                {'ticker': 'MSFT', 'price': None, 'reason': 'Test'},  # None price
                {'ticker': 'GOOGL', 'price': 100.00, 'reason': 'Test'},  # Valid price
            ],
            'sell_recommendations': []
        }
        
        result = self.service._convert_sentiment_currency(data, 'EUR')
        
        # Should not crash, handle gracefully
        assert result['buy_recommendations'][0].get('price') is None
        assert result['buy_recommendations'][1]['price'] is None
        assert result['buy_recommendations'][2]['price'] == 92.0


class TestMarketSentimentServiceCurrency:
    """Integration tests for market sentiment with currency"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = MarketSentimentService()
    
    def test_get_daily_sentiment_default_usd(self):
        """Test get_daily_sentiment defaults to USD"""
        result = self.service.get_daily_sentiment(force_refresh=False)
        
        # Should return data structure with currency field
        assert 'currency' in result
        # Default should be USD
        assert result['currency'] in ['USD', 'NATIVE']  # Allow both
    
    def test_get_daily_sentiment_explicit_currency(self):
        """Test get_daily_sentiment accepts currency parameter"""
        result = self.service.get_daily_sentiment(force_refresh=False, currency='EUR')
        
        assert 'currency' in result
        assert result['currency'] == 'EUR'
    
    def test_get_daily_sentiment_invalid_currency_fallback(self):
        """Test invalid currency falls back gracefully"""
        result = self.service.get_daily_sentiment(force_refresh=False, currency='INVALID')
        
        # Should not crash, should have currency field
        assert 'currency' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
