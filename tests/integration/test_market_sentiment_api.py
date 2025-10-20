"""
Integration tests for market sentiment API with currency support
"""
import pytest
import sys
import os
import json

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.web import create_app

class TestMarketSentimentAPI:
    """Integration tests for /market-sentiment endpoint"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_market_sentiment_endpoint_exists(self):
        """Test market sentiment endpoint is accessible"""
        response = self.client.get('/market-sentiment')
        
        # Should not be 404
        assert response.status_code != 404
    
    def test_market_sentiment_default_currency(self):
        """Test market sentiment returns default currency (USD)"""
        response = self.client.get('/market-sentiment')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have currency field
        assert 'currency' in data
        # Default should be USD
        assert data['currency'] in ['USD', 'NATIVE']
    
    def test_market_sentiment_with_usd_currency(self):
        """Test market sentiment with explicit USD currency"""
        response = self.client.get('/market-sentiment?currency=USD')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        data = result['data']
        
        assert data['currency'] == 'USD'
    
    def test_market_sentiment_with_eur_currency(self):
        """Test market sentiment with EUR currency"""
        response = self.client.get('/market-sentiment?currency=EUR')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        data = result['data']
        
        assert data['currency'] == 'EUR'
    
    def test_market_sentiment_with_gbp_currency(self):
        """Test market sentiment with GBP currency"""
        response = self.client.get('/market-sentiment?currency=GBP')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        data = result['data']
        
        assert data['currency'] == 'GBP'
    
    def test_market_sentiment_with_native_currency(self):
        """Test market sentiment with NATIVE currency"""
        response = self.client.get('/market-sentiment?currency=NATIVE')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        data = result['data']
        
        assert data['currency'] == 'NATIVE'
    
    def test_market_sentiment_with_invalid_currency(self):
        """Test market sentiment with invalid currency defaults to USD"""
        response = self.client.get('/market-sentiment?currency=INVALID')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        data = result['data']
        
        # Should fallback to USD
        assert data['currency'] == 'USD'
    
    def test_market_sentiment_lowercase_currency(self):
        """Test market sentiment handles lowercase currency"""
        response = self.client.get('/market-sentiment?currency=eur')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        data = result['data']
        
        # Should convert to uppercase
        assert data['currency'] == 'EUR'
    
    def test_market_sentiment_response_structure(self):
        """Test market sentiment returns expected structure"""
        response = self.client.get('/market-sentiment?currency=USD')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['success'] is True
        data = result['data']
        
        # Check required fields
        assert 'currency' in data
        assert 'buy_recommendations' in data
        assert 'sell_recommendations' in data
        
        # Check recommendations have price field
        if data['buy_recommendations']:
            for rec in data['buy_recommendations']:
                assert 'ticker' in rec
                assert 'price' in rec
                assert 'reason' in rec
        
        if data['sell_recommendations']:
            for rec in data['sell_recommendations']:
                assert 'ticker' in rec
                assert 'price' in rec
                assert 'reason' in rec
    
    def test_market_sentiment_price_conversion(self):
        """Test that prices are actually converted between currencies"""
        # Get USD prices
        response_usd = self.client.get('/market-sentiment?currency=USD&force_refresh=true')
        result_usd = json.loads(response_usd.data)
        data_usd = result_usd['data']
        
        # Get EUR prices
        response_eur = self.client.get('/market-sentiment?currency=EUR')
        result_eur = json.loads(response_eur.data)
        data_eur = result_eur['data']
        
        # If we have recommendations, prices should differ
        if data_usd.get('buy_recommendations') and data_eur.get('buy_recommendations'):
            usd_price = data_usd['buy_recommendations'][0].get('price')
            eur_price = data_eur['buy_recommendations'][0].get('price')
            
            # If both have prices, they should be different (unless rate is 1.0)
            if usd_price and eur_price:
                # EUR price should be approximately 0.92 * USD price
                expected_eur = round(usd_price * 0.92, 2)
                assert abs(eur_price - expected_eur) < 0.01, \
                    f"EUR price {eur_price} should be ~{expected_eur} (USD {usd_price} * 0.92)"
    
    def test_market_sentiment_with_force_refresh(self):
        """Test market sentiment with force_refresh parameter"""
        response = self.client.get('/market-sentiment?force_refresh=true&currency=USD')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        data = result['data']
        
        assert 'currency' in data
        assert data['currency'] == 'USD'
    
    def test_market_sentiment_cache_respects_currency(self):
        """Test that cache is converted to requested currency"""
        # First request (creates cache in USD)
        response1 = self.client.get('/market-sentiment?currency=USD')
        result1 = json.loads(response1.data)
        data1 = result1['data']
        
        # Second request in different currency (should convert cached data)
        response2 = self.client.get('/market-sentiment?currency=EUR')
        result2 = json.loads(response2.data)
        data2 = result2['data']
        
        assert data1['currency'] == 'USD'
        assert data2['currency'] == 'EUR'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
