"""
Vestor - AI-Powered Stock Market Education Chatbot

Vestor is a modular chatbot designed to educate users about stock market investing,
providing personalized guidance based on user experience levels, explaining financial
concepts, and offering analysis of stocks and market trends.

Modules:
    core: Main bot orchestration and AI model management
    conversation: Context management, intent detection, ticker resolution
    security: Input validation and prompt injection detection
    knowledge: Financial knowledge base (sectors, indicators, concepts)
    responses: Response generation and formatting

Example:
    >>> from vestor.core import VestorBot
    >>> bot = VestorBot()
    >>> response = bot.ask("What are stocks?")
    >>> print(response)

Architecture:
    This package follows a modular architecture with clear separation of concerns:
    - Security layer validates all inputs
    - Conversation layer manages context and intent
    - Knowledge layer provides financial information
    - Response layer generates formatted answers
    - Core layer orchestrates all components

Author: Vestor Team
Version: 2.0.0
Date: October 2025
License: MIT
"""

__version__ = '2.0.0'
__author__ = 'Vestor Team'
__license__ = 'MIT'

# Re-export commonly used security functions for convenience
from .security import (
    validate_input,
    sanitize_input,
    detect_prompt_injection,
    Severity
)

__all__ = [
    'validate_input',
    'sanitize_input', 
    'detect_prompt_injection',
    'Severity'
]
