# 📊 AI Stock Portfolio Analyzer

**Professional-grade stock and cryptocurrency analysis powered by AI sentiment analysis, technical indicators, and interactive visualizations.**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

---

## 🚀 Quick Start for Non-Technical Users

**Choose your preferred installation method:**

### 🐳 Docker (Recommended - Works Everywhere)
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Run:
   ```bash
   ./start-docker.sh
   ```
3. Open http://localhost:5000 in your browser

### 💻 One-Click Installers
- **Windows**: Run `install-windows.bat`
- **Linux/Mac**: Run `./start-docker.sh`

### 📦 For Developers
```bash
pip install -r requirements.txt
python3 app.py
```

**See [DISTRIBUTION.md](DISTRIBUTION.md) for packaging and deployment options.**

---

## ✨ Features

### 🤖 AI-Powered Analysis
- **FinBERT Sentiment** - Financial news analysis using state-of-the-art NLP (440MB model)
- **Twitter-RoBERTa** - Social media sentiment from tweets and discussions (501MB model)
- **DistilBERT Chat** - Interactive Q&A assistant for stock queries (250MB model)

### 📈 Technical Analysis
- **RSI** (Relative Strength Index) - Overbought/oversold detection
- **MACD** (Moving Average Convergence Divergence) - Trend momentum
- **Moving Averages** - SMA(20), SMA(50), EMA(12)
- **Bollinger Bands** - Volatility and price levels

### 💹 Global Market Support
- **US Stocks** - NASDAQ, NYSE (AAPL, MSFT, TSLA, etc.)
- **International** - 15+ markets with exchange suffixes (.IR, .L, .DE, .T, .PA, .TO, .AX, .HK, etc.)
- **Cryptocurrencies** - Bitcoin, Ethereum, and 10,000+ cryptos via CoinGecko API
- **Currency Support** - View prices in USD, EUR, GBP, or native currency

### 🎨 Modern Web Interface
- **Interactive Charts** - Candlestick, Line, OHLC, Area, Mountain, Volume charts
- **Accordion View** - Expandable stock details with lazy-loaded charts
- **Configuration Panel** - Manage portfolio, chart preferences, currency settings
- **Toast Notifications** - Non-blocking, elegant user feedback
- **Responsive Design** - Works on desktop, tablet, and mobile

### 💬 AI Chat Assistant
- Ask natural questions about analyzed stocks
- Currency conversion on demand (EUR, GBP, JPY)
- Smart ticker extraction from questions
- Context-aware responses with helpful suggestions

### � Persistent Storage
- **Portfolio** - Save favorite tickers in browser localStorage
- **Session** - Temporary analysis tickers (cleared on refresh)
- **Configuration** - Chart type, currency, display preferences

## Project Structure

```
FinBertTest/
├── app.py                      # Flask web application
├── requirements.txt            # Python dependencies
├── src/                        # Source modules
│   ├── __init__.py
│   ├── sentiment_analyzer.py  # FinBERT sentiment analysis
│   ├── technical_analyzer.py  # Technical indicators (RSI, MACD, etc.)
│   ├── data_fetcher.py         # Yahoo Finance data fetching
│   ├── chart_generator.py      # Plotly chart generation
│   └── portfolio_analyzer.py   # Main analysis orchestration
├── templates/                  # HTML templates
│   └── index.html
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── exports/                    # Generated analysis files
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (Python 3.10+ recommended)
- **8GB RAM** minimum (16GB recommended for large portfolios)
- **GPU** (optional) - CUDA-compatible GPU for faster inference
- **Internet connection** - Required for fetching market data

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/JewelIT/StockAnalysisHelper.git
cd StockAnalysisHelper
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

**Dependencies include:**
- Flask 3.1.2 - Web framework
- yfinance - Stock market data
- transformers - HuggingFace models
- torch - PyTorch for AI models
- pandas, numpy - Data processing
- plotly - Interactive charts
- requests - API calls

3. **Run the application**
```bash
python3 app.py
```

4. **Open your browser**
```
http://localhost:5000
```

### First-Time Setup

On first analysis, the app will download AI models (~1.2GB total):
- FinBERT: 440MB
- Twitter-RoBERTa: 501MB
- DistilBERT: 250MB

**Note:** Models are cached in `~/.cache/huggingface/` and only download once.

---

## 📖 Usage Guide

### Basic Workflow

1. **Add Tickers**
   - Click "Configuration" (⚙️ button)
   - Add tickers in "Portfolio Management" section
   - Supports: US stocks (AAPL), International (UPL.IR), Crypto (BTC-USD)

2. **Analyze Portfolio**
   - Click "Analyze Portfolio" button
   - Wait for AI models to load (first time only)
   - View results in accordion format

3. **Explore Results**
   - Click stock name to expand details
   - View sentiment, technical indicators, charts
   - Ask questions in AI Chat panel

4. **Configure Preferences**
   - Currency: USD / EUR / Native
   - Default chart type: Candlestick, Line, OHLC, etc.
   - Save portfolio for future sessions

### International Ticker Examples

```
US Stocks:         AAPL, MSFT, GOOGL, TSLA, NVDA
Ireland:           UPL.IR (Uniphar)
UK:                HSBA.L (HSBC), BP.L (BP)
Germany:           VOW3.DE (Volkswagen), SAP.DE (SAP)
France:            MC.PA (LVMH), OR.PA (L'Oréal)
Japan:             7203.T (Toyota), 6758.T (Sony)
Cryptocurrency:    BTC-USD, ETH-USD, XRP-EUR, ADA-USD
```

See [INTERNATIONAL_TICKERS.md](INTERNATIONAL_TICKERS.md) for complete guide.

### AI Chat Examples

```
💬 "What's the current price?"
💬 "What's the price in euros?"
💬 "What's the recommendation?"
💬 "Is the sentiment positive?"
💬 "What are the technical indicators showing?"
💬 "What's the RSI value?"
```

**Note:** Stock must be analyzed first before asking questions.

## Technical Analysis Indicators

- **RSI (Relative Strength Index)**: Identifies overbought/oversold conditions
- **MACD (Moving Average Convergence Divergence)**: Trend following momentum
- **Moving Averages**: SMA(20), SMA(50), EMA(12)
- **Bollinger Bands**: Volatility and price levels

---

## 📊 How It Works

### Analysis Pipeline

```
1. Data Fetching
   ├─ Stock prices (yfinance)
   ├─ Crypto prices (CoinGecko)
   ├─ News articles (Yahoo Finance)
   └─ Social media (Twitter/Reddit - optional)

2. Sentiment Analysis
   ├─ FinBERT → News sentiment
   └─ Twitter-RoBERTa → Social sentiment

3. Technical Analysis
   ├─ Calculate indicators (RSI, MACD, SMA, Bollinger)
   ├─ Generate signals (Bullish/Bearish/Neutral)
   └─ Technical score (0.0 - 1.0)

4. Combined Scoring
   ├─ 40% Sentiment weight
   ├─ 60% Technical weight
   └─ Final recommendation

5. Visualization
   ├─ Interactive Plotly charts
   ├─ Sentiment breakdown
   └─ Portfolio statistics
```

### Recommendation Thresholds

| Score       | Recommendation  | Meaning                       |
|-------------|-----------------|-------------------------------|
| > 0.65      | **STRONG BUY**  | High confidence buy signal    |
| 0.55 - 0.65 | **BUY**         | Positive outlook              |
| 0.45 - 0.55 | **HOLD**        | Neutral, wait for clarity     |
| 0.35 - 0.45 | **SELL**        | Negative outlook              |
| < 0.35      | **STRONG SELL** | High confidence sell signal   |

---

## 🗂️ Project Structure

```
StockAnalysisHelper/
├── app.py                          # Flask application & routes
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── INTERNATIONAL_TICKERS.md        # Global markets guide
├── CHAT_ASSISTANT_GUIDE.md        # AI chat documentation
├── LICENSE                         # MIT License
│
├── src/                            # Source modules
│   ├── __init__.py
│   ├── sentiment_analyzer.py      # FinBERT & Twitter-RoBERTa
│   ├── technical_analyzer.py      # RSI, MACD, indicators
│   ├── data_fetcher.py             # yfinance + CoinGecko
│   ├── coingecko_fetcher.py        # Crypto price data
│   ├── chart_generator.py          # Plotly visualizations
│   ├── portfolio_analyzer.py       # Main orchestration
│   └── stock_chat.py               # DistilBERT Q&A assistant
│
├── templates/                      # HTML templates
│   └── index.html                  # Main web interface
│
├── static/                         # Frontend assets
│   ├── css/
│   │   └── style.css               # Styling (1100+ lines)
│   └── js/
│       └── app.js                  # Frontend logic (1200+ lines)
│
└── exports/                        # Generated analysis files
    └── analysis_YYYYMMDD_HHMMSS.json
```

---

## ⚙️ Configuration

### Currency Settings

Set preferred display currency in Configuration panel:
- **USD** - US Dollar (default)
- **EUR** - Euro
- **GBP** - British Pound
- **Native** - Ticker's original currency

**Note:** Chat assistant can convert prices on demand:
- "What's the price in euros?"
- "Convert to GBP"

### Chart Types

- **Candlestick** - OHLC with wicks (default)
- **Line** - Simple price line
- **OHLC** - Open-High-Low-Close bars
- **Area** - Filled area chart
- **Mountain** - Gradient area
- **Volume** - Trading volume bars

### Social Media APIs (Optional)

For enhanced sentiment analysis:

```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
```

**Note:** StockTwits API currently unavailable (403 errors).

---

## 🛠️ Troubleshooting

### Common Issues

**1. "No module named 'transformers'"**
```bash
pip install --upgrade transformers torch
```

**2. "CUDA out of memory"**
- Close other GPU applications
- Reduce number of tickers analyzed simultaneously
- Or disable GPU: Models will use CPU (slower but works)

**3. "possibly delisted; no price data found"**
- Check ticker symbol is correct
- International stocks need exchange suffix (e.g., UPL.IR not UPL)
- See [INTERNATIONAL_TICKERS.md](INTERNATIONAL_TICKERS.md)

**4. "CoinGecko API error 429"**
- Rate limit reached (30 calls/minute on free tier)
- Wait 2 minutes before retrying
- Reduce number of crypto tickers

**5. Charts not loading**
- Check browser console (F12) for errors
- Ensure Plotly CDN is accessible
- Try refreshing the page

### Debug Mode

Flask runs in debug mode by default:
- Auto-reloads on code changes
- Detailed error messages
- Debugger PIN shown in console

**For production:** Set `debug=False` in `app.py`

---

## 📚 Documentation

- **[INTERNATIONAL_TICKERS.md](INTERNATIONAL_TICKERS.md)** - Global market ticker formats
- **[CHAT_ASSISTANT_GUIDE.md](CHAT_ASSISTANT_GUIDE.md)** - AI chat usage and capabilities

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Real-time data streaming
- [ ] More technical indicators
- [ ] Portfolio performance tracking
- [ ] Earnings calendar integration
- [ ] Risk analysis tools
- [ ] Multi-language support
- [ ] Mobile app version

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **HuggingFace** - AI models (FinBERT, RoBERTa, DistilBERT)
- **Yahoo Finance** - Market data via yfinance
- **CoinGecko** - Cryptocurrency data
- **Plotly** - Interactive charts
- **Flask** - Web framework

---

## 📧 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Built with ❤️ for traders and investors worldwide** 🌍📈

## License

MIT
