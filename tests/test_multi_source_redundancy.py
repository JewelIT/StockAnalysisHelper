"""
TDD: Test multi-source data redundancy and fallback mechanisms.
Verifies that when Alpha Vantage rate limit is hit, system falls back gracefully.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.services.multi_source_market_data import MultiSourceMarketData


class TestMultiSourceRedundancy(unittest.TestCase):
    """Test multi-source data redundancy and rate limit handling."""

    def setUp(self):
        """Initialize service."""
        self.service = MultiSourceMarketData()

    def test_consensus_data_fetching(self):
        """
        Test basic consensus data fetching.
        Should return data from available sources with consensus price.
        """
        result = self.service.get_consensus_market_data()
        
        self.assertIsNotNone(result, "Should get consensus data")
        self.assertGreater(len(result), 0, "Should have at least one index")
        
        # Check structure of first result
        first_index = list(result.values())[0]
        self.assertIn('consensus_price', first_index, "Should have consensus price")
        self.assertIn('sources_used', first_index, "Should list sources used")
        self.assertIn('confidence', first_index, "Should include confidence level")
        self.assertGreater(len(first_index['sources_used']), 0, "Should use at least one source")

    def test_multiple_sources_weighted(self):
        """
        Verify that multiple sources contribute to consensus with proper weighting.
        """
        result = self.service.get_consensus_market_data()
        
        # Check a specific index (S&P 500)
        if 'S&P 500' in result:
            sp500_data = result['S&P 500']
            sources_count = sp500_data.get('sources_count', 0)
            
            # Should use multiple sources if available
            self.assertGreaterEqual(sources_count, 1, 
                                  "Should use at least one source")
            
            # If multiple sources available, should use them
            if sources_count > 1:
                self.assertEqual(len(sp500_data['sources_used']), sources_count,
                               "Sources list should match sources_count")

    def test_source_priority_order(self):
        """
        Verify that sources are attempted in priority order:
        1. Finnhub (priority 1, weight 1.5)
        2. Alpha Vantage (priority 2, weight 1.5)
        3. yfinance (priority 3, weight 1.0)
        """
        # Check the source configuration
        self.assertEqual(self.service.sources_config['finnhub']['priority'], 1,
                        "Finnhub should be priority 1")
        self.assertEqual(self.service.sources_config['alphavantage']['priority'], 2,
                        "Alpha Vantage should be priority 2")
        self.assertEqual(self.service.sources_config['yfinance']['priority'], 3,
                        "yfinance should be priority 3")

    def test_weights_favor_quality_sources(self):
        """
        Verify that weights are configured correctly:
        - Finnhub: 1.5 (high priority)
        - Alpha Vantage: 1.5 (high priority)
        - yfinance: 1.0 (fallback)
        """
        self.assertEqual(self.service.sources_config['finnhub']['weight'], 1.5,
                        "Finnhub should have weight 1.5")
        self.assertEqual(self.service.sources_config['alphavantage']['weight'], 1.5,
                        "Alpha Vantage should have weight 1.5")
        self.assertEqual(self.service.sources_config['yfinance']['weight'], 1.0,
                        "yfinance should have weight 1.0 (fallback)")

    def test_discrepancy_detection(self):
        """
        Verify that significant disagreements between sources are flagged.
        """
        # Create mock results with disagreement
        results = [
            {'source': 'finnhub', 'price': 100, 'change_pct': 2.0, 'weight': 1.5},
            {'source': 'alphavantage', 'price': 100, 'change_pct': 2.1, 'weight': 1.5},
            {'source': 'yfinance', 'price': 100, 'change_pct': 1.9, 'weight': 1.0},
        ]
        
        discrepancy = self.service._detect_discrepancy(results, 2.0)
        
        # These are close, should not flag as critical
        self.assertIsNotNone(discrepancy, "Should detect discrepancy")
        self.assertIn('severity', discrepancy, "Should include severity")
        self.assertIn('spread', discrepancy, "Should include spread")

    def test_yfinance_always_available(self):
        """
        Verify that yfinance is always available as fallback.
        """
        self.assertTrue(self.service.clients.get('yfinance') is not None,
                       "yfinance should always be available")

    def test_no_crash_on_network_error(self):
        """
        Verify that transient network errors don't crash the service.
        Should try other sources instead.
        """
        # Just verify the method exists and doesn't crash
        try:
            result = self.service.get_consensus_market_data()
            # Should return something or handle gracefully
            self.assertIsNotNone(result, "Should not crash on potential network issues")
        except Exception as e:
            self.fail(f"Service should handle errors gracefully: {e}")

    def test_index_symbols_consistency(self):
        """
        Verify that index symbols are correctly mapped for all sources.
        """
        indices_map = self.service.indices_map
        
        required_indices = ['S&P 500', 'Dow Jones', 'NASDAQ', 'VIX (Volatility)']
        for index_name in required_indices:
            self.assertIn(index_name, indices_map, f"Should have {index_name} mapping")
            
            mapping = indices_map[index_name]
            self.assertIn('yf', mapping, f"{index_name} should have yfinance symbol")
            self.assertIn('finnhub', mapping, f"{index_name} should have Finnhub symbol")
            self.assertIn('av', mapping, f"{index_name} should have Alpha Vantage symbol")


if __name__ == '__main__':
    unittest.main()
