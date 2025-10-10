"""
Main routes - Home page and utility endpoints
"""
from flask import Blueprint, render_template, jsonify, session, request
import time
from app.services.market_sentiment_service import get_market_sentiment_service

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main page"""
    # Cache busting parameter based on current time
    cache_bust = int(time.time())
    return render_template('index.html', cache_bust=cache_bust)

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
        service = get_market_sentiment_service()
        sentiment_data = service.get_daily_sentiment(force_refresh=force_refresh)
        return jsonify({
            'success': True,
            'data': sentiment_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
