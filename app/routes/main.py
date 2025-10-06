"""
Main routes - Home page and utility endpoints
"""
from flask import Blueprint, render_template, jsonify, session

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main page"""
    return render_template('index.html')

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
