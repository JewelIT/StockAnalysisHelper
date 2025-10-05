"""Tests for sentiment analysis module"""

import unittest
from stock_analysis_helper.sentiment import SentimentAnalyzer


class TestSentimentAnalyzer(unittest.TestCase):
    """Test cases for SentimentAnalyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = SentimentAnalyzer()
    
    def test_analyze_positive_text(self):
        """Test analyzing positive text"""
        result = self.analyzer.analyze_text("Apple stock surges on strong earnings report")
        
        self.assertIn('sentiment', result)
        self.assertIn('compound', result)
        self.assertIn(result['sentiment'], ['positive', 'neutral'])
    
    def test_analyze_negative_text(self):
        """Test analyzing negative text"""
        result = self.analyzer.analyze_text("Market crashes as investors panic sell")
        
        self.assertIn('sentiment', result)
        self.assertIn(result['sentiment'], ['negative', 'neutral'])
    
    def test_analyze_neutral_text(self):
        """Test analyzing neutral text"""
        result = self.analyzer.analyze_text("The market opened today")
        
        self.assertIn('sentiment', result)
        self.assertEqual(result['sentiment'], 'neutral')
    
    def test_analyze_multiple(self):
        """Test analyzing multiple texts"""
        texts = [
            "Great earnings report!",
            "Stock price falling",
            "Market remains stable"
        ]
        
        results = self.analyzer.analyze_multiple(texts)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIn('sentiment', result)
            self.assertIn('compound', result)
    
    def test_aggregate_sentiment(self):
        """Test aggregating sentiment"""
        texts = [
            "Excellent performance!",
            "Strong growth potential",
            "Market concerns remain"
        ]
        
        aggregated = self.analyzer.aggregate_sentiment(texts)
        
        self.assertIn('overall_sentiment', aggregated)
        self.assertIn('average_compound', aggregated)
        self.assertIn('positive_count', aggregated)
        self.assertIn('negative_count', aggregated)
        self.assertIn('total_texts', aggregated)
        self.assertEqual(aggregated['total_texts'], 3)
    
    def test_empty_texts(self):
        """Test with empty text list"""
        aggregated = self.analyzer.aggregate_sentiment([])
        
        self.assertEqual(aggregated['overall_sentiment'], 'neutral')
        self.assertEqual(aggregated['total_texts'], 0)


if __name__ == '__main__':
    unittest.main()
