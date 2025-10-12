"""
Utility Functions
Common helper functions used across the application
"""
from datetime import timedelta
import re


def format_timeframe_display(time_delta):
    """
    Convert timedelta to human-readable format
    
    Args:
        time_delta: datetime.timedelta object
        
    Returns:
        str: Human-readable time range (e.g., "5 hours", "30 minutes", "3 months", "1 week")
    """
    total_seconds = time_delta.total_seconds()
    days = time_delta.days
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    
    # Less than 1 hour - show minutes
    if total_seconds < 3600:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    # Less than 1 day - show hours
    elif days == 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    # Less than 1 week - show days
    elif days < 7:
        return f"{days} day{'s' if days != 1 else ''}"
    # Less than 1 month - show weeks
    elif days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks != 1 else ''}"
    # Less than 1 year - show months
    elif days < 365:
        months = days // 30
        return f"{months} month{'s' if months != 1 else ''}"
    # 1 year or more - show years
    else:
        years = days // 365
        return f"{years} year{'s' if years != 1 else ''}"


def format_price(price, ticker=None):
    """
    Format price with appropriate decimal places
    
    Args:
        price: float or int
        ticker: str, optional ticker symbol to determine formatting
        
    Returns:
        str: Formatted price string
    """
    if price is None:
        return "N/A"
    
    # Cryptocurrencies or very low prices need more decimals
    if ticker and ('-USD' in ticker or '-EUR' in ticker):
        if price < 1:
            return f"${price:.6f}"
        elif price < 100:
            return f"${price:.4f}"
    
    # Standard stock prices
    if price < 1:
        return f"${price:.4f}"
    else:
        return f"${price:.2f}"


def calculate_percentage_change(old_value, new_value):
    """
    Calculate percentage change with safety checks
    
    Args:
        old_value: float or int, original value
        new_value: float or int, new value
        
    Returns:
        float: Percentage change, or 0 if old_value is 0
    """
    if old_value == 0:
        return 0.0
    
    return ((new_value - old_value) / abs(old_value)) * 100


def validate_ticker(ticker):
    """
    Validate ticker symbol format
    
    Args:
        ticker: str, ticker symbol to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not ticker or not isinstance(ticker, str):
        return False
    
    # Max length check
    if len(ticker) > 10:
        return False
    
    # Pattern check: letters, numbers, dots, hyphens only
    pattern = r'^[A-Z0-9\.\-]+$'
    return bool(re.match(pattern, ticker.upper()))


def validate_timeframe(timeframe):
    """
    Validate timeframe parameter
    
    Args:
        timeframe: str, timeframe to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    valid_timeframes = ['1d', '5d', '1wk', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']
    return timeframe in valid_timeframes


def sanitize_user_input(text, max_length=1000):
    """
    Sanitize user input for chat and other text fields
    
    Args:
        text: str, input text to sanitize
        max_length: int, maximum allowed length
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Convert to string and strip whitespace
    text = str(text).strip()
    
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove potentially dangerous characters
    # Keep alphanumeric, spaces, and common punctuation
    text = re.sub(r'[^\w\s\.\,\?\!\-\'\"\:\;\(\)\@\#\$\%]', '', text)
    
    return text


def convert_analyst_rating_to_gauge(rating):
    """
    Convert analyst rating (1-5 scale) to gauge percentage (0-100)
    
    Args:
        rating: float, analyst recommendation mean (1=Strong Buy, 5=Strong Sell)
        
    Returns:
        float: Gauge percentage (0-100, higher is better)
    """
    # Invert the scale: 1 (best) -> 100%, 5 (worst) -> 0%
    return ((5 - rating) / 4) * 100


def get_recommendation_color(score):
    """
    Get color code for recommendation score
    
    Args:
        score: float, recommendation score (0-1)
        
    Returns:
        str: HTML color code
    """
    if score >= 0.7:
        return '#22c55e'  # Green - Buy
    elif score >= 0.55:
        return '#86efac'  # Light Green - Moderate Buy
    elif score >= 0.45:
        return '#fbbf24'  # Yellow - Hold
    elif score >= 0.3:
        return '#fb923c'  # Orange - Moderate Sell
    else:
        return '#ef4444'  # Red - Sell


def get_recommendation_label(score):
    """
    Get recommendation label for score
    
    Args:
        score: float, recommendation score (0-1)
        
    Returns:
        str: Recommendation label
    """
    if score >= 0.7:
        return 'STRONG BUY'
    elif score >= 0.55:
        return 'BUY'
    elif score >= 0.45:
        return 'HOLD'
    elif score >= 0.3:
        return 'SELL'
    else:
        return 'STRONG SELL'


def truncate_text(text, max_length=200, suffix='...'):
    """
    Truncate text to specified length
    
    Args:
        text: str, text to truncate
        max_length: int, maximum length
        suffix: str, suffix to add if truncated
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_large_number(number):
    """
    Format large numbers with K, M, B suffixes
    
    Args:
        number: int or float
        
    Returns:
        str: Formatted number (e.g., "1.5M", "2.3B")
    """
    if number is None:
        return "N/A"
    
    abs_number = abs(number)
    
    if abs_number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    elif abs_number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    elif abs_number >= 1_000:
        return f"{number / 1_000:.2f}K"
    else:
        return f"{number:.2f}"


def safe_divide(numerator, denominator, default=0):
    """
    Safe division with fallback
    
    Args:
        numerator: float or int
        denominator: float or int
        default: value to return if division fails
        
    Returns:
        float: Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def is_market_hours():
    """
    Check if current time is during US market hours (9:30 AM - 4:00 PM ET)
    
    Returns:
        bool: True if during market hours, False otherwise
    """
    from datetime import datetime
    import pytz
    
    try:
        et = pytz.timezone('US/Eastern')
        now = datetime.now(et)
        
        # Check if weekday (Monday=0, Sunday=6)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check time (9:30 AM - 4:00 PM)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    except:
        # If timezone check fails, assume market hours
        return True
