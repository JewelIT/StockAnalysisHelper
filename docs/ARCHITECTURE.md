# Vestor Project Structure & Architecture

**Last Updated**: October 12, 2025  
**Status**: Clean, Production-Ready Structure

---

## 📁 Directory Structure

```
StockAnalysisHelper/
│
├── run.py                          # 🚀 APPLICATION ENTRY POINT
├── requirements.txt                # 📦 Python dependencies
├── README.md                       # 📖 Main documentation
├── LICENSE                         # ⚖️ MIT License
├── .gitignore                      # 🚫 Git ignore rules
│
├── src/                            # 📂 SOURCE CODE (Organized by Layer)
│   │
│   ├── web/                       # 🌐 FLASK WEB APPLICATION
│   │   ├── __init__.py           # Application factory (create_app)
│   │   │
│   │   ├── routes/               # 🛣️ Route Blueprints (HTTP Endpoints)
│   │   │   ├── __init__.py
│   │   │   ├── main.py          # Home, market sentiment, utility routes
│   │   │   ├── analysis.py      # Stock/portfolio analysis endpoints
│   │   │   └── chat.py          # Vestor AI chat endpoints
│   │   │
│   │   └── services/             # 💼 Business Logic Layer
│   │       ├── __init__.py
│   │       ├── analysis_service.py          # Analysis orchestration
│   │       ├── vestor_service.py            # Vestor AI conversation
│   │       └── market_sentiment_service.py  # Market overview
│   │
│   ├── config/                    # ⚙️ CONFIGURATION
│   │   ├── config.py             # Application constants & settings
│   │   └── logging_config.py     # Centralized logging setup
│   │
│   ├── core/                      # 🧠 CORE BUSINESS LOGIC
│   │   └── portfolio_analyzer.py # Main portfolio analysis orchestration
│   │
│   ├── data/                      # 📊 DATA FETCHERS
│   │   ├── data_fetcher.py       # Yahoo Finance stock data
│   │   ├── coingecko_fetcher.py  # Cryptocurrency data (CoinGecko API)
│   │   └── social_media_fetcher.py  # Reddit/StockTwits (optional)
│   │
│   ├── ai/                        # 🤖 AI/ML MODELS & LOGIC
│   │   ├── sentiment_analyzer.py         # FinBERT & Twitter-RoBERTa
│   │   ├── multi_model_sentiment.py      # Multi-model aggregation
│   │   ├── stock_chat.py                 # StockChatAssistant (AI core)
│   │   └── natural_response_generator.py # Natural language generation
│   │
│   ├── utils/                     # 🔧 UTILITY FUNCTIONS
│   │   ├── chart_generator.py    # Plotly chart generation
│   │   ├── technical_analyzer.py # RSI, MACD, Bollinger Bands
│   │   ├── analyst_consensus.py  # Analyst recommendations
│   │   └── helpers.py            # Helper functions (formatting, etc.)
│   │
│   └── vestor/                    # 💬 VESTOR CHATBOT SUBSYSTEM
│       ├── __init__.py
│       ├── conversation/         # Conversation state management
│       ├── knowledge/            # Knowledge base & prompts
│       ├── responses/            # Response generation
│       ├── core/                 # Core Vestor logic
│       └── security/             # Input validation & safety
│
├── templates/                      # 🎨 JINJA2 HTML TEMPLATES
│   └── index.html                 # Main web interface (single-page app)
│
├── static/                         # 🖼️ FRONTEND ASSETS
│   ├── css/
│   │   ├── modern.css            # Modern theme styles
│   │   └── style.css             # Legacy styles
│   ├── js/
│   │   └── app.js                # Main frontend application logic
│   └── favicon.svg               # Application icon
│
├── docs/                           # 📚 DOCUMENTATION
│   ├── README.md                  # Documentation index
│   ├── ARCHITECTURE.md            # This file - system architecture
│   ├── TESTING_GUIDE.md          # Testing documentation
│   ├── LOGGING_CONTROL.md        # Logging features
│   ├── VESTOR_MODULAR_ARCHITECTURE.md  # Vestor subsystem design
│   └── ...                        # Feature implementation guides
│
├── logs/                           # 📝 APPLICATION LOGS (git ignored)
│   ├── flask.log                  # Main application log
│   ├── security.log               # Security events
│   ├── chat.log                   # Chat interactions
│   └── analysis.log               # Analysis requests
│
├── exports/                        # 💾 ANALYSIS EXPORTS (git ignored)
│   └── analysis_*.json            # Generated analysis files
│
├── tests/                          # 🧪 TEST SUITE
│   ├── __init__.py
│   ├── test_integration.py        # Integration tests
│   ├── test_vestor_service.py     # Vestor AI tests
│   ├── test_newsfeed_ui_integration.py  # Newsfeed tests
│   ├── test_analyst_integration.py      # Analyst data tests
│   ├── test_logging_config.py          # Logging tests
│   ├── integration/              # Integration test suite
│   ├── unit/                     # Unit tests
│   └── conversation_scenarios/   # Conversation test scenarios
│
└── __pycache__/                    # 🗑️ Python bytecode (git ignored)
```

---

## 🏗️ Architecture Overview

### Layered Architecture Pattern

The application follows a clean **layered architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│  (templates/index.html, static/js/app.js)              │
│          User Interface & Frontend Logic                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                      WEB LAYER                          │
│              (src/web/routes/*.py)                      │
│     HTTP Endpoints, Request/Response Handling           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   SERVICE LAYER                         │
│            (src/web/services/*.py)                      │
│         Business Logic & Orchestration                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    CORE LAYER                           │
│    (src/core/, src/ai/, src/data/, src/utils/)        │
│     Analysis, AI Models, Data Fetching, Utilities      │
└─────────────────────────────────────────────────────────┘
```

### Application Factory Pattern

**Entry Point**: `run.py` → **Factory**: `src/web/__init__.py:create_app()` → Flask app instance

```python
# run.py
from src.web import create_app
from src.config.logging_config import setup_logging

logger = setup_logging()
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Blueprint Registration

Routes are organized as Flask blueprints:

```python
# src/web/__init__.py
from src.web.routes import analysis, chat, main

app.register_blueprint(main.bp)
app.register_blueprint(analysis.bp)
app.register_blueprint(chat.bp)
```

---

## 🔄 Request Flow

### Stock Analysis Request

```
1. User clicks "Analyze Portfolio" 
   ↓
2. Frontend (app.js) → POST /analyze
   ↓
3. Route (src/web/routes/analysis.py) → Validates request
   ↓
4. Service (src/web/services/analysis_service.py) → Orchestrates
   ↓
5. Core (src/core/portfolio_analyzer.py) → Analyzes
   ├─ Data Layer (src/data/) → Fetches stock/crypto data
   ├─ AI Layer (src/ai/) → Sentiment analysis
   └─ Utils Layer (src/utils/) → Technical indicators & charts
   ↓
6. Response JSON → Frontend
   ↓
7. Frontend renders results (charts, sentiment, recommendations)
```

### Chat Request

```
1. User types question
   ↓
2. Frontend (app.js) → POST /chat
   ↓
3. Route (src/web/routes/chat.py) → Validates & logs
   ↓
4. Service (src/web/services/vestor_service.py) → Processes
   ├─ Vestor Subsystem (src/vestor/) → Conversation logic
   ├─ Stock Chat (src/ai/stock_chat.py) → AI response generation
   └─ Analysis Service → If stock analysis needed
   ↓
5. Response JSON → Frontend
   ↓
6. Frontend renders message in chat panel
```

---

## 📦 Key Components

### 1. Web Layer (`src/web/`)

**Purpose**: HTTP interface, request/response handling

**Components**:
- **Routes** (`src/web/routes/`):
  - `main.py`: Home page, market sentiment overview
  - `analysis.py`: Portfolio/stock analysis endpoints
  - `chat.py`: Vestor AI chat endpoints
  
- **Services** (`src/web/services/`):
  - `analysis_service.py`: Analysis orchestration & caching
  - `vestor_service.py`: Vestor conversation management
  - `market_sentiment_service.py`: Market overview data

**Key Features**:
- Blueprint-based routing
- Request validation
- Error handling
- Logging integration

### 2. Config Layer (`src/config/`)

**Purpose**: Application configuration & logging

**Components**:
- `config.py`: Constants, API endpoints, model configurations
- `logging_config.py`: Centralized logging setup with file rotation

**Features**:
- Environment variable support
- Per-module log level control
- Structured logging (JSON-ready)

### 3. Core Layer (`src/core/`)

**Purpose**: Core business logic

**Components**:
- `portfolio_analyzer.py`: Main portfolio analysis orchestration
  - Coordinates data fetching, sentiment analysis, technical analysis
  - Generates combined scores and recommendations
  - Handles multi-ticker analysis

**Responsibilities**:
- Business logic encapsulation
- Data aggregation
- Score calculation algorithms

### 4. Data Layer (`src/data/`)

**Purpose**: External data retrieval

**Components**:
- `data_fetcher.py`: Yahoo Finance integration (stocks)
- `coingecko_fetcher.py`: CoinGecko API (cryptocurrencies)
- `social_media_fetcher.py`: Reddit/StockTwits (social media)

**Features**:
- API client abstraction
- Error handling & retries
- Data normalization

### 5. AI Layer (`src/ai/`)

**Purpose**: AI/ML models and logic

**Components**:
- `sentiment_analyzer.py`: FinBERT & Twitter-RoBERTa models
- `multi_model_sentiment.py`: Multi-model sentiment aggregation
- `stock_chat.py`: StockChatAssistant (conversational AI)
- `natural_response_generator.py`: Natural language generation

**Features**:
- Model loading & caching
- GPU/CPU detection
- Batch processing
- Sentiment scoring

### 6. Utils Layer (`src/utils/`)

**Purpose**: Utility functions & helpers

**Components**:
- `chart_generator.py`: Plotly chart generation (all chart types)
- `technical_analyzer.py`: Technical indicators (RSI, MACD, etc.)
- `analyst_consensus.py`: Analyst ratings & price targets
- `helpers.py`: Helper functions (formatting, validation)

**Features**:
- Reusable utilities
- No business logic
- Pure functions

### 7. Vestor Subsystem (`src/vestor/`)

**Purpose**: Vestor chatbot subsystem (modular architecture)

**Components**:
- `conversation/`: Conversation state management
- `knowledge/`: Knowledge base & prompts
- `responses/`: Response generation logic
- `core/`: Core Vestor logic
- `security/`: Input validation & safety

**Features**:
- Context-aware conversations
- Educational content
- Ticker extraction
- Safety controls

---

## 🔐 Security Architecture

### Input Validation

- **Routes**: Basic validation (required fields, types)
- **Services**: Business logic validation (ticker format, limits)
- **Vestor Security**: Prompt injection protection, content filtering

### Logging & Monitoring

- **Security Log**: Authentication, rate limiting, suspicious activity
- **Chat Log**: All conversations (for improvement & monitoring)
- **Analysis Log**: Analysis requests & performance
- **Unanswered Questions**: Questions Vestor couldn't answer (for training)

### Rate Limiting

- Implemented in `src/web/__init__.py`
- Per-endpoint limits
- IP-based tracking

---

## 📊 Data Flow

### Analysis Pipeline

```
User Request
    ↓
[Validation]
    ↓
[Data Fetching] (Yahoo Finance / CoinGecko)
    ├─ Price data
    ├─ News articles
    └─ Social media (optional)
    ↓
[Sentiment Analysis] (FinBERT + Twitter-RoBERTa)
    ├─ News sentiment: 0.0 - 1.0
    └─ Social sentiment: 0.0 - 1.0
    ↓
[Technical Analysis] (RSI, MACD, SMA, Bollinger)
    ├─ Indicators
    ├─ Signals (Bullish/Bearish/Neutral)
    └─ Technical score: 0.0 - 1.0
    ↓
[Analyst Consensus] (Yahoo Finance)
    ├─ Buy/Hold/Sell ratings
    ├─ Price targets
    └─ Coverage depth
    ↓
[Combined Scoring]
    ├─ 40% Sentiment weight
    ├─ 60% Technical weight
    └─ Final score: 0.0 - 1.0
    ↓
[Recommendation] (BUY / HOLD / SELL)
    ↓
[Chart Generation] (Plotly)
    ↓
Response JSON
```

### Chat Pipeline

```
User Question
    ↓
[Input Sanitization]
    ↓
[Ticker Extraction] (if mentioned)
    ↓
[Context Retrieval] (analyzed stocks)
    ↓
[Vestor Processing]
    ├─ Knowledge base query
    ├─ Conversation context
    └─ Response generation
    ↓
[AI Response] (StockChatAssistant)
    ↓
[Post-processing]
    ├─ Currency conversion (if requested)
    ├─ Formatting
    └─ Suggestions
    ↓
Response JSON
```

---

## 🧪 Testing Architecture

### Test Organization

```
tests/
├── test_integration.py              # Full integration tests
├── test_vestor_service.py           # Vestor AI tests
├── test_newsfeed_ui_integration.py  # Newsfeed feature tests
├── test_logging_config.py           # Logging tests
├── test_analyst_integration.py      # Analyst data tests
├── integration/                     # Integration test suite
│   └── test_market_sentiment_api.py
├── unit/                            # Unit tests
│   └── test_currency_conversion.py
└── conversation_scenarios/          # Conversation test data
```

### Test Strategy

- **Unit Tests**: Individual functions & classes
- **Integration Tests**: Multi-component workflows
- **End-to-End Tests**: Full request/response cycles
- **Conversation Tests**: Vestor dialogue scenarios

---

## 📝 Configuration Management

### Environment Variables

```bash
# Required
export SECRET_KEY="production-secret-key"
export FLASK_ENV="production"

# Optional: Social Media APIs
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"

# Optional: Logging
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

### Application Config

Located in `src/config/config.py`:

```python
class Config:
    # API Endpoints
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    
    # Model Configurations
    FINBERT_MODEL = "ProsusAI/finbert"
    TWITTER_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    # Analysis Defaults
    DEFAULT_TIMEFRAME = "3mo"
    DEFAULT_CHART_TYPE = "candlestick"
    DEFAULT_CURRENCY = "USD"
    
    # Limits
    MAX_TICKERS = 10
    MAX_NEWS = 10
    MAX_SOCIAL = 10
```

---

## 🚀 Deployment Considerations

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure reverse proxy (nginx/Apache)
- [ ] Enable HTTPS
- [ ] Set up log rotation
- [ ] Configure database (if needed)
- [ ] Set resource limits
- [ ] Enable rate limiting
- [ ] Monitor logs

### Docker Deployment

```bash
# Build
docker build -t vestor-ai .

# Run
docker run -p 5000:5000 \
  -e SECRET_KEY="your-secret" \
  -e FLASK_ENV="production" \
  vestor-ai
```

### Scaling Considerations

- **Stateless Design**: No server-side sessions (uses client localStorage)
- **Model Caching**: AI models loaded once, shared across requests
- **API Rate Limits**: Respect external API limits (Yahoo Finance, CoinGecko)
- **Memory**: ~4GB per worker (due to AI models)

---

## 📈 Performance Optimization

### Caching Strategy

- **AI Models**: Loaded once, cached in memory
- **Analysis Results**: Optional caching in analysis service
- **API Responses**: Client-side caching (localStorage)

### GPU Acceleration

- **PyTorch**: Automatic GPU detection
- **FinBERT & RoBERTa**: 5-10x faster on GPU
- **Fallback**: CPU mode (slower but reliable)

---

## 🔄 Future Architecture

### Planned Enhancements

1. **Database Layer**: PostgreSQL/MongoDB for persistent storage
2. **Message Queue**: Celery for background analysis
3. **WebSocket**: Real-time data streaming
4. **Microservices**: Split into analysis, chat, data services
5. **API Gateway**: RESTful API for external integrations

---

## 📚 Additional Documentation

- **[TESTING_GUIDE.md](TESTING_GUIDE.md)**: Testing strategies & examples
- **[LOGGING_CONTROL.md](LOGGING_CONTROL.md)**: Logging features & usage
- **[VESTOR_MODULAR_ARCHITECTURE.md](VESTOR_MODULAR_ARCHITECTURE.md)**: Vestor subsystem design

---

**Last Updated**: October 12, 2025  
**Architecture Version**: 2.0 (Post-Reorganization)
