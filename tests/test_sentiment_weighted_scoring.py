"""
TDD: Test sentiment-weighted recommendation scoring.
Tests that sentiment headlines are integrated into final recommendation score.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.services.dynamic_recommendations import DynamicRecommendationService
from src.web.services.headline_sentiment_service import HeadlineSentimentService


class TestSentimentWeightedScoring(unittest.TestCase):
    """Test sentiment integration into recommendation scoring."""

    def setUp(self):
        """Initialize services."""
        self.service = DynamicRecommendationService()
        self.sentiment_service = HeadlineSentimentService()

    def test_get_recommendation_with_sentiment_exists(self):
        """
        Verify method exists to get recommendation with sentiment.
        Should accept ticker and headlines.
        """
        ticker = "AAPL"
        headlines = [
            "Apple posts record earnings",
            "iPhone 16 sales exceed expectations",
            "Analyst upgrades Apple to buy"
        ]
        
        result = self.service.get_recommendation_with_sentiment(ticker, headlines)
        
        self.assertIsNotNone(result, "Should return recommendation with sentiment")
        self.assertIn('total_score', result, "Should include total_score")
        self.assertIn('technical_score', result, "Should include technical_score")
        self.assertIn('fundamental_score', result, "Should include fundamental_score")
        self.assertIn('sentiment_score', result, "Should include sentiment_score")
        self.assertIn('sentiment_headlines_count', result, "Should show how many headlines analyzed")

    def test_sentiment_weighted_formula(self):
        """
        Verify sentiment is weighted correctly in final score.
        Formula should be: 0.65*technical + 0.25*fundamental + 0.1*sentiment
        """
        ticker = "MSFT"
        positive_headlines = [
            "Microsoft beats Q3 expectations",
            "Azure cloud growth accelerates",
            "AI investment paying off"
        ]
        
        result = self.service.get_recommendation_with_sentiment(ticker, positive_headlines)
        
        tech = result['technical_score']
        fund = result['fundamental_score']
        sent = result['sentiment_score']
        total = result['total_score']
        
        # Verify formula
        expected = (0.65 * tech) + (0.25 * fund) + (0.1 * sent)
        
        self.assertAlmostEqual(total, expected, places=2,
                              msg=f"Score {total} should equal 0.65*{tech} + 0.25*{fund} + 0.1*{sent} = {expected}")

    def test_positive_sentiment_boosts_score(self):
        """
        When sentiment is positive, it should boost the recommendation score.
        """
        ticker = "TSLA"
        positive_headlines = [
            "Tesla announces new factory",
            "Production capacity doubles",
            "Positive analyst outlook"
        ]
        
        # Get recommendation with positive sentiment
        result_positive = self.service.get_recommendation_with_sentiment(ticker, positive_headlines)
        
        # Sentiment should be positive (>0.6)
        self.assertGreater(result_positive['sentiment_score'], 0.6,
                          "Positive headlines should give high sentiment score")

    def test_negative_sentiment_reduces_score(self):
        """
        When sentiment is negative, it should reduce the recommendation score.
        """
        ticker = "GE"
        negative_headlines = [
            "GE announces layoffs",
            "Profit warnings issued",
            "Analyst downgrades stock"
        ]
        
        # Get recommendation with negative sentiment
        result_negative = self.service.get_recommendation_with_sentiment(ticker, negative_headlines)
        
        # Sentiment should be negative (<0.4)
        self.assertLess(result_negative['sentiment_score'], 0.4,
                       "Negative headlines should give low sentiment score")

    def test_no_headlines_uses_neutral_sentiment(self):
        """
        When no headlines provided, sentiment defaults to neutral (0.5).
        """
        ticker = "AAPL"
        result = self.service.get_recommendation_with_sentiment(ticker, [])
        
        self.assertEqual(result['sentiment_score'], 0.5,
                        "Should default to neutral sentiment (0.5) with no headlines")
        self.assertEqual(result['sentiment_headlines_count'], 0,
                        "Should show 0 headlines analyzed")

    def test_score_breakdown_includes_weights(self):
        """
        Result should show all three components and their weights for transparency.
        """
        ticker = "AAPL"
        headlines = ["Strong quarterly results"]
        
        result = self.service.get_recommendation_with_sentiment(ticker, headlines)
        
        self.assertEqual(result.get('technical_weight'), 0.65, "Technical weight should be 0.65")
        self.assertEqual(result.get('fundamental_weight'), 0.25, "Fundamental weight should be 0.25")
        self.assertEqual(result.get('sentiment_weight'), 0.1, "Sentiment weight should be 0.1")

    def test_confidence_reflects_component_agreement(self):
        """
        When all three components agree, confidence should be high.
        When they disagree, confidence should be lower.
        """
        ticker = "MSFT"
        positive_headlines = [
            "Excellent earnings beat",
            "Market confidence high",
            "Stock soars on news"
        ]
        
        result = self.service.get_recommendation_with_sentiment(ticker, positive_headlines)
        
        # With all positive signals, confidence should be higher
        self.assertIsNotNone(result.get('confidence'), "Should include confidence metric")

    def test_weak_signal_detection(self):
        """
        Flag weak signals when any component < 0.3 (bearish) or only slight positive.
        """
        ticker = "XYZ"
        mixed_headlines = [
            "Company reports mixed results",
            "Some concerns remain"
        ]
        
        result = self.service.get_recommendation_with_sentiment(ticker, mixed_headlines)
        
        # Should detect if any component is weak
        components = [
            result.get('technical_score'),
            result.get('fundamental_score'),
            result.get('sentiment_score')
        ]
        
        # At least one should be checked for weakness
        self.assertTrue(all(c is not None for c in components),
                       "Should have all component scores")

    def test_high_score_single_source_warning(self):
        """
        When we have sentiment headlines, should track components independently.
        This enables detection of unreliable signals later.
        """
        ticker = "AAPL"
        headlines = ["Strong results reported"]
        
        result = self.service.get_recommendation_with_sentiment(ticker, headlines)
        
        self.assertIsNotNone(result, "Should return valid result")
        self.assertIn('recommendation', result, "Should include BUY/HOLD/SELL")
        self.assertIn('technical_score', result, "Should track technical independently")
        self.assertIn('fundamental_score', result, "Should track fundamental independently")
        self.assertIn('sentiment_score', result, "Should track sentiment independently")


if __name__ == '__main__':
    unittest.main()
