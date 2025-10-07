"""
Chat routes - Vestor AI conversation endpoints
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime

from app.services.vestor_service import VestorService
from src.logging_config import log_chat_interaction

bp = Blueprint('chat', __name__)

# Initialize Vestor service
vestor_service = VestorService()

@bp.route('/chat', methods=['POST'])
def chat():
    """Vestor AI conversation endpoint"""
    data = request.get_json()
    question = data.get('question', '')
    ticker = data.get('ticker', '')
    context_ticker = data.get('context_ticker', '')
    
    # Check session for last ticker
    if not context_ticker and 'last_ticker' in session:
        context_ticker = session.get('last_ticker', '')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    # Get conversation history
    conversation_history = session.get('conversation_history', [])
    
    # Process with Vestor
    result = vestor_service.process_chat(
        question=question,
        ticker=ticker,
        context_ticker=context_ticker,
        conversation_history=conversation_history
    )
    
    # Extract ticker for session storage
    result_ticker = result.get('ticker', '') or result.get('pending_ticker', '')
    
    # Store in session
    _store_chat_in_session(question, result['answer'], result_ticker)
    
    # Update last_ticker
    if result_ticker:
        session['last_ticker'] = result_ticker
    
    # Log interaction
    if result.get('success'):
        log_chat_interaction(
            question=question[:100],
            response_type=result.get('vestor_mode', 'conversation'),
            ticker=result_ticker,
            success=True
        )
    
    return jsonify(result)


def _store_chat_in_session(question, answer, ticker=''):
    """Store chat message in session history"""
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    
    # Store user question
    session['conversation_history'].append({
        'role': 'user',
        'content': question,
        'ticker': ticker,
        'timestamp': datetime.now().isoformat()
    })
    
    # Store Vestor's answer
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
    
    session.modified = True
