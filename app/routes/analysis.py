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
    
    # Process analysis
    results = analysis_service.analyze(
        tickers=tickers,
        chart_type=chart_type,
        timeframe=timeframe,
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

@bp.route('/exports/<path:filename>')
def download_export(filename):
    """Download exported analysis"""
    return send_from_directory(current_app.config['EXPORTS_FOLDER'], filename)
