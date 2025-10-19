"""
Configuration Module
Central location for all configuration constants and settings
"""

class Config:
    """Application configuration constants"""
    
    # ==================== DATA FETCHING ====================
    
    # Interval configurations for different timeframes
    INTRADAY_INTERVAL = "30m"      # 30-minute intervals for 1 day
    WEEKLY_INTERVAL = "1h"         # Hourly intervals for 1 week
    DAILY_INTERVAL = "1d"          # Daily intervals for longer periods
    
    # Timeframe to interval mapping
    # For intraday timeframes, we need to map to both period and interval
    INTERVAL_MAP = {
        # Intraday (these are intervals, not periods - handled specially)
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "3h": "3h",      # Not supported by yfinance, will use 1h
        "6h": "6h",      # Not supported by yfinance, will use 1h
        "12h": "12h",    # Not supported by yfinance, will use 1h
        # Daily and longer
        "1d": INTRADAY_INTERVAL,
        "5d": DAILY_INTERVAL,
        "1wk": DAILY_INTERVAL,
        "1mo": DAILY_INTERVAL,
        "3mo": DAILY_INTERVAL,
        "6mo": WEEKLY_INTERVAL,
        "1y": WEEKLY_INTERVAL,
        "2y": WEEKLY_INTERVAL,
        "5y": WEEKLY_INTERVAL,
        "max": WEEKLY_INTERVAL,
    }
    
    # ==================== TECHNICAL INDICATORS ====================
    
    # Minimum data points required for analysis
    MIN_DATA_POINTS = 5
    
    # Standard indicator windows (when enough data is available)
    STANDARD_SMA_SHORT = 20
    STANDARD_SMA_LONG = 50
    STANDARD_RSI_WINDOW = 14
    STANDARD_MACD_FAST = 12
    STANDARD_MACD_SLOW = 26
    STANDARD_MACD_SIGNAL = 9
    STANDARD_BB_WINDOW = 20
    
    # Adaptive window calculation functions
    # These scale down for limited data
    @staticmethod
    def adaptive_sma_short(data_points):
        return min(20, max(5, data_points // 3))
    
    @staticmethod
    def adaptive_sma_long(data_points):
        return min(50, max(10, data_points // 2))
    
    @staticmethod
    def adaptive_rsi(data_points):
        return min(14, max(5, data_points // 4))
    
    @staticmethod
    def adaptive_macd_fast(data_points):
        return min(12, max(3, data_points // 5))
    
    @staticmethod
    def adaptive_macd_slow(data_points):
        return min(26, max(6, data_points // 3))
    
    @staticmethod
    def adaptive_macd_signal(data_points):
        return min(9, max(3, data_points // 6))
    
    @staticmethod
    def adaptive_bb_window(data_points):
        return min(20, max(5, data_points // 3))
    
    # ==================== ANALYST CONSENSUS ====================
    
    # Minimum number of analysts required for consensus
    ANALYST_MIN_COVERAGE = 2
    
    # Coverage level thresholds
    ANALYST_LIMITED_THRESHOLD = 4      # 2-4 analysts = limited
    ANALYST_STANDARD_THRESHOLD = 9     # 5-9 analysts = standard
    ANALYST_STRONG_THRESHOLD = 10      # 10+ analysts = strong
    
    # Analyst recommendation scale (Yahoo Finance)
    ANALYST_SCALE_MIN = 1.0  # Strong Buy
    ANALYST_SCALE_MAX = 5.0  # Strong Sell
    
    # ==================== RECOMMENDATION WEIGHTS ====================
    
    # With analyst data available
    WEIGHT_SENTIMENT_WITH_ANALYST = 0.20
    WEIGHT_TECHNICAL_WITH_ANALYST = 0.30
    WEIGHT_ANALYST = 0.50
    
    # Without analyst data
    WEIGHT_SENTIMENT_NO_ANALYST = 0.40
    WEIGHT_TECHNICAL_NO_ANALYST = 0.60
    
    # Cryptocurrency-specific weights (no analyst data, news sentiment unreliable)
    # Crypto moves on technical + on-chain data, NOT news sentiment
    WEIGHT_CRYPTO_SENTIMENT_NO_ANALYST = 0.10  # Minimal weight - crypto sentiment inflated
    WEIGHT_CRYPTO_TECHNICAL_NO_ANALYST = 0.90  # Dominant weight - technical is king for crypto
    
    # ==================== CHART VISUALIZATION ====================
    
    # Gauge chart dimensions
    GAUGE_WIDTH = 280
    GAUGE_HEIGHT = 180
    GAUGE_MARGIN = {'t': 10, 'r': 10, 'b': 10, 'l': 10}
    
    # Chart heights
    CHART_HEIGHT_STANDARD = 800
    CHART_HEIGHT_VOLUME = 900
    
    # Chart row heights (as proportions)
    CHART_ROWS_STANDARD = [0.6, 0.2, 0.2]      # Price, MACD, RSI
    CHART_ROWS_VOLUME = [0.4, 0.2, 0.2, 0.2]   # Price, Volume, MACD, RSI
    
    # Chart colors
    COLOR_BULLISH = '#26a69a'
    COLOR_BEARISH = '#ef5350'
    COLOR_MACD = '#2196F3'
    COLOR_SIGNAL = '#FF9800'
    COLOR_RSI = '#9C27B0'
    COLOR_SMA_20 = 'orange'
    COLOR_SMA_50 = 'blue'
    COLOR_BB = 'gray'
    
    # Gauge color ranges (0-100 scale, inverted from 1-5 analyst scale)
    GAUGE_COLORS = [
        (0, 20, '#ef4444'),      # Strong Sell - Red
        (20, 40, '#fb923c'),     # Sell - Orange
        (40, 60, '#fbbf24'),     # Hold - Yellow
        (60, 80, '#86efac'),     # Buy - Light Green
        (80, 100, '#22c55e')     # Strong Buy - Green
    ]
    
    # ==================== NEWS & SOCIAL MEDIA ====================
    
    # Default limits
    DEFAULT_MAX_NEWS = 10
    DEFAULT_MAX_SOCIAL = 10
    DEFAULT_NEWS_DAYS = 7
    DEFAULT_SOCIAL_DAYS = 7
    
    # Valid sort options
    VALID_SORT_OPTIONS = ['relevance', 'latest', 'oldest']
    
    # ==================== API RATE LIMITS ====================
    
    # Rate limiting (requests per time period)
    RATE_LIMIT_REQUESTS = 200
    RATE_LIMIT_PERIOD = "day"  # Options: "second", "minute", "hour", "day"
    
    # ==================== CACHING ====================
    
    # Cache timeouts (seconds)
    CACHE_STOCK_DATA = 300         # 5 minutes
    CACHE_ANALYST_DATA = 3600      # 1 hour
    CACHE_NEWS_DATA = 1800         # 30 minutes
    CACHE_SOCIAL_DATA = 900        # 15 minutes
    
    # ==================== UI PREFERENCES ====================
    
    # Chart types
    CHART_TYPES = ['candlestick', 'line', 'ohlc', 'area', 'volume', 'mountain']
    DEFAULT_CHART_TYPE = 'candlestick'
    
    # Timeframes
    VALID_TIMEFRAMES = ['1d', '1wk', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']
    DEFAULT_TIMEFRAME = '3mo'
    
    # ==================== LOGGING ====================
    
    # Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
    # Set via environment variable: LOG_LEVEL=ERROR or LOG_LEVEL=DEBUG
    LOG_LEVEL = 'INFO'  # Default level (can be overridden by environment)
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'flask.log'
    LOG_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Console/Browser debugging
    # Set DEBUG_MODE=true in environment to enable verbose frontend logging
    DEBUG_MODE = False  # Set to True to enable console.log statements
    
    # ==================== SECURITY ====================
    
    # Input validation
    MAX_TICKER_LENGTH = 10
    MAX_CHAT_MESSAGE_LENGTH = 1000
    ALLOWED_TICKER_PATTERN = r'^[A-Z0-9\.\-]+$'
    
    # Session
    SESSION_TIMEOUT = 3600  # 1 hour
    
    # ==================== HELPER METHODS ====================
    
    @staticmethod
    def get_interval_for_period(period):
        """Get appropriate interval for a given period"""
        return Config.INTERVAL_MAP.get(period, Config.DAILY_INTERVAL)
    
    @staticmethod
    def get_coverage_level(num_analysts):
        """Determine analyst coverage level"""
        if num_analysts >= Config.ANALYST_STRONG_THRESHOLD:
            return 'strong'
        elif num_analysts >= Config.ANALYST_LIMITED_THRESHOLD + 1:
            return 'standard'
        elif num_analysts >= Config.ANALYST_MIN_COVERAGE:
            return 'limited'
        else:
            return 'none'
    
    @staticmethod
    def is_cryptocurrency(ticker: str) -> bool:
        """
        Detect if a ticker symbol represents a cryptocurrency
        
        Cryptocurrencies typically:
        - End with -USD, -EUR, -GBP, -JPY (fiat pair)
        - Are known crypto symbols (BTC, ETH, XRP, etc.)
        - Don't appear in stock markets
        """
        if not ticker:
            return False
        
        ticker_upper = ticker.upper()
        
        # Check for fiat currency pairs (crypto indicator)
        fiat_suffixes = ('-USD', '-EUR', '-GBP', '-JPY', '-AUD', '-CAD', '-CHF')
        if any(ticker_upper.endswith(suffix) for suffix in fiat_suffixes):
            # Get the base symbol without the fiat pair
            base = ticker_upper.split('-')[0]
            # Common crypto tickers
            known_cryptos = {
                'BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LTC', 'BCH', 'EOS', 'XLM',
                'LINK', 'XMR', 'ZEC', 'DOGE', 'USDT', 'USDC', 'DAI', 'BUSD',
                'SOL', 'AVAX', 'MATIC', 'FTX', 'NEAR', 'APT', 'ARB', 'OP',
                'ATOM', 'ICP', 'ALGO', 'FLOW', 'FIL', 'AAVE', 'UNI', 'SUSHI',
                'CAKE', 'CRV', 'SNX', 'MKR', 'COMP', 'YEARN'
            }
            return base in known_cryptos
        
        return False
    
    @staticmethod
    def get_recommendation_weights(has_analyst_data, is_crypto=False):
        """
        Get recommendation weights based on data availability and asset type
        
        Args:
            has_analyst_data: Whether analyst consensus data is available
            is_crypto: Whether this is a cryptocurrency (affects weighting)
        """
        if is_crypto and not has_analyst_data:
            # Crypto: minimize sentiment (unreliable), maximize technical
            return {
                'sentiment': Config.WEIGHT_CRYPTO_SENTIMENT_NO_ANALYST,
                'technical': Config.WEIGHT_CRYPTO_TECHNICAL_NO_ANALYST,
                'analyst': 0.0
            }
        elif has_analyst_data:
            return {
                'sentiment': Config.WEIGHT_SENTIMENT_WITH_ANALYST,
                'technical': Config.WEIGHT_TECHNICAL_WITH_ANALYST,
                'analyst': Config.WEIGHT_ANALYST
            }
        else:
            return {
                'sentiment': Config.WEIGHT_SENTIMENT_NO_ANALYST,
                'technical': Config.WEIGHT_TECHNICAL_NO_ANALYST,
                'analyst': 0.0
            }


# Convenience exports
MIN_DATA_POINTS = Config.MIN_DATA_POINTS
ANALYST_MIN_COVERAGE = Config.ANALYST_MIN_COVERAGE
DEFAULT_TIMEFRAME = Config.DEFAULT_TIMEFRAME
DEFAULT_CHART_TYPE = Config.DEFAULT_CHART_TYPE
