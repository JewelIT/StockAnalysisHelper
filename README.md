# StockAnalysisHelper

An AI powered stock analysis and investment helper that leverages open-source tools and AI models to assist in investment decision-making and portfolio management.

## Features

- **📊 Portfolio Management**: Configure and track your stocks and cryptocurrency holdings
- **📈 Market Analysis**: Real-time market data fetching and analysis using Yahoo Finance
- **😊 Sentiment Analysis**: Analyze market sentiment from news articles using VADER sentiment analysis
- **📰 News Summarization**: Fetch and summarize financial news from multiple sources
- **📉 Chart Plotting**: Generate interactive charts with technical indicators (SMA, EMA, RSI, MACD)
- **🤖 AI Chatbot**: Interactive chatbot to discuss portfolio and market insights

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/JewelIT/StockAnalysisHelper.git
cd StockAnalysisHelper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys if needed
```

## Quick Start

### 1. Configure Your Portfolio

Edit the `configs/portfolio.yaml` file with your holdings:

```yaml
stocks:
  - symbol: AAPL
    shares: 10
    purchase_price: 150.00
  
  - symbol: MSFT
    shares: 5
    purchase_price: 300.00

crypto:
  - symbol: BTC
    amount: 0.5
    purchase_price: 40000.00

watchlist:
  - symbol: TSLA
    type: stock
```

### 2. Run the Analysis

```bash
python main.py --portfolio configs/portfolio.yaml
```

Or without chart generation:
```bash
python main.py --portfolio configs/portfolio.yaml --no-charts
```

## Usage Examples

### Using Individual Components

```python
from stock_analysis_helper.portfolio import PortfolioManager
from stock_analysis_helper.market import MarketDataFetcher
from stock_analysis_helper.sentiment import SentimentAnalyzer
from stock_analysis_helper.news import NewsSummarizer
from stock_analysis_helper.charts import ChartPlotter

# Portfolio management
portfolio = PortfolioManager("configs/portfolio.yaml")
summary = portfolio.get_portfolio_summary()

# Fetch market data
fetcher = MarketDataFetcher()
data = fetcher.get_stock_data("AAPL", period="1mo")
info = fetcher.get_stock_info("AAPL")

# Sentiment analysis
analyzer = SentimentAnalyzer()
sentiment = analyzer.analyze_text("Apple stock surges on strong earnings")

# News fetching
news = NewsSummarizer()
articles = news.search_news_for_symbol("AAPL", max_results=10)

# Chart plotting
plotter = ChartPlotter()
chart_path = plotter.plot_price_with_indicators(data, "AAPL", ['SMA20', 'SMA50'])
```

See `examples/example_usage.py` for more detailed examples.

## Module Overview

### Portfolio Manager (`stock_analysis_helper.portfolio`)
- Load/save portfolio configurations
- Add stocks and cryptocurrencies
- Manage watchlist
- Get portfolio summaries

### Market Data Fetcher (`stock_analysis_helper.market`)
- Fetch historical price data
- Get current prices and stock information
- Calculate returns and performance metrics
- Support for stocks and cryptocurrencies

### Sentiment Analyzer (`stock_analysis_helper.sentiment`)
- Analyze sentiment from text using VADER
- Aggregate sentiment across multiple articles
- Classify as positive, negative, or neutral

### News Summarizer (`stock_analysis_helper.news`)
- Fetch news from RSS feeds
- Search news for specific symbols
- Get trending financial news
- Extract text for sentiment analysis

### Chart Plotter (`stock_analysis_helper.charts`)
- Generate candlestick charts
- Add technical indicators (SMA, EMA, RSI, MACD)
- Create portfolio overview charts
- Export charts as PNG images

### Chatbot Assistant (`stock_analysis_helper.chatbot`)
- Interactive chat interface
- Answer questions about portfolio and market
- Provide summaries and insights
- Context-aware responses

## Configuration

### Portfolio Configuration

The portfolio configuration file (YAML or JSON) should have the following structure:

```yaml
stocks:
  - symbol: <TICKER>
    shares: <NUMBER>
    purchase_price: <PRICE>

crypto:
  - symbol: <SYMBOL>  # e.g., BTC, ETH
    amount: <AMOUNT>
    purchase_price: <PRICE>

watchlist:
  - symbol: <SYMBOL>
    type: stock|crypto
```

### Environment Variables

Optional environment variables can be set in a `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key  # For enhanced chatbot (optional)
```

## Technical Indicators

The chart plotter supports the following technical indicators:

- **SMA (Simple Moving Average)**: 20-day and 50-day periods
- **EMA (Exponential Moving Average)**: Customizable periods
- **RSI (Relative Strength Index)**: 14-day period with overbought/oversold levels
- **MACD (Moving Average Convergence Divergence)**: With signal line and histogram

## Data Sources

- **Market Data**: Yahoo Finance (via yfinance)
- **News**: Yahoo Finance RSS feeds, Seeking Alpha
- **Sentiment Analysis**: VADER (Valence Aware Dictionary and sEntiment Reasoner)

## Command Line Options

```bash
python main.py [OPTIONS]

Options:
  -p, --portfolio PATH    Path to portfolio configuration file (default: configs/portfolio.yaml)
  --no-charts            Disable chart generation
  -h, --help             Show help message
```

## Project Structure

```
StockAnalysisHelper/
├── stock_analysis_helper/     # Main package
│   ├── portfolio/             # Portfolio management
│   ├── market/                # Market data fetching
│   ├── sentiment/             # Sentiment analysis
│   ├── news/                  # News fetching and summarization
│   ├── charts/                # Chart plotting
│   └── chatbot/               # Chatbot assistant
├── configs/                   # Configuration files
│   └── portfolio.yaml         # Example portfolio
├── examples/                  # Usage examples
│   └── example_usage.py       # Example scripts
├── tests/                     # Test suite (future)
├── charts/                    # Generated charts output
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for informational and educational purposes only. It is not financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions.

## Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) for market data
- [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment) for sentiment analysis
- [mplfinance](https://github.com/matplotlib/mplfinance) for financial charts
- All other open-source libraries used in this project

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

Made with ❤️ using open-source tools and AI
