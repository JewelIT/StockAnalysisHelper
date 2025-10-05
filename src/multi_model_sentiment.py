"""
Multi-Model Sentiment Analyzer
Supports multiple HuggingFace models optimized for different text sources
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import numpy as np

class MultiModelSentimentAnalyzer:
    def __init__(self, model_type='finbert'):
        """
        Initialize sentiment analyzer with specified model
        
        Args:
            model_type: 'finbert' (default), 'twitter-financial', or 'general'
        """
        self.model_type = model_type
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        # Model configurations
        self.models = {
            'finbert': {
                'name': 'yiyanghkust/finbert-tone',
                'description': 'FinBERT - Best for financial news and formal text',
                'labels': {'positive': 'positive', 'neutral': 'neutral', 'negative': 'negative'}
            },
            'twitter-financial': {
                'name': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
                'description': 'Twitter-RoBERTa - Best for social media and informal text',
                'labels': {'positive': 'positive', 'neutral': 'neutral', 'negative': 'negative'}
            },
            'distilbert-financial': {
                'name': 'ProsusAI/finbert',
                'description': 'Alternative FinBERT - Good balance of speed and accuracy',
                'labels': {'positive': 'positive', 'neutral': 'neutral', 'negative': 'negative'}
            }
        }
        
        # Load the specified model
        self.load_model(model_type)
    
    def load_model(self, model_type):
        """Load a specific model from HuggingFace"""
        if model_type not in self.models:
            print(f"⚠️  Unknown model type '{model_type}', defaulting to 'finbert'")
            model_type = 'finbert'
        
        self.model_type = model_type
        model_config = self.models[model_type]
        model_name = model_config['name']
        
        print(f"📥 Loading {model_type} model: {model_name}")
        print(f"   {model_config['description']}")
        
        try:
            # Load model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Create pipeline for easier inference
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            print(f"✅ {model_type} model loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading {model_type} model: {e}")
            raise
    
    def analyze(self, text, max_length=512):
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            max_length: Maximum token length
            
        Returns:
            Dict with 'label', 'score', 'positive', 'neutral', 'negative'
        """
        if not text or len(text.strip()) == 0:
            return {
                'label': 'neutral',
                'score': 0.5,
                'positive': 0.33,
                'neutral': 0.34,
                'negative': 0.33
            }
        
        try:
            # Truncate text if too long
            text = text[:max_length * 4]  # Rough character estimate
            
            # Get predictions
            results = self.pipeline(text, truncation=True, max_length=max_length)
            
            # Get full probability distribution
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length)
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                probs = probs[0].cpu().numpy()
            
            # Map to standard labels (positive, neutral, negative)
            label_map = {
                'LABEL_0': 'negative',
                'LABEL_1': 'neutral', 
                'LABEL_2': 'positive',
                'negative': 'negative',
                'neutral': 'neutral',
                'positive': 'positive'
            }
            
            predicted_label = results[0]['label']
            predicted_label = label_map.get(predicted_label, predicted_label).lower()
            
            # Extract probabilities
            if len(probs) == 3:
                # Assuming order: negative, neutral, positive OR positive, neutral, negative
                # For most models: [negative, neutral, positive]
                if self.model_type == 'finbert':
                    positive_prob = float(probs[2])
                    neutral_prob = float(probs[1])
                    negative_prob = float(probs[0])
                else:
                    # For twitter-roberta and others
                    negative_prob = float(probs[0])
                    neutral_prob = float(probs[1])
                    positive_prob = float(probs[2])
            else:
                # Fallback
                positive_prob = 0.33
                neutral_prob = 0.34
                negative_prob = 0.33
            
            # Calculate composite score (0-1 scale)
            composite_score = (positive_prob - negative_prob + 1) / 2
            
            return {
                'label': predicted_label,
                'score': composite_score,
                'positive': positive_prob,
                'neutral': neutral_prob,
                'negative': negative_prob,
                'model': self.model_type
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'label': 'neutral',
                'score': 0.5,
                'positive': 0.33,
                'neutral': 0.34,
                'negative': 0.33,
                'error': str(e)
            }
    
    def analyze_batch(self, texts, batch_size=8):
        """
        Analyze multiple texts efficiently
        
        Args:
            texts: List of texts to analyze
            batch_size: Batch size for processing
            
        Returns:
            List of sentiment dicts
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            for text in batch:
                result = self.analyze(text)
                results.append(result)
        
        return results
    
    @staticmethod
    def get_available_models():
        """Return list of available models"""
        return [
            {
                'id': 'finbert',
                'name': 'FinBERT',
                'description': 'Best for financial news and formal text',
                'best_for': ['news', 'earnings reports', 'financial documents']
            },
            {
                'id': 'twitter-financial',
                'name': 'Twitter-RoBERTa',
                'description': 'Best for social media and informal text',
                'best_for': ['tweets', 'reddit', 'stocktwits', 'casual discussions']
            },
            {
                'id': 'distilbert-financial',
                'name': 'Alternative FinBERT',
                'description': 'Good balance of speed and accuracy',
                'best_for': ['general financial text', 'mixed sources']
            }
        ]
