"""Chatbot Assistant for discussing portfolio and market analysis"""

import os
from typing import Dict, List, Optional
import json


class ChatbotAssistant:
    """AI-powered chatbot for discussing portfolio and market insights"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize chatbot assistant
        
        Args:
            api_key: OpenAI API key (optional, can use env variable)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.conversation_history = []
        self.context = {}
    
    def set_context(self, portfolio_data: Dict, market_data: Dict, 
                   sentiment_data: Dict, news_data: Dict) -> None:
        """
        Set context for the chatbot
        
        Args:
            portfolio_data: Portfolio information
            market_data: Market data
            sentiment_data: Sentiment analysis results
            news_data: News articles
        """
        self.context = {
            "portfolio": portfolio_data,
            "market": market_data,
            "sentiment": sentiment_data,
            "news": news_data
        }
    
    def generate_summary(self) -> str:
        """
        Generate a summary of portfolio and market conditions
        
        Returns:
            Summary text
        """
        summary_parts = []
        
        # Portfolio summary
        if "portfolio" in self.context:
            portfolio = self.context["portfolio"]
            summary_parts.append(f"Portfolio Summary:")
            summary_parts.append(f"  - Total stocks: {portfolio.get('total_stocks', 0)}")
            summary_parts.append(f"  - Total crypto: {portfolio.get('total_crypto', 0)}")
            summary_parts.append(f"  - Watchlist items: {portfolio.get('watchlist_items', 0)}")
        
        # Market summary
        if "market" in self.context and isinstance(self.context["market"], list):
            summary_parts.append(f"\nMarket Overview:")
            for item in self.context["market"][:5]:  # Show top 5
                symbol = item.get("symbol", "N/A")
                price = item.get("current_price", 0)
                change = item.get("change_pct", 0)
                summary_parts.append(f"  - {symbol}: ${price:.2f} ({change:+.2f}%)")
        
        # Sentiment summary
        if "sentiment" in self.context:
            sentiment = self.context["sentiment"]
            overall = sentiment.get("overall_sentiment", "neutral")
            avg_compound = sentiment.get("average_compound", 0)
            summary_parts.append(f"\nSentiment Analysis:")
            summary_parts.append(f"  - Overall sentiment: {overall.upper()}")
            summary_parts.append(f"  - Average score: {avg_compound:.3f}")
            summary_parts.append(f"  - Positive articles: {sentiment.get('positive_count', 0)}")
            summary_parts.append(f"  - Negative articles: {sentiment.get('negative_count', 0)}")
        
        # News summary
        if "news" in self.context:
            news = self.context["news"]
            total_articles = news.get("total_articles", 0)
            summary_parts.append(f"\nNews Summary:")
            summary_parts.append(f"  - Total articles: {total_articles}")
            if news.get("latest_article"):
                latest = news["latest_article"]
                summary_parts.append(f"  - Latest: {latest.get('title', 'N/A')}")
        
        return "\n".join(summary_parts) if summary_parts else "No data available."
    
    def chat(self, user_message: str) -> str:
        """
        Process user message and generate response
        
        Args:
            user_message: User's message
            
        Returns:
            Bot's response
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Simple rule-based responses (can be enhanced with OpenAI API)
        response = self._generate_response(user_message)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def _generate_response(self, message: str) -> str:
        """
        Generate response based on message
        
        Args:
            message: User message
            
        Returns:
            Response text
        """
        message_lower = message.lower()
        
        # Check for specific queries
        if any(word in message_lower for word in ["summary", "overview", "status"]):
            return self.generate_summary()
        
        elif any(word in message_lower for word in ["sentiment", "feeling", "mood"]):
            if "sentiment" in self.context:
                sentiment = self.context["sentiment"]
                overall = sentiment.get("overall_sentiment", "neutral")
                return f"The overall market sentiment is {overall.upper()}. " \
                       f"Based on analysis of {sentiment.get('total_texts', 0)} articles, " \
                       f"with {sentiment.get('positive_count', 0)} positive and " \
                       f"{sentiment.get('negative_count', 0)} negative articles."
            return "No sentiment data available."
        
        elif any(word in message_lower for word in ["news", "article", "latest"]):
            if "news" in self.context:
                news = self.context["news"]
                articles = news.get("articles", [])
                if articles:
                    response = f"Found {len(articles)} recent articles:\n\n"
                    for i, article in enumerate(articles[:3], 1):
                        response += f"{i}. {article.get('title', 'N/A')}\n"
                    return response
                return "No news articles available."
            return "No news data available."
        
        elif any(word in message_lower for word in ["portfolio", "holdings", "stocks"]):
            if "portfolio" in self.context:
                portfolio = self.context["portfolio"]
                response = f"Your portfolio contains:\n"
                response += f"- {portfolio.get('total_stocks', 0)} stocks\n"
                response += f"- {portfolio.get('total_crypto', 0)} cryptocurrencies\n"
                response += f"- {portfolio.get('watchlist_items', 0)} watchlist items\n"
                
                if portfolio.get('stocks'):
                    response += "\nStocks:\n"
                    for stock in portfolio['stocks'][:5]:
                        response += f"  - {stock.get('symbol', 'N/A')}: {stock.get('shares', 0)} shares\n"
                
                return response
            return "No portfolio data available."
        
        elif any(word in message_lower for word in ["help", "what can you do"]):
            return """I can help you with:
- Portfolio overview and summary
- Market analysis and current prices
- Sentiment analysis from news
- Latest financial news
- Technical analysis and charts

Try asking me:
- "Show me a summary"
- "What's the sentiment?"
- "What's the latest news?"
- "Show me my portfolio"
"""
        
        else:
            return "I'm here to help with your portfolio analysis. " \
                   "Try asking about your portfolio, market sentiment, or latest news. " \
                   "Say 'help' for more information."
    
    def get_conversation_history(self) -> List[Dict]:
        """
        Get conversation history
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history
    
    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
