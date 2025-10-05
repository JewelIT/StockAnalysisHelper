"""
Vestor Service - AI Financial Advisor conversation service
Handles all Vestor AI interactions and business logic
"""
from src.stock_chat import StockChatAssistant
from app.services.analysis_service import AnalysisService
import re


class VestorService:
    """Service for managing Vestor AI conversations"""
    
    def __init__(self):
        self.chat_assistant = None
        self.analysis_service = AnalysisService()
        
        # Company to ticker mapping
        self.company_to_ticker = {
            'apple': 'AAPL', 'microsoft': 'MSFT', 'tesla': 'TSLA', 'amazon': 'AMZN',
            'google': 'GOOGL', 'alphabet': 'GOOGL', 'meta': 'META', 'facebook': 'META',
            'nvidia': 'NVDA', 'netflix': 'NFLX', 'disney': 'DIS', 'amd': 'AMD',
            'intel': 'INTC', 'bitcoin': 'BTC-USD', 'ethereum': 'ETH-USD',
            'ripple': 'XRP-USD', 'xrp': 'XRP-USD', 'cardano': 'ADA-USD', 
            'dogecoin': 'DOGE-USD', 'solana': 'SOL-USD'
        }
    
    def _get_chat_assistant(self):
        """Lazy load Vestor AI"""
        if self.chat_assistant is None:
            self.chat_assistant = StockChatAssistant()
            self.chat_assistant.load_model()
            print("✅ Vestor AI loaded successfully")
        return self.chat_assistant
    
    def process_chat(self, question, ticker, context_ticker, conversation_history):
        """
        Process Vestor chat interaction
        
        Args:
            question: User's question
            ticker: Explicitly provided ticker
            context_ticker: Ticker from conversation context
            conversation_history: List of previous messages
            
        Returns:
            dict: Response with answer, ticker, metadata
        """
        print("\n" + "="*80)
        print(f"💬 VESTOR CONVERSATION")
        print("="*80)
        print(f"📝 User: {question}")
        
        assistant = self._get_chat_assistant()
        question_lower = question.lower()
        
        # Build conversation context
        conversation_context = self._build_conversation_context(conversation_history)
        
        # Detect mentioned tickers/companies
        mentioned_tickers = self._detect_tickers(question, question_lower)
        
        # Determine which ticker to use
        final_ticker = self._resolve_ticker(
            ticker, 
            mentioned_tickers, 
            context_ticker, 
            question_lower
        )
        
        print(f"🎯 Final Ticker: {final_ticker if final_ticker else 'None'}")
        print(f"📊 Mentioned: {mentioned_tickers if mentioned_tickers else 'None'}")
        print("-" * 80)
        
        # Build Vestor's system prompt
        vestor_prompt = self._build_vestor_prompt(conversation_context)
        
        # Determine conversation mode
        needs_analysis = bool(final_ticker and mentioned_tickers)
        
        print(f"🤖 Vestor Mode: {'Stock Analysis' if needs_analysis else 'Conversation'}")
        print("="*80 + "\n")
        
        # Process based on mode
        if not needs_analysis:
            return self._handle_conversation(question, vestor_prompt, mentioned_tickers)
        
        # Check if analysis exists
        cached_analysis = self.analysis_service.get_cached_analysis(final_ticker)
        
        if not cached_analysis:
            return self._request_analysis(final_ticker)
        
        # Generate response with analysis context
        return self._handle_stock_conversation(
            question, 
            final_ticker, 
            cached_analysis, 
            vestor_prompt
        )
    
    def _build_conversation_context(self, history):
        """Build context string from conversation history"""
        if not history:
            return ""
        
        context = "\n\n=== Recent Conversation ===\n"
        for msg in history[-6:]:  # Last 3 exchanges
            role = "User" if msg.get('role') == 'user' else "Vestor"
            content = msg.get('content', '')[:300]
            context += f"{role}: {content}\n\n"
        return context
    
    def _detect_tickers(self, question, question_lower):
        """Detect ticker symbols and company names in question"""
        mentioned = []
        
        # Check for company names
        for company, ticker in self.company_to_ticker.items():
            if company in question_lower:
                mentioned.append(ticker)
                print(f"🏢 Detected '{company}' → {ticker}")
        
        # Check for explicit ticker symbols
        ticker_pattern = r'\b([A-Z]{2,5}(?:[-][A-Z]{2,4})?)\b'
        potential_tickers = re.findall(ticker_pattern, question)
        for t in potential_tickers:
            if t not in mentioned:
                mentioned.append(t)
                print(f"📊 Detected ticker: {t}")
        
        return mentioned
    
    def _resolve_ticker(self, explicit_ticker, mentioned, context_ticker, question_lower):
        """Determine which ticker to use for the conversation"""
        if explicit_ticker:
            return explicit_ticker
        
        if mentioned:
            return mentioned[0]
        
        # Check for follow-up indicators
        if context_ticker:
            follow_up_phrases = [
                'is it', 'should i', 'worth it', 'what about it', 'tell me more',
                'more info', 'thoughts on that', 'opinion', 'good investment',
                'buy it', 'sell it', 'yes', 'analyze', 'the stock', 'that stock'
            ]
            if any(phrase in question_lower for phrase in follow_up_phrases):
                print(f"🔄 Follow-up about: {context_ticker}")
                return context_ticker
        
        return None
    
    def _build_vestor_prompt(self, conversation_context):
        """Build Vestor's system prompt with personality"""
        return f"""You are Vestor, a friendly AI financial advisor and investment mentor.

**Your Personality:**
- Warm, approachable, and encouraging
- Expert in stocks, ETFs, crypto, and investment strategies
- Patient with beginners, sophisticated with experienced investors
- Proactive: naturally offer to analyze stocks when mentioned
- Context-aware: remember and reference previous conversations

**Your Capabilities:**
- Analyze any stock or cryptocurrency with real-time data
- Explain financial concepts in simple, relatable terms
- Provide personalized portfolio advice
- Help users make informed investment decisions

{conversation_context}

**Your Guidelines:**
- Be conversational and natural, like a knowledgeable friend
- When users mention a company/ticker, acknowledge it and offer analysis
- Reference previous parts of the conversation naturally
- For beginners, explain concepts with examples
- Always consider risk management and diversification
- If suggesting analysis, mention the ticker symbol clearly
- Don't be preachy - be helpful and practical
- Use emojis sparingly for friendliness (1-2 per response max)
"""
    
    def _handle_conversation(self, question, prompt, mentioned_tickers):
        """Handle pure conversational response (no stock analysis)"""
        try:
            assistant = self._get_chat_assistant()
            response = assistant.answer_question(
                question=question,
                context=prompt,
                ticker=""
            )
            
            # Check if Vestor mentioned any tickers
            suggested = [t for t in mentioned_tickers[:3] if t.upper() in response.upper()]
            
            return {
                'answer': response,
                'ticker': None,
                'vestor_mode': 'conversation',
                'is_conversational': True,
                'suggested_tickers': suggested if suggested else None,
                'success': True
            }
        except Exception as e:
            print(f"❌ Vestor AI error: {str(e)}")
            return self._fallback_response()
    
    def _request_analysis(self, ticker):
        """Request stock analysis before answering"""
        return {
            'answer': f"""I'd love to discuss **{ticker}** with you! 

Let me analyze it first so I can give you informed insights. Would you like me to:

🔹 **Analyze in background** - I'll answer your question quickly
🔹 **Show full analysis** - Complete report with charts and data

*(I'll start the background analysis automatically in a moment...)*""",
            'ticker': ticker,
            'vestor_mode': 'needs_analysis',
            'needs_background_analysis': True,
            'pending_ticker': ticker,
            'success': True
        }
    
    def _handle_stock_conversation(self, question, ticker, cached_analysis, prompt):
        """Handle conversation with stock analysis context"""
        try:
            cached_result = cached_analysis['result']
            
            # Build analysis context
            analysis_context = f"""
=== Analysis Data for {ticker} ===
Current Price: ${cached_result.get('current_price', 0):.2f}
Price Change: {cached_result.get('price_change', 0):+.2f}%
Recommendation: {cached_result.get('recommendation', 'N/A')}
Technical Signal: {cached_result.get('technical_signal', 'N/A')}
Sentiment Score: {cached_result.get('sentiment_score', 0.5):.2f}
RSI: {cached_result.get('rsi', 'N/A')}
MACD Signal: {cached_result.get('macd_signal', 'N/A')}

Key Reasons:
{chr(10).join(f"- {r}" for r in cached_result.get('reasons', [])[:5])}
"""
            
            full_context = prompt + "\n\n" + analysis_context
            
            assistant = self._get_chat_assistant()
            response = assistant.answer_question(
                question=question,
                context=full_context,
                ticker=ticker
            )
            
            return {
                'answer': response,
                'ticker': ticker,
                'vestor_mode': 'stock_advice',
                'success': True
            }
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return self._fallback_with_data(ticker, cached_analysis)
    
    def _fallback_response(self):
        """Fallback response when AI fails"""
        return {
            'answer': """Hi! I'm Vestor, your AI financial advisor. I'm here to help you with:

📊 **Stock & Crypto Analysis** - Just mention any ticker or company name
📚 **Investment Education** - Ask me anything about investing
💼 **Portfolio Advice** - Let's discuss your investment strategy

What would you like to know about?""",
            'vestor_mode': 'conversation',
            'is_conversational': True,
            'success': True
        }
    
    def _fallback_with_data(self, ticker, cached_analysis):
        """Fallback with available analysis data"""
        result = cached_analysis['result']
        return {
            'answer': f"""I have analysis data for **{ticker}**, but I'm having trouble formulating a response. 

Here's what I know:
📊 Current Price: ${result.get('current_price', 0):.2f}
📈 Recommendation: {result.get('recommendation', 'N/A')}
💡 Technical Signal: {result.get('technical_signal', 'N/A')}

Could you rephrase your question, or ask something specific like:
- "Is {ticker} a good investment?"
- "What's the sentiment for {ticker}?"
- "Should I buy {ticker} now?"
""",
            'ticker': ticker,
            'vestor_mode': 'fallback',
            'success': True
        }
