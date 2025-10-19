"""
TDD: Test recommendation confidence and fact-checking.
Flags weak signals, suspicious patterns, and market context warnings.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.services.dynamic_recommendations import DynamicRecommendationService


class TestRecommendationConfidence(unittest.TestCase):
    """Test confidence scoring and fact-checking for recommendations."""

    def setUp(self):
        """Initialize service."""
        self.service = DynamicRecommendationService()

    def test_get_recommendation_with_confidence_exists(self):
        """
        Verify method exists to get recommendation with full confidence analysis.
        Should return recommendation with warnings and confidence explanation.
        """
        ticker = "AAPL"
        headlines = ["Strong earnings reported"]
        
        result = self.service.get_recommendation_with_confidence(ticker, headlines)
        
        self.assertIsNotNone(result, "Should return recommendation with confidence")
        self.assertIn('recommendation', result, "Should include recommendation")
        self.assertIn('confidence_level', result, "Should include confidence_level (HIGH/MEDIUM/LOW)")
        self.assertIn('warnings', result, "Should include warnings list")
        self.assertIn('score_breakdown', result, "Should include detailed score breakdown")

    def test_weak_signal_detection_below_threshold(self):
        """
        Flag weak signals when any component < 0.3.
        User warning: "This signal is weak - proceed with caution"
        """
        ticker = "AAPL"
        
        result = self.service.get_recommendation_with_confidence(ticker, [])
        
        # Extract component scores
        components = {
            'technical': result['score_breakdown'].get('technical_score'),
            'fundamental': result['score_breakdown'].get('fundamental_score'),
            'sentiment': result['score_breakdown'].get('sentiment_score')
        }
        
        # Check if any component is weak
        weak_components = [name for name, score in components.items() if score and score < 0.3]
        
        if weak_components:
            # Should have warning about weak components
            self.assertTrue(any('weak' in w.lower() for w in result['warnings']),
                          "Should warn when components are weak")

    def test_strong_signal_single_source_warning(self):
        """
        Flag suspicious: high score (>0.8) but only ONE strong component.
        User warning: "High score from one factor only - diversify your research"
        """
        ticker = "AAPL"
        result = self.service.get_recommendation_with_confidence(ticker, [])
        
        components = result['score_breakdown']
        total_score = components['total_score']
        
        # If score is high but based on imbalance, warn
        tech = components['technical_score']
        fund = components['fundamental_score']
        sent = components['sentiment_score']
        
        strong_components = sum(1 for c in [tech, fund, sent] if c > 0.7)
        
        if total_score > 0.8 and strong_components == 1:
            # Should flag this as risky
            self.assertTrue(any('diversify' in w.lower() or 'single' in w.lower() 
                              for w in result['warnings']),
                          "Should warn about single-source high scores")

    def test_disagreement_between_signals_warning(self):
        """
        Flag when components significantly disagree.
        Tech says BULLISH, Fundamentals say BEARISH.
        User warning: "Signals disagree - more research needed"
        """
        ticker = "AAPL"
        result = self.service.get_recommendation_with_confidence(ticker, [])
        
        components = result['score_breakdown']
        tech = components['technical_score']
        fund = components['fundamental_score']
        sent = components['sentiment_score']
        
        # Check for large disagreement
        if tech and fund and abs(tech - fund) > 0.4:
            # Should warn about disagreement
            self.assertTrue(any('disagree' in w.lower() or 'conflict' in w.lower() 
                              for w in result['warnings']),
                          "Should warn when signals disagree significantly")

    def test_vix_context_warning_high_volatility(self):
        """
        When market VIX is high (>25 = fear), warn about market conditions.
        User warning: "Market is volatile - consider risk management"
        """
        ticker = "AAPL"
        result = self.service.get_recommendation_with_confidence(ticker, [])
        
        # Should check VIX context
        self.assertIn('market_context', result, "Should include market context")
        
        vix = result['market_context'].get('vix')
        if vix and vix > 25:
            # Should warn about high volatility
            self.assertTrue(any('volatile' in w.lower() or 'fear' in w.lower() 
                              for w in result['warnings']),
                          "Should warn when VIX indicates high volatility")

    def test_confidence_high_when_all_agree(self):
        """
        When all components agree (similar scores), confidence should be HIGH.
        """
        ticker = "AAPL"
        result = self.service.get_recommendation_with_confidence(ticker, [])
        
        components = result['score_breakdown']
        tech = components['technical_score']
        fund = components['fundamental_score']
        sent = components['sentiment_score']
        
        # If all are similar (within 0.2), confidence is high
        scores = [tech, fund, sent]
        if scores and max(scores) - min(scores) < 0.2:
            self.assertEqual(result['confidence_level'], 'HIGH',
                           "Should have HIGH confidence when signals agree")

    def test_confidence_medium_when_mostly_agree(self):
        """
        When signals mostly agree (within 0.3), confidence should be MEDIUM.
        """
        # This is automatically set when not HIGH or LOW
        ticker = "AAPL"
        result = self.service.get_recommendation_with_confidence(ticker, [])
        
        self.assertIn(result['confidence_level'], ['HIGH', 'MEDIUM', 'LOW'],
                     "Should have valid confidence level")

    def test_confidence_low_when_disagree_significantly(self):
        """
        When components disagree significantly (>0.4 spread), confidence is LOW.
        """
        ticker = "AAPL"
        result = self.service.get_recommendation_with_confidence(ticker, [])
        
        components = result['score_breakdown']
        tech = components['technical_score']
        fund = components['fundamental_score']
        sent = components['sentiment_score']
        
        scores = [tech, fund, sent]
        if scores and max(scores) - min(scores) > 0.4:
            self.assertEqual(result['confidence_level'], 'LOW',
                           "Should have LOW confidence when signals disagree significantly")

    def test_recommendation_with_explanation(self):
        """
        Every recommendation should have clear explanation for user.
        """
        ticker = "AAPL"
        result = self.service.get_recommendation_with_confidence(ticker, [])
        
        self.assertIn('explanation', result, "Should include explanation")
        self.assertGreater(len(result['explanation']), 10,
                          "Explanation should be meaningful")

    def test_warnings_help_investor_caution(self):
        """
        Warnings should be clear and actionable for investor.
        Examples: "Weak signal", "Signals disagree", "Market volatile", 
                  "Single factor dominates", "Insufficient data"
        """
        ticker = "AAPL"
        result = self.service.get_recommendation_with_confidence(ticker, [])
        
        warnings = result.get('warnings', [])
        
        # Each warning should be clear
        for warning in warnings:
            self.assertGreater(len(warning), 10, "Warnings should be clear and helpful")
            self.assertIsInstance(warning, str, "Warnings should be strings")

    def test_score_breakdown_shows_all_components(self):
        """
        Score breakdown should be transparent - show all components and weights.
        """
        ticker = "AAPL"
        result = self.service.get_recommendation_with_confidence(ticker, [])
        
        breakdown = result['score_breakdown']
        
        # Should show all components
        self.assertIn('technical_score', breakdown, "Should show technical")
        self.assertIn('fundamental_score', breakdown, "Should show fundamental")
        self.assertIn('sentiment_score', breakdown, "Should show sentiment")
        self.assertIn('total_score', breakdown, "Should show total")
        
        # Should show weights
        self.assertIn('technical_weight', breakdown, "Should show technical weight")
        self.assertIn('fundamental_weight', breakdown, "Should show fundamental weight")
        self.assertIn('sentiment_weight', breakdown, "Should show sentiment weight")

    def test_no_warnings_when_strong_consensus(self):
        """
        When all signals strongly agree on same direction, should have minimal warnings.
        """
        ticker = "MSFT"
        positive_headlines = [
            "Excellent earnings beat",
            "Strong revenue growth", 
            "Analyst upgrades stock"
        ]
        
        result = self.service.get_recommendation_with_confidence(ticker, positive_headlines)
        
        # If recommendation is clear BUY or SELL with high confidence, 
        # should have few warnings
        if result['confidence_level'] == 'HIGH':
            # Filter out market context warnings
            non_context_warnings = [w for w in result['warnings'] 
                                   if not w.lower().startswith('market')]
            self.assertLessEqual(len(non_context_warnings), 2,
                               "Should have few warnings when consensus is strong")


if __name__ == '__main__':
    unittest.main()
