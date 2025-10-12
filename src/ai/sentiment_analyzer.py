"""
Sentiment Analysis Module using FinBERT
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class SentimentAnalyzer:
    def __init__(self, model_name="yiyanghkust/finbert-tone"):
        """Initialize FinBERT model"""
        print(f"Loading FinBERT model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.labels = ['positive', 'neutral', 'negative']
        print("✅ Model loaded successfully")
    
    def analyze(self, text):
        """Analyze sentiment of text"""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        positive_prob = predictions[0][0].item()
        neutral_prob = predictions[0][1].item()
        negative_prob = predictions[0][2].item()
        
        label_index = predictions.argmax().item()
        sentiment_label = self.labels[label_index]
        
        # Composite score: 0 = very negative, 0.5 = neutral, 1 = very positive
        sentiment_score = (positive_prob - negative_prob + 1) / 2
        
        return {
            'label': sentiment_label,
            'score': sentiment_score,
            'positive': positive_prob,
            'neutral': neutral_prob,
            'negative': negative_prob
        }
