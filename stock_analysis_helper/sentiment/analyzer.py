"""Sentiment Analyzer for analyzing market sentiment from text"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, List, Optional


class SentimentAnalyzer:
    """Analyzes sentiment from news articles and social media"""
    
    def __init__(self):
        """Initialize sentiment analyzer"""
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        scores = self.vader.polarity_scores(text)
        
        # Determine overall sentiment
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = "positive"
        elif compound <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "sentiment": sentiment,
            "positive": scores['pos'],
            "negative": scores['neg'],
            "neutral": scores['neu'],
            "compound": scores['compound']
        }
    
    def analyze_multiple(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment of multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment analysis results
        """
        return [self.analyze_text(text) for text in texts]
    
    def aggregate_sentiment(self, texts: List[str]) -> Dict:
        """
        Aggregate sentiment from multiple texts
        
        Args:
            texts: List of texts
            
        Returns:
            Aggregated sentiment scores
        """
        if not texts:
            return {
                "overall_sentiment": "neutral",
                "average_compound": 0.0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "total_texts": 0
            }
        
        results = self.analyze_multiple(texts)
        
        positive_count = sum(1 for r in results if r['sentiment'] == 'positive')
        negative_count = sum(1 for r in results if r['sentiment'] == 'negative')
        neutral_count = sum(1 for r in results if r['sentiment'] == 'neutral')
        
        avg_compound = sum(r['compound'] for r in results) / len(results)
        
        # Determine overall sentiment
        if avg_compound >= 0.05:
            overall = "positive"
        elif avg_compound <= -0.05:
            overall = "negative"
        else:
            overall = "neutral"
        
        return {
            "overall_sentiment": overall,
            "average_compound": avg_compound,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "total_texts": len(texts),
            "positive_ratio": positive_count / len(texts) if texts else 0,
            "negative_ratio": negative_count / len(texts) if texts else 0
        }
    
    def analyze_for_symbol(self, symbol: str, news_texts: List[str]) -> Dict:
        """
        Analyze sentiment for a specific symbol
        
        Args:
            symbol: Stock/crypto symbol
            news_texts: List of news articles or texts
            
        Returns:
            Sentiment analysis for the symbol
        """
        aggregated = self.aggregate_sentiment(news_texts)
        
        return {
            "symbol": symbol,
            **aggregated
        }
