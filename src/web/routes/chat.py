"""
Chat routes - Vestor AI conversation endpoints
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
import os
from pathlib import Path

from src.web.services.vestor_service import VestorService
from src.config.logging_config import log_chat_interaction

bp = Blueprint('chat', __name__)

# Feedback log file
FEEDBACK_LOG_FILE = Path('logs/chat_feedback.jsonl')

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


@bp.route('/chat-trainer', methods=['POST'])
def chat_trainer():
    """
    Chat endpoint with feedback collection for training.
    Returns answer + session ID for later feedback submission.
    """
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
    
    # Generate unique interaction ID
    interaction_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Store interaction for potential feedback
    _store_trainer_interaction(
        interaction_id=interaction_id,
        question=question,
        answer=result['answer'],
        ticker=result_ticker,
        vestor_mode=result.get('vestor_mode', 'conversation')
    )
    
    # Store in session
    _store_chat_in_session(question, result['answer'], result_ticker)
    
    # Update last_ticker
    if result_ticker:
        session['last_ticker'] = result_ticker
    
    # Return result with interaction ID for feedback
    return jsonify({
        **result,
        'interaction_id': interaction_id,
        'feedback_enabled': True
    })


@bp.route('/chat-trainer/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback for a chat interaction.
    Accepts rating (0-5) or thumbs up/down (yes/no).
    """
    data = request.get_json()
    interaction_id = data.get('interaction_id')
    
    # Rating can be numeric (0-5) or boolean (yes/no, thumbs up/down)
    rating = data.get('rating')  # 0-5 scale
    thumbs = data.get('thumbs')  # 'up' or 'down'
    helpful = data.get('helpful')  # True/False
    comment = data.get('comment', '')  # Optional text feedback
    
    if not interaction_id:
        return jsonify({'error': 'No interaction_id provided'}), 400
    
    if rating is None and thumbs is None and helpful is None:
        return jsonify({'error': 'No feedback provided (rating, thumbs, or helpful required)'}), 400
    
    # Normalize feedback to a common format
    feedback = {
        'interaction_id': interaction_id,
        'timestamp': datetime.now().isoformat(),
        'feedback': {}
    }
    
    if rating is not None:
        # Validate rating is 0-5
        try:
            rating_num = int(rating)
            if 0 <= rating_num <= 5:
                feedback['feedback']['rating'] = rating_num
                feedback['feedback']['helpful'] = rating_num >= 3  # 3+ = helpful
            else:
                return jsonify({'error': 'Rating must be between 0 and 5'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid rating value'}), 400
    
    if thumbs is not None:
        thumbs_str = str(thumbs).lower()
        if thumbs_str in ['up', 'down', 'yes', 'no', 'true', 'false']:
            is_positive = thumbs_str in ['up', 'yes', 'true']
            feedback['feedback']['thumbs'] = 'up' if is_positive else 'down'
            feedback['feedback']['helpful'] = is_positive
            # Convert to rating scale (thumbs up = 4, thumbs down = 1)
            feedback['feedback']['rating'] = 4 if is_positive else 1
        else:
            return jsonify({'error': 'Thumbs must be up/down or yes/no'}), 400
    
    if helpful is not None:
        feedback['feedback']['helpful'] = bool(helpful)
        if 'rating' not in feedback['feedback']:
            # Convert boolean to rating (True = 4, False = 1)
            feedback['feedback']['rating'] = 4 if helpful else 1
    
    if comment:
        feedback['feedback']['comment'] = comment[:500]  # Limit comment length
    
    # Add user agent and IP (for analysis, not identification)
    feedback['metadata'] = {
        'user_agent': request.headers.get('User-Agent', '')[:200],
        'ip_hash': hash(request.remote_addr) % 10000  # Anonymized
    }
    
    # Log the feedback
    success = _log_feedback(feedback)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Feedback received! Thank you for helping improve the chatbot.',
            'interaction_id': interaction_id
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to log feedback. Please try again.',
            'interaction_id': interaction_id
        }), 500


def _store_trainer_interaction(interaction_id, question, answer, ticker, vestor_mode):
    """Store interaction temporarily for feedback correlation"""
    # Store in session for correlation with feedback
    if 'trainer_interactions' not in session:
        session['trainer_interactions'] = {}
    
    session['trainer_interactions'][interaction_id] = {
        'question': question,
        'answer': answer[:500],  # Store truncated answer
        'ticker': ticker,
        'vestor_mode': vestor_mode,
        'timestamp': datetime.now().isoformat()
    }
    
    # Keep only last 10 interactions
    if len(session['trainer_interactions']) > 10:
        # Remove oldest
        oldest_key = min(session['trainer_interactions'].keys())
        del session['trainer_interactions'][oldest_key]
    
    session.modified = True


def _log_feedback(feedback_data):
    """
    Log feedback to JSONL file for later analysis.
    Each line is a complete JSON object.
    """
    try:
        # Ensure logs directory exists
        FEEDBACK_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to get the original interaction from session
        interaction_id = feedback_data['interaction_id']
        if 'trainer_interactions' in session:
            original = session['trainer_interactions'].get(interaction_id)
            if original:
                feedback_data['interaction'] = original
        
        # Append to JSONL file (one JSON object per line)
        with open(FEEDBACK_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_data) + '\n')
        
        return True
    except Exception as e:
        print(f"Error logging feedback: {e}")
        return False
