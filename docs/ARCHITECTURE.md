# Vestor Project Structure & Architecture

**Last Updated**: October 5, 2025  
**Status**: Clean, Production-Ready Structure

---

## 📁 Directory Structure

```
StockAnalysisHelper/
│
├── run.py                          # 🚀 APPLICATION ENTRY POINT
├── logging_config.py               # 📝 Centralized logging configuration
├── requirements.txt                # 📦 Python dependencies
├── README.md                       # 📖 Main documentation
├── DISTRIBUTION.md                 # 📦 Packaging & deployment guide
├── MODEL_CREDITS.md                # 🙏 AI model attributions
├── LICENSE                         # ⚖️ MIT License
├── .gitignore                      # 🚫 Git ignore rules
│
├── app/                            # 🏗️ FLASK APPLICATION PACKAGE
│   ├── __init__.py                # Application factory (create_app)
│   │
│   ├── routes/                    # 🛣️ Route Blueprints
│   │   ├── __init__.py
│   │   ├── main.py               # Home, legacy, utility routes
│   │   ├── analysis.py           # Stock/portfolio analysis endpoints
│   │   └── chat.py               # Vestor AI chat endpoints
│   │
│   ├── services/                  # 💼 Business Logic Layer
│   │   ├── __init__.py
│   │   ├── analysis_service.py   # Analysis orchestration
│   │   └── vestor_service.py     # Vestor AI conversation service
│   │
│   ├── models/                    # 📊 Data Models (future)
│   │   └── __init__.py
│   │
│   └── utils/                     # 🔧 Utility Functions (future)
│       └── __init__.py
│
├── src/                            # 🧠 CORE ANALYSIS MODULES
│   ├── __init__.py
│   ├── portfolio_analyzer.py      # Main portfolio analysis orchestration
│   ├── stock_chat.py              # StockChatAssistant (AI chat core)
│   ├── sentiment_analyzer.py      # FinBERT & Twitter-RoBERTa sentiment
│   ├── multi_model_sentiment.py   # Multi-model sentiment aggregation
│   ├── technical_analyzer.py      # RSI, MACD, indicators
│   ├── data_fetcher.py            # Yahoo Finance data fetching
│   ├── coingecko_fetcher.py       # Cryptocurrency data (CoinGecko API)
│   ├── social_media_fetcher.py    # Reddit/Twitter data (optional)
│   └── chart_generator.py         # Plotly chart generation
│
├── templates/                      # 🎨 JINJA2 HTML TEMPLATES
│   ├── index-modern.html          # Main modern UI
│   └── index-legacy.html          # Legacy UI (for reference)
│
├── static/                         # 🖼️ FRONTEND ASSETS
│   ├── css/
│   │   ├── modern.css            # Modern theme (Bootstrap 5.3)
│   │   └── style.css             # Legacy styles
│   └── js/
│       └── app.js                # Main frontend application logic
│
├── docs/                           # 📚 DOCUMENTATION
│   └── .archive/                  # 🗄️ Archived dev notes (git ignored)
│       ├── app.py                 # Old monolithic app
│       ├── vestor_chat.py         # Old chat logic
│       ├── *.md                   # Old planning documents
│       └── ...
│
├── logs/                           # 📝 APPLICATION LOGS (git ignored)
│   ├── flask.log                  # Main application log
│   ├── security.log               # Security events
│   ├── chat.log                   # Chat interactions
│   ├── analysis.log               # Analysis requests
│   └── unanswered_questions.log   # Chat questions needing improvement
│
├── exports/                        # 💾 ANALYSIS EXPORTS (git ignored)
│   └── analysis_*.json            # Generated analysis files
│
└── __pycache__/                    # 🗑️ Python bytecode (git ignored)
```

---

## 🏗️ Architecture Overview

### Application Factory Pattern

**`run.py`** → **`app/__init__.py:create_app()`** → Flask app instance

```python
# run.py
from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Blueprint Structure

| Blueprint | Prefix | File | Purpose |
|-----------|--------|------|---------|
| `main` | `/` | `routes/main.py` | Home, legacy, utilities |
| `analysis` | `/analyze`, `/exports` | `routes/analysis.py` | Stock analysis |
| `chat` | `/chat`, `/get-chat-history` | `routes/chat.py` | Vestor conversations |

### Service Layer Pattern

Separates business logic from HTTP layer:

```
routes/chat.py → services/vestor_service.py → src/stock_chat.py
                                              → src/sentiment_analyzer.py
                                              → services/analysis_service.py
```

---

## 🎯 Key Components

### 1. Application Entry (`run.py`)

- **Purpose**: Start Flask application
- **Responsibilities**:
  - Import `create_app()` factory
  - Configure logging
  - Run development server

### 2. Application Factory (`app/__init__.py`)

- **Pattern**: Factory pattern for testability
- **Responsibilities**:
  - Create Flask app instance
  - Configure sessions, secrets
  - Register blueprints
  - Set up folders (exports)

### 3. Routes (Blueprints)

#### `routes/main.py`
- `/` - Home page (modern UI)
- `/legacy` - Legacy UI
- `/clear-chat` - Clear session

#### `routes/analysis.py`
- `POST /analyze` - Analyze stocks/portfolio
- `GET /exports/<filename>` - Download analysis

#### `routes/chat.py`
- `POST /chat` - Vestor conversation
- `GET /get-chat-history` - Load chat history

### 4. Services (Business Logic)

#### `services/vestor_service.py`
- **Class**: `VestorService`
- **Methods**:
  - `process_chat()` - Main conversation handler
  - `_detect_tickers()` - Extract tickers from text
  - `_build_vestor_prompt()` - Create AI system prompt
  - `_resolve_ticker()` - Determine which stock to discuss

#### `services/analysis_service.py`
- **Class**: `AnalysisService`
- **Methods**:
  - `analyze_ticker()` - Single stock analysis
  - `get_cached_analysis()` - Retrieve cached results
  - Cache management

### 5. Core Modules (`src/`)

#### `stock_chat.py`
- **Class**: `StockChatAssistant`
- **AI Models**: DistilBERT for conversational Q&A
- **Purpose**: Natural language understanding

#### `sentiment_analyzer.py`
- **Models**: FinBERT, Twitter-RoBERTa
- **Purpose**: News and social media sentiment

#### `technical_analyzer.py`
- **Indicators**: RSI, MACD, SMA, EMA, Bollinger Bands
- **Purpose**: Technical analysis signals

#### `portfolio_analyzer.py`
- **Purpose**: Orchestrate analysis pipeline
- **Workflow**:
  1. Fetch data (data_fetcher, coingecko_fetcher)
  2. Sentiment analysis
  3. Technical analysis
  4. Score combination
  5. Recommendation generation

---

## 🔄 Request Flow Examples

### Chat Request Flow

```
User Message
    ↓
[Frontend: app.js] POST /chat
    ↓
[Blueprint: routes/chat.py] chat()
    ↓
[Service: vestor_service.py] VestorService.process_chat()
    ↓
    ├─ Detect tickers (company→ticker mapping)
    ├─ Build conversation context
    ├─ Determine mode (conversation vs analysis)
    ↓
    ├─ [If conversation] → src/stock_chat.py → AI response
    ↓
    └─ [If stock analysis] → services/analysis_service.py
                            → src/portfolio_analyzer.py
                            → sentiment + technical analysis
                            → Generate insights
    ↓
[Response] JSON with answer, ticker, metadata
    ↓
[Frontend] Display in chat interface
```

### Analysis Request Flow

```
User clicks "Analyze"
    ↓
[Frontend: app.js] POST /analyze {tickers: [...]}
    ↓
[Blueprint: routes/analysis.py] analyze()
    ↓
[Service: analysis_service.py] AnalysisService.analyze_ticker()
    ↓
[Core: portfolio_analyzer.py] PortfolioAnalyzer.analyze()
    ↓
    ├─ data_fetcher.py → Yahoo Finance
    ├─ coingecko_fetcher.py → Crypto data
    ├─ sentiment_analyzer.py → FinBERT + RoBERTa
    ├─ technical_analyzer.py → RSI, MACD, etc.
    └─ chart_generator.py → Plotly charts
    ↓
[Cache] Store in analysis_cache
    ↓
[Response] JSON with analysis results
    ↓
[Frontend] Display in accordion cards
```

---

## 🔐 Security & Logging

### Logging Configuration (`logging_config.py`)

**Log Files**:
- `logs/flask.log` - General application logs
- `logs/security.log` - Security events (prompt injection attempts)
- `logs/chat.log` - All chat interactions
- `logs/analysis.log` - Analysis requests
- `logs/unanswered_questions.log` - Chat questions needing improvement

**Functions**:
- `setup_logging()` - Configure handlers
- `log_security_event()` - Log security incidents
- `log_chat_interaction()` - Track conversations
- `log_analysis_request()` - Track analyses
- `log_unanswered_question()` - Track unhandled queries

### Session Management

- **Storage**: Flask server-side sessions
- **Data**:
  - `conversation_history` - Last 30 messages
  - `last_ticker` - Context for follow-ups
- **Security**: HttpOnly cookies, SameSite=Lax

---

## 🧪 Testing Strategy (Future)

```
tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures
├── unit/
│   ├── test_vestor_service.py # Service layer tests
│   ├── test_analysis_service.py
│   └── test_stock_chat.py     # AI model tests
├── integration/
│   ├── test_chat_routes.py    # Route integration tests
│   └── test_analysis_routes.py
└── e2e/
    └── test_user_workflows.py # End-to-end scenarios
```

**Run tests**:
```bash
pytest tests/
pytest --cov=app --cov=src tests/
```

---

## 📦 Deployment

### Docker

```bash
docker-compose up -d
```

### Production (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Environment Variables

```bash
export SECRET_KEY="production-secret-key"
export FLASK_ENV="production"
```

---

## 🧹 Code Quality Standards

### Python Style
- **PEP 8** compliance
- **Type hints** for function signatures
- **Docstrings** for all modules, classes, methods

### File Organization
- **No dead code** - All code actively used
- **Single Responsibility** - Each module has clear purpose
- **DRY** (Don't Repeat Yourself)
- **Service layer** for business logic
- **Blueprints** for route organization

### Naming Conventions
- **snake_case** for functions, variables
- **PascalCase** for classes
- **UPPER_CASE** for constants
- **Descriptive names** - No abbreviations

---

## 🗂️ Archive Policy

**`docs/.archive/`** contains:
- Old monolithic `app.py`
- Planning documents (CRITICAL_BUGS.md, etc.)
- Development notes
- Intermediate implementations

**Purpose**: Historical reference, not production code

**Git**: Ignored via `.gitignore`

---

## 📝 Documentation Standards

### README.md
- User-facing documentation
- Quick start guide
- Feature overview

### DISTRIBUTION.md
- Packaging instructions
- Deployment guides
- Platform-specific notes

### MODEL_CREDITS.md
- AI model attributions
- License compliance

### Code Comments
- **Why**, not what
- Complex logic explanations
- TODO/FIXME markers

---

## 🎯 Vestor Persona

**Name**: Vestor  
**Role**: AI Financial Advisor

**Personality Traits**:
- Friendly and approachable
- Knowledgeable but not condescending
- Patient with beginners
- Context-aware
- Proactive (offers to analyze stocks)

**Capabilities**:
- Natural conversation
- Investment education
- Stock/crypto analysis
- Portfolio advice
- Risk management guidance

**Implementation**: `app/services/vestor_service.py` + `src/stock_chat.py`

---

**This document reflects the clean, production-ready structure as of October 5, 2025.**
