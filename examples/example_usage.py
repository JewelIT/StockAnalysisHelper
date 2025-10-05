#!/usr/bin/env python3
"""
Example usage of StockAnalysisHelper components
"""

from stock_analysis_helper.portfolio import PortfolioManager
from stock_analysis_helper.market import MarketDataFetcher
from stock_analysis_helper.sentiment import SentimentAnalyzer
from stock_analysis_helper.news import NewsSummarizer
from stock_analysis_helper.charts import ChartPlotter
from stock_analysis_helper.chatbot import ChatbotAssistant


def example_portfolio_management():
    """Example of portfolio management"""
    print("\n=== Portfolio Management Example ===\n")
    
    # Create a new portfolio
    portfolio = PortfolioManager()
    
    # Add stocks
    portfolio.add_stock("AAPL", 10, 150.00)
    portfolio.add_stock("MSFT", 5, 300.00)
    
    # Add crypto
    portfolio.add_crypto("BTC", 0.5, 40000.00)
    portfolio.add_crypto("ETH", 2.0, 2500.00)
    
    # Add to watchlist
    portfolio.add_to_watchlist("TSLA", "stock")
    portfolio.add_to_watchlist("SOL", "crypto")
    
    # Get summary
    summary = portfolio.get_portfolio_summary()
    print(f"Total stocks: {summary['total_stocks']}")
    print(f"Total crypto: {summary['total_crypto']}")
    print(f"Watchlist items: {summary['watchlist_items']}")
    
    # Save portfolio
    portfolio.save_portfolio("my_portfolio.yaml")
    print("\nPortfolio saved to my_portfolio.yaml")


def example_market_data():
    """Example of fetching market data"""
    print("\n=== Market Data Example ===\n")
    
    fetcher = MarketDataFetcher()
    
    # Get stock data
    data = fetcher.get_stock_data("AAPL", period="1mo")
    print(f"AAPL data shape: {data.shape}")
    print(f"Latest close: ${data['Close'].iloc[-1]:.2f}")
    
    # Get stock info
    info = fetcher.get_stock_info("AAPL")
    print(f"\nAAPL Info:")
    print(f"  Name: {info['name']}")
    print(f"  Current Price: ${info['current_price']:.2f}")
    print(f"  Market Cap: ${info['market_cap']:,}")
    
    # Calculate returns
    returns = fetcher.calculate_returns("AAPL", "1mo")
    print(f"\nAAPL 1-month return: {returns['total_return_pct']:.2f}%")


def example_sentiment_analysis():
    """Example of sentiment analysis"""
    print("\n=== Sentiment Analysis Example ===\n")
    
    analyzer = SentimentAnalyzer()
    
    # Analyze sample texts
    texts = [
        "Apple stock surges on strong earnings report",
        "Market concerns grow over economic uncertainty",
        "Tech stocks show mixed performance today"
    ]
    
    results = analyzer.analyze_multiple(texts)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. Sentiment: {result['sentiment'].upper()} (score: {result['compound']:.3f})")
        print(f"   Text: {result['text']}")
    
    # Aggregate sentiment
    aggregated = analyzer.aggregate_sentiment(texts)
    print(f"\nOverall sentiment: {aggregated['overall_sentiment'].upper()}")
    print(f"Average score: {aggregated['average_compound']:.3f}")


def example_news_summarization():
    """Example of news summarization"""
    print("\n=== News Summarization Example ===\n")
    
    summarizer = NewsSummarizer()
    
    # Get trending news
    news = summarizer.get_trending_news(max_results=5)
    print(f"Found {len(news)} trending articles:")
    
    for i, article in enumerate(news[:3], 1):
        print(f"\n{i}. {article.get('title', 'N/A')}")
        print(f"   Source: {article.get('source', 'Unknown')}")
    
    # Search news for specific symbol
    print("\n\nSearching news for AAPL...")
    aapl_news = summarizer.search_news_for_symbol("AAPL", max_results=3)
    print(f"Found {len(aapl_news)} articles about AAPL")


def example_chart_plotting():
    """Example of chart plotting"""
    print("\n=== Chart Plotting Example ===\n")
    
    fetcher = MarketDataFetcher()
    plotter = ChartPlotter(output_dir="example_charts")
    
    # Get data and create chart
    data = fetcher.get_stock_data("AAPL", period="3mo")
    
    if not data.empty:
        # Plot price with indicators
        chart_path = plotter.plot_price_with_indicators(
            data, "AAPL", indicators=['SMA20', 'SMA50']
        )
        print(f"Created price chart: {chart_path}")
        
        # Plot RSI
        rsi_path = plotter.plot_rsi(data, "AAPL")
        print(f"Created RSI chart: {rsi_path}")
        
        # Plot MACD
        macd_path = plotter.plot_macd(data, "AAPL")
        print(f"Created MACD chart: {macd_path}")


def example_chatbot():
    """Example of chatbot usage"""
    print("\n=== Chatbot Example ===\n")
    
    chatbot = ChatbotAssistant()
    
    # Set context
    chatbot.set_context(
        portfolio_data={"total_stocks": 3, "total_crypto": 2, "watchlist_items": 3},
        market_data=[],
        sentiment_data={"overall_sentiment": "positive", "average_compound": 0.5},
        news_data={"total_articles": 10}
    )
    
    # Example conversation
    questions = [
        "Show me a summary",
        "What's the sentiment?",
        "Tell me about my portfolio"
    ]
    
    for question in questions:
        print(f"User: {question}")
        response = chatbot.chat(question)
        print(f"Bot: {response}\n")


if __name__ == "__main__":
    print("StockAnalysisHelper - Example Usage")
    print("=" * 50)
    
    # Run examples
    try:
        example_portfolio_management()
        example_market_data()
        example_sentiment_analysis()
        example_news_summarization()
        example_chart_plotting()
        example_chatbot()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
