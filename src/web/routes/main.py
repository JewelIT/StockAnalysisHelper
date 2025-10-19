"""
Main routes - Home page and utility endpoints
"""
from flask import Blueprint, render_template, jsonify, session, request
import time
from src.web.services.market_sentiment_service import get_market_sentiment_service

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main page"""
    # Cache busting parameter based on current time
    cache_bust = int(time.time())
    return render_template('index.html', cache_bust=cache_bust)

@bp.route('/chat-trainer')
def chat_trainer():
    """Chat trainer page for collecting feedback"""
    return render_template('chat_trainer.html')

@bp.route('/clear-chat', methods=['POST'])
def clear_chat():
    """Clear Vestor conversation history"""
    session.pop('conversation_history', None)
    session.pop('last_ticker', None)
    session.pop('conversation_tickers', None)
    return jsonify({'success': True, 'message': 'Conversation history cleared'})

@bp.route('/get-chat-history', methods=['GET'])
def get_chat_history():
    """Retrieve Vestor conversation history from session"""
    history = session.get('conversation_history', [])
    last_ticker = session.get('last_ticker', '')
    return jsonify({
        'history': history,
        'last_ticker': last_ticker,
        'success': True
    })

@bp.route('/market-sentiment', methods=['GET'])
def market_sentiment():
    """Get daily market sentiment analysis"""
    try:
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        currency = request.args.get('currency', 'USD').upper()
        
        # Validate currency
        valid_currencies = ['USD', 'EUR', 'GBP', 'NATIVE']
        if currency not in valid_currencies:
            currency = 'USD'
        
        service = get_market_sentiment_service()
        sentiment_data = service.get_daily_sentiment(
            force_refresh=force_refresh,
            currency=currency
        )
        return jsonify({
            'success': True,
            'data': sentiment_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/refresh-buy-recommendations', methods=['POST'])
def refresh_buy_recommendations():
    """Refresh ONLY the buy recommendations (independent from sentiment)"""
    try:
        currency = request.args.get('currency', 'USD').upper()
        
        # Validate currency
        valid_currencies = ['USD', 'EUR', 'GBP', 'NATIVE']
        if currency not in valid_currencies:
            currency = 'USD'
        
        service = get_market_sentiment_service()
        
        # Get current cached data WITHOUT regenerating sentiment
        cached_data = service.load_cache()
        if not cached_data:
            # No cache, need full refresh
            cached_data = service.get_daily_sentiment(force_refresh=True, currency=currency)
        
        # Regenerate ONLY buy recommendations
        sector_data = cached_data.get('top_sectors', {})
        sentiment = cached_data.get('sentiment', 'NEUTRAL')
        
        buy_recs = service._generate_buy_recommendations(sector_data, sentiment, max_recommendations=10)
        buy_recs = buy_recs[:3]  # Top 3
        
        # Update cache with new buy recommendations
        cached_data['buy_recommendations'] = buy_recs
        service.save_cache(cached_data)
        
        # Convert currency if needed
        converted_data = service._convert_sentiment_currency(cached_data, currency)
        
        return jsonify({
            'success': True,
            'buy_recommendations': converted_data.get('buy_recommendations', [])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/refresh-sell-recommendations', methods=['POST'])
def refresh_sell_recommendations():
    """Refresh ONLY the sell recommendations (independent from sentiment and buy recs)"""
    try:
        currency = request.args.get('currency', 'USD').upper()
        
        # Validate currency
        valid_currencies = ['USD', 'EUR', 'GBP', 'NATIVE']
        if currency not in valid_currencies:
            currency = 'USD'
        
        service = get_market_sentiment_service()
        
        # Get current cached data WITHOUT regenerating sentiment
        cached_data = service.load_cache()
        if not cached_data:
            # No cache, need full refresh
            cached_data = service.get_daily_sentiment(force_refresh=True, currency=currency)
        
        # Regenerate ONLY sell recommendations (exclude current buy tickers)
        sector_data = cached_data.get('top_sectors', {})
        sentiment = cached_data.get('sentiment', 'NEUTRAL')
        buy_tickers = {r['ticker'] for r in cached_data.get('buy_recommendations', [])}
        
        sell_recs = service._generate_sell_recommendations(
            sector_data, sentiment, 
            max_recommendations=10,
            excluded_tickers=buy_tickers
        )
        sell_recs = sell_recs[:3]  # Top 3
        
        # Update cache with new sell recommendations
        cached_data['sell_recommendations'] = sell_recs
        service.save_cache(cached_data)
        
        # Convert currency if needed
        converted_data = service._convert_sentiment_currency(cached_data, currency)
        
        return jsonify({
            'success': True,
            'sell_recommendations': converted_data.get('sell_recommendations', [])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
