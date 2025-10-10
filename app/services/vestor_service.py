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
            # Tech Giants
            'apple': 'AAPL', 'microsoft': 'MSFT', 'tesla': 'TSLA', 'amazon': 'AMZN',
            'google': 'GOOGL', 'alphabet': 'GOOGL', 'meta': 'META', 'facebook': 'META',
            'nvidia': 'NVDA', 'netflix': 'NFLX', 'amd': 'AMD', 'intel': 'INTC',
            
            # Aerospace & Defense
            'boeing': 'BA', 'lockheed': 'LMT', 'lockheed martin': 'LMT',
            'northrop': 'NOC', 'northrop grumman': 'NOC', 'raytheon': 'RTX',
            
            # Finance
            'jpmorgan': 'JPM', 'jp morgan': 'JPM', 'bank of america': 'BAC',
            'wells fargo': 'WFC', 'goldman': 'GS', 'goldman sachs': 'GS',
            'morgan stanley': 'MS', 'citigroup': 'C', 'visa': 'V', 'mastercard': 'MA',
            
            # Retail & Consumer
            'walmart': 'WMT', 'target': 'TGT', 'costco': 'COST', 'home depot': 'HD',
            'mcdonalds': 'MCD', "mcdonald's": 'MCD', 'starbucks': 'SBUX',
            'coca cola': 'KO', 'coca-cola': 'KO', 'pepsi': 'PEP', 'pepsico': 'PEP',
            'nike': 'NKE', 'procter': 'PG', 'procter & gamble': 'PG',
            
            # Healthcare & Pharma
            'johnson': 'JNJ', 'johnson & johnson': 'JNJ', 'pfizer': 'PFE',
            'moderna': 'MRNA', 'merck': 'MRK', 'abbvie': 'ABBV',
            'unitedhealth': 'UNH', 'united health': 'UNH',
            
            # Energy
            'exxon': 'XOM', 'exxonmobil': 'XOM', 'chevron': 'CVX',
            'conocophillips': 'COP', 'shell': 'SHEL',
            
            # Entertainment & Media
            'disney': 'DIS', 'warner': 'WBD', 'comcast': 'CMCSA',
            'paramount': 'PARA', 'sony': 'SONY',
            
            # Automotive
            'ford': 'F', 'gm': 'GM', 'general motors': 'GM',
            
            # Cryptocurrency
            'bitcoin': 'BTC-USD', 'ethereum': 'ETH-USD',
            'ripple': 'XRP-USD', 'xrp': 'XRP-USD', 'cardano': 'ADA-USD', 
            'dogecoin': 'DOGE-USD', 'solana': 'SOL-USD', 'bnb': 'BNB-USD',
            'binance coin': 'BNB-USD', 'polkadot': 'DOT-USD'
        }
    
    def _get_chat_assistant(self):
        """Lazy load Vestor AI"""
        if self.chat_assistant is None:
            self.chat_assistant = StockChatAssistant()
            self.chat_assistant.load_model()
            print("✅ Vestor AI loaded successfully")
        return self.chat_assistant
    
    def _handle_ticker_lookup(self, question, question_lower):
        """
        Handle questions asking for ticker symbols
        Returns response dict if it's a ticker lookup question, None otherwise
        """
        # Patterns that indicate ticker lookup questions
        ticker_lookup_patterns = [
            r"what(?:'s| is) the ticker (?:for|of|symbol for)\s+(.+?)(?:\?|$)",
            r"what ticker (?:is|for)\s+(.+?)(?:\?|$)",
            r"ticker (?:for|of|symbol for)\s+(.+?)(?:\?|$)",
            r"(?:what|give me|tell me) (?:the )?ticker\s+(?:for|of)\s+(.+?)(?:\?|$)",
            r"(?:do you know|what's) (?:the )?(?:stock )?symbol (?:for|of)\s+(.+?)(?:\?|$)",
        ]
        
        for pattern in ticker_lookup_patterns:
            match = re.search(pattern, question_lower)
            if match:
                company_name = match.group(1).strip()
                
                # Clean up common words
                company_name = re.sub(r'\b(stock|company|corp|corporation|inc|limited|ltd)\b', '', company_name).strip()
                
                # Look up in our mapping
                ticker = self.company_to_ticker.get(company_name.lower())
                
                if ticker:
                    # Success - found the ticker
                    print(f"🎯 Ticker lookup: '{company_name}' → {ticker}")
                    
                    return {
                        'answer': f"""📊 **{company_name.title()}** trades under the ticker symbol **{ticker}**.

Would you like me to analyze {ticker} for you? I can provide:
- Current price and performance
- Technical indicators (RSI, MACD)
- Market sentiment analysis
- Investment recommendation

Just say "analyze {ticker}" or "what do you think about {ticker}?" and I'll dive right in! 🚀""",
                        'ticker': ticker,
                        'vestor_mode': 'ticker_lookup',
                        'is_conversational': True,
                        'success': True
                    }
                else:
                    # Company not in our database - provide helpful response
                    print(f"❓ Unknown company: '{company_name}'")
                    
                    # Try to extract potential ticker if it looks like one (2-5 capital letters)
                    potential_ticker_match = re.search(r'\b([A-Z]{2,5})\b', question)
                    if potential_ticker_match:
                        potential_ticker = potential_ticker_match.group(1)
                        return {
                            'answer': f"""I don't have **{company_name}** in my database yet, but if you know the ticker symbol, you can just tell me!

💡 **Try one of these:**
- If the ticker is **{potential_ticker}**, just say "analyze {potential_ticker}"
- Search for the company on [Yahoo Finance](https://finance.yahoo.com) or [Google Finance](https://www.google.com/finance)
- Tell me the ticker directly: "What do you think about [TICKER]?"

**Popular tickers I know:**
🏢 Tech: AAPL (Apple), MSFT (Microsoft), GOOGL (Google), META (Facebook), NVDA (Nvidia)
✈️ Aerospace: BA (Boeing), LMT (Lockheed Martin), RTX (Raytheon)
🏦 Finance: JPM (JPMorgan), BAC (Bank of America), V (Visa)
🛒 Retail: WMT (Walmart), COST (Costco), HD (Home Depot)
💊 Healthcare: JNJ (Johnson & Johnson), PFE (Pfizer)

Once you have the ticker, I can analyze it for you! 📈""",
                            'ticker': None,
                            'vestor_mode': 'ticker_lookup_not_found',
                            'is_conversational': True,
                            'success': True
                        }
                    
                    return {
                        'answer': f"""I don't have **{company_name}** in my database yet. 

💡 **Here's what you can do:**
1. Search for the company on [Yahoo Finance](https://finance.yahoo.com) or [Google Finance](https://www.google.com/finance) to find its ticker
2. Once you have the ticker symbol (usually 1-5 letters), tell me: "analyze [TICKER]"
3. Or ask me about companies I know!

**Popular companies I can help with:**
- 🏢 Tech: Apple, Microsoft, Google, Meta, Nvidia, Tesla, Amazon
- ✈️ Aerospace: Boeing, Lockheed Martin, Raytheon
- 🏦 Finance: JPMorgan, Bank of America, Goldman Sachs
- 🛒 Retail: Walmart, Costco, Target, Home Depot
- 💊 Healthcare: Johnson & Johnson, Pfizer, Moderna
- 🪙 Crypto: Bitcoin, Ethereum, Solana

Just say the company name and I'll look it up for you! 📊""",
                        'ticker': None,
                        'vestor_mode': 'ticker_lookup_not_found',
                        'is_conversational': True,
                        'success': True
                    }
        
        return None
    
    def _handle_list_companies(self, question_lower):
        """Handle questions asking for list of supported companies"""
        list_patterns = [
            'what companies', 'which companies', 'list companies', 'list of companies',
            'what tickers', 'which tickers', 'list tickers', 'list the tickers', 'what stocks',
            'which stocks', 'what can you analyze', 'what do you support', 'tickers you support',
            'companies you know', 'tickers you know', 'stocks you know', 'companies do you know'
        ]
        
        if any(pattern in question_lower for pattern in list_patterns):
            print("📋 Listing supported companies")
            
            # Organize by category
            categories = {
                '🏢 Tech Giants': ['apple', 'microsoft', 'google', 'meta', 'nvidia', 'amazon', 'tesla', 'netflix'],
                '✈️ Aerospace & Defense': ['boeing', 'lockheed martin', 'northrop grumman', 'raytheon'],
                '🏦 Finance & Banking': ['jpmorgan', 'bank of america', 'goldman sachs', 'morgan stanley', 'visa', 'mastercard'],
                '🛒 Retail & Consumer': ['walmart', 'costco', 'target', 'home depot', 'starbucks', 'nike'],
                '💊 Healthcare & Pharma': ['johnson & johnson', 'pfizer', 'moderna', 'unitedhealth'],
                '⚡ Energy': ['exxonmobil', 'chevron', 'conocophillips'],
                '🎬 Entertainment': ['disney', 'sony', 'comcast'],
                '🚗 Automotive': ['ford', 'general motors'],
                '🪙 Cryptocurrencies': ['bitcoin', 'ethereum', 'solana', 'cardano', 'dogecoin']
            }
            
            response = "📊 **Here are the companies and tickers I can analyze:**\n\n"
            
            for category, companies in categories.items():
                response += f"**{category}**\n"
                for company in companies:
                    ticker = self.company_to_ticker.get(company, '')
                    if ticker:
                        response += f"• {company.title()} → **{ticker}**\n"
                response += "\n"
            
            response += """💡 **How to use:**
- Just mention the company name: "What about Apple?"
- Or use the ticker: "Analyze AAPL"
- Or ask for the ticker: "What's the ticker for Boeing?"

**Don't see a company?** You can still analyze any stock by using its ticker symbol directly! Just say "analyze [TICKER]" and I'll get the data for you.

**What would you like to explore?** 🚀"""
            
            return {
                'answer': response,
                'ticker': None,
                'vestor_mode': 'company_list',
                'is_conversational': True,
                'success': True
            }
        
        return None
    
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
        
        # Check if there's a ticker mentioned or in context
        if final_ticker:
            # Check if analysis exists
            cached_analysis = self.analysis_service.get_cached_analysis(final_ticker)
            
            if cached_analysis:
                print(f"🤖 Vestor Mode: Stock Analysis (with data for {final_ticker})")
                print("="*80 + "\n")
                # Generate response with analysis context
                return self._handle_stock_conversation(
                    question, 
                    final_ticker, 
                    cached_analysis, 
                    vestor_prompt
                )
            else:
                print(f"🤖 Vestor Mode: Stock Conversation (no data yet for {final_ticker})")
                print("="*80 + "\n")
                # Answer the question anyway, and suggest analysis
                return self._handle_conversation_with_ticker(
                    question,
                    final_ticker,
                    vestor_prompt
                )
        else:
            print(f"🤖 Vestor Mode: General Conversation")
            print("="*80 + "\n")
            # Pure conversational response
            return self._handle_conversation(question, vestor_prompt, mentioned_tickers)
    
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
        
        # Common words to exclude from ticker detection
        excluded_words = {
            'HELLO', 'HI', 'HEY', 'THANKS', 'THANK', 'YOU', 'YES', 'NO', 'OK', 'OKAY',
            'BYE', 'GOODBYE', 'PLEASE', 'SORRY', 'THE', 'AND', 'FOR', 'BUT', 'NOT',
            'WITH', 'FROM', 'ABOUT', 'WHAT', 'WHERE', 'WHEN', 'WHY', 'HOW', 'WHO',
            'WHICH', 'THIS', 'THAT', 'THESE', 'THOSE', 'CAN', 'COULD', 'WOULD',
            'SHOULD', 'WILL', 'SHALL', 'MAY', 'MIGHT', 'MUST', 'JUST', 'VERY',
            'ALSO', 'EVEN', 'STILL', 'ONLY', 'LIKE', 'NEED', 'WANT', 'MAKE',
            'KNOW', 'THINK', 'TAKE', 'COME', 'GIVE', 'LOOK', 'USE', 'FIND'
        }
        
        # Commodity/general investment terms that shouldn't be treated as tickers
        # unless explicitly meant as tickers (e.g., "analyze CORN" vs "invest in corn")
        commodity_terms = {'CORN', 'WHEAT', 'RICE', 'GOLD', 'SILVER', 'OIL', 'GAS', 'WATER'}
        
        # Check for company names first (these take priority)
        for company, ticker in self.company_to_ticker.items():
            if company in question_lower:
                mentioned.append(ticker)
                print(f"🏢 Detected '{company}' → {ticker}")
        
        # Check for explicit ticker symbols
        ticker_pattern = r'\b([A-Z]{2,5}(?:[-][A-Z]{2,4})?)\b'
        potential_tickers = re.findall(ticker_pattern, question)
        for t in potential_tickers:
            if t not in mentioned and t not in excluded_words:
                # If it's a commodity term, only include if used as ticker (e.g., "analyze CORN", not "corn investment")
                if t in commodity_terms:
                    # Check if it's used in a ticker-like context
                    if re.search(rf'\b(analyze|check|look at|show me|ticker|symbol)\s+{t}\b', question, re.IGNORECASE):
                        mentioned.append(t)
                        print(f"📊 Detected ticker: {t} (explicit usage)")
                    else:
                        print(f"⏭️  Skipping '{t}' - looks like commodity/general term, not ticker")
                else:
                    mentioned.append(t)
                    print(f"📊 Detected ticker: {t}")
        
        return mentioned
    
    def _resolve_ticker(self, explicit_ticker, mentioned, context_ticker, question_lower):
        """Determine which ticker to use for the conversation"""
        # Priority 1: Explicit ticker parameter
        if explicit_ticker:
            return explicit_ticker
        
        # Priority 2: Newly mentioned ticker in THIS message
        if mentioned:
            return mentioned[0]
        
        # Priority 3: Check for follow-up indicators about previous ticker
        # Only use context ticker if NO new ticker was mentioned
        if context_ticker and not mentioned:
            follow_up_phrases = [
                'is it', 'worth it', 'what about it', 'tell me more',
                'more info', 'thoughts on that', 'opinion on it', 'the stock', 'that stock',
                'analyze it', 'buy it', 'sell it'
            ]
            # More specific follow-up: requires at least one phrase AND short question
            if any(phrase in question_lower for phrase in follow_up_phrases) and len(question_lower) < 100:
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
    
    def _handle_conversation_with_ticker(self, question, ticker, prompt):
        """Handle conversation when ticker is mentioned but not yet analyzed"""
        try:
            # Add ticker context to the prompt
            ticker_context = f"\n\nUser is asking about **{ticker}**. Answer their question naturally. If you don't have analysis data yet, you can:\n- Answer general questions about the company\n- Explain what the ticker represents\n- Offer to analyze it if they want specific data\n- Just have a natural conversation about it"
            
            full_context = prompt + ticker_context
            
            assistant = self._get_chat_assistant()
            response = assistant.answer_question(
                question=question,
                context=full_context,
                ticker=ticker
            )
            
            # Extract the answer
            answer_text = response.get('answer', '') if isinstance(response, dict) else str(response)
            
            # Add a friendly offer to analyze at the end if not already mentioned
            if 'analyze' not in answer_text.lower() and len(answer_text) < 500:
                answer_text += f"\n\n💡 Would you like me to analyze **{ticker}** with real-time data? Just say 'analyze {ticker}' or click the analyze button!"
            
            return {
                'answer': answer_text,
                'ticker': ticker,
                'vestor_mode': 'conversation_with_ticker',
                'suggested_ticker': ticker,
                'success': True
            }
        except Exception as e:
            print(f"❌ Error in conversation with ticker: {str(e)}")
            # Fallback: simple response
            return {
                'answer': f"""I'd be happy to discuss **{ticker}** with you!

{question}

To give you data-driven insights, I can analyze {ticker} with real-time information. Just say "analyze {ticker}" or use the analyze button, and I'll pull the latest:
- Stock price and performance
- Technical indicators
- Market sentiment
- Investment recommendation

What would you like to know about {ticker}?""",
                'ticker': ticker,
                'vestor_mode': 'conversation_with_ticker',
                'suggested_ticker': ticker,
                'success': True
            }
    
    def _handle_conversation(self, question, prompt, mentioned_tickers):
        """Handle pure conversational response (no stock analysis)"""
        question_lower = question.lower().strip()
        
        # Handle greetings with friendly responses
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
        if any(question_lower == greeting or question_lower.startswith(greeting + ' ') for greeting in greetings):
            return {
                'answer': """👋 Hello! I'm **Vestor**, your AI financial advisor and investment mentor.

I'm here to help you with:

📊 **Stock & Crypto Analysis** - Just mention any ticker (e.g., "What about AAPL?" or "Tell me about Bitcoin")
📚 **Investment Education** - Ask me about investing strategies, risk management, or financial concepts
💼 **Portfolio Guidance** - Get insights on diversification and investment decisions

**What would you like to explore today?**

*Remember: All advice is for educational purposes. Always do your own research and consider consulting a licensed financial advisor.*""",
                'ticker': None,
                'vestor_mode': 'conversation',
                'is_conversational': True,
                'suggested_tickers': None,
                'success': True
            }
        
        # Handle thank you messages
        if any(word in question_lower for word in ['thanks', 'thank you', 'appreciate']):
            return {
                'answer': """You're very welcome! 😊

I'm always here to help with your investment journey. Feel free to ask me:
- About any stock or cryptocurrency
- Investment strategies and education
- Risk management tips
- Or anything else finance-related!

**What else would you like to know?**""",
                'ticker': None,
                'vestor_mode': 'conversation',
                'is_conversational': True,
                'suggested_tickers': None,
                'success': True
            }
        
        # Handle ticker lookup questions
        ticker_lookup = self._handle_ticker_lookup(question, question_lower)
        if ticker_lookup:
            return ticker_lookup
        
        # Handle company list questions
        list_response = self._handle_list_companies(question_lower)
        if list_response:
            return list_response
        
        # For any other question, use the AI assistant - answer naturally!
        try:
            assistant = self._get_chat_assistant()
            
            # Enhance prompt to answer ANY question naturally
            open_prompt = prompt + """

**IMPORTANT**: Answer the user's question naturally and helpfully, regardless of topic:
- Financial questions: Give detailed investment advice
- Stock market questions: Explain concepts clearly
- General questions: Provide helpful, friendly responses
- Educational questions: Teach and explain
- "What is X?" questions: Define and explain clearly

Be conversational, helpful, and knowledgeable. Don't refuse to answer - just be honest about your knowledge limits if needed."""
            
            response = assistant.answer_question(
                question=question,
                context=open_prompt,
                ticker=""
            )
            
            # Extract the answer string from the response dict
            answer_text = response.get('answer', '') if isinstance(response, dict) else str(response)
            
            # Check if Vestor mentioned any tickers
            suggested = [t for t in mentioned_tickers[:3] if t.upper() in answer_text.upper()]
            
            return {
                'answer': answer_text,
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
=== Real-Time Analysis Data for {ticker} ===
Current Price: ${cached_result.get('current_price', 0):.2f}
Price Change: {cached_result.get('price_change', 0):+.2f}%
Recommendation: {cached_result.get('recommendation', 'N/A')}
Technical Signal: {cached_result.get('technical_signal', 'N/A')}
Sentiment Score: {cached_result.get('sentiment_score', 0.5):.2f}
RSI: {cached_result.get('rsi', 'N/A')}
MACD Signal: {cached_result.get('macd_signal', 'N/A')}

Key Reasons:
{chr(10).join(f"- {r}" for r in cached_result.get('reasons', [])[:5])}

**Instructions**: Use this analysis data to answer the user's question about {ticker}. 
- Answer their specific question directly
- Reference the data when relevant
- Be conversational and helpful
- Provide your investment perspective
- Don't just repeat the data - add insights and context
"""
            
            full_context = prompt + "\n\n" + analysis_context
            
            assistant = self._get_chat_assistant()
            print(f"🤖 Calling AI with ticker='{ticker}' and analysis data")
            response = assistant.answer_question(
                question=question,
                context=full_context,
                ticker=ticker
            )
            print(f"✅ AI Response received")
            
            # Extract the answer string from the response dict
            answer_text = response.get('answer', '') if isinstance(response, dict) else str(response)
            
            return {
                'answer': answer_text,
                'ticker': ticker,
                'vestor_mode': 'stock_advice',
                'has_analysis_data': True,
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
