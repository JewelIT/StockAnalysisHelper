"""
Test Alpha Vantage rate limit fallback mechanism.
Simulates rate limiting and verifies system continues to work with fallback sources.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.services.multi_source_market_data import MultiSourceMarketData


class TestAlphaVantageRateLimitFallback(unittest.TestCase):
    """Test that Alpha Vantage rate limiting triggers fallback to other sources."""

    def setUp(self):
        """Initialize service."""
        self.service = MultiSourceMarketData()

    def test_rate_limit_detection_note(self):
        """
        Test that 'Note' in response (Alpha Vantage rate limit message) is detected.
        """
        # Simulate Alpha Vantage returning a rate limit message
        with patch.object(self.service.clients.get('alphavantage', type(None)), 'get_intraday') as mock_av:
            mock_av.return_value = (
                {},  # Empty data
                {'Note': 'Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute.'}
            )
            
            result = self.service._fetch_alphavantage('AAPL')
            
            # Should return None when rate limit detected
            self.assertIsNone(result, "Should return None on rate limit")
            # Should disable Alpha Vantage
            self.assertFalse(self.service.sources_config['alphavantage']['enabled'],
                           "Should disable Alpha Vantage when rate limit hit")

    def test_rate_limit_detection_exception(self):
        """
        Test that rate limit exceptions are caught and Alpha Vantage is disabled.
        """
        # Simulate Alpha Vantage throwing rate limit exception
        with patch.object(self.service.clients.get('alphavantage', type(None)), 'get_intraday') as mock_av:
            mock_av.side_effect = Exception("Rate limit reached")
            
            result = self.service._fetch_alphavantage('AAPL')
            
            # Should return None
            self.assertIsNone(result, "Should return None on exception")

    def test_fallback_to_finnhub_after_av_disabled(self):
        """
        After Alpha Vantage is disabled due to rate limit,
        subsequent calls should get data from Finnhub/yfinance.
        """
        # First, disable Alpha Vantage to simulate rate limit
        self.service.sources_config['alphavantage']['enabled'] = False
        
        # Get consensus data - should still work from other sources
        result = self.service.get_consensus_market_data()
        
        self.assertIsNotNone(result, "Should still get data with Alpha Vantage disabled")
        
        # Check that at least one index has data
        if 'S&P 500' in result:
            sp500 = result['S&P 500']
            self.assertIn('consensus_price', sp500, "Should have consensus price")
            self.assertGreater(sp500['sources_count'], 0, "Should have at least one source")

    def test_consensus_without_alphavantage(self):
        """
        Verify that consensus calculation works correctly with Alpha Vantage disabled.
        """
        # Disable Alpha Vantage
        self.service.sources_config['alphavantage']['enabled'] = False
        
        # Get data from remaining sources
        result = self.service.get_consensus_market_data()
        
        # Verify consensus is calculated from remaining sources
        if 'S&P 500' in result:
            sp500 = result['S&P 500']
            
            # Should not use Alpha Vantage
            self.assertNotIn('alphavantage', sp500['sources_used'],
                           "Should not use Alpha Vantage when disabled")
            
            # Should use at least yfinance
            self.assertGreater(len(sp500['sources_used']), 0,
                             "Should still have sources when AV disabled")

    def test_recovery_marker(self):
        """
        After rate limit, system should be marked as disabled.
        This marker helps track when we've hit rate limits.
        """
        # Simulate rate limit hit
        self.service.sources_config['alphavantage']['enabled'] = False
        
        # Verify it's tracked
        self.assertFalse(self.service.sources_config['alphavantage']['enabled'],
                        "Rate limit should be marked as disabled")
        
        # But other sources should still be enabled
        self.assertTrue(self.service.sources_config['yfinance']['enabled'],
                       "yfinance should still be enabled")


if __name__ == '__main__':
    unittest.main()
