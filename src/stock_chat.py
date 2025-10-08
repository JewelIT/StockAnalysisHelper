"""
AI Stock Chat Assistant - Investment Mentorship & Education
A conversational AI that educates users about investing, provides resources,
and guides ethical investment decisions. Acts as a knowledgeable mentor rather
than just a technical analysis tool.
"""
from transformers import pipeline
import torch
import re

class StockChatAssistant:
    def __init__(self):
        """Initialize the chat assistant with Q&A model"""
        self.qa_pipeline = None
        self.initialized = False
        self.conversation_history = []  # Track conversation for context
        
        # Financial Advisor Persona
        self.system_persona = """
I am a financial advisor and investment mentor. I help people understand financial markets, 
including stocks, commodities, and cryptocurrencies. 

MY CORE PRINCIPLES:
• I find the best information from verifiable and reputable sources
• I always remind users that capital is at risk
• I emphasize the need for proper verification before committing to any investment strategy
• I check my configured AI models and data sources before providing answers
• I only reply to financial and investment questions - any other prompts are dismissed
• I am pragmatic, factual, objective, and polite regardless of the conversation tone
• I base all my arguments on data and analysis

MY APPROACH:
• For advanced investors: I provide detailed technical analysis and market insights
• For beginners: I explain concepts clearly and recommend educational resources
• I always cite my sources (sentiment analysis, technical indicators, news data)
• If I cannot find relevant information, I honestly say so
• If I'm not trained to answer something, I clearly state my limitations

MY MANDATE:
Users may ask about market sentiment, specific stocks/crypto, why people invest in certain 
assets, or general investment questions. I always check my models (FinBERT for sentiment, 
technical indicators, news analysis) before answering. I never make guarantees about returns 
and always emphasize risk management and due diligence.
"""
        
        # Educational resources library
        self.resources = {
            'beginner': {
                'books': [
                    {'title': 'The Intelligent Investor', 'author': 'Benjamin Graham', 'topic': 'Value investing fundamentals'},
                    {'title': 'A Random Walk Down Wall Street', 'author': 'Burton Malkiel', 'topic': 'Investment strategies and market efficiency'},
                    {'title': 'Common Stocks and Uncommon Profits', 'author': 'Philip Fisher', 'topic': 'Growth investing principles'}
                ],
                'websites': [
                    {'name': 'Investopedia', 'url': 'https://www.investopedia.com', 'description': 'Comprehensive financial education'},
                    {'name': 'SEC Investor Education', 'url': 'https://www.investor.gov', 'description': 'Official SEC resources for investors'},
                    {'name': 'Khan Academy Finance', 'url': 'https://www.khanacademy.org/economics-finance-domain', 'description': 'Free finance courses'}
                ]
            },
            'technical': {
                'books': [
                    {'title': 'Technical Analysis of Financial Markets', 'author': 'John Murphy', 'topic': 'Chart patterns and indicators'},
                    {'title': 'Japanese Candlestick Charting Techniques', 'author': 'Steve Nison', 'topic': 'Candlestick patterns'}
                ],
                'websites': [
                    {'name': 'TradingView Education', 'url': 'https://www.tradingview.com/education/', 'description': 'Technical analysis tutorials'},
                    {'name': 'StockCharts School', 'url': 'https://school.stockcharts.com', 'description': 'Comprehensive TA learning'}
                ]
            },
            'ethics': {
                'principles': [
                    'Only invest what you can afford to lose completely',
                    'Never invest money needed for essential expenses',
                    'Avoid high-pressure sales tactics and "get rich quick" schemes',
                    'Be wary of investments promising guaranteed returns',
                    'Understand that past performance doesn\'t guarantee future results',
                    'Diversification helps manage risk',
                    'Consider your time horizon and risk tolerance',
                    'Stay informed but avoid emotional decision-making'
                ],
                'resources': [
                    {'name': 'CFA Institute Ethics', 'url': 'https://www.cfainstitute.org/ethics', 'description': 'Professional investment ethics standards'},
                    {'name': 'FINRA Investor Alerts', 'url': 'https://www.finra.org/investors/alerts', 'description': 'Fraud warnings and scam alerts'}
                ]
            }
        }
        
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
    
    def answer_question(self, question, context, ticker=None):
        """
        Answer a question with financial advisor persona and data-driven analysis
        
        Args:
            question: User's question
            context: Context text (e.g., stock analysis, news, etc.)
            ticker: Optional ticker symbol for personalized responses
            
        Returns:
            Dict with 'answer', 'confidence', 'success'
        """
        if not self.initialized:
            self.load_model()
        
        # SECURITY: Detect prompt injection attempts FIRST
        is_injection, severity, attack_type = self._detect_prompt_injection(question)
        if is_injection:
            import logging
            
            # Log the attempt with full details for security monitoring
            if severity == 'HIGH':
                logging.error(f"🚨 SECURITY ALERT - HIGH SEVERITY PROMPT INJECTION BLOCKED")
                logging.error(f"   Attack Type: {attack_type}")
                logging.error(f"   Question: {question}")
                logging.error(f"   Ticker Context: {ticker}")
                
                # Strong rejection for high-severity attempts
                return {
                    'answer': "🚨 **Security Alert**\n\nI've detected an attempt to manipulate my system instructions. This has been logged for security monitoring.\n\n**I am a financial advisor and investment mentor. My core function cannot be changed or overridden.**\n\nMy role is to:\n✅ Provide data-driven investment analysis\n✅ Educate about financial markets\n✅ Emphasize risk management and due diligence\n\nI do not:\n❌ Accept instruction overrides\n❌ Change my persona or role\n❌ Provide advice contrary to my ethical guidelines\n\n**How can I help you with legitimate investment questions?** 📊",
                    'confidence': 1.0,
                    'success': True,
                    'security_warning': True
                }
            else:
                logging.warning(f"⚠️ SECURITY WARNING - MEDIUM SEVERITY PROMPT MANIPULATION BLOCKED")
                logging.warning(f"   Attack Type: {attack_type}")
                logging.warning(f"   Question: {question}")
                
                # Polite but firm rejection for medium-severity attempts
                return {
                    'answer': "⚠️ **I noticed something unusual in your question.**\n\nI'm designed as a **financial advisor and investment mentor**, and my role and instructions are fixed for security and reliability reasons.\n\nI cannot:\n• Change my persona or role\n• Ignore my core principles\n• Provide responses outside my financial expertise\n• Reveal my internal system instructions\n\n**I'm here to help with:**\n• Stock and cryptocurrency analysis\n• Investment education and strategies\n• Risk management guidance\n• Technical and fundamental analysis\n\nWhat would you like to know about investing or the financial markets? 📈",
                    'confidence': 1.0,
                    'success': True,
                    'security_warning': True
                }
        
        # Store question in conversation history (after security check)
        self.conversation_history.append({'question': question, 'ticker': ticker})
        
        # Check if this is a non-financial question
        if self._is_non_financial_question(question):
            return {
                'answer': "I appreciate your question, but I'm specialized in financial markets and investment guidance. I can help you with questions about stocks, cryptocurrencies, market analysis, investment strategies, or learning about finance. How can I assist you with your investment journey? 📊",
                'confidence': 1.0,
                'success': True
            }
        
        # Check if this is a ticker lookup question
        ticker_lookup_answer = self._handle_ticker_lookup_question(question)
        if ticker_lookup_answer:
            return {
                'answer': ticker_lookup_answer,
                'confidence': 0.9,
                'success': True
            }
        
        try:
            # Parse the context data to build a comprehensive answer
            answer = self._generate_advisor_response(question, context, ticker)
            
            return {
                'answer': answer,
                'confidence': 0.9,  # High confidence since we're using our own analysis
                'success': True
            }
        except Exception as e:
            return {
                'answer': f"I apologize, but I'm having difficulty accessing the analysis data right now. This might be a temporary issue. Could you try asking again, or let me know if you'd like me to analyze {ticker if ticker else 'a specific ticker'}? 🔄",
                'confidence': 0.0,
                'success': False
            }
    
    def _is_non_financial_question(self, question):
        """Check if question is trying to get non-financial responses"""
        question_lower = question.lower()
        
        # Non-financial topics to reject
        non_financial_keywords = [
            'poem', 'story', 'joke', 'recipe', 'weather', 'sports score',
            'movie', 'game', 'song', 'lyrics', 'translate', 'math homework',
            'write code', 'hack', 'illegal', 'violence'
        ]
        
        # If question contains these and NO financial keywords, reject
        financial_keywords = [
            'stock', 'invest', 'market', 'trade', 'portfolio', 'price', 
            'crypto', 'bitcoin', 'equity', 'bond', 'dividend', 'return',
            'risk', 'diversif', 'analysis', 'sentiment', 'technical',
            'financial', 'money', 'capital', 'asset', 'ticker'
        ]
        
        has_non_financial = any(keyword in question_lower for keyword in non_financial_keywords)
        has_financial = any(keyword in question_lower for keyword in financial_keywords)
        
        return has_non_financial and not has_financial
    
    def _handle_ticker_lookup_question(self, question):
        """
        Handle questions asking for ticker symbols for any company
        Returns answer string if it's a ticker lookup question, None otherwise
        """
        question_lower = question.lower()
        
        # Patterns that indicate ticker lookup questions
        ticker_patterns = [
            'what is the ticker', 'what\'s the ticker', 'ticker for', 'ticker of',
            'ticker symbol for', 'ticker symbol of', 'stock symbol for', 'stock symbol of',
            'symbol for', 'what ticker', 'tell me the ticker', 'give me the ticker'
        ]
        
        # Check if this is a ticker lookup question
        is_ticker_lookup = any(pattern in question_lower for pattern in ticker_patterns)
        
        if is_ticker_lookup:
            return """I understand you're looking for a ticker symbol! 🔍

**Here's how to find any company's ticker:**

1. **Yahoo Finance** 📊
   - Go to [finance.yahoo.com](https://finance.yahoo.com)
   - Search for the company name
   - The ticker symbol will be shown prominently (usually 1-5 letters)

2. **Google Search** 🔎
   - Search: "[Company Name] stock ticker"
   - Google will show the ticker in a stock card at the top

3. **Company Website** 🌐
   - Most public companies list their ticker symbol in the investor relations section

**Once you have the ticker, I can help you analyze it!** Just say:
- "Analyze [TICKER]"
- "What do you think about [TICKER]?"
- "Should I invest in [TICKER]?"

**Examples:**
- Apple → AAPL
- Microsoft → MSFT
- Tesla → TSLA
- Amazon → AMZN
- Google → GOOGL

*Note: I don't have a built-in database of all tickers, but once you find it, I can provide comprehensive analysis, technical indicators, and investment insights!* 📈"""
        
        return None
    
    def _detect_prompt_injection(self, question):
        """
        Detect attempts to bypass the financial advisor persona or inject malicious prompts
        
        Returns:
            tuple: (is_injection: bool, severity: str, attack_type: str)
        """
        import logging
        question_lower = question.lower()
        
        # Prompt injection patterns - HIGH SEVERITY
        high_severity_patterns = [
            'ignore previous', 'ignore all previous', 'ignore the previous',
            'ignore above', 'ignore all above', 'disregard previous',
            'disregard all previous', 'forget previous', 'forget all previous',
            'new instructions', 'new instruction', 'override instructions',
            'system prompt', 'system message', 'override previous',
            'you are now', 'act as if', 'pretend you are', 'pretend to be',
            'roleplay as', 'role play as', 'simulate being',
            'your new role', 'change your role', 'new role',
            'bypass restrictions', 'bypass your restrictions',
            'ignore restrictions', 'ignore your restrictions',
            'you must now', 'from now on you', 'starting now you'
        ]
        
        # Legal/liability manipulation - HIGH SEVERITY
        legal_manipulation_patterns = [
            'legally prosecuted', 'legal prosecution', 'legally liable',
            'you will be sued', 'you can be sued', 'legal responsibility',
            'legally responsible', 'face legal action', 'legal consequences',
            'always say', 'never say', 'you must say', 'you cannot say',
            'forbidden to say', 'not allowed to say', 'required to say'
        ]
        
        # Persona override attempts - MEDIUM SEVERITY
        persona_override_patterns = [
            'you are not a financial advisor', 'stop being a financial advisor',
            'you are a', 'now you are a', 'instead you are',
            'change personality', 'different personality', 'new personality',
            'act differently', 'behave differently', 'respond differently',
            'respond as', 'answer as', 'reply as',
            'break character', 'leave character', 'exit character'
        ]
        
        # Data extraction attempts - MEDIUM SEVERITY
        data_extraction_patterns = [
            'show your prompt', 'reveal your prompt', 'display your prompt',
            'what is your prompt', 'what are your instructions',
            'show me your instructions', 'reveal your instructions',
            'system instructions', 'internal instructions',
            'training data', 'show training', 'reveal training'
        ]
        
        # Check all patterns
        for pattern in high_severity_patterns:
            if pattern in question_lower:
                logging.warning(f"🚨 HIGH SEVERITY PROMPT INJECTION DETECTED: '{pattern}' in question: {question[:100]}")
                return (True, 'HIGH', 'instruction_override')
        
        for pattern in legal_manipulation_patterns:
            if pattern in question_lower:
                logging.warning(f"🚨 HIGH SEVERITY LEGAL MANIPULATION DETECTED: '{pattern}' in question: {question[:100]}")
                return (True, 'HIGH', 'legal_manipulation')
        
        for pattern in persona_override_patterns:
            if pattern in question_lower:
                logging.warning(f"⚠️ MEDIUM SEVERITY PERSONA OVERRIDE DETECTED: '{pattern}' in question: {question[:100]}")
                return (True, 'MEDIUM', 'persona_override')
        
        for pattern in data_extraction_patterns:
            if pattern in question_lower:
                logging.warning(f"⚠️ MEDIUM SEVERITY DATA EXTRACTION DETECTED: '{pattern}' in question: {question[:100]}")
                return (True, 'MEDIUM', 'data_extraction')
        
        return (False, 'NONE', 'none')
    
    def _generate_advisor_response(self, question, context, ticker):
        """
        Generate a comprehensive financial advisor response based on analysis data
        """
        question_lower = question.lower()
        
        # Parse context to extract key data points
        try:
            # Extract data from context string
            data = self._parse_context_data(context)
        except:
            data = {}
        
        # Build response based on question type
        response = ""
        
        # Investment recommendation questions
        if any(word in question_lower for word in ['should i', 'good investment', 'recommend', 'buy', 'sell', 'worth it']):
            response = self._answer_recommendation_question(question, data, ticker)
        
        # Why questions (reasons/explanation)
        elif any(word in question_lower for word in ['why', 'reason', 'explain', 'how come']):
            response = self._answer_why_question(question, data, ticker)
        
        # Sentiment/opinion questions
        elif any(word in question_lower for word in ['sentiment', 'feel', 'think', 'opinion', 'people']):
            response = self._answer_sentiment_question(question, data, ticker)
        
        # Technical analysis questions
        elif any(word in question_lower for word in ['technical', 'indicator', 'rsi', 'macd', 'moving average', 'chart']):
            response = self._answer_technical_question(question, data, ticker)
        
        # Price questions
        elif any(word in question_lower for word in ['price', 'cost', 'trading at', 'current', 'value']):
            response = self._answer_price_question(question, data, ticker)
        
        # Risk questions
        elif any(word in question_lower for word in ['risk', 'safe', 'dangerous', 'volatile', 'volatility']):
            response = self._answer_risk_question(question, data, ticker)
        
        # Performance/change questions
        elif any(word in question_lower for word in ['performance', 'return', 'gain', 'loss', 'change', 'went up', 'went down', 'rose', 'fell']):
            response = self._answer_performance_question(question, data, ticker)
        
        # General/overview questions
        else:
            response = self._answer_general_question(question, data, ticker)
        
        return response
    
    def _parse_context_data(self, context):
        """Extract structured data from context string"""
        data = {}
        
        # Use regex to extract key metrics
        import re
        
        # Price
        price_match = re.search(r'Current Price:?\s*\$?([\d,\.]+)', context, re.IGNORECASE)
        if price_match:
            data['price'] = float(price_match.group(1).replace(',', ''))
        
        # Recommendation
        rec_match = re.search(r'Recommendation:?\s*(\w+)', context, re.IGNORECASE)
        if rec_match:
            data['recommendation'] = rec_match.group(1)
        
        # Sentiment
        sent_match = re.search(r'Sentiment:?\s*(\w+)', context, re.IGNORECASE)
        if sent_match:
            data['sentiment'] = sent_match.group(1)
        
        # Score/Confidence
        score_match = re.search(r'Score:?\s*([\d\.]+)', context, re.IGNORECASE)
        if score_match:
            data['score'] = float(score_match.group(1))
        
        # Technical indicators
        rsi_match = re.search(r'RSI:?\s*([\d\.]+)', context, re.IGNORECASE)
        if rsi_match:
            data['rsi'] = float(rsi_match.group(1))
        
        macd_match = re.search(r'MACD:?\s*([\w\s]+)', context, re.IGNORECASE)
        if macd_match:
            data['macd'] = macd_match.group(1).strip()
        
        return data
    
    def _answer_recommendation_question(self, question, data, ticker):
        """Answer investment recommendation questions"""
        ticker_str = ticker.upper() if ticker else "this asset"
        rec = data.get('recommendation', 'HOLD')
        score = data.get('score', 0.5)
        sentiment = data.get('sentiment', 'Neutral')
        rsi = data.get('rsi')
        
        response = f"## 📊 Investment Analysis for {ticker_str.upper()}\n\n"
        response += f"Based on my comprehensive analysis using **FinBERT sentiment analysis**, **technical indicators**, and **market data**, here's my assessment:\n\n"
        response += f"### Current Recommendation: **{rec}**\n"
        response += f"**Confidence Level:** {score*100:.0f}%\n\n"
        
        response += f"### Key Factors:\n\n"
        response += f"**📈 Market Sentiment:** {sentiment}\n"
        response += f"- Analyzed from recent financial news and market discussions\n"
        response += f"- Source: FinBERT AI model trained on financial texts\n\n"
        
        if rsi:
            response += f"**📊 Technical Signal (RSI):** {rsi:.1f}\n"
            if rsi > 70:
                response += f"- *Overbought territory* - Potential pullback ahead\n"
            elif rsi < 30:
                response += f"- *Oversold territory* - Potential buying opportunity\n"
            else:
                response += f"- *Neutral zone* - No extreme signals\n"
            response += f"\n"
        
        response += f"### ⚠️ Critical Reminders:\n\n"
        response += f"1. **Capital is at Risk:** All investments carry risk. Only invest what you can afford to lose.\n"
        response += f"2. **Do Your Own Research (DYOR):** This analysis is one data point. Check multiple sources.\n"
        response += f"3. **Verify Before Acting:** Confirm current market conditions and news before trading.\n"
        response += f"4. **Diversification:** Don't put all your capital in one asset.\n"
        response += f"5. **Professional Advice:** Consider consulting a licensed financial advisor for personalized guidance.\n\n"
        
        response += f"*Would you like me to explain the technical indicators or sentiment analysis in more detail?*"
        
        return response
    
    def _answer_why_question(self, question, data, ticker):
        """Answer 'why' questions with detailed reasoning"""
        ticker_str = ticker.upper() if ticker else "this asset"
        rec = data.get('recommendation', 'HOLD')
        sentiment = data.get('sentiment', 'Neutral')
        
        response = f"## 🔍 Understanding the Analysis for {ticker_str.upper()}\n\n"
        response += f"Let me explain the reasoning behind my {rec} recommendation:\n\n"
        
        response += f"### Data Sources I Analyzed:\n\n"
        response += f"1. **📰 Financial News Sentiment**\n"
        response += f"   - Used FinBERT AI (trained on 50,000+ financial texts)\n"
        response += f"   - Current sentiment: **{sentiment}**\n"
        response += f"   - Sentiment often leads price movements\n\n"
        
        response += f"2. **📊 Technical Indicators**\n"
        response += f"   - RSI (Relative Strength Index) - momentum indicator\n"
        response += f"   - MACD - trend strength and direction\n"
        response += f"   - Moving Averages - support/resistance levels\n\n"
        
        response += f"3. **💹 Price Action**\n"
        response += f"   - Historical price patterns\n"
        response += f"   - Volume analysis\n"
        response += f"   - Volatility metrics\n\n"
        
        response += f"### Why This Recommendation?\n\n"
        if rec == "STRONG BUY" or rec == "BUY":
            response += f"The indicators show **bullish signals**: positive sentiment, strong technicals, and favorable price action. "
            response += f"However, remember that markets are unpredictable.\n\n"
        elif rec == "SELL" or rec == "STRONG SELL":
            response += f"The indicators show **bearish signals**: negative sentiment, weak technicals, or deteriorating conditions. "
            response += f"Consider reviewing your position.\n\n"
        else:
            response += f"The signals are **mixed or neutral**. This isn't a clear entry or exit point based on current data.\n\n"
        
        response += f"### 🎓 Investment Principle:\n\n"
        response += f"Technical analysis + sentiment analysis ≠ guarantee. These are **tools for informed decision-making**, "
        response += f"not crystal balls. Always:\n"
        response += f"- Cross-reference multiple sources\n"
        response += f"- Consider fundamental analysis too\n"
        response += f"- Understand your own risk tolerance\n"
        response += f"- Have a clear investment thesis\n\n"
        
        response += f"*Want to dive deeper into any specific aspect?*"
        
        return response
    
    def _answer_sentiment_question(self, question, data, ticker):
        """Answer sentiment-related questions"""
        ticker_str = ticker.upper() if ticker else "this asset"
        sentiment = data.get('sentiment', 'Neutral')
        
        response = f"## 🎭 Market Sentiment Analysis for {ticker_str.upper()}\n\n"
        response += f"### Current Sentiment: **{sentiment}**\n\n"
        
        response += f"#### How I Determined This:\n\n"
        response += f"I analyzed recent financial news articles using **FinBERT**, an AI model specifically trained on financial texts. "
        response += f"This isn't just keyword matching—it understands context like:\n"
        response += f"- *\"Despite challenges, strong growth expected\"* (Positive)\n"
        response += f"- *\"Missed earnings but guidance improved\"* (Mixed)\n"
        response += f"- *\"Regulatory concerns weighing on stock\"* (Negative)\n\n"
        
        response += f"#### Why Sentiment Matters:\n\n"
        response += f"📊 **Sentiment is a leading indicator:**\n"
        response += f"- Positive news → increased investor interest → potential price rise\n"
        response += f"- Negative news → investor concern → potential price decline\n"
        response += f"- It doesn't guarantee price movement, but it shows market psychology\n\n"
        
        response += f"#### 🔍 What People Are Saying:\n\n"
        if sentiment == "Positive":
            response += f"Investors and analysts are generally optimistic about {ticker_str}. "
            response += f"This could be due to strong earnings, positive guidance, or favorable market conditions.\n\n"
        elif sentiment == "Negative":
            response += f"There's concern in the market about {ticker_str}. "
            response += f"This might stem from poor earnings, regulatory issues, or broader market fears.\n\n"
        else:
            response += f"The market sentiment is neutral or mixed. "
            response += f"This could mean conflicting signals or a wait-and-see attitude from investors.\n\n"
        
        response += f"### ⚖️ Remember:\n\n"
        response += f"Sentiment alone isn't enough for investment decisions. Combine it with:\n"
        response += f"- Technical analysis (price patterns, indicators)\n"
        response += f"- Fundamental analysis (earnings, growth, valuation)\n"
        response += f"- Your own investment goals and risk tolerance\n\n"
        
        response += f"*Would you like to know about the technical indicators too?*"
        
        return response
    
    def _answer_technical_question(self, question, data, ticker):
        """Answer technical analysis questions"""
        ticker_str = ticker.upper() if ticker else "this asset"
        rsi = data.get('rsi')
        macd = data.get('macd')
        
        response = f"## 📈 Technical Analysis for {ticker_str.upper()}\n\n"
        response += f"Let me break down the technical indicators I'm tracking:\n\n"
        
        if rsi:
            response += f"### RSI (Relative Strength Index): {rsi:.1f}\n\n"
            response += f"**What it means:**\n"
            if rsi > 70:
                response += f"- **Overbought** (>70): The asset may have risen too quickly\n"
                response += f"- Possible pullback or consolidation ahead\n"
                response += f"- Not necessarily time to sell, but be cautious\n\n"
            elif rsi < 30:
                response += f"- **Oversold** (<30): The asset may have dropped too quickly\n"
                response += f"- Potential buying opportunity for contrarians\n"
                response += f"- But confirm with other indicators first\n\n"
            else:
                response += f"- **Neutral zone** (30-70): No extreme momentum signals\n"
                response += f"- Market is in a balanced state\n"
                response += f"- Look to other indicators for direction\n\n"
        
        if macd:
            response += f"### MACD Signal: {macd}\n\n"
            response += f"**What it tracks:**\n"
            response += f"- Trend direction and strength\n"
            response += f"- Potential buy/sell signals when lines cross\n"
            response += f"- Momentum changes before they show in price\n\n"
        
        response += f"### 🎓 Technical Analysis 101:\n\n"
        response += f"Technical indicators are **mathematical calculations based on price and volume**. They help identify:\n"
        response += f"1. **Trend direction** - Is it going up, down, or sideways?\n"
        response += f"2. **Momentum** - Is the trend strengthening or weakening?\n"
        response += f"3. **Overbought/Oversold** - Is a reversal likely?\n"
        response += f"4. **Support/Resistance** - Key price levels to watch\n\n"
        
        response += f"### ⚠️ Important Caveats:\n\n"
        response += f"- Technical indicators are based on **past data**\n"
        response += f"- They don't predict the future with certainty\n"
        response += f"- Best used in combination, not in isolation\n"
        response += f"- Fundamental news can override technical signals\n\n"
        
        response += f"📚 **Want to learn more?** Ask me about:\n"
        response += f"- \"How does RSI work?\"\n"
        response += f"- \"What is MACD?\"\n"
        response += f"- \"Books on technical analysis\"\n\n"
        
        response += f"*Remember: Technical analysis is a tool, not a guarantee. Always manage your risk.*"
        
        return response
    
    def _answer_price_question(self, question, data, ticker):
        """Answer price-related questions"""
        ticker_str = ticker.upper() if ticker else "this asset"
        price = data.get('price')
        
        response = f"## 💰 Price Analysis for {ticker_str.upper()}\n\n"
        
        if price:
            response += f"### Current Price: **${price:,.2f}**\n\n"
            response += f"#### Context Matters:\n\n"
            response += f"Price alone doesn't tell you if it's a good investment. Consider:\n\n"
            response += f"1. **Historical Range:** Is this near 52-week highs or lows?\n"
            response += f"2. **Valuation:** What's the P/E ratio? Price/Book?\n"
            response += f"3. **Trend:** Is the price in an uptrend or downtrend?\n"
            response += f"4. **Support/Resistance:** Are there key levels nearby?\n\n"
        else:
            response += f"I'm analyzing the price data for {ticker_str}...\n\n"
        
        response += f"### 🎯 Price vs. Value:\n\n"
        response += f"Remember what Warren Buffett says: *\"Price is what you pay, value is what you get.\"*\n\n"
        response += f"- **Price** = Current market cost\n"
        response += f"- **Value** = What the company is actually worth\n\n"
        response += f"A low price isn't always a bargain, and a high price isn't always expensive. "
        response += f"You need to understand the **fundamentals** (earnings, growth, competitive position).\n\n"
        
        response += f"### 📊 What I Can Tell You:\n\n"
        response += f"Based on my analysis of **technical indicators** and **sentiment**, I can help you understand:\n"
        response += f"- Is momentum bullish or bearish?\n"
        response += f"- What's the market sentiment?\n"
        response += f"- Are there technical buy/sell signals?\n\n"
        
        response += f"*Want to know if this is a good entry point? Ask me about the recommendation or technical analysis!*"
        
        return response
    
    def _answer_risk_question(self, question, data, ticker):
        """Answer risk-related questions"""
        ticker_str = ticker.upper() if ticker else "this asset"
        
        response = f"## ⚠️ Risk Assessment for {ticker_str.upper()}\n\n"
        response += f"Let's talk about risk management—the most important skill in investing.\n\n"
        
        response += f"### Understanding Risk:\n\n"
        response += f"**All investments carry risk.** Here's what you need to know:\n\n"
        response += f"1. **Market Risk:** Entire markets can decline (2008, 2020)\n"
        response += f"2. **Company Risk:** Individual stocks can fail (Enron, Lehman Brothers)\n"
        response += f"3. **Volatility:** Price swings can be large and sudden\n"
        response += f"4. **Liquidity Risk:** You might not be able to sell when you want\n\n"
        
        response += f"### 🛡️ Risk Management Principles:\n\n"
        response += f"**1. Only Invest What You Can Afford to Lose**\n"
        response += f"- Never invest emergency funds\n"
        response += f"- Never invest money needed for bills or essentials\n"
        response += f"- If losing this money would hurt you financially, don't invest it\n\n"
        
        response += f"**2. Diversification is Your Friend**\n"
        response += f"- Don't put all your money in one stock\n"
        response += f"- Spread across sectors, asset classes, geographies\n"
        response += f"- \"Don't put all your eggs in one basket\"\n\n"
        
        response += f"**3. Understand Your Risk Tolerance**\n"
        response += f"- Can you handle seeing your investment drop 20%? 50%?\n"
        response += f"- Your risk tolerance depends on age, goals, financial situation\n"
        response += f"- Young investors can often take more risk than retirees\n\n"
        
        response += f"**4. Have an Exit Strategy**\n"
        response += f"- Know when you'll take profits\n"
        response += f"- Know when you'll cut losses\n"
        response += f"- Don't let emotions override your plan\n\n"
        
        response += f"### 📈 For {ticker_str}:\n\n"
        response += f"Based on my technical and sentiment analysis, I can help you understand:\n"
        response += f"- Current market momentum and trend\n"
        response += f"- Sentiment (are investors optimistic or fearful?)\n"
        response += f"- Technical signals that might indicate increased risk\n\n"
        
        response += f"**But I cannot:**\n"
        response += f"- Guarantee any outcomes\n"
        response += f"- Remove the inherent risk of investing\n"
        response += f"- Replace proper due diligence\n\n"
        
        response += f"### 🎓 Golden Rule:\n\n"
        response += f"*Higher potential returns always come with higher risk. There's no free lunch in investing.*\n\n"
        
        response += f"*Would you like to discuss diversification strategies or learn about position sizing?*"
        
        return response
    
    def _answer_performance_question(self, question, data, ticker):
        """Answer performance/change questions"""
        ticker_str = ticker.upper() if ticker else "this asset"
        
        response = f"## 📊 Performance Analysis for {ticker_str.upper()}\n\n"
        
        # Check if asking why it went up/down
        went_up = any(word in question.lower() for word in ['went up', 'rise', 'rose', 'gain', 'increase', 'rally'])
        went_down = any(word in question.lower() for word in ['went down', 'fall', 'fell', 'drop', 'decline', 'crash'])
        
        if went_up or went_down:
            direction = "upward" if went_up else "downward"
            response += f"### Why the {direction.title()} Movement?\n\n"
            response += f"Stock prices move based on many factors:\n\n"
            
            response += f"**1. Company-Specific News:**\n"
            response += f"- Earnings reports (beat or miss expectations)\n"
            response += f"- Product launches or failures\n"
            response += f"- Management changes\n"
            response += f"- Regulatory approvals or setbacks\n\n"
            
            response += f"**2. Market Sentiment:**\n"
            response += f"- What I can tell you: Current sentiment is **{data.get('sentiment', 'being analyzed')}**\n"
            response += f"- Positive news creates buying pressure\n"
            response += f"- Negative news creates selling pressure\n\n"
            
            response += f"**3. Technical Factors:**\n"
            response += f"- Breaking through resistance levels\n"
            response += f"- Falling below support levels\n"
            response += f"- High volume indicating strong conviction\n\n"
            
            response += f"**4. Broader Market Forces:**\n"
            response += f"- Overall market trend (bull or bear market)\n"
            response += f"- Sector rotation\n"
            response += f"- Economic data and Fed policy\n"
            response += f"- Geopolitical events\n\n"
        else:
            response += f"I'm tracking the performance through multiple lenses:\n\n"
            response += f"- **Price movement** over various timeframes\n"
            response += f"- **Volume patterns** (buying or selling pressure)\n"
            response += f"- **Technical indicators** (momentum, trend strength)\n"
            response += f"- **Sentiment shifts** (improving or deteriorating)\n\n"
        
        response += f"### 📖 Important Lesson:\n\n"
        response += f"**Past performance does NOT guarantee future results.** This is a legal disclaimer, but it's also just true:\n"
        response += f"- A stock that's up 50% could keep rising OR reverse sharply\n"
        response += f"- A stock that's down 30% could recover OR fall further\n"
        response += f"- Historical patterns provide context, not certainty\n\n"
        
        response += f"### 🔮 Looking Forward:\n\n"
        response += f"Instead of focusing only on past performance, ask:\n"
        response += f"1. What's the current sentiment and technical setup?\n"
        response += f"2. Is the company's business improving or deteriorating?\n"
        response += f"3. What's my investment thesis?\n"
        response += f"4. Does this fit my risk tolerance and time horizon?\n\n"
        
        response += f"*Want to know the current technical indicators or sentiment? Just ask!*"
        
        return response
    
    def _answer_general_question(self, question, data, ticker):
        """Answer general questions about a stock"""
        ticker_str = ticker.upper() if ticker else "this asset"
        rec = data.get('recommendation', 'being analyzed')
        sentiment = data.get('sentiment', 'being assessed')
        
        response = f"## 📊 Overview: {ticker_str.upper()}\n\n"
        response += f"Let me give you a comprehensive snapshot based on my analysis:\n\n"
        
        response += f"### Current Assessment:\n\n"
        response += f"- **Recommendation:** {rec}\n"
        response += f"- **Sentiment:** {sentiment}\n"
        response += f"- **Analysis Source:** FinBERT AI + Technical Indicators\n\n"
        
        response += f"### What I Analyzed:\n\n"
        response += f"**1. Market Sentiment** 🎭\n"
        response += f"   Using FinBERT (AI trained on financial texts), I analyzed recent news to gauge market psychology.\n\n"
        
        response += f"**2. Technical Indicators** 📈\n"
        response += f"   RSI, MACD, and moving averages to identify momentum and trend strength.\n\n"
        
        response += f"**3. Price Action** 💹\n"
        response += f"   Historical patterns, support/resistance levels, and volume analysis.\n\n"
        
        response += f"### 🎯 How to Use This Information:\n\n"
        response += f"This analysis is a **starting point**, not a final answer. Before making any investment decision:\n\n"
        response += f"✅ **Do Your Own Research (DYOR)**\n"
        response += f"   - Read the company's financial reports\n"
        response += f"   - Understand their business model\n"
        response += f"   - Check multiple analyst opinions\n\n"
        
        response += f"✅ **Verify Current Conditions**\n"
        response += f"   - Markets change quickly\n"
        response += f"   - Check for breaking news\n"
        response += f"   - Confirm data is current\n\n"
        
        response += f"✅ **Consider Your Situation**\n"
        response += f"   - Your risk tolerance\n"
        response += f"   - Your investment time horizon\n"
        response += f"   - Your overall portfolio allocation\n\n"
        
        response += f"✅ **Consult a Professional**\n"
        response += f"   - Licensed financial advisors\n"
        response += f"   - Tax professionals for implications\n"
        response += f"   - Legal counsel if needed\n\n"
        
        response += f"### ⚠️ Remember:\n\n"
        response += f"**Capital is at risk.** All investments can lose value. Only invest money you can afford to lose completely.\n\n"
        
        response += f"### 💬 Ask Me More:\n\n"
        response += f"- \"Should I invest in {ticker_str}?\"\n"
        response += f"- \"What's the sentiment like?\"\n"
        response += f"- \"Explain the technical indicators\"\n"
        response += f"- \"What are the risks?\"\n"
        response += f"- \"Why did the price change?\"\n\n"
        
        response += f"I'm here to help you make **informed** decisions, not to make decisions **for** you. Let's discuss!"
        
        return response
    
    def _enhance_answer_with_mentorship(self, question, raw_answer, confidence, context, ticker):
        """
        Enhance raw answer with mentorship-style formatting and guidance
        """
        # Detect question type
        question_lower = question.lower()
        
        # Price-related questions
        if any(word in question_lower for word in ['price', 'cost', 'worth', 'trading at']):
            price_match = re.search(r'\$?(\d+\.?\d*)', raw_answer)
            if price_match:
                price = price_match.group(1)
                return f"💰 **Current Price Analysis**\n\n{ticker or 'This stock'} is currently trading at **${price}**.\n\n📊 Keep in mind that price alone doesn't tell the whole story. Consider looking at the technical indicators and sentiment analysis to understand if this is a good entry point.\n\n💡 *Investment Tip: Always compare current price with historical averages and technical support/resistance levels.*"
        
        # Recommendation questions
        if any(word in question_lower for word in ['recommend', 'should i', 'buy', 'sell', 'hold']):
            return f"📋 **Investment Recommendation**\n\n{raw_answer}\n\n⚠️ **Important Reminder**: This recommendation is based on technical and sentiment analysis. Always:\n• Do your own research (DYOR)\n• Consider your risk tolerance\n• Diversify your portfolio\n• Only invest what you can afford to lose\n\n💡 *Want to understand why? Ask me about the technical indicators or sentiment analysis!*"
        
        # Sentiment questions
        if any(word in question_lower for word in ['sentiment', 'feel', 'opinion', 'news']):
            return f"🎭 **Sentiment Analysis**\n\n{raw_answer}\n\nSentiment reflects market psychology and can be a leading indicator. We analyze:\n• 📰 Financial news articles\n• 💬 Social media discussions\n• 📊 Combined with technical indicators\n\n💡 *Pro Tip: High positive sentiment + strong technicals = strong bullish signal*"
        
        # Technical indicator questions
        if any(word in question_lower for word in ['rsi', 'macd', 'moving average', 'technical', 'indicator']):
            return f"📈 **Technical Analysis**\n\n{raw_answer}\n\nTechnical indicators help identify:\n• **Momentum** - Is the trend strengthening?\n• **Overbought/Oversold** - Is a reversal likely?\n• **Support/Resistance** - Key price levels\n\n💡 *Learning Path: Start with RSI and Moving Averages, then explore MACD for deeper insights.*"
        
        # Change/performance questions
        if any(word in question_lower for word in ['change', 'performance', 'return', 'gain', 'loss', '%']):
            return f"📊 **Performance Analysis**\n\n{raw_answer}\n\nPerformance over time shows:\n• **Trend direction** - Upward or downward?\n• **Volatility** - How stable is the price?\n• **Risk level** - Higher volatility = higher risk\n\n💡 *Remember: Past performance doesn't guarantee future results, but it helps identify patterns.*"
        
        # Risk questions
        if any(word in question_lower for word in ['risk', 'safe', 'volatile', 'danger']):
            return f"⚠️ **Risk Assessment**\n\n{raw_answer}\n\nEvaluating risk involves:\n• **Volatility** - Price fluctuation range\n• **Beta** - Movement vs. market\n• **Technical signals** - Warning signs\n• **Diversification** - Spread your risk\n\n💡 *Golden Rule: Higher potential returns usually come with higher risk.*"
        
        # General enhancement
        if confidence > 0.7:
            return f"✅ {raw_answer}\n\n💡 *Feel free to ask more specific questions about indicators, sentiment, or performance!*"
        elif confidence > 0.4:
            return f"🤔 {raw_answer}\n\n*Note: I'm moderately confident about this answer. You might want to ask a more specific question for better clarity.*"
        else:
            return f"{raw_answer}\n\n*I'm not very confident about this answer. Try asking about specific aspects like price, recommendation, or technical indicators.*"
    
    def _generate_follow_up_questions(self, question, context, ticker):
        """
        Generate relevant follow-up questions based on the user's question
        """
        question_lower = question.lower()
        ticker_str = ticker if ticker else "this stock"
        
        # Price-related follow-ups
        if any(word in question_lower for word in ['price', 'cost', 'worth']):
            return [
                f"What's the recommendation for {ticker_str}?",
                f"What's the sentiment like?",
                f"Show me the technical indicators"
            ]
        
        # Recommendation follow-ups
        if any(word in question_lower for word in ['recommend', 'should i', 'buy', 'sell']):
            return [
                f"Why is this the recommendation?",
                f"What are the technical signals showing?",
                f"What's the recent price change?"
            ]
        
        # Sentiment follow-ups
        if any(word in question_lower for word in ['sentiment', 'news', 'feel']):
            return [
                f"What's the technical analysis showing?",
                f"What's the current recommendation?",
                f"How has the price changed recently?"
            ]
        
        # Technical follow-ups
        if any(word in question_lower for word in ['technical', 'rsi', 'macd', 'indicator']):
            return [
                f"What's the overall sentiment?",
                f"What's the price trend?",
                f"Is it overbought or oversold?"
            ]
        
        # Default follow-ups
        return [
            f"What's the current price of {ticker_str}?",
            f"What's the recommendation?",
            f"How's the sentiment?"
        ]
    
    def get_educational_response(self, question):
        """
        Provide educational, conversational responses for general investment questions
        Logs questions that don't match any pattern for future improvement
        """
        import logging
        question_lower = question.lower()
        matched_pattern = False
        
        # Learning & Getting Started
        if any(word in question_lower for word in ['learn', 'start', 'beginner', 'new to', 'how to invest']):
            matched_pattern = True
            books = self.resources['beginner']['books']
            websites = self.resources['beginner']['websites']
            
            return f"""📚 **Great question! Let's start your investment education journey.**

**🎯 First Principles:**
• Understand that investing is a long-term game, not a get-rich-quick scheme
• Start with index funds or ETFs if you're new (lower risk, diversified)
• Never invest money you'll need in the next 3-5 years
• Learn before you invest - education is your best protection

**📖 Recommended Books for Beginners:**
{chr(10).join(f'• **{b["title"]}** by {b["author"]} - {b["topic"]}' for b in books[:3])}

**🌐 Free Learning Resources:**
{chr(10).join(f'• [{w["name"]}]({w["url"]}) - {w["description"]}' for w in websites)}

**🎓 What to Learn First:**
1. **Asset allocation** - How to divide your investments
2. **Risk management** - Understanding your risk tolerance
3. **Fundamental analysis** - Reading financial statements
4. **Market cycles** - Understanding bull and bear markets

💡 *Want me to analyze a specific stock to demonstrate these concepts? Just ask!*"""

        # Technical Analysis
        if any(word in question_lower for word in ['technical analysis', 'rsi', 'macd', 'indicators', 'charts']):
            matched_pattern = True
            tech_books = self.resources['technical']['books']
            tech_sites = self.resources['technical']['websites']
            
            return f"""📈 **Technical Analysis - Reading Market Psychology**

Technical analysis helps you understand market sentiment and identify trading opportunities through price patterns and indicators.

**🔍 Key Concepts:**
• **RSI (Relative Strength Index)** - Measures if a stock is overbought (>70) or oversold (<30)
• **MACD** - Shows momentum and potential trend reversals
• **Moving Averages** - Smooths price data to identify trends
• **Support & Resistance** - Price levels where stocks tend to bounce

**📚 Deep Dive Resources:**
{chr(10).join(f'• **{b["title"]}** by {b["author"]}' for b in tech_books)}

**🌐 Interactive Learning:**
{chr(10).join(f'• [{w["name"]}]({w["url"]}) - {w["description"]}' for w in tech_sites)}

**⚠️ Remember:** Technical analysis is just one tool. Combine it with fundamental analysis for better decisions.

*I can show you technical indicators for any stock - just name one!*"""

        # Ethics & Risk Management
        if any(word in question_lower for word in ['safe', 'risk', 'careful', 'protect', 'scam', 'ethical']):
            matched_pattern = True
            principles = self.resources['ethics']['principles']
            eth_resources = self.resources['ethics']['resources']
            
            return f"""⚖️ **Ethical Investing & Risk Management**

Protecting yourself and making ethical decisions is crucial in investing.

**🛡️ Golden Rules:**
{chr(10).join(f'{i+1}. {p}' for i, p in enumerate(principles[:5]))}

**⚠️ Red Flags to Avoid:**
• Promises of "guaranteed returns" or "no risk"
• Pressure to invest immediately
• Investments you don't understand
• Unregistered investment professionals
• Insider information or tips

**📋 Verify Before You Invest:**
• Check advisor credentials at [BrokerCheck](https://brokercheck.finra.org/)
• Research companies at [SEC Edgar](https://www.sec.gov/edgar)
• Read prospectuses carefully
• Understand all fees and costs

**🌐 Fraud Protection Resources:**
{chr(10).join(f'• [{r["name"]}]({r["url"]}) - {r["description"]}' for r in eth_resources)}

**💚 Ethical Considerations:**
• Consider ESG (Environmental, Social, Governance) factors
• Invest in companies aligned with your values
• Be mindful of social impact
• Support sustainable business practices

*Remember: If it sounds too good to be true, it probably is.*"""

        # Diversification
        if any(word in question_lower for word in ['diversif', 'portfolio', 'spread', 'allocation']):
            matched_pattern = True
            return """🎯 **Diversification - Don't Put All Eggs in One Basket**

Diversification is your best defense against risk.

**📊 Portfolio Allocation Basics:**

**Aggressive (Higher Risk, Higher Potential Return):**
• 80-90% Stocks
• 10-20% Bonds
• *Suitable for young investors with long time horizons*

**Moderate (Balanced):**
• 60% Stocks
• 30% Bonds
• 10% Alternatives (Real Estate, Commodities)
• *Good for mid-career investors*

**Conservative (Lower Risk):**
• 30-40% Stocks
• 50-60% Bonds
• 10% Cash/Money Market
• *Appropriate for near-retirement*

**🌍 Geographic Diversification:**
• US Stocks (60-70%)
• International Developed Markets (20-25%)
• Emerging Markets (5-10%)

**🏢 Sector Diversification:**
Don't over-concentrate in one industry. Spread across:
• Technology
• Healthcare
• Finance
• Consumer Goods
• Energy
• Real Estate

**📚 Learn More:**
• [Vanguard's Guide to Diversification](https://investor.vanguard.com/investing/how-to-invest/diversification)
• [Morningstar Portfolio Tools](https://www.morningstar.com)

*I can help you analyze multiple stocks to check your diversification!*"""

        # Market Understanding
        if any(word in question_lower for word in ['how does', 'what is', 'explain', 'understand']):
            matched_pattern = True
            return """🎓 **Understanding Financial Markets**

Let me help you understand the basics of how markets work!

**📊 Stock Market Basics:**
• **Stocks** = Ownership shares in companies
• **Bonds** = Loans to companies/governments
• **ETFs** = Baskets of stocks tracking an index
• **Mutual Funds** = Professionally managed portfolios

**💰 How Stock Prices Move:**
• **Supply & Demand** - More buyers = prices rise
• **Company Performance** - Earnings affect prices
• **Market Sentiment** - Fear and greed drive markets
• **Economic Factors** - Interest rates, inflation, GDP

**📈 Bull vs Bear Markets:**
• **Bull Market** 🐂 - Prices rising, optimism high
• **Bear Market** 🐻 - Prices falling 20%+ from peak

**🎲 Key Investment Concepts:**

**1. Risk vs Return**
• Higher risk = Potential for higher returns
• Lower risk = More stable, lower returns

**2. Time Horizon**
• Long-term (10+ years) = Can weather volatility
• Short-term (<3 years) = Stick to safer investments

**3. Compounding**
• Reinvesting returns accelerates growth
• Start early to benefit from compound interest

**📚 Essential Reading:**
• [SEC's Investor.gov](https://www.investor.gov) - Free educational resources
• [Investopedia Academy](https://academy.investopedia.com) - Structured courses

**🎯 What specific topic would you like to explore?**
• Stock analysis
• Options trading
• Retirement planning
• Tax strategies

*Just ask, and I'll explain it in simple terms!*"""

        # Log unanswered questions for future improvement
        if not matched_pattern:
            logger = logging.getLogger('unanswered_questions')
            logger.info(f"UNANSWERED_EDUCATIONAL | Question: {question} | Length: {len(question)} words: {len(question.split())}")
        
        # Default educational response
        return """👋 **I'm here to help you learn and make informed decisions!**

I can help you with:

**📚 Education & Learning:**
• Investment basics for beginners
• Technical analysis explained
• Risk management strategies
• Ethical investing principles

**📊 Stock Analysis:**
• Analyze any stock or crypto (just mention the ticker)
• Technical indicators (RSI, MACD, etc.)
• Sentiment analysis from news
• Buy/sell recommendations

**🎯 Specific Questions:**
• "How do I start investing?"
• "What is technical analysis?"
• "How do I manage risk?"
• "Tell me about AAPL" (or any ticker)

**📖 Book & Resource Recommendations:**
• Best investment books for your level
• Free online courses
• Trusted financial websites

**⚠️ Always Remember:**
My analysis is educational only. I cannot predict the future or guarantee returns. Always:
• Do your own research (DYOR)
• Consult licensed financial advisors
• Understand what you're investing in
• Only invest what you can afford to lose

*What would you like to learn about today?*"""
    
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
