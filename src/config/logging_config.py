"""
Logging Configuration for FinBERT Portfolio Analysis
Tracks security events, errors, and system operations
"""
import logging
import os
from datetime import datetime

def setup_logging():
    """
    Configure logging with security event tracking
    Respects LOG_LEVEL environment variable for control
    
    Environment Variables:
        LOG_LEVEL: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   Example: LOG_LEVEL=ERROR (only show errors)
                   Example: LOG_LEVEL=DEBUG (show everything)
                   Default: INFO
    """
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, f'finbert_app_{timestamp}.log')
    security_log_file = os.path.join(log_dir, f'security_{timestamp}.log')
    
    # Get log level from environment or use INFO as default
    log_level_name = os.environ.get('LOG_LEVEL', 'WARNING').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler - respects configured level
            logging.StreamHandler(),
            # File handler for all logs
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    
    # Create dedicated security logger
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.WARNING)
    
    # Security file handler (WARNING and above only)
    security_handler = logging.FileHandler(security_log_file, encoding='utf-8')
    security_handler.setLevel(logging.WARNING)
    security_formatter = logging.Formatter(
        '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
    )
    security_handler.setFormatter(security_formatter)
    security_logger.addHandler(security_handler)
    
    # Log startup
    logging.info("=" * 80)
    logging.info("FinBERT Portfolio Analysis Application Started")
    logging.info(f"Log Level: {log_level_name}")
    logging.info(f"Log file: {log_file}")
    logging.info(f"Security log: {security_log_file}")
    logging.info("=" * 80)
    
    return logging.getLogger(__name__)

def log_security_event(event_type, severity, details, user_info=None):
    """
    Log a security event with full context
    
    Args:
        event_type: Type of security event (e.g., 'prompt_injection', 'unauthorized_access')
        severity: 'HIGH', 'MEDIUM', 'LOW'
        details: Dict with event details
        user_info: Optional dict with user/session info
    """
    security_logger = logging.getLogger('security')
    
    log_message = f"""
    EVENT TYPE: {event_type}
    SEVERITY: {severity}
    TIMESTAMP: {datetime.now().isoformat()}
    DETAILS: {details}
    """
    
    if user_info:
        log_message += f"\n    USER INFO: {user_info}"
    
    if severity == 'HIGH':
        security_logger.error(log_message)
    elif severity == 'MEDIUM':
        security_logger.warning(log_message)
    else:
        security_logger.info(log_message)

def log_chat_interaction(question, response_type, ticker=None, success=True):
    """
    Log chat interactions for analysis and improvement
    
    Args:
        question: User's question (sanitized)
        response_type: Type of response ('recommendation', 'educational', etc.)
        ticker: Optional ticker symbol
        success: Whether the interaction was successful
    """
    logger = logging.getLogger('chat')
    
    log_entry = f"CHAT | Type: {response_type} | Ticker: {ticker or 'N/A'} | Success: {success} | Question: {question[:100]}"
    
    if success:
        logger.info(log_entry)
    else:
        logger.warning(log_entry)

def log_unanswered_question(question, question_type='general', context=None):
    """
    Log questions that the bot couldn't answer properly
    This helps identify patterns and improve the bot over time
    
    Args:
        question: The user's question
        question_type: Type of question ('educational', 'ticker-specific', 'comparison', etc.)
        context: Additional context (tickers available, etc.)
    """
    logger = logging.getLogger('improvement')
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'question': question,
        'question_type': question_type,
        'question_length': len(question),
        'word_count': len(question.split()),
        'context': context or {}
    }
    
    logger.info(f"UNANSWERED | Type: {question_type} | Q: {question[:150]} | Context: {context}")
    
    return log_entry

def analyze_unanswered_questions(log_file_path):
    """
    Helper function to analyze patterns in unanswered questions
    Run this periodically to identify common question types that need new handlers
    
    Args:
        log_file_path: Path to the log file
    
    Returns:
        Dict with analysis results
    """
    import re
    from collections import Counter
    
    unanswered_questions = []
    
    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                if 'UNANSWERED' in line:
                    # Extract question from log line
                    match = re.search(r'Q: (.+?) \|', line)
                    if match:
                        unanswered_questions.append(match.group(1))
    except FileNotFoundError:
        return {'error': 'Log file not found'}
    
    if not unanswered_questions:
        return {'message': 'No unanswered questions found'}
    
    # Analyze common words and patterns
    all_words = []
    for q in unanswered_questions:
        words = q.lower().split()
        all_words.extend([w for w in words if len(w) > 3])  # Skip short words
    
    common_words = Counter(all_words).most_common(20)
    
    # Identify question patterns
    patterns = {
        'what': len([q for q in unanswered_questions if q.lower().startswith('what')]),
        'how': len([q for q in unanswered_questions if q.lower().startswith('how')]),
        'why': len([q for q in unanswered_questions if q.lower().startswith('why')]),
        'should': len([q for q in unanswered_questions if 'should' in q.lower()]),
        'can': len([q for q in unanswered_questions if q.lower().startswith('can')]),
        'tell me': len([q for q in unanswered_questions if 'tell me' in q.lower()])
    }
    
    return {
        'total_unanswered': len(unanswered_questions),
        'common_words': common_words,
        'question_patterns': patterns,
        'sample_questions': unanswered_questions[:10]
    }

def log_analysis_request(tickers, user_session=None):
    """
    Log portfolio analysis requests
    
    Args:
        tickers: List of ticker symbols
        user_session: Optional session identifier
    """
    logger = logging.getLogger('analysis')
    logger.info(f"ANALYSIS REQUEST | Tickers: {', '.join(tickers)} | Session: {user_session or 'anonymous'}")

def log_error(error_type, error_message, context=None):
    """
    Log application errors with context
    
    Args:
        error_type: Type of error
        error_message: Error message
        context: Optional context information
    """
    logger = logging.getLogger('error')
    log_msg = f"ERROR | Type: {error_type} | Message: {error_message}"
    if context:
        log_msg += f" | Context: {context}"
    logger.error(log_msg)
