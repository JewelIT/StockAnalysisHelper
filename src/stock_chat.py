"""
AI Stock Chat Assistant
Uses HuggingFace models to answer questions about stocks
"""
from transformers import pipeline
import torch

class StockChatAssistant:
    def __init__(self):
        """Initialize the chat assistant with Q&A model"""
        self.qa_pipeline = None
        self.initialized = False
        
    def load_model(self):
        """Load the question-answering model"""
        if self.initialized:
            return
        
        try:
            print("📥 Loading AI chat model...")
            # Use DistilBERT for Q&A - good balance of speed and accuracy
            self.qa_pipeline = pipeline(
                "question-answering",
                model="distilbert-base-cased-distilled-squad",
                device=0 if torch.cuda.is_available() else -1
            )
            self.initialized = True
            print("✅ AI chat model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading chat model: {e}")
            raise
    
    def answer_question(self, question, context):
        """
        Answer a question based on provided context
        
        Args:
            question: User's question
            context: Context text (e.g., stock analysis, news, etc.)
            
        Returns:
            Dict with 'answer', 'confidence', 'start', 'end'
        """
        if not self.initialized:
            self.load_model()
        
        try:
            result = self.qa_pipeline(question=question, context=context)
            return {
                'answer': result['answer'],
                'confidence': result['score'],
                'success': True
            }
        except Exception as e:
            return {
                'answer': f"Sorry, I couldn't process that question: {str(e)}",
                'confidence': 0.0,
                'success': False
            }
    
    def generate_context_from_analysis(self, analysis_result):
        """
        Generate a context string from analysis results for Q&A
        
        Args:
            analysis_result: Dict containing stock analysis
            
        Returns:
            String context for Q&A
        """
        ticker = analysis_result.get('ticker', 'Unknown')
        name = analysis_result.get('name', ticker)
        price = analysis_result.get('current_price', 0)
        change = analysis_result.get('price_change', 0)
        recommendation = analysis_result.get('recommendation', 'N/A')
        sentiment_score = analysis_result.get('sentiment_score', 0.5)
        technical_score = analysis_result.get('technical_score', 0.5)
        technical_signal = analysis_result.get('technical_signal', 'N/A')
        technical_reasons = analysis_result.get('technical_reasons', [])
        
        # Build context
        context = f"""
        Stock Analysis for {ticker} ({name}):
        
        Current Price: ${price:.2f}
        Price Change (3 months): {change:+.2f}%
        
        Recommendation: {recommendation}
        Overall Sentiment Score: {sentiment_score:.2%}
        Technical Score: {technical_score:.2%}
        Technical Signal: {technical_signal}
        
        Technical Analysis Reasons:
        {chr(10).join(f'- {reason}' for reason in technical_reasons)}
        
        News Sentiment: {analysis_result.get('news_sentiment_score', 0.5):.2%}
        Social Media Sentiment: {analysis_result.get('social_sentiment_score', 0.5):.2%}
        
        Sector: {analysis_result.get('sector', 'N/A')}
        Industry: {analysis_result.get('industry', 'N/A')}
        """
        
        # Add news summaries if available
        if 'sentiment_results' in analysis_result:
            news_items = [s for s in analysis_result['sentiment_results'] if s.get('source_type') == 'news']
            if news_items:
                context += "\n\nRecent News Headlines:\n"
                for item in news_items[:5]:
                    context += f"- {item.get('title', 'Untitled')} (Sentiment: {item.get('label', 'N/A')})\n"
        
        return context.strip()
