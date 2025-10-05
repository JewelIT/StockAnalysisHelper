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
    
    # Get context from analysis cache or provide generic response
    context = ""
    if ticker and ticker in analysis_cache:
        cached_result = analysis_cache[ticker]['result']
        context = chat_assistant.generate_context_from_analysis(cached_result)
    elif ticker:
        context = f"I don't have recent analysis data for {ticker}. Please analyze this stock first."
    else:
        context = "I can answer questions about stocks you've analyzed. Please specify a ticker symbol or analyze a stock first."
    
    # Answer the question
    result = chat_assistant.answer_question(question, context)
    
    return jsonify({
        'question': question,
        'answer': result['answer'],
        'confidence': result['confidence'],
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
