#!/usr/bin/env python3
"""
StockAnalysisHelper - Main Application
AI powered stock analysis and investment helper
"""

import os
import sys
from pathlib import Path
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress

from stock_analysis_helper.portfolio import PortfolioManager
from stock_analysis_helper.market import MarketDataFetcher
from stock_analysis_helper.sentiment import SentimentAnalyzer
from stock_analysis_helper.news import NewsSummarizer
from stock_analysis_helper.charts import ChartPlotter
from stock_analysis_helper.chatbot import ChatbotAssistant

console = Console()


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║       StockAnalysisHelper - AI Investment Tool        ║
    ║              Powered by Open Source AI                ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def analyze_portfolio(portfolio_path: str, output_charts: bool = True):
    """
    Main analysis function
    
    Args:
        portfolio_path: Path to portfolio configuration
        output_charts: Whether to generate charts
    """
    console.print("\n[bold green]Starting Portfolio Analysis...[/bold green]\n")
    
    # Initialize components
    portfolio_manager = PortfolioManager(portfolio_path)
    market_fetcher = MarketDataFetcher()
    sentiment_analyzer = SentimentAnalyzer()
    news_summarizer = NewsSummarizer()
    chart_plotter = ChartPlotter()
    chatbot = ChatbotAssistant()
    
    # Get portfolio summary
    portfolio_summary = portfolio_manager.get_portfolio_summary()
    console.print("[bold]Portfolio Summary:[/bold]")
    console.print(f"  Stocks: {portfolio_summary['total_stocks']}")
    console.print(f"  Crypto: {portfolio_summary['total_crypto']}")
    console.print(f"  Watchlist: {portfolio_summary['watchlist_items']}\n")
    
    # Get all symbols
    symbols = portfolio_manager.get_all_symbols()
    console.print(f"[bold]Analyzing {len(symbols)} symbols...[/bold]\n")
    
    # Fetch market data
    with Progress() as progress:
        task = progress.add_task("[cyan]Fetching market data...", total=len(symbols))
        market_summary = market_fetcher.get_market_summary(symbols)
        progress.update(task, advance=len(symbols))
    
    # Display market data
    table = Table(title="Market Summary")
    table.add_column("Symbol", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Price", style="green")
    table.add_column("Change %", style="yellow")
    
    for item in market_summary:
        if "error" not in item:
            change_style = "green" if item.get("change_pct", 0) >= 0 else "red"
            table.add_row(
                item["symbol"],
                item.get("name", "N/A")[:30],
                f"${item.get('current_price', 0):.2f}",
                f"[{change_style}]{item.get('change_pct', 0):+.2f}%[/{change_style}]"
            )
    
    console.print(table)
    console.print()
    
    # Fetch and analyze news
    console.print("[bold]Fetching news articles...[/bold]")
    all_news = []
    
    for symbol in symbols[:3]:  # Limit to first 3 symbols for demo
        news = news_summarizer.search_news_for_symbol(symbol, max_results=5)
        all_news.extend(news)
    
    news_summary = news_summarizer.summarize_news(all_news)
    console.print(f"Found {news_summary['total_articles']} articles\n")
    
    # Sentiment analysis
    if all_news:
        console.print("[bold]Analyzing sentiment...[/bold]")
        news_texts = news_summarizer.extract_text_from_articles(all_news)
        sentiment_result = sentiment_analyzer.aggregate_sentiment(news_texts)
        
        sentiment_color = {
            "positive": "green",
            "negative": "red",
            "neutral": "yellow"
        }.get(sentiment_result["overall_sentiment"], "white")
        
        console.print(Panel(
            f"Overall Sentiment: [{sentiment_color}]{sentiment_result['overall_sentiment'].upper()}[/{sentiment_color}]\n"
            f"Score: {sentiment_result['average_compound']:.3f}\n"
            f"Positive: {sentiment_result['positive_count']} | "
            f"Negative: {sentiment_result['negative_count']} | "
            f"Neutral: {sentiment_result['neutral_count']}",
            title="Sentiment Analysis",
            border_style="blue"
        ))
        console.print()
    
    # Generate charts
    if output_charts and symbols:
        console.print("[bold]Generating charts...[/bold]")
        
        for symbol in symbols[:3]:  # Generate charts for first 3 symbols
            try:
                data = market_fetcher.get_stock_data(symbol, period="3mo")
                if not data.empty:
                    chart_path = chart_plotter.plot_price_with_indicators(
                        data, symbol, indicators=['SMA20', 'SMA50']
                    )
                    console.print(f"  ✓ Created chart for {symbol}: {chart_path}")
            except Exception as e:
                console.print(f"  ✗ Error creating chart for {symbol}: {e}", style="red")
        
        console.print()
    
    # Set up chatbot context
    chatbot.set_context(
        portfolio_data=portfolio_summary,
        market_data=market_summary,
        sentiment_data=sentiment_result if all_news else {},
        news_data=news_summary
    )
    
    # Interactive chat mode
    console.print("[bold green]Analysis complete! Starting chat interface...[/bold green]")
    console.print("[dim]Type 'exit' or 'quit' to end the session[/dim]\n")
    
    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            if not user_input.strip():
                continue
            
            response = chatbot.chat(user_input)
            console.print(f"[bold green]Assistant:[/bold green] {response}\n")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="StockAnalysisHelper - AI powered stock analysis tool"
    )
    parser.add_argument(
        "--portfolio",
        "-p",
        default="configs/portfolio.yaml",
        help="Path to portfolio configuration file"
    )
    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="Disable chart generation"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check if portfolio file exists
    if not os.path.exists(args.portfolio):
        console.print(f"[red]Error: Portfolio file not found: {args.portfolio}[/red]")
        console.print("[yellow]Please create a portfolio configuration file.[/yellow]")
        console.print(f"[dim]Example: {args.portfolio}[/dim]")
        sys.exit(1)
    
    try:
        analyze_portfolio(args.portfolio, output_charts=not args.no_charts)
    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
