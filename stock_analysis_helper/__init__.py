"""
StockAnalysisHelper - AI powered stock analysis and investment helper
"""

__version__ = "0.1.0"
__author__ = "JewelIT"

# Import components lazily to avoid dependency issues
__all__ = [
    "PortfolioManager",
    "MarketDataFetcher",
    "SentimentAnalyzer",
    "NewsSummarizer",
    "ChartPlotter",
    "ChatbotAssistant",
]


def __getattr__(name):
    """Lazy import to handle optional dependencies"""
    if name == "PortfolioManager":
        from .portfolio.manager import PortfolioManager
        return PortfolioManager
    elif name == "MarketDataFetcher":
        from .market.data_fetcher import MarketDataFetcher
        return MarketDataFetcher
    elif name == "SentimentAnalyzer":
        from .sentiment.analyzer import SentimentAnalyzer
        return SentimentAnalyzer
    elif name == "NewsSummarizer":
        from .news.summarizer import NewsSummarizer
        return NewsSummarizer
    elif name == "ChartPlotter":
        from .charts.plotter import ChartPlotter
        return ChartPlotter
    elif name == "ChatbotAssistant":
        from .chatbot.assistant import ChatbotAssistant
        return ChatbotAssistant
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
