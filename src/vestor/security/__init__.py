"""
Security Package - Input Validation and Attack Prevention

This package provides security utilities for validating user inputs and
preventing various attacks including XSS, SQL injection, and prompt injection.

Modules:
    input_validator: Validates and sanitizes user inputs
    prompt_injection: Detects prompt injection attempts
    rate_limiter: Rate limiting to prevent abuse (future)

Example:
    >>> from vestor.security import validate_input, detect_prompt_injection
    >>> 
    >>> if not validate_input(user_question):
    ...     return "Invalid input"
    >>> 
    >>> injection_result = detect_prompt_injection(user_question)
    >>> if injection_result.is_attack:
    ...     log_security_event(injection_result)

Author: Vestor Team
Version: 2.0
Date: October 2025
"""

from .input_validator import (
    validate_input, 
    sanitize_input, 
    is_safe_input,
    ValidationResult,
    InputValidator
)
from .prompt_injection import (
    detect_prompt_injection, 
    is_safe_from_injection,
    get_injection_logger,
    InjectionResult, 
    Severity,
    PromptInjectionDetector,
    InjectionLogger
)

__all__ = [
    # Input validation functions
    'validate_input',
    'sanitize_input',
    'is_safe_input',
    'ValidationResult',
    'InputValidator',
    
    # Prompt injection detection
    'detect_prompt_injection',
    'is_safe_from_injection',
    'get_injection_logger',
    'InjectionResult',
    'Severity',
    'PromptInjectionDetector',
    'InjectionLogger'
]

__version__ = '2.0.0'
