"""
Flask Web Application for Portfolio Analysis
"""
from flask import Flask, render_template, request, jsonify, send_from_directory, session
from datetime import datetime
import json
import os
import logging
from src.portfolio_analyzer import PortfolioAnalyzer
from src.stock_chat import StockChatAssistant
from logging_config import setup_logging, log_security_event, log_chat_interaction, log_analysis_request, log_unanswered_question

# Setup logging first
logger = setup_logging()

app = Flask(__name__)
app.config['EXPORTS_FOLDER'] = 'exports'
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize analyzer (will load model on first request)
analyzer = None
chat_assistant = None
# Cache for storing analysis data per ticker (for chart regeneration)
analysis_cache = {}

@app.route('/')
def index():
    """Main page - Modern Bootstrap UI"""
    return render_template('index-modern.html')

@app.route('/legacy')
def legacy():
    """Legacy page for fallback"""
    return render_template('index.html')

@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    """Clear conversation history"""
    session.pop('conversation_history', None)
    session.pop('last_ticker', None)
    session.pop('conversation_tickers', None)
    return jsonify({'success': True, 'message': 'Conversation history cleared'})

@app.route('/get-chat-history', methods=['GET'])
def get_chat_history():
    """Retrieve conversation history from session"""
    history = session.get('conversation_history', [])
    last_ticker = session.get('last_ticker', '')
    return jsonify({
        'history': history,
        'last_ticker': last_ticker,
        'success': True
    })

def get_analyzer():
    global analyzer
    if analyzer is None:
        analyzer = PortfolioAnalyzer()
    return analyzer

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze portfolio endpoint"""
    global analysis_cache
    
    data = request.get_json()
    tickers = data.get('tickers', [])
    chart_type = data.get('chart_type', 'candlestick')
    timeframe = data.get('timeframe', '3mo')
    use_cache = data.get('use_cache', False)  # For chart-only updates
    
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    
    # Validate chart type
    valid_chart_types = ['candlestick', 'line', 'ohlc', 'area', 'mountain', 'volume']
    if chart_type not in valid_chart_types:
        chart_type = 'candlestick'
    
    # Validate timeframe
    valid_timeframes = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']
    if timeframe not in valid_timeframes:
        timeframe = '3mo'
    
    # Get analyzer instance
    portfolio_analyzer = get_analyzer()
    
    # If using cache (chart update only), regenerate charts from cached data
    if use_cache and len(tickers) == 1 and tickers[0] in analysis_cache:
        ticker = tickers[0]
        cached = analysis_cache[ticker]
        
        # Regenerate chart with new type
        from src.chart_generator import ChartGenerator
        chart_gen = ChartGenerator()
        chart_fig = chart_gen.create_candlestick_chart(
            ticker, 
            cached['df'], 
            cached['indicators'], 
            chart_type
        )
        
        # Return cached result with new chart
        result = cached['result'].copy()
        result['chart_data'] = chart_fig.to_json() if chart_fig else None
        result['chart_type_used'] = chart_type
        
        return jsonify({
            'results': [result],
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'from_cache': True
        })
    
    # Analyze portfolio (fresh analysis)
    results = portfolio_analyzer.analyze_portfolio(tickers, chart_type=chart_type, timeframe=timeframe)
    
    # Cache the data for each ticker (store df and indicators for chart regeneration)
    for result in results:
        if result.get('success'):
            ticker = result['ticker']
            # Re-fetch data to cache
            from src.data_fetcher import DataFetcher
            from src.technical_analyzer import TechnicalAnalyzer
            
            fetcher = DataFetcher()
            df = fetcher.fetch_historical_data(ticker, '3mo')
            
            if df is not None and not df.empty:
                tech = TechnicalAnalyzer()
                indicators = tech.calculate_indicators(df)
                
                analysis_cache[ticker] = {
                    'df': df,
                    'indicators': indicators,
                    'result': result
                }
    
    # Save results to exports folder
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_file = os.path.join(app.config['EXPORTS_FOLDER'], f'analysis_{timestamp}.json')
    
    with open(export_file, 'w') as f:
        # Remove chart HTML from JSON export (too large)
        export_data = []
        for r in results:
            r_copy = r.copy()
            r_copy.pop('chart', None)
            export_data.append(r_copy)
        json.dump(export_data, f, indent=2)
    
    return jsonify({
        'results': results,
        'export_file': export_file,
        'timestamp': timestamp
    })

@app.route('/exports/<path:filename>')
def download_export(filename):
    """Download exported analysis"""
    return send_from_directory(app.config['EXPORTS_FOLDER'], filename)

# Track conversation context across requests
chat_context = {
    'last_ticker': None,
    'last_topic': None,
    'conversation_tickers': []
}

def store_chat_in_session(question, answer, ticker=''):
    """Store chat message in session history (last 30 exchanges)"""
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    
    # Store user question
    session['conversation_history'].append({
        'role': 'user',
        'content': question,
        'ticker': ticker,
        'timestamp': datetime.now().isoformat()
    })
    
    # Store assistant answer
    session['conversation_history'].append({
        'role': 'assistant',
        'content': answer,
        'ticker': ticker,
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last 30 messages (15 exchanges)
    if len(session['conversation_history']) > 30:
        session['conversation_history'] = session['conversation_history'][-30:]
    
    # Update last ticker
    if ticker:
        session['last_ticker'] = ticker
    
    # Mark session as modified
    session.modified = True

@app.route('/chat', methods=['POST'])
def chat():
    """AI chat endpoint - Conversational and context-aware"""
    global chat_assistant, analysis_cache, chat_context
    
    data = request.get_json()
    question = data.get('question', '')
    ticker = data.get('ticker', '')
    context_ticker = data.get('context_ticker', '')  # From frontend context
    
    # Check session for last ticker if not provided
    if not context_ticker and 'last_ticker' in session:
        context_ticker = session.get('last_ticker', '')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    # Initialize chat assistant if needed
    if chat_assistant is None:
        try:
            chat_assistant = StockChatAssistant()
            chat_assistant.load_model()
        except Exception as e:
            return jsonify({'error': f'Could not load chat model: {str(e)}'}), 500
    
    question_lower = question.lower()
    
    # Check for educational questions first (highest priority)
    # These are general investing questions that don't require a specific ticker
    educational_keywords = [
        'learn', 'beginner', 'start', 'starting', 'new to', 'just starting',
        'how to invest', 'how do i invest', 'what should i', 'suggest', 'advice',
        'book', 'books', 'read', 'resource', 'course', 'education',
        'diversif', 'portfolio', 'allocation', 'asset allocation',
        'technical analysis', 'fundamental', 'fundamental analysis',
        'ethical', 'ethics', 'responsible investing', 'esg',
        'what is', 'what are', 'explain', 'definition of',
        'how does', 'how do', 'tell me about investing',
        'risk management', 'manage risk', 'how risky',
        'difference between', 'vs', 'versus', 'compare stocks',
        'trading', 'day trading', 'swing trading', 'long term',
        'dividend', 'dividends', 'passive income',
        'index fund', 'etf', 'mutual fund', 'bonds',
        'market crash', 'recession', 'bear market', 'bull market',
        'dollar cost averaging', 'dca', 'compound interest',
        'tax', 'taxes', 'capital gains', 'tax efficient'
    ]
    is_educational = any(keyword in question_lower for keyword in educational_keywords)
    
    # Special case: if question is very short or general without ticker, treat as educational
    is_general_question = (
        len(question.split()) <= 10 and 
        not ticker and 
        not any(char.isupper() for word in question.split() for char in word if len(word) > 1)
    )
    
    if (is_educational or is_general_question) and not ticker:
        educational_response = chat_assistant.get_educational_response(question)
        store_chat_in_session(question, educational_response, '')
        return jsonify({
            'question': question,
            'answer': educational_response,
            'ticker': '',
            'success': True,
            'educational': True
        })
    
    # Try to determine which ticker the user is asking about
    if not ticker:
        # 1. Try to extract ticker from question
        import re
        ticker_pattern = r'\b([A-Z]{2,5}(?:[-\.][A-Z]{2,4})?)\b'
        potential_tickers = re.findall(ticker_pattern, question)
        
        # 2. Check if extracted ticker is already analyzed
        for potential_ticker in potential_tickers:
            if potential_ticker in analysis_cache:
                ticker = potential_ticker
                chat_context['last_ticker'] = ticker
                break
        
        # 3. Use context ticker from frontend (last discussed)
        if not ticker and context_ticker and context_ticker in analysis_cache:
            ticker = context_ticker
        
        # 4. Use last_ticker from server context (for follow-up questions)
        if not ticker and chat_context['last_ticker'] and chat_context['last_ticker'] in analysis_cache:
            ticker = chat_context['last_ticker']
        
        # 5. If ticker found but not analyzed, offer background analysis
        if not ticker and potential_tickers:
            unanalyzed_ticker = potential_tickers[0]
            chat_context['last_ticker'] = unanalyzed_ticker
            
            answer = f'🔍 I can analyze **{unanalyzed_ticker}** for you!\n\nWould you like me to:\n\n1️⃣ **Analyze in background** - Quick, just answer your question\n2️⃣ **Full analysis** - Display complete analysis on screen\n\n*(Reply "background" or "full", or I\'ll do background analysis automatically)*'
            store_chat_in_session(question, answer, unanalyzed_ticker)
            return jsonify({
                'question': question,
                'answer': answer,
                'ticker': unanalyzed_ticker,
                'success': True,
                'needs_background_analysis': True,
                'pending_ticker': unanalyzed_ticker
            })
        
        # 6. No ticker found - check if it's a follow-up question
        if not ticker:
            # Check for follow-up question patterns
            follow_up_patterns = [
                'is it', 'should i', 'why', 'how come', 'what about', 'tell me more',
                'explain', 'worth it', 'good investment', 'recommend', 'buy', 'sell'
            ]
            is_follow_up = any(pattern in question_lower for pattern in follow_up_patterns)
            
            if is_follow_up and list(analysis_cache.keys()):
                # This looks like a follow-up question about analyzed stocks
                available_tickers = list(analysis_cache.keys())
                last_ticker = available_tickers[-1]  # Most recent
                
                answer = f'🤔 **Great question!** I think you\'re asking about **{last_ticker}**.\n\n'
                
                # Try to answer based on the question type
                if any(word in question_lower for word in ['good investment', 'should i buy', 'worth it', 'recommend']):
                    result = analysis_cache[last_ticker]['result']
                    rec = result.get('recommendation', 'N/A')
                    score = result.get('combined_score', 0.5)
                    reasons = result.get('reasons', [])
                    
                    answer += f'Based on my analysis:\n\n'
                    answer += f'📊 **Recommendation:** {rec}\n'
                    answer += f'📈 **Confidence Score:** {score:.1%}\n\n'
                    answer += f'**Key Factors:**\n'
                    for reason in reasons[:3]:
                        answer += f'• {reason}\n'
                    answer += f'\n⚠️ **Remember:** This is based on technical and sentiment analysis. Always:\n'
                    answer += f'• Do your own research (DYOR)\n'
                    answer += f'• Consider your risk tolerance\n'
                    answer += f'• Diversify your portfolio\n'
                    answer += f'• Consult with a financial advisor\n\n'
                    answer += f'*Want to know more? Ask about the technical indicators or sentiment!*'
                    
                    chat_context['last_ticker'] = last_ticker
                    store_chat_in_session(question, answer, last_ticker)
                    
                    return jsonify({
                        'question': question,
                        'answer': answer,
                        'ticker': last_ticker,
                        'success': True,
                        'inferred_ticker': True
                    })
                
                elif any(word in question_lower for word in ['why', 'reason', 'because']):
                    answer += f'Let me explain the analysis...\n\n'
                    ticker = last_ticker
                    # Continue to normal processing below
                
                else:
                    answer += f'*If you meant a different stock, just mention it by name!*\n\n'
                    ticker = last_ticker
                    # Continue to normal processing below
            
            # 7. Still no ticker - provide helpful guidance
            if not ticker:
                # Log this as potentially unanswered if it's a substantive question
                if len(question.split()) > 3 and not any(word in question_lower for word in ['help', 'hello', 'hi', 'hey', 'thanks', 'thank you']):
                    log_unanswered_question(
                        question=question,
                        question_type='no_ticker_found',
                        context={
                            'analyzed_tickers': list(analysis_cache.keys()) if analysis_cache else [],
                            'question_length': len(question),
                            'has_analysis': len(analysis_cache) > 0
                        }
                    )
                
                if analysis_cache:
                    available_tickers = ', '.join(analysis_cache.keys())
                    answer = f'💡 **I\'d love to help!**\n\n**Available analysis:** {available_tickers}\n\n**You can ask me:**\n• "Is {list(analysis_cache.keys())[0]} a good investment?"\n• "Why did it go up/down?"\n• "What\'s the sentiment?"\n\n**Or learn about investing:**\n• "How do I start investing?"\n• "What books should I read?"\n• "Explain technical analysis"\n\n⚠️ *My analysis is for educational purposes only. Always do your own research!*'
                else:
                    answer = '� **Welcome! I\'m your AI Investment Advisor.**\n\n**I can help you:**\n\n📊 **Analyze Stocks/Crypto:**\nJust mention any ticker (e.g., "What about AAPL?" or "Tell me about BTC-USD")\n\n📚 **Learn About Investing:**\n• "How do I start investing?"\n• "What books should I read?"\n• "Explain diversification"\n• "How do I manage risk?"\n\n**I\'ll answer naturally - just ask!**\n\n⚠️ *Educational purposes only. Not financial advice.*'
                
                store_chat_in_session(question, answer, '')
                return jsonify({
                    'question': question,
                    'answer': answer,
                    'ticker': '',
                    'success': True,
                    'general_response': True
                })
    
    # We have a ticker! Update context and get analysis
    chat_context['last_ticker'] = ticker
    if ticker not in chat_context['conversation_tickers']:
        chat_context['conversation_tickers'].append(ticker)
    
    # Check if we have analysis for this ticker
    if ticker not in analysis_cache:
        answer = f'🔍 I need to analyze **{ticker}** first!\n\nWould you like:\n\n1️⃣ **Background analysis** - Quick answer to your question\n2️⃣ **Full analysis** - Complete report with charts\n\n*(I\'ll do background analysis by default in 3 seconds...)*'
        store_chat_in_session(question, answer, ticker)
        return jsonify({
            'question': question,
            'answer': answer,
            'ticker': ticker,
            'success': True,
            'needs_background_analysis': True,
            'pending_ticker': ticker
        })
    
    # Get context from analysis cache
    cached_result = analysis_cache[ticker]['result']
    context = chat_assistant.generate_context_from_analysis(cached_result)
    
    # Check if this is a currency conversion question
    currency_keywords = ['euro', 'eur', 'euros', 'pound', 'gbp', 'pounds', 'yen', 'jpy', 'convert']
    asking_for_currency = any(keyword in question.lower() for keyword in currency_keywords)
    
    if asking_for_currency:
        price_usd = cached_result.get('current_price', 0)
        
        # Simple currency conversion rates (hardcoded for now)
        rates = {
            'eur': 0.92,
            'euro': 0.92,
            'euros': 0.92,
            'gbp': 0.79,
            'pound': 0.79,
            'pounds': 0.79,
            'jpy': 149.50,
            'yen': 149.50
        }
        
        # Try to find which currency they're asking for
        detected_currency = None
        for curr_word in ['eur', 'euro', 'euros', 'gbp', 'pound', 'pounds', 'jpy', 'yen']:
            if curr_word in question.lower():
                detected_currency = curr_word
                break
        
        if detected_currency and detected_currency in rates:
            converted_price = price_usd * rates[detected_currency]
            currency_symbol = '€' if detected_currency in ['eur', 'euro', 'euros'] else '£' if detected_currency in ['gbp', 'pound', 'pounds'] else '¥'
            currency_code = 'EUR' if detected_currency in ['eur', 'euro', 'euros'] else 'GBP' if detected_currency in ['gbp', 'pound', 'pounds'] else 'JPY'
            
            answer = f'''{ticker} is currently **{currency_symbol}{converted_price:.2f} {currency_code}**

(Converted from ${price_usd:.2f} USD using approximate exchange rate)'''
            store_chat_in_session(question, answer, ticker)
            return jsonify({
                'question': question,
                'answer': answer,
                'ticker': ticker,
                'success': True
            })
        else:
            answer = f'''I can't convert to that currency right now. I currently support:
• EUR (Euro)
• GBP (British Pound)
• JPY (Japanese Yen)

The current price is **${price_usd:.2f} USD**.'''
            store_chat_in_session(question, answer, ticker)
            return jsonify({
                'question': question,
                'answer': answer,
                'ticker': ticker,
                'success': True
            })
    
    # Answer the question
    result = chat_assistant.answer_question(question, context, ticker)
    
    # Log security warnings if present
    if result.get('security_warning'):
        log_security_event(
            event_type='prompt_injection_attempt',
            severity='HIGH',
            details={
                'question': question[:200],  # Truncate for logging
                'ticker': ticker,
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'ip_address': request.remote_addr
            },
            user_info={
                'session': request.cookies.get('session', 'anonymous'),
                'timestamp': datetime.now().isoformat()
            }
        )
        # Log chat interaction
        log_chat_interaction(
            question=question[:100],
            response_type='security_rejection',
            ticker=ticker,
            success=False
        )
    else:
        # Log normal chat interaction
        log_chat_interaction(
            question=question[:100],
            response_type='financial_advice',
            ticker=ticker,
            success=result.get('success', False)
        )
    
    # Check if confidence is too low
    if result['confidence'] < 0.3:
        # Provide helpful response based on what data we have
        available_info = f"""
I'm not sure how to answer that specific question, but here's what I know about {ticker}:

📊 **Current Price**: ${cached_result.get('current_price', 0):.2f} USD
📈 **3-Month Change**: {cached_result.get('price_change', 0):+.2f}%
💡 **Recommendation**: {cached_result.get('recommendation', 'N/A')}
🎯 **Technical Signal**: {cached_result.get('technical_signal', 'N/A')}

**I can answer questions like:**
• What's the current price?
• What's the recommendation?
• What are the technical indicators showing?
• Is the sentiment positive or negative?
• What's the RSI value?
        """.strip()
        
        store_chat_in_session(question, available_info, ticker)
        return jsonify({
            'question': question,
            'answer': available_info,
            'ticker': ticker,
            'success': True,
            'low_confidence': True
        })
    
    # Store successful chat interaction
    store_chat_in_session(question, result['answer'], ticker)
    
    return jsonify({
        'question': question,
        'answer': result['answer'],
        'ticker': ticker,
        'success': result['success']
    })

if __name__ == '__main__':
    # Ensure exports folder exists
    os.makedirs(app.config['EXPORTS_FOLDER'], exist_ok=True)
    
    print("🚀 Starting Portfolio Analysis Web Application")
    print("📊 Access the app at: http://localhost:5000")
    print("💡 The FinBERT model will load on first analysis request")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
