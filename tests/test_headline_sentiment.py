"""
TDD: Test headline sentiment analysis service.
Uses HuggingFace DistilBERT for local sentiment inference.
"""

import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.services.headline_sentiment_service import HeadlineSentimentService


class TestHeadlineSentiment(unittest.TestCase):
    """Test headline sentiment analysis."""

    def setUp(self):
        """Initialize service."""
        self.service = HeadlineSentimentService()

    def test_service_initializes(self):
        """Verify sentiment model initializes successfully."""
        self.assertIsNotNone(self.service.sentiment_pipeline,
                           "Sentiment pipeline should initialize")

    def test_analyze_positive_headline(self):
        """
        Test that positive news is correctly classified.
        """
        positive_headlines = [
            "Apple reports record earnings and beats expectations",
            "Microsoft stock soars on strong cloud growth",
            "Tech stocks surge on optimistic economic outlook",
        ]
        
        for headline in positive_headlines:
            result = self.service.analyze_headline(headline)
            
            self.assertIsNotNone(result, f"Should analyze: {headline}")
            self.assertEqual(result['sentiment'], 'POSITIVE',
                           f"Should be positive: {headline}")
            self.assertGreaterEqual(result['sentiment_score'], 0.7,
                                  f"Score should be high for positive headline")

    def test_analyze_negative_headline(self):
        """
        Test that negative news is correctly classified.
        """
        negative_headlines = [
            "Tesla cuts prices amid falling demand",
            "Bank stock plunges on loan losses",
            "Tech sector faces worst quarter in years",
        ]
        
        for headline in negative_headlines:
            result = self.service.analyze_headline(headline)
            
            self.assertIsNotNone(result, f"Should analyze: {headline}")
            self.assertEqual(result['sentiment'], 'NEGATIVE',
                           f"Should be negative: {headline}")
            self.assertLessEqual(result['sentiment_score'], 0.3,
                               f"Score should be low for negative headline")

    def test_analyze_neutral_headline(self):
        """
        Test that neutral news gets intermediate scores.
        """
        neutral_headlines = [
            "Company announces quarterly earnings",
            "New product release scheduled for next month",
            "Analyst maintains stock rating at hold",
        ]
        
        for headline in neutral_headlines:
            result = self.service.analyze_headline(headline)
            
            if result:  # Might be classified as slightly positive/negative
                self.assertIsNotNone(result['sentiment_score'])
                self.assertGreaterEqual(result['sentiment_score'], 0.0)
                self.assertLessEqual(result['sentiment_score'], 1.0)

    def test_sentiment_score_range(self):
        """
        Verify sentiment score is always 0-1 for all headlines.
        """
        test_headlines = [
            "This is amazing news",
            "This is terrible news",
            "This is normal news",
            "Stock rises on positive results",
            "Stock falls on concerns",
        ]
        
        for headline in test_headlines:
            result = self.service.analyze_headline(headline)
            if result:
                self.assertGreaterEqual(result['sentiment_score'], 0.0,
                                      f"Score too low: {headline}")
                self.assertLessEqual(result['sentiment_score'], 1.0,
                                   f"Score too high: {headline}")

    def test_batch_analysis(self):
        """
        Test analyzing multiple headlines together.
        """
        headlines = [
            "Strong Q3 results exceed forecasts",
            "Company cuts guidance and lays off workers",
            "New partnership announced",
            "Accounting irregularities discovered",
            "Market analyst raises price target",
        ]
        
        result = self.service.analyze_headlines_batch(headlines)
        
        self.assertIsNotNone(result, "Should return batch result")
        self.assertEqual(result['count'], 5, "Should analyze all 5 headlines")
        self.assertGreaterEqual(result['average_sentiment'], 0.0)
        self.assertLessEqual(result['average_sentiment'], 1.0)
        self.assertEqual(len(result['results']), 5, "Should include all results")

    def test_batch_consensus_bullish(self):
        """
        Test that consensus is 'BULLISH' when majority positive.
        """
        positive_headlines = [
            "Excellent earnings beat",
            "Stock soars on good news",
            "Market optimistic about future",
            "Revenue growth accelerates",
        ]
        
        result = self.service.analyze_headlines_batch(positive_headlines)
        
        self.assertEqual(result['consensus'], 'BULLISH',
                        "Should be bullish when mostly positive")
        self.assertGreater(result['positive_ratio'], 50,
                          "Should have positive ratio > 50%")

    def test_batch_consensus_bearish(self):
        """
        Test that consensus is 'BEARISH' when majority negative.
        """
        negative_headlines = [
            "Worse than expected earnings",
            "Stock plunges on bad news",
            "Market concerned about future",
            "Revenue decline continues",
        ]
        
        result = self.service.analyze_headlines_batch(negative_headlines)
        
        self.assertEqual(result['consensus'], 'BEARISH',
                        "Should be bearish when mostly negative")
        self.assertGreater(result['negative_ratio'], 50,
                          "Should have negative ratio > 50%")

    def test_stock_sentiment_score(self):
        """
        Test getting sentiment score for a stock.
        """
        headlines = [
            "Microsoft reports strong cloud growth",
            "Azure adoption accelerates",
            "Positive analyst outlook on AI investments",
        ]
        
        score = self.service.get_sentiment_score_for_stock("MSFT", headlines)
        
        self.assertIsNotNone(score, "Should return sentiment score")
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        self.assertGreater(score, 0.5, "Should be positive for positive headlines")

    def test_empty_headlines(self):
        """
        Test handling of empty input.
        """
        result = self.service.analyze_headline("")
        self.assertIsNone(result, "Should handle empty headline")
        
        batch_result = self.service.analyze_headlines_batch([])
        self.assertEqual(batch_result['count'], 0, "Should handle empty batch")
        self.assertEqual(batch_result['average_sentiment'], 0.5,
                        "Should return neutral score for empty input")

    def test_model_consistency(self):
        """
        Same headline should give consistent results.
        """
        headline = "Strong earnings report released"
        
        result1 = self.service.analyze_headline(headline)
        result2 = self.service.analyze_headline(headline)
        
        self.assertAlmostEqual(result1['sentiment_score'],
                              result2['sentiment_score'],
                              places=3,
                              msg="Same headline should give consistent scores")


if __name__ == '__main__':
    unittest.main()
