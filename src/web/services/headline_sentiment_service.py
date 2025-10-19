import logging
from typing import Dict, List, Optional
from transformers import pipeline

logger = logging.getLogger(__name__)


class HeadlineSentimentService:
    def __init__(self):
        self.sentiment_pipeline = None
        self._init_sentiment_model()
    
    def _init_sentiment_model(self):
        try:
            self.sentiment_pipeline = pipeline(
                'sentiment-analysis',
                model='distilbert-base-uncased-finetuned-sst-2-english'
            )
            logger.info("Sentiment model initialized")
        except Exception as e:
            logger.error(f"Failed to init sentiment model: {e}")
            self.sentiment_pipeline = None
    
    def analyze_headline(self, headline: str) -> Optional[Dict]:
        if not headline or not self.sentiment_pipeline:
            return None
        
        try:
            text = headline[:200]
            result = self.sentiment_pipeline(text)
            
            if not result or len(result) == 0:
                return None
            
            sentiment_result = result[0]
            label = sentiment_result['label']
            score = sentiment_result['score']
            
            if label == 'POSITIVE':
                normalized = score
            else:
                normalized = 1 - score
            
            return {
                'headline': headline,
                'sentiment': label,
                'confidence': round(score, 3),
                'sentiment_score': round(normalized, 3)
            }
        except Exception as e:
            logger.warning(f"Failed to analyze: {e}")
            return None
    
    def analyze_headlines_batch(self, headlines: List[str]) -> Dict:
        if not headlines:
            return {
                'results': [],
                'average_sentiment': 0.5,
                'positive_ratio': 0,
                'negative_ratio': 0,
                'consensus': 'MIXED',
                'count': 0
            }
        
        results = []
        for headline in headlines:
            result = self.analyze_headline(headline)
            if result:
                results.append(result)
        
        if not results:
            return {
                'results': [],
                'average_sentiment': 0.5,
                'positive_ratio': 0,
                'negative_ratio': 0,
                'consensus': 'MIXED',
                'count': 0
            }
        
        sentiment_scores = [r['sentiment_score'] for r in results]
        average_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        positive_count = sum(1 for r in results if r['sentiment'] == 'POSITIVE')
        negative_count = sum(1 for r in results if r['sentiment'] == 'NEGATIVE')
        
        positive_ratio = (positive_count / len(results)) * 100
        negative_ratio = (negative_count / len(results)) * 100
        
        if average_sentiment >= 0.6:
            consensus = 'BULLISH'
        elif average_sentiment <= 0.4:
            consensus = 'BEARISH'
        else:
            consensus = 'MIXED'
        
        return {
            'results': results,
            'average_sentiment': round(average_sentiment, 3),
            'positive_ratio': round(positive_ratio, 1),
            'negative_ratio': round(negative_ratio, 1),
            'consensus': consensus,
            'count': len(results)
        }
    
    def get_sentiment_score_for_stock(self, ticker: str, headlines: List[str]) -> float:
        if not headlines:
            return 0.5
        
        analysis = self.analyze_headlines_batch(headlines)
        
        if analysis['count'] == 0:
            return 0.5
        
        logger.info(f"{ticker} sentiment: {analysis['consensus']}")
        return analysis['average_sentiment']
