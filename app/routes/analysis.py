"""
Analysis routes - Stock and portfolio analysis endpoints
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from datetime import datetime
import json
import os

from app.services.analysis_service import AnalysisService

bp = Blueprint('analysis', __name__)

# Initialize service
analysis_service = AnalysisService()

@bp.route('/analyze', methods=['POST'])
def analyze():
    """Analyze portfolio endpoint"""
    data = request.get_json()
    tickers = data.get('tickers', [])
    chart_type = data.get('chart_type', 'candlestick')
    timeframe = data.get('timeframe', '3mo')
    theme = data.get('theme', 'dark')
    use_cache = data.get('use_cache', False)
    max_news = data.get('max_news', 5)
    max_social = data.get('max_social', 5)
    news_sort = data.get('news_sort', 'relevance')
    social_sort = data.get('social_sort', 'relevance')
    news_days = data.get('news_days', 3)
    social_days = data.get('social_days', 7)
    
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    
    # Validate inputs
    valid_chart_types = ['candlestick', 'line', 'ohlc', 'area', 'mountain', 'volume']
    if chart_type not in valid_chart_types:
        chart_type = 'candlestick'
    
    valid_timeframes = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']
    if timeframe not in valid_timeframes:
        timeframe = '3mo'
    
    valid_themes = ['dark', 'light']
    if theme not in valid_themes:
        theme = 'dark'
    
    # Process analysis
    results = analysis_service.analyze(
        tickers=tickers,
        chart_type=chart_type,
        timeframe=timeframe,
        theme=theme,
        use_cache=use_cache,
        max_news=max_news,
        max_social=max_social,
        news_sort=news_sort,
        social_sort=social_sort,
        news_days=news_days,
        social_days=social_days
    )
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_file = os.path.join(
        current_app.config['EXPORTS_FOLDER'], 
        f'analysis_{timestamp}.json'
    )
    
    with open(export_file, 'w') as f:
        export_data = []
        for r in results:
            r_copy = r.copy()
            r_copy.pop('chart', None)  # Remove large chart HTML
            export_data.append(r_copy)
        json.dump(export_data, f, indent=2)
    
    return jsonify({
        'results': results,
        'export_file': export_file,
        'timestamp': timestamp
    })

@bp.route('/search_ticker', methods=['GET'])
def search_ticker():
    """Search for ticker symbols by company name or ticker"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'results': []})
    
    try:
        import yfinance as yf
        import requests
        
        results = []
        query_upper = query.upper()
        
        # Method 1: Try direct ticker lookup (for when user types ticker)
        try:
            ticker_obj = yf.Ticker(query_upper)
            info = ticker_obj.info
            
            if info and info.get('symbol') and (info.get('longName') or info.get('shortName')):
                results.append({
                    'ticker': info.get('symbol', query_upper),
                    'name': info.get('longName') or info.get('shortName', ''),
                    'exchange': info.get('exchange', ''),
                    'type': info.get('quoteType', 'EQUITY')
                })
        except:
            pass
        
        # Method 2: Use Yahoo Finance search API for company name search
        try:
            search_url = f"https://query2.finance.yahoo.com/v1/finance/search"
            params = {
                'q': query,
                'quotesCount': 8,
                'newsCount': 0,
                'enableFuzzyQuery': False,
                'quotesQueryId': 'tss_match_phrase_query'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                quotes = data.get('quotes', [])
                
                for quote in quotes:
                    ticker = quote.get('symbol', '')
                    name = quote.get('longname') or quote.get('shortname', '')
                    exchange = quote.get('exchDisp', '')
                    quote_type = quote.get('quoteType', 'EQUITY')
                    
                    # Skip if already in results
                    if any(r['ticker'] == ticker for r in results):
                        continue
                    
                    # Only include stocks, ETFs, crypto
                    if quote_type in ['EQUITY', 'ETF', 'CRYPTOCURRENCY', 'MUTUALFUND', 'INDEX']:
                        results.append({
                            'ticker': ticker,
                            'name': name,
                            'exchange': exchange,
                            'type': quote_type
                        })
                    
                    if len(results) >= 10:
                        break
        except Exception as e:
            print(f"Yahoo search API error: {e}")
        
        # Method 3: If still no results, try common variations
        if len(results) == 0:
            common_suffixes = ['', '-USD', '.US', '.L', '.TO', '.AX']
            for suffix in common_suffixes:
                test_ticker = query_upper + suffix
                
                try:
                    test_obj = yf.Ticker(test_ticker)
                    test_info = test_obj.info
                    
                    if test_info and test_info.get('symbol') and (test_info.get('longName') or test_info.get('shortName')):
                        results.append({
                            'ticker': test_info.get('symbol', test_ticker),
                            'name': test_info.get('longName') or test_info.get('shortName', ''),
                            'exchange': test_info.get('exchange', ''),
                            'type': test_info.get('quoteType', 'EQUITY')
                        })
                        
                        if len(results) >= 5:
                            break
                except:
                    continue
        
        return jsonify({'results': results[:10]})  # Max 10 results
        
    except Exception as e:
        print(f"Ticker search error: {e}")
        return jsonify({'results': []})

@bp.route('/exports/<path:filename>')
def download_export(filename):
    """Download exported analysis"""
    return send_from_directory(current_app.config['EXPORTS_FOLDER'], filename)
