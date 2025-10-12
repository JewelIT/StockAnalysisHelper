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
