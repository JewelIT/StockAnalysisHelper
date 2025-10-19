"""
TDD: Test consolidated scoring (technical + fundamental).
This ensures that when both scores are combined, results make sense.
"""

import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.services.dynamic_recommendations import DynamicRecommendationService


class TestConsolidatedScoring(unittest.TestCase):
    """Test consolidated technical + fundamental scoring."""

    def setUp(self):
        """Initialize service."""
        self.service = DynamicRecommendationService()

    def test_get_consolidated_score_exists(self):
        """
        Verify method exists and can be called.
        Should return dict with 'score' (0-1) and component breakdown.
        """
        ticker = "AAPL"
        result = self.service.get_consolidated_score(ticker)
        
        self.assertIsNotNone(result, "Should return a result")
        self.assertIn('total_score', result, "Should include total_score")
        self.assertIn('technical_score', result, "Should include technical_score")
        self.assertIn('fundamental_score', result, "Should include fundamental_score")
        
        # All scores should be 0-1
        self.assertGreaterEqual(result['total_score'], 0.0)
        self.assertLessEqual(result['total_score'], 1.0)
        self.assertGreaterEqual(result['technical_score'], 0.0)
        self.assertLessEqual(result['technical_score'], 1.0)
        self.assertGreaterEqual(result['fundamental_score'], 0.0)
        self.assertLessEqual(result['fundamental_score'], 1.0)

    def test_scoring_weights_are_applied(self):
        """
        Verify that weights are applied correctly.
        Formula should be: 0.7*technical + 0.3*fundamental
        """
        ticker = "AAPL"
        result = self.service.get_consolidated_score(ticker)
        
        tech_score = result['technical_score']
        fund_score = result['fundamental_score']
        total_score = result['total_score']
        
        # Calculate expected score
        expected = (0.7 * tech_score) + (0.3 * fund_score)
        
        # Allow small rounding difference
        self.assertAlmostEqual(total_score, expected, places=2,
                              msg=f"Score {total_score} should equal 0.7*{tech_score} + 0.3*{fund_score} = {expected}")

    def test_high_technical_low_fundamental(self):
        """
        Test: Strong momentum/technical but weak fundamentals.
        Should pull score down from pure technical score, but not as low as fundamentals alone.
        """
        # This is a real scenario - stock with good momentum but weak balance sheet
        ticker = "TSLA"  # Often has strong momentum, variable fundamentals
        result = self.service.get_consolidated_score(ticker)
        
        tech = result['technical_score']
        fund = result['fundamental_score']
        total = result['total_score']
        
        # Should be between technical and fundamental
        if tech != fund:  # If they differ
            self.assertLess(total, tech + 0.01, "Total should be pulled down from pure technical")
            self.assertGreater(total, fund - 0.01, "Total should be higher than pure fundamental")

    def test_scoring_consistency(self):
        """
        Repeated calls should give consistent results
        (small variance allowed due to API updates).
        """
        ticker = "MSFT"
        result1 = self.service.get_consolidated_score(ticker)
        result2 = self.service.get_consolidated_score(ticker)
        
        self.assertAlmostEqual(result1['total_score'], result2['total_score'], delta=0.05,
                              msg="Repeated calls should give consistent scores")

    def test_score_breakdown_included(self):
        """
        Result should include detailed breakdown for transparency.
        """
        ticker = "AAPL"
        result = self.service.get_consolidated_score(ticker)
        
        # Should have components for transparency
        self.assertIn('technical_factors', result,
                     "Should include technical factors breakdown")
        self.assertIn('fundamental_factors', result,
                     "Should include fundamental factors breakdown")

    def test_quality_filters_respected(self):
        """
        Quality filters should prevent scoring penny stocks or invalid tickers.
        Should return None for data that fails quality checks.
        """
        # Try a ticker that might not have data or is invalid
        ticker = "INVALID_TICKER_XYZ"
        result = self.service.get_consolidated_score(ticker)
        
        # Should handle gracefully - either None or valid score
        if result is not None:
            # If it returns something, it should be valid
            self.assertGreaterEqual(result.get('total_score', 0.5), 0.0)
            self.assertLessEqual(result.get('total_score', 0.5), 1.0)
        # If None, that's also acceptable (quality filter rejected it)

    def test_multiple_tickers_scoring(self):
        """
        Test scoring multiple stocks to verify consistency across tickers.
        """
        tickers = ["AAPL", "MSFT", "GE"]
        results = {}
        
        for ticker in tickers:
            result = self.service.get_consolidated_score(ticker)
            self.assertIsNotNone(result, f"Should get result for {ticker}")
            results[ticker] = result['total_score']
        
        # All should be valid scores
        for ticker, score in results.items():
            self.assertGreaterEqual(score, 0.0, f"{ticker} score should be >= 0")
            self.assertLessEqual(score, 1.0, f"{ticker} score should be <= 1")


if __name__ == '__main__':
    unittest.main()
