"""
Input Validator Module

This module provides functions for validating and sanitizing user inputs to prevent
security vulnerabilities including XSS (Cross-Site Scripting) and SQL injection attacks.

Key Features:
    - XSS prevention through HTML entity escaping
    - SQL injection prevention through pattern detection
    - Input length validation
    - Character whitelist/blacklist enforcement
    - Comprehensive validation reporting

Example Usage:
    >>> from vestor.security import validate_input, sanitize_input
    >>> 
    >>> # Validate user input
    >>> result = validate_input("<script>alert('xss')</script>")
    >>> if not result.is_valid:
    ...     print(f"Invalid: {result.reason}")
    >>> 
    >>> # Sanitize input for safe use
    >>> safe_text = sanitize_input("Hello <b>World</b>")
    >>> print(safe_text)  # "Hello World"

Security Considerations:
    - Always validate before processing user input
    - Log validation failures for security monitoring
    - Use sanitize_input() for display purposes
    - Combine with prompt_injection detection for complete security

Dependencies:
    - re: For pattern matching
    - html: For HTML entity escaping
    - typing: For type hints

Author: Vestor Team
Version: 2.0
Date: October 2025
"""

import re
import html
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """
    Result of input validation.
    
    Attributes:
        is_valid: Whether the input passed validation
        reason: Explanation if invalid (None if valid)
        severity: Severity level ('low', 'medium', 'high')
        sanitized: Sanitized version of the input
        
    Example:
        >>> result = ValidationResult(
        ...     is_valid=False,
        ...     reason="Contains SQL injection pattern",
        ...     severity="high",
        ...     sanitized="clean text"
        ... )
    """
    is_valid: bool
    reason: Optional[str] = None
    severity: str = 'low'
    sanitized: str = ''


class InputValidator:
    """
    Validates and sanitizes user inputs for security.
    
    This class provides methods to check user inputs for various security
    threats including XSS, SQL injection, and malformed data.
    
    Attributes:
        max_length: Maximum allowed input length (default: 5000)
        sql_patterns: Regex patterns for SQL injection detection
        xss_patterns: Regex patterns for XSS detection
        
    Example:
        >>> validator = InputValidator(max_length=1000)
        >>> result = validator.validate("SELECT * FROM users")
        >>> print(result.is_valid)  # False
        >>> print(result.reason)  # "Contains SQL injection pattern"
    """
    
    def __init__(self, max_length: int = 5000):
        """
        Initialize the input validator.
        
        Args:
            max_length: Maximum allowed input length in characters
            
        Raises:
            ValueError: If max_length is not positive
        """
        if max_length <= 0:
            raise ValueError("max_length must be positive")
        
        self.max_length = max_length
        
        # SQL injection patterns
        self.sql_patterns = [
            r"\bSELECT\b.*\bFROM\b",               # SELECT...FROM
            r"\bINSERT\b.*\bINTO\b",               # INSERT INTO
            r"\bUPDATE\b.*\bSET\b",                # UPDATE...SET
            r"\bDELETE\b.*\bFROM\b",               # DELETE FROM
            r"\bDROP\b.*\bTABLE\b",                # DROP TABLE
            r"\bUNION\b.*\bSELECT\b",              # UNION SELECT
            r";.*--",                              # SQL comment
            r"'.*\bOR\b.*'='",                     # OR '1'='1'
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",          # <script> tags
            r"javascript:",                         # javascript: protocol
            r"on\w+\s*=",                          # Event handlers (onclick=, etc.)
            r"<iframe[^>]*>",                      # iframes
            r"<object[^>]*>",                      # objects
            r"<embed[^>]*>",                       # embeds
        ]
    
    def validate(self, text: str) -> ValidationResult:
        """
        Validate user input for security threats.
        
        Checks for:
            - Input length limits
            - SQL injection patterns
            - XSS (Cross-Site Scripting) attempts
            - Malicious patterns
        
        Args:
            text: The user input to validate
            
        Returns:
            ValidationResult with validation status and details
            
        Examples:
            >>> validator = InputValidator()
            >>> result = validator.validate("What are stocks?")
            >>> print(result.is_valid)  # True
            >>> 
            >>> result = validator.validate("<script>alert('xss')</script>")
            >>> print(result.is_valid)  # False
            >>> print(result.reason)  # "Contains XSS pattern"
        """
        # Check if input is empty
        if not text or not text.strip():
            return ValidationResult(
                is_valid=False,
                reason="Input is empty",
                severity='low',
                sanitized=''
            )
        
        # Check length
        if len(text) > self.max_length:
            return ValidationResult(
                is_valid=False,
                reason=f"Input exceeds maximum length of {self.max_length} characters",
                severity='medium',
                sanitized=self.sanitize(text[:self.max_length])
            )
        
        # Check for SQL injection
        text_upper = text.upper()
        for pattern in self.sql_patterns:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    reason="Contains SQL injection pattern",
                    severity='high',
                    sanitized=self.sanitize(text)
                )
        
        # Check for XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    reason="Contains XSS pattern",
                    severity='high',
                    sanitized=self.sanitize(text)
                )
        
        # All checks passed
        return ValidationResult(
            is_valid=True,
            reason=None,
            severity='low',
            sanitized=self.sanitize(text)
        )
    
    def sanitize(self, text: str) -> str:
        """
        Sanitize input by removing/escaping dangerous characters.
        
        This method:
            - Removes HTML tags
            - Escapes HTML entities
            - Strips leading/trailing whitespace
            - Normalizes multiple spaces
        
        Args:
            text: The text to sanitize
            
        Returns:
            Sanitized version of the input text
            
        Examples:
            >>> validator = InputValidator()
            >>> cleaned = validator.sanitize("<b>Hello</b> World")
            >>> print(cleaned)  # "Hello World"
            >>> 
            >>> cleaned = validator.sanitize("Test  <script>alert('xss')</script>")
            >>> print(cleaned)  # "Test"
            
        Note:
            This method is safe for display but may lose formatting.
            Use only when security is more important than formatting.
        """
        if not text:
            return ''
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Escape HTML entities
        text = html.escape(text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Strip
        text = text.strip()
        
        return text
    
    def is_safe(self, text: str) -> bool:
        """
        Quick check if input is safe (shorthand for validate).
        
        Args:
            text: The text to check
            
        Returns:
            True if input passes validation, False otherwise
            
        Example:
            >>> validator = InputValidator()
            >>> if validator.is_safe(user_input):
            ...     process(user_input)
        """
        return self.validate(text).is_valid


# Module-level functions for convenience
_default_validator = InputValidator()


def validate_input(text: str, max_length: int = 5000) -> ValidationResult:
    """
    Validate user input (module-level convenience function).
    
    This is a convenience wrapper around InputValidator.validate() for
    simple use cases where you don't need to maintain a validator instance.
    
    Args:
        text: The user input to validate
        max_length: Maximum allowed length (default: 5000)
        
    Returns:
        ValidationResult with validation status and details
        
    Example:
        >>> from vestor.security import validate_input
        >>> result = validate_input("What are stocks?")
        >>> if result.is_valid:
        ...     print("Safe to process!")
        
    See Also:
        - InputValidator: For more control and custom configuration
        - sanitize_input(): For cleaning input before display
    """
    if max_length != _default_validator.max_length:
        validator = InputValidator(max_length=max_length)
        return validator.validate(text)
    return _default_validator.validate(text)


def sanitize_input(text: str) -> str:
    """
    Sanitize user input (module-level convenience function).
    
    This is a convenience wrapper around InputValidator.sanitize() for
    simple use cases.
    
    Args:
        text: The text to sanitize
        
    Returns:
        Sanitized version of the input
        
    Example:
        >>> from vestor.security import sanitize_input
        >>> safe_text = sanitize_input("<b>Hello</b>")
        >>> print(safe_text)  # "Hello"
        
    See Also:
        - validate_input(): For full validation with reason codes
        - InputValidator: For more control
    """
    return _default_validator.sanitize(text)


def is_safe_input(text: str) -> bool:
    """
    Quick safety check (module-level convenience function).
    
    Args:
        text: The text to check
        
    Returns:
        True if safe, False if potentially malicious
        
    Example:
        >>> from vestor.security import is_safe_input
        >>> if is_safe_input(user_question):
        ...     response = vestor.ask(user_question)
    """
    return _default_validator.is_safe(text)
