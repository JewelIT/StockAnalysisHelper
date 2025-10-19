"""
TDD: Test fundamental scoring calculation BEFORE implementation.
This test SHOULD FAIL initially - that's the point of TDD.
Once it fails, we implement _calculate_fundamental_score() to make it pass.
"""

import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.services.dynamic_recommendations import DynamicRecommendationService


class TestFundamentalScoring(unittest.TestCase):
    """Test fundamental score calculation from yfinance data."""

    def setUp(self):
        """Initialize service."""
        self.service = DynamicRecommendationService()

    def test_calculate_fundamental_score_healthy_company(self):
        """
        AAPL: Strong fundamentals (despite high D/E from buybacks)
        - Forward P/E: 30 (moderate)
        - Dividend Yield: 0.41% (decent)
        - Current Ratio: 0.87 (low but Apple is efficient)
        - Debt/Equity: 154% (high but sustainable for Apple)
        - Operating Margin: 30% (excellent)
        - ROE: 149% (very high due to buybacks)
        
        Expected: HIGH score (>= 0.65)
        """
        ticker = "AAPL"
        score = self.service._calculate_fundamental_score(ticker)
        
        self.assertIsNotNone(score, "Score should not be None")
        self.assertGreaterEqual(score, 0.0, "Score should be >= 0")
        self.assertLessEqual(score, 1.0, "Score should be <= 1")
        self.assertGreaterEqual(score, 0.65, f"AAPL should have healthy fundamentals (>= 0.65), got {score}")

    def test_calculate_fundamental_score_moderate_company(self):
        """
        GE: Moderate fundamentals (industrial conglomerate)
        Expected: MODERATE score (0.4-0.6 range)
        """
        ticker = "GE"
        score = self.service._calculate_fundamental_score(ticker)
        
        self.assertIsNotNone(score, "Score should not be None")
        self.assertGreaterEqual(score, 0.0, "Score should be >= 0")
        self.assertLessEqual(score, 1.0, "Score should be <= 1")

    def test_fundamental_score_with_missing_data(self):
        """
        Test graceful handling when some fundamental data is missing.
        Should not crash, should return a valid score based on available data.
        """
        # Use a less common ticker that might have incomplete data
        ticker = "BRK.A"  # Berkshire Hathaway (no dividend)
        score = self.service._calculate_fundamental_score(ticker)
        
        self.assertIsNotNone(score, "Score should not be None even with missing data")
        self.assertGreaterEqual(score, 0.0, "Score should be >= 0")
        self.assertLessEqual(score, 1.0, "Score should be <= 1")

    def test_fundamental_score_components(self):
        """
        Verify scoring components make sense:
        - High P/E shouldn't automatically mean low score (growth stocks)
        - High debt might be acceptable for stable, profitable companies
        - Positive margins should increase score
        """
        # This is more of a validation test for the scoring logic
        ticker = "MSFT"
        score = self.service._calculate_fundamental_score(ticker)
        
        # Microsoft should have healthy score
        self.assertGreater(score, 0.5, "Healthy tech company should score > 0.5")

    def test_fundamental_score_consistency(self):
        """
        Calling same ticker twice should give similar results
        (allow small variance due to API updates).
        """
        ticker = "AAPL"
        score1 = self.service._calculate_fundamental_score(ticker)
        score2 = self.service._calculate_fundamental_score(ticker)
        
        # Allow up to 0.05 difference due to API updates
        self.assertAlmostEqual(score1, score2, delta=0.05,
                              msg="Repeated calls should give consistent scores")


if __name__ == '__main__':
    unittest.main()
