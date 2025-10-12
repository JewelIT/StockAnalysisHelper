# 🤖 Vestor - AI Financial Advisor

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

**Your intelligent financial advisor powered by AI, providing real-time stock analysis, conversational investment guidance, and portfolio management.**

---

## 🤖 Meet Vestor

Vestor is your friendly, knowledgeable AI financial advisor that:

- 📊 **Analyzes stocks & cryptocurrencies** with real-time data
- 💬 **Converses naturally** about investments, strategies, and markets
- 🎓 **Educates beginners** with patient, clear explanations
- 📈 **Provides insights** powered by FinBERT sentiment analysis
- 🔍 **Tracks portfolios** and offers personalized recommendations

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (Python 3.10+ recommended)
- **8GB RAM** minimum (16GB recommended for large portfolios)
- **GPU** (optional) - CUDA-compatible GPU for faster AI inference
- **Internet connection** - Required for fetching market data

### 🐳 Docker (Recommended)

```bash
./start-docker.sh
# Open http://localhost:5000
```

### 💻 Local Installation

```bash
# 1. Clone repository
git clone https://github.com/JewelIT/StockAnalysisHelper.git
cd StockAnalysisHelper

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python3 run.py

# 4. Open browser
# Visit http://localhost:5000
```

### First-Time Setup

On first analysis, the app will download AI models (~1.2GB total):
- **FinBERT**: 440MB (financial news sentiment)
- **Twitter-RoBERTa**: 501MB (social media sentiment)

**Note:** Models are cached in `~/.cache/huggingface/` and only download once.

---

## ✨ Features

### 🤖 AI-Powered Analysis

- **FinBERT** - Financial news sentiment analysis using state-of-the-art NLP
- **Twitter-RoBERTa** - Social media sentiment from tweets and discussions
- **Multi-model** scoring for accurate recommendations

### 📈 Technical Analysis

- **RSI** (Relative Strength Index) - Overbought/oversold detection
- **MACD** (Moving Average Convergence Divergence) - Trend momentum
- **Moving Averages** - SMA(20), SMA(50), EMA(12)
- **Bollinger Bands** - Volatility and price levels
- **Analyst Consensus** - Professional analyst ratings and price targets

### 💹 Global Market Support

- **US Stocks** - NASDAQ, NYSE (AAPL, MSFT, TSLA, etc.)
- **International** - 15+ markets (.IR, .L, .DE, .T, .PA, .TO, .AX, .HK, etc.)
- **Cryptocurrencies** - Bitcoin, Ethereum, and 10,000+ cryptos via CoinGecko
- **Currency Support** - View prices in USD, EUR, GBP, or native currency

### 🎨 Modern Web Interface

- **Interactive Charts** - Candlestick, Line, OHLC, Area, Mountain, Volume
- **Toast Notifications** - Non-blocking, elegant user feedback
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Dark/Light Theme** - Automatic theme detection with manual override

### 💬 AI Chat Assistant

- Ask natural questions about analyzed stocks
- Currency conversion on demand (EUR, GBP, JPY)
- Smart ticker extraction from questions
- Context-aware responses with helpful suggestions

### 💾 Persistent Storage

- **Portfolio** - Save favorite tickers in browser localStorage
- **Session** - Temporary analysis tickers (cleared on refresh)
- **Configuration** - Chart type, currency, display preferences

---

## 📁 Project Structure

```
StockAnalysisHelper/
├── run.py                          # 🚀 Application entry point
├── requirements.txt                # 📦 Python dependencies
├── README.md                       # 📖 This file
├── LICENSE                         # ⚖️ MIT License
│
├── src/                            # 📂 Source code (organized by layer)
│   ├── web/                       # 🌐 Flask web application
│   │   ├── __init__.py           # App factory (create_app)
│   │   ├── routes/               # 🛣️ HTTP endpoints
│   │   │   ├── main.py          # Home, market sentiment
│   │   │   ├── analysis.py      # Stock/portfolio analysis
│   │   │   └── chat.py          # Vestor AI chat
│   │   └── services/             # 💼 Business logic layer
│   │       ├── analysis_service.py   # Analysis orchestration
│   │       ├── vestor_service.py     # Vestor conversation
│   │       └── market_sentiment_service.py  # Market overview
│   │
│   ├── config/                    # ⚙️ Configuration
│   │   ├── config.py             # App constants & settings
│   │   └── logging_config.py     # Logging configuration
│   │
│   ├── core/                      # 🧠 Business logic
│   │   └── portfolio_analyzer.py # Main analysis orchestration
│   │
│   ├── data/                      # 📊 Data fetchers
│   │   ├── data_fetcher.py       # Yahoo Finance
│   │   ├── coingecko_fetcher.py  # Cryptocurrency
│   │   └── social_media_fetcher.py  # Reddit/StockTwits
│   │
│   ├── ai/                        # 🤖 AI/ML models
│   │   ├── sentiment_analyzer.py     # FinBERT
│   │   ├── multi_model_sentiment.py  # Multi-model aggregation
│   │   ├── stock_chat.py            # Chat assistant
│   │   └── natural_response_generator.py  # NLG
│   │
│   ├── utils/                     # 🔧 Utilities
│   │   ├── chart_generator.py    # Plotly charts
│   │   ├── technical_analyzer.py # RSI, MACD, indicators
│   │   ├── analyst_consensus.py  # Analyst ratings
│   │   └── helpers.py            # Helper functions
│   │
│   └── vestor/                    # 💬 Vestor chatbot subsystem
│       ├── conversation/         # Conversation management
│       ├── knowledge/            # Knowledge base
│       ├── responses/            # Response generation
│       └── security/             # Input validation
│
├── templates/                      # 🎨 HTML templates
│   └── index.html                 # Main web interface
│
├── static/                         # 🖼️ Frontend assets
│   ├── css/
│   │   ├── modern.css            # Modern theme
│   │   └── style.css             # Legacy styles
│   ├── js/
│   │   └── app.js                # Frontend logic
│   └── favicon.svg               # App icon
│
├── docs/                           # 📚 Documentation
│   ├── ARCHITECTURE.md            # System architecture
│   ├── TESTING_GUIDE.md          # Testing documentation
│   ├── LOGGING_CONTROL.md        # Logging features
│   └── ...                        # Feature docs
│
├── tests/                          # 🧪 Test suite
│   ├── test_integration.py        # Integration tests
│   ├── test_vestor_service.py     # Vestor AI tests
│   └── ...                        # Additional tests
│
├── logs/                           # 📝 Application logs (ignored)
├── exports/                        # 💾 Analysis exports (ignored)
└── __pycache__/                    # 🗑️ Python bytecode (ignored)
```

---

## 🎯 Usage Guide

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

## 🛠️ Technology Stack

- **Backend**: Flask 3.1.2, Python 3.8+
- **AI/ML**:
  - FinBERT (ProsusAI/finbert) - Financial sentiment
  - Twitter-RoBERTa - Social media sentiment
  - PyTorch - Model inference
- **Data Sources**:
  - Yahoo Finance (yfinance)
  - CoinGecko API
  - Reddit API (optional)
- **Charts**: Plotly
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Storage**: Flask sessions, browser localStorage

---

## ⚙️ Configuration

### Environment Variables

```bash
export SECRET_KEY="your-secret-key-change-in-production"
export FLASK_ENV="development"  # or "production"

# Optional: Social media APIs
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
```

### Application Settings

Configure in the web UI:
- **Portfolio tickers** - Saved in browser localStorage
- **Default currency** - USD, EUR, GBP, or native
- **Chart preferences** - Type, colors, indicators
- **Theme** - Light or dark mode
- **Logging level** - Developer menu (hidden tab in settings)

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

**4. "CoinGecko API error 429"**
- Rate limit reached (30 calls/minute on free tier)
- Wait 2 minutes before retrying

**5. Charts not loading**
- Check browser console (F12) for errors
- Ensure Plotly CDN is accessible
- Try refreshing the page

### Debug Mode

```bash
# Set logging level
export LOG_LEVEL="DEBUG"  # or INFO, WARNING, ERROR

# Run application
python3 run.py
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_integration.py

# Run with coverage
pytest --cov=src --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow PEP 8 style guidelines
4. Add tests for new features
5. Update documentation
6. Submit a pull request

### Development Priorities

- [ ] Real-time data streaming
- [ ] Portfolio performance tracking
- [ ] More technical indicators
- [ ] Earnings calendar integration
- [ ] Risk analysis tools
- [ ] Multi-language support
- [ ] Mobile app version

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## ⚠️ Disclaimer

**Vestor is for educational and informational purposes only.**

- Not financial advice
- Always do your own research (DYOR)
- Consult qualified financial advisors
- Only invest what you can afford to lose
- Past performance doesn't guarantee future results

---

## 🙏 Acknowledgments

- **HuggingFace** - AI models (FinBERT, RoBERTa)
- **Yahoo Finance** - Market data via yfinance
- **CoinGecko** - Cryptocurrency data
- **Plotly** - Interactive charts
- **Flask** - Web framework
- **Bootstrap** - UI framework

---

## 📧 Contact

- **Repository**: [StockAnalysisHelper](https://github.com/JewelIT/StockAnalysisHelper)
- **Issues**: [GitHub Issues](https://github.com/JewelIT/StockAnalysisHelper/issues)
- **GitHub**: [@JewelIT](https://github.com/JewelIT)

---

**Built with ❤️ for traders and investors worldwide** 🌍📈
