# 🤖 Vestor - AI Financial Advisor# Vestor - AI Financial Advisor# 📊 AI Stock Portfolio Analyzer



![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)

![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)

![License](https://img.shields.io/badge/License-MIT-yellow.svg)An intelligent financial advisor powered by AI, providing real-time stock analysis, portfolio management, and investment guidance.**Professional-grade stock and cryptocurrency analysis powered by AI sentiment analysis, technical indicators, and interactive visualizations.**

![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)



**Your intelligent financial advisor powered by AI, providing real-time stock analysis, conversational investment guidance, and portfolio management.**

## 🤖 Meet Vestor![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)

---

![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)

## 🤖 Meet Vestor

Vestor is your friendly AI financial advisor that helps you:![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Vestor is your friendly, knowledgeable AI financial advisor that:

- **Analyze stocks and cryptocurrencies** with real-time data![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

- 📊 **Analyzes stocks & cryptocurrencies** with real-time data

- 💬 **Converses naturally** about investments, strategies, and markets- **Get investment insights** powered by FinBERT and sentiment analysis

- 🎓 **Educates beginners** with patient, clear explanations

- 📈 **Provides insights** powered by FinBERT sentiment analysis- **Learn about investing** through conversational AI---

- 🔍 **Tracks portfolios** and offers personalized recommendations

- **Make informed decisions** with technical and fundamental analysis

---

## 🚀 Quick Start for Non-Technical Users

## 🚀 Quick Start

## 🚀 Quick Start

### 🐳 Docker (Recommended)

**Choose your preferred installation method:**

```bash

./start-docker.sh### Prerequisites

# Open http://localhost:5000

```- Python 3.8+### 🐳 Docker (Recommended - Works Everywhere)



### 💻 Local Installation- pip1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)



```bash- CUDA-capable GPU (optional, for faster processing)2. Run:

# Clone repository

git clone https://github.com/JewelIT/StockAnalysisHelper.git   ```bash

cd StockAnalysisHelper

### Installation   ./start-docker.sh

# Install dependencies

pip install -r requirements.txt   ```



# Run application```bash3. Open http://localhost:5000 in your browser

python3 run.py

# Clone the repository

# Visit http://localhost:5000

```git clone https://github.com/JewelIT/StockAnalysisHelper.git### 💻 One-Click Installers



### 📦 One-Click Installerscd StockAnalysisHelper- **Windows**: Run `install-windows.bat`



- **Windows**: Run `install-windows.bat`- **Linux/Mac**: Run `./start-docker.sh`

- **Linux/Mac**: Run `./start-docker.sh`

# Install dependencies

---

pip install -r requirements.txt### 📦 For Developers

## ✨ Features

```bash

### 💬 Conversational AI

- Natural language conversations with Vestor# Run the applicationpip install -r requirements.txt

- Context-aware responses that remember your discussion

- Investment education for beginnerspython run.pypython3 app.py

- Portfolio advice and risk management tips

- Stock-specific insights when you mention companies``````



### 📊 AI-Powered Analysis

- **FinBERT** - Financial news sentiment (440MB)

- **Twitter-RoBERTa** - Social media sentiment (501MB)Visit `http://localhost:5000` in your browser.**See [DISTRIBUTION.md](DISTRIBUTION.md) for packaging and deployment options.**

- **Technical Indicators** - RSI, MACD, Bollinger Bands, Moving Averages

- **Multi-model** scoring for accurate recommendations



### 🌍 Global Market Support## 📁 Project Structure---

- **US Stocks** - NASDAQ, NYSE (AAPL, MSFT, TSLA)

- **International** - 15+ markets (.IR, .L, .DE, .T, .PA, .TO, .AX, .HK)

- **Cryptocurrencies** - Bitcoin, Ethereum, 10,000+ coins via CoinGecko

- **Currency Support** - USD, EUR, GBP, native currency```## ✨ Features



### 🎨 Modern Web Interface├── app/                    # Main application package

- Interactive Plotly charts (Candlestick, Line, OHLC, Area)

- Responsive Bootstrap 5 design│   ├── __init__.py        # App factory### 🤖 AI-Powered Analysis

- Dark/Light theme support

- Real-time chat interface│   ├── routes/            # Route blueprints- **FinBERT Sentiment** - Financial news analysis using state-of-the-art NLP (440MB model)

- Portfolio configuration panel

│   │   ├── main.py        # Home and utility routes- **Twitter-RoBERTa** - Social media sentiment from tweets and discussions (501MB model)

---

│   │   ├── analysis.py    # Stock analysis endpoints- **DistilBERT Chat** - Interactive Q&A assistant for stock queries (250MB model)

## 📁 Project Structure

│   │   └── chat.py        # Vestor chat endpoints

```

StockAnalysisHelper/│   ├── services/          # Business logic layer### 📈 Technical Analysis

├── run.py                      # Application entry point

├── logging_config.py           # Centralized logging setup│   │   ├── analysis_service.py   # Analysis operations- **RSI** (Relative Strength Index) - Overbought/oversold detection

├── requirements.txt            # Python dependencies

││   │   └── vestor_service.py     # Vestor AI logic- **MACD** (Moving Average Convergence Divergence) - Trend momentum

├── app/                        # Flask application package

│   ├── __init__.py            # App factory│   ├── models/            # Data models (future)- **Moving Averages** - SMA(20), SMA(50), EMA(12)

│   ├── routes/                # Route blueprints

│   │   ├── main.py           # Home and utility routes│   └── utils/             # Utility functions (future)- **Bollinger Bands** - Volatility and price levels

│   │   ├── analysis.py       # Stock analysis endpoints

│   │   └── chat.py           # Vestor chat endpoints├── src/                   # Core analysis modules

│   ├── services/              # Business logic layer

│   │   ├── analysis_service.py   # Analysis operations│   ├── portfolio_analyzer.py     # Portfolio analysis### 💹 Global Market Support

│   │   └── vestor_service.py     # Vestor AI conversation logic

│   ├── models/                # Data models (future)│   ├── stock_chat.py             # AI chat assistant- **US Stocks** - NASDAQ, NYSE (AAPL, MSFT, TSLA, etc.)

│   └── utils/                 # Utility functions (future)

││   ├── sentiment_analyzer.py    # FinBERT sentiment- **International** - 15+ markets with exchange suffixes (.IR, .L, .DE, .T, .PA, .TO, .AX, .HK, etc.)

├── src/                       # Core analysis modules

│   ├── portfolio_analyzer.py # Portfolio analysis orchestration│   ├── technical_analyzer.py    # Technical indicators- **Cryptocurrencies** - Bitcoin, Ethereum, and 10,000+ cryptos via CoinGecko API

│   ├── stock_chat.py          # AI chat assistant (StockChatAssistant)

│   ├── sentiment_analyzer.py # FinBERT sentiment analysis│   ├── data_fetcher.py           # Market data retrieval- **Currency Support** - View prices in USD, EUR, GBP, or native currency

│   ├── technical_analyzer.py # Technical indicators

│   ├── data_fetcher.py        # Yahoo Finance data│   ├── chart_generator.py       # Chart generation

│   ├── coingecko_fetcher.py   # Cryptocurrency data

│   ├── chart_generator.py     # Plotly chart generation│   └── ...### 🎨 Modern Web Interface

│   └── ...

│├── templates/             # HTML templates- **Interactive Charts** - Candlestick, Line, OHLC, Area, Mountain, Volume charts

├── templates/                 # Jinja2 HTML templates

│   ├── index-modern.html     # Main web interface├── static/                # CSS, JS, assets- **Accordion View** - Expandable stock details with lazy-loaded charts

│   └── index-legacy.html     # Legacy interface

│├── docs/                  # Documentation- **Configuration Panel** - Manage portfolio, chart preferences, currency settings

├── static/                    # Frontend assets

│   ├── css/│   └── .archive/          # Archived development notes- **Toast Notifications** - Non-blocking, elegant user feedback

│   │   ├── modern.css        # Modern theme styles

│   │   └── style.css         # Legacy styles├── logs/                  # Application logs- **Responsive Design** - Works on desktop, tablet, and mobile

│   └── js/

│       └── app.js            # Frontend JavaScript├── exports/               # Analysis exports

│

├── docs/                      # Documentation├── run.py                 # Application entry point### 💬 AI Chat Assistant

│   └── .archive/             # Archived development notes (ignored)

│├── logging_config.py      # Logging configuration- Ask natural questions about analyzed stocks

├── logs/                      # Application logs (ignored)

├── exports/                   # Analysis exports (ignored)└── requirements.txt       # Python dependencies- Currency conversion on demand (EUR, GBP, JPY)

└── .gitignore                # Git ignore rules

``````- Smart ticker extraction from questions



---- Context-aware responses with helpful suggestions



## 🎯 Usage Examples## 🎯 Features



### Conversational AI with Vestor### � Persistent Storage



```### Stock Analysis- **Portfolio** - Save favorite tickers in browser localStorage

You: Hello! I'm new to investing.

- Real-time price data from Yahoo Finance- **Session** - Temporary analysis tickers (cleared on refresh)

Vestor: Hi! Welcome! I'm Vestor, your AI financial advisor. I'd love to help 

        you get started with investing. What would you like to know?- Technical indicators (RSI, MACD, Bollinger Bands, etc.)- **Configuration** - Chart type, currency, display preferences



You: I'm thinking about buying crypto, what's your take?- Sentiment analysis from social media and news



Vestor: Crypto can be exciting but it's also high-risk! For beginners, I'd - Interactive charts (Candlestick, Line, OHLC, etc.)## Project Structure

        recommend starting with:

        • Understanding your risk tolerance- Buy/Hold/Sell recommendations

        • Researching major cryptocurrencies like Bitcoin (BTC) and Ethereum (ETH)

        • Only investing what you can afford to lose```

        

        Would you like me to analyze any specific cryptocurrency?### Vestor AI ChatFinBertTest/



You: Tell me about Bitcoin- Natural language conversations about investing├── app.py                      # Flask web application



Vestor: I'll analyze Bitcoin (BTC-USD) for you! Let me fetch the latest data...- Context-aware responses├── requirements.txt            # Python dependencies

        [Analysis begins automatically]

```- Stock-specific insights and recommendations├── src/                        # Source modules



### Stock Analysis- Educational content for beginners│   ├── __init__.py



```- Portfolio advice│   ├── sentiment_analyzer.py  # FinBERT sentiment analysis

You: What about Apple?

│   ├── technical_analyzer.py  # Technical indicators (RSI, MACD, etc.)

Vestor: Let me analyze AAPL for you!

        [Provides sentiment, technical indicators, recommendation]### Portfolio Management│   ├── data_fetcher.py         # Yahoo Finance data fetching



You: Is it a good investment?- Multi-ticker analysis│   ├── chart_generator.py      # Plotly chart generation



Vestor: Based on my analysis:- Risk assessment│   └── portfolio_analyzer.py   # Main analysis orchestration

        📊 Recommendation: BUY

        📈 Technical Signal: Bullish- Diversification recommendations├── templates/                  # HTML templates

        💭 Sentiment: 0.75 (Positive)

        - Export analysis reports│   └── index.html

        Key reasons:

        • Strong positive sentiment from news├── static/                     # Static assets

        • RSI indicates healthy momentum

        • MACD shows bullish trend## 🛠️ Technology Stack│   ├── css/

```

│   │   └── style.css

---

- **Backend**: Flask (Python)│   └── js/

## 🛠️ Technology Stack

- **AI/ML**: │       └── app.js

- **Backend**: Flask 3.1.2, Python 3.8+

- **AI/ML**:   - FinBERT (Financial sentiment analysis)└── exports/                    # Generated analysis files

  - FinBERT (ProsusAI/finbert) - Financial sentiment

  - Twitter-RoBERTa - Social media sentiment  - Twitter-RoBERTa (Social media sentiment)```

  - DistilBERT - Conversational AI

  - PyTorch - Model inference  - Conversational AI for Vestor

- **Data Sources**: 

  - Yahoo Finance (yfinance)- **Data**: Yahoo Finance API, CoinGecko API## 🚀 Quick Start

  - CoinGecko API

- **Frontend**: - **Charts**: Plotly

  - Bootstrap 5.3

  - Vanilla JavaScript- **Frontend**: Bootstrap 5, Vanilla JavaScript### Prerequisites

  - Plotly.js for charts

- **Storage**: Flask sessions, browser localStorage- **Python 3.8+** (Python 3.10+ recommended)



---## 📊 API Endpoints- **8GB RAM** minimum (16GB recommended for large portfolios)



## 🧪 Testing- **GPU** (optional) - CUDA-compatible GPU for faster inference



```bash### Analysis- **Internet connection** - Required for fetching market data

# Run test suite (coming soon)

python -m pytest tests/- `POST /api/analyze` - Analyze stocks/portfolio



# Run with coverage- `GET /api/exports/<filename>` - Download analysis report### Installation

pytest --cov=app --cov=src tests/

```



---### Chat1. **Clone the repository**



## 📝 Configuration- `POST /api/chat` - Chat with Vestor```bash



### Environment Variables- `GET /get-chat-history` - Get conversation historygit clone https://github.com/JewelIT/StockAnalysisHelper.git



```bash- `POST /clear-chat` - Clear conversationcd StockAnalysisHelper

export SECRET_KEY="your-secret-key-change-in-production"

export FLASK_ENV="development"  # or "production"```



# Optional: Social media APIs## 🧪 Testing

export REDDIT_CLIENT_ID="your_client_id"

export REDDIT_CLIENT_SECRET="your_client_secret"2. **Install Python dependencies**

```

```bash```bash

### Application Settings

# Run tests (coming soon)pip install -r requirements.txt

Configure in the web UI:

- **Portfolio tickers** - Saved in browser localStoragepython -m pytest tests/```

- **Default currency** - USD, EUR, GBP, or native

- **Chart preferences** - Type, colors, indicators```

- **Theme** - Light or dark mode

**Dependencies include:**

---

## 📝 Configuration- Flask 3.1.2 - Web framework

## 🐛 Troubleshooting

- yfinance - Stock market data

### Model Loading Issues

Set environment variables:- transformers - HuggingFace models

```bash

# Clear model cache```bash- torch - PyTorch for AI models

rm -rf ~/.cache/huggingface/

export SECRET_KEY="your-secret-key"- pandas, numpy - Data processing

# Reinstall transformers

pip install --upgrade transformers torchexport FLASK_ENV="production"  # or "development"- plotly - Interactive charts

```

```- requests - API calls

### CUDA/GPU Issues



```bash

# Check PyTorch GPU availability## 🤝 Contributing3. **Run the application**

python -c "import torch; print(torch.cuda.is_available())"

```bash

# Force CPU mode (slower but reliable)

export CUDA_VISIBLE_DEVICES=""1. Fork the repositorypython3 app.py

```

2. Create a feature branch (`git checkout -b feature/amazing-feature`)```

### International Tickers

3. Commit your changes (`git commit -m 'Add amazing feature'`)

- Use exchange suffixes: `UPL.IR` (Ireland), `HSBA.L` (London), `VOW3.DE` (Germany)

- See [DISTRIBUTION.md](DISTRIBUTION.md) for complete guide4. Push to the branch (`git push origin feature/amazing-feature`)4. **Open your browser**



---5. Open a Pull Request```



## 🤝 Contributinghttp://localhost:5000



Contributions welcome! Please:## 📄 License```



1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)

3. Follow PEP 8 style guidelinesThis project is licensed under the MIT License - see the LICENSE file for details.### First-Time Setup

4. Add tests for new features

5. Update documentation

6. Submit a pull request

## ⚠️ DisclaimerOn first analysis, the app will download AI models (~1.2GB total):

### Development Priorities

- FinBERT: 440MB

- [ ] Comprehensive test suite (pytest)

- [ ] Real-time data streamingVestor is for educational and informational purposes only. It does not constitute financial advice. Always consult with a qualified financial advisor before making investment decisions.- Twitter-RoBERTa: 501MB

- [ ] Portfolio performance tracking

- [ ] Mobile app version- DistilBERT: 250MB

- [ ] More technical indicators

- [ ] Multi-language support## 🔗 Credits



---**Note:** Models are cached in `~/.cache/huggingface/` and only download once.



## 📄 License- FinBERT: ProsusAI/finbert



MIT License - See [LICENSE](LICENSE) file- Twitter-RoBERTa: cardiffnlp/twitter-roberta-base-sentiment-latest---



---- Market Data: Yahoo Finance, CoinGecko



## ⚠️ Disclaimer## 📖 Usage Guide



**Vestor is for educational and informational purposes only.**## 📧 Contact



- Not financial advice### Basic Workflow

- Always do your own research (DYOR)

- Consult qualified financial advisors- GitHub: [@JewelIT](https://github.com/JewelIT)

- Only invest what you can afford to lose

- Past performance doesn't guarantee future results- Repository: [StockAnalysisHelper](https://github.com/JewelIT/StockAnalysisHelper)1. **Add Tickers**



---   - Click "Configuration" (⚙️ button)

   - Add tickers in "Portfolio Management" section

## 🙏 Credits   - Supports: US stocks (AAPL), International (UPL.IR), Crypto (BTC-USD)



- **HuggingFace** - AI models (FinBERT, RoBERTa, DistilBERT)2. **Analyze Portfolio**

- **Yahoo Finance** - Market data via yfinance   - Click "Analyze Portfolio" button

- **CoinGecko** - Cryptocurrency data   - Wait for AI models to load (first time only)

- **Plotly** - Interactive charts   - View results in accordion format

- **Flask** - Web framework

- **Bootstrap** - UI framework3. **Explore Results**

   - Click stock name to expand details

---   - View sentiment, technical indicators, charts

   - Ask questions in AI Chat panel

## 📧 Contact

4. **Configure Preferences**

- **Repository**: [StockAnalysisHelper](https://github.com/JewelIT/StockAnalysisHelper)   - Currency: USD / EUR / Native

- **Issues**: [GitHub Issues](https://github.com/JewelIT/StockAnalysisHelper/issues)   - Default chart type: Candlestick, Line, OHLC, etc.

- **GitHub**: [@JewelIT](https://github.com/JewelIT)   - Save portfolio for future sessions



---### International Ticker Examples



**Built with ❤️ for traders and investors worldwide** 🌍📈```

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
