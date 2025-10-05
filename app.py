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
from vestor_chat import process_vestor_chat
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
    """Vestor - Your AI Financial Advisor - Fully conversational, context-aware chat"""
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
    
    # ========== VESTOR CHAT LOGGING ==========
    print("\n" + "="*80)
    print(f"💬 VESTOR CONVERSATION")
    print("="*80)
    print(f"📝 User: {question}")
    print(f"🎯 Explicit Ticker: {ticker if ticker else 'None'}")
    print(f"🔄 Context Ticker: {context_ticker if context_ticker else 'None'}")
    print(f"💾 Session Last Ticker: {session.get('last_ticker', 'None')}")
    
    # Initialize Vestor (AI chat assistant) if needed
    if chat_assistant is None:
        try:
            chat_assistant = StockChatAssistant()
            chat_assistant.load_model()
            print("✅ Vestor AI loaded successfully")
        except Exception as e:
            return jsonify({'error': f'Could not load Vestor AI: {str(e)}'}), 500
    
    # Get conversation history for context
    conversation_history = session.get('conversation_history', [])
    
    # ========== USE NEW VESTOR AI PROCESSING ==========
    # This replaces all the old pattern-matching logic with AI-driven conversation
    result = process_vestor_chat(
        question=question,
        ticker=ticker,
        context_ticker=context_ticker,
        conversation_history=conversation_history,
        chat_assistant=chat_assistant,
        analysis_cache=analysis_cache,
        session=session
    )
    
    # Extract ticker from result for session storage
    result_ticker = result.get('ticker', '') or result.get('pending_ticker', '')
    
    # Store in session
    store_chat_in_session(question, result['answer'], result_ticker)
    
    # Update last_ticker in session if we have one
    if result_ticker:
        session['last_ticker'] = result_ticker
        chat_context['last_ticker'] = result_ticker
    
    # Log the interaction
    if result.get('success'):
        log_chat_interaction(
            question=question[:100],
            response_type=result.get('vestor_mode', 'conversation'),
            ticker=result_ticker,
            success=True
        )
    
    return jsonify(result)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Ensure exports folder exists
    os.makedirs(app.config['EXPORTS_FOLDER'], exist_ok=True)
    
    print("🚀 Starting Portfolio Analysis Web Application")
    print("📊 Access the app at: http://localhost:5000")
    print("💡 The FinBERT model will load on first analysis request")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
