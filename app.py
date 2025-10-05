"""
Flask Web Application for Portfolio Analysis
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import json
import os
from src.portfolio_analyzer import PortfolioAnalyzer
from src.stock_chat import StockChatAssistant

app = Flask(__name__)
app.config['EXPORTS_FOLDER'] = 'exports'

# Initialize analyzer (will load model on first request)
analyzer = None
chat_assistant = None
# Cache for storing analysis data per ticker (for chart regeneration)
analysis_cache = {}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

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

@app.route('/chat', methods=['POST'])
def chat():
    """AI chat endpoint for stock questions"""
    global chat_assistant, analysis_cache
    
    data = request.get_json()
    question = data.get('question', '')
    ticker = data.get('ticker', '')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    # Initialize chat assistant if needed
    if chat_assistant is None:
        try:
            chat_assistant = StockChatAssistant()
            chat_assistant.load_model()
        except Exception as e:
            return jsonify({'error': f'Could not load chat model: {str(e)}'}), 500
    
    # Check if stock has been analyzed
    if ticker and ticker not in analysis_cache:
        return jsonify({
            'question': question,
            'answer': f'⚠️ I don\'t have analysis data for {ticker} yet. Please analyze this stock first using the "Analyze Portfolio" button.',
            'ticker': ticker,
            'success': False,
            'needs_analysis': True
        })
    
    # If no ticker provided, try to infer from question or provide general guidance
    if not ticker:
        # Try to extract ticker from question
        import re
        ticker_pattern = r'\b([A-Z]{2,5}(?:[-\.][A-Z]{2,4})?)\b'
        potential_tickers = re.findall(ticker_pattern, question)
        
        # Check if any extracted ticker is in our analysis cache
        for potential_ticker in potential_tickers:
            if potential_ticker in analysis_cache:
                ticker = potential_ticker
                break
        
        # If still no ticker found, provide general market guidance
        if not ticker:
            # Provide general financial advice without specific stock
            general_responses = {
                'market': '📊 For general market questions, I can help once you analyze some stocks. Common analysis includes:\n\n• **Sentiment Analysis** - How news affects stock prices\n• **Technical Indicators** - RSI, MACD, Moving Averages\n• **Buy/Sell Signals** - Based on combined sentiment + technical analysis\n\nTry analyzing stocks like AAPL, MSFT, or TSLA to get started!',
                'how': '🤔 I analyze stocks using:\n\n1. **AI Sentiment Analysis** - FinBERT analyzes news sentiment\n2. **Technical Analysis** - RSI, MACD, Bollinger Bands\n3. **Combined Score** - 40% sentiment + 60% technical indicators\n\nAdd some tickers and click "Analyze" to see it in action!',
                'recommend': '💡 To get stock recommendations:\n\n1. Add tickers (e.g., AAPL, MSFT)\n2. Click "Analyze Portfolio"\n3. I\'ll provide BUY/SELL/HOLD recommendations\n4. Then ask me questions about specific stocks!',
            }
            
            question_lower = question.lower()
            if any(word in question_lower for word in ['market', 'markets', 'generally', 'overall']):
                answer = general_responses['market']
            elif any(word in question_lower for word in ['how', 'what', 'explain', 'work']):
                answer = general_responses['how']
            elif any(word in question_lower for word in ['recommend', 'suggestion', 'advice', 'should i']):
                answer = general_responses['recommend']
            else:
                answer = '💡 I can answer questions about analyzed stocks!\n\n**To get started:**\n1. Add tickers to analyze\n2. Click "Analyze Portfolio"\n3. Ask me questions!\n\n**Or mention a ticker** in your question (e.g., "What about AAPL?")\n\n**Available stocks:** ' + (', '.join(analysis_cache.keys()) if analysis_cache else 'None yet')
            
            return jsonify({
                'question': question,
                'answer': answer,
                'ticker': '',
                'success': True,
                'general_response': True
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
            
            return jsonify({
                'question': question,
                'answer': f'''{ticker} is currently **{currency_symbol}{converted_price:.2f} {currency_code}**

(Converted from ${price_usd:.2f} USD using approximate exchange rate)''',
                'ticker': ticker,
                'success': True
            })
        else:
            return jsonify({
                'question': question,
                'answer': f'''I can't convert to that currency right now. I currently support:
• EUR (Euro)
• GBP (British Pound)
• JPY (Japanese Yen)

The current price is **${price_usd:.2f} USD**.''',
                'ticker': ticker,
                'success': True
            })
    
    # Answer the question
    result = chat_assistant.answer_question(question, context)
    
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
        
        return jsonify({
            'question': question,
            'answer': available_info,
            'ticker': ticker,
            'success': True,
            'low_confidence': True
        })
    
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
