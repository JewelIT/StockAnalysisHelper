# Vestor Modular Architecture

**Version**: 2.0  
**Date**: October 10, 2025  
**Purpose**: Refactor monolithic codebase into modular, maintainable components

## 📋 Table of Contents

1. [Overview](#overview)
2. [Folder Structure](#folder-structure)
3. [Module Responsibilities](#module-responsibilities)
4. [Documentation Standards](#documentation-standards)
5. [Migration Plan](#migration-plan)
6. [Benefits](#benefits)

---

## 🎯 Overview

This document describes the new modular architecture for Vestor, transitioning from a monolithic `stock_chat.py` (1,194 lines) to a well-organized set of focused modules.

### Design Principles

1. **Single Responsibility** - Each file has one clear purpose
2. **Small Files** - Maximum 300 lines per file
3. **Comprehensive Documentation** - Google-style docstrings for auto-generation
4. **Type Safety** - All functions use type hints
5. **Clear Dependencies** - Explicit imports, no wildcards

---

## 📁 Folder Structure

```
src/vestor/
├── __init__.py                     # Package exports
├── core/                           # Core bot logic
│   ├── __init__.py
│   ├── vestor_bot.py              # Main orchestrator (~250 lines)
│   └── ai_models.py               # AI model management (~150 lines)
├── conversation/                   # Conversation handling
│   ├── __init__.py
│   ├── context_manager.py         # Context tracking (~120 lines)
│   ├── intent_detector.py         # Question classification (~180 lines)
│   └── ticker_resolver.py         # Company → Ticker mapping (~100 lines)
├── security/                       # Security & validation
│   ├── __init__.py
│   ├── input_validator.py         # Input sanitization (~150 lines)
│   ├── prompt_injection.py        # Injection detection (~200 lines)
│   └── rate_limiter.py            # Rate limiting (~100 lines)
├── knowledge/                      # Financial knowledge base
│   ├── __init__.py
│   ├── sectors.py                 # Market sectors (~250 lines)
│   ├── indicators.py              # Technical indicators (~280 lines)
│   ├── concepts.py                # Investment concepts (~200 lines)
│   └── resources.py               # Educational resources (~150 lines)
└── responses/                      # Response generation
    ├── __init__.py
    ├── generator.py               # Response builder (~250 lines)
    ├── formatters.py              # Markdown formatting (~120 lines)
    └── templates.py               # Templates (optional, ~100 lines)
```

**Total**: ~2,600 lines across 17 files (vs 1,194 in one file)  
**Average per file**: ~153 lines

---

## 📦 Module Responsibilities

### `core/` - Core Functionality

#### `vestor_bot.py`
**Purpose**: Main VestorBot orchestrator

**Responsibilities**:
- Initialize and configure Vestor
- Route questions to appropriate handlers
- Manage conversation flow
- Coordinate between modules

**Key Classes**:
- `VestorBot` - Main bot interface

**Example**:
```python
from vestor import VestorBot

vestor = VestorBot()
response = vestor.ask("What are consumer staples?")
```

#### `ai_models.py`
**Purpose**: AI model loading and caching

**Responsibilities**:
- Lazy-load AI models (DistilBERT, FinBERT)
- Cache loaded models
- Handle GPU/CPU selection
- Model health checks

**Key Classes**:
- `AIModelManager` - Singleton for model management

---

### `conversation/` - Conversation Management

#### `context_manager.py`
**Purpose**: Track conversation context

**Responsibilities**:
- Store conversation history
- Track mentioned tickers
- Maintain topic context
- Provide context to other modules

**Key Classes**:
- `ConversationContext` - Context state
- `ContextManager` - Context operations

#### `intent_detector.py`
**Purpose**: Classify user questions

**Responsibilities**:
- Detect question type (educational, recommendation, technical)
- Extract key entities (tickers, concepts)
- Provide intent metadata

**Key Classes**:
- `IntentDetector` - Intent classification

**Intent Types**:
- `EDUCATIONAL` - "What is RSI?"
- `RECOMMENDATION` - "Should I buy Apple?"
- `TECHNICAL` - "What's the MACD?"
- `SENTIMENT` - "What's the market feeling?"
- `GENERAL` - Other questions

#### `ticker_resolver.py`
**Purpose**: Resolve company names to tickers

**Responsibilities**:
- Map company names to symbols ("Apple" → "AAPL")
- Handle crypto ("Bitcoin" → "BTC-USD")
- Detect ticker mentions in text
- Validate ticker symbols

**Key Functions**:
- `resolve_ticker(text: str) -> Optional[str]`
- `detect_tickers(text: str) -> List[str]`

---

### `security/` - Security & Validation

#### `input_validator.py`
**Purpose**: Validate and sanitize user inputs

**Responsibilities**:
- XSS prevention
- SQL injection prevention
- Input length limits
- Character whitelist/blacklist

**Key Functions**:
- `validate_input(text: str) -> ValidationResult`
- `sanitize_input(text: str) -> str`
- `is_safe(text: str) -> bool`

#### `prompt_injection.py`
**Purpose**: Detect prompt injection attacks

**Responsibilities**:
- Detect role manipulation attempts
- Identify instruction override attempts
- Classify attack severity
- Log security events

**Key Functions**:
- `detect_injection(text: str) -> InjectionResult`
- `get_severity(text: str) -> Severity`

**Severity Levels**:
- `LOW` - Suspicious but unclear
- `MEDIUM` - Likely manipulation attempt
- `HIGH` - Clear attack pattern

#### `rate_limiter.py`
**Purpose**: Prevent abuse and spam

**Responsibilities**:
- Track request rates per IP/user
- Enforce rate limits
- Implement backoff strategies
- Log abuse attempts

---

### `knowledge/` - Financial Knowledge Base

#### `sectors.py`
**Purpose**: Market sector information

**Responsibilities**:
- Define sector characteristics
- List companies by sector
- Explain sector dynamics
- Provide sector recommendations

**Key Functions**:
- `get_sector_info(sector: str) -> SectorInfo`
- `get_companies_in_sector(sector: str) -> List[str]`
- `explain_sector(sector: str) -> str`

**Sectors Covered**:
- Technology, Healthcare, Financials
- Consumer Staples, Consumer Discretionary
- Energy, Industrials, Materials
- Real Estate, Utilities, Communication Services

#### `indicators.py`
**Purpose**: Technical indicator explanations

**Responsibilities**:
- Explain technical indicators (RSI, MACD, etc.)
- Provide interpretation guidelines
- Give usage examples
- Explain limitations

**Key Functions**:
- `explain_rsi() -> str`
- `explain_macd() -> str`
- `explain_moving_averages() -> str`
- `get_indicator_info(name: str) -> IndicatorInfo`

#### `concepts.py`
**Purpose**: Investment concept education

**Responsibilities**:
- Explain financial concepts
- Provide real-world examples
- Link related concepts
- Recommend learning paths

**Key Functions**:
- `explain_concept(name: str) -> str`
- `get_related_concepts(name: str) -> List[str]`

**Concepts Covered**:
- P/E Ratio, Dividends, Market Cap
- Volatility, Beta, Diversification
- Bull/Bear Markets, ETFs, Options

#### `resources.py`
**Purpose**: Educational resources

**Responsibilities**:
- Recommend books, courses, websites
- Organize resources by level
- Provide verified sources
- Update resource database

**Key Functions**:
- `get_beginner_resources() -> List[Resource]`
- `get_technical_resources() -> List[Resource]`
- `get_book_recommendations(topic: str) -> List[Book]`

---

### `responses/` - Response Generation

#### `generator.py`
**Purpose**: Generate formatted responses

**Responsibilities**:
- Build responses based on intent
- Inject knowledge from knowledge base
- Apply response formatters
- Ensure no conversation loops

**Key Functions**:
- `generate_response(question: str, intent: Intent, context: Context) -> str`
- `generate_educational_response(...) -> str`
- `generate_recommendation_response(...) -> str`

#### `formatters.py`
**Purpose**: Format text for display

**Responsibilities**:
- Apply Markdown formatting
- Create bulleted/numbered lists
- Format tables
- Add emojis/icons

**Key Functions**:
- `format_markdown(text: str) -> str`
- `create_list(items: List[str], style: str) -> str`
- `create_table(data: Dict) -> str`
- `add_emojis(text: str) -> str`

#### `templates.py`
**Purpose**: Response templates (if needed)

**Responsibilities**:
- Store reusable response patterns
- Provide template variables
- Ensure consistency

---

## 📝 Documentation Standards

### Google-Style Docstrings

All functions, classes, and modules use Google-style docstrings for Sphinx auto-documentation:

```python
def resolve_ticker(company_name: str, include_crypto: bool = True) -> Optional[str]:
    """
    Resolve a company name to its ticker symbol.
    
    This function searches the internal company-to-ticker mapping and returns
    the corresponding ticker symbol. It supports both stocks and cryptocurrencies.
    
    Args:
        company_name: The name of the company (e.g., "Apple", "Microsoft")
        include_crypto: Whether to include cryptocurrency mappings (default: True)
        
    Returns:
        The ticker symbol (e.g., "AAPL") if found, None otherwise
        
    Raises:
        ValueError: If company_name is empty or invalid
        
    Examples:
        >>> resolve_ticker("Apple")
        "AAPL"
        >>> resolve_ticker("Bitcoin")
        "BTC-USD"
        >>> resolve_ticker("Unknown Company")
        None
        
    Note:
        Case-insensitive matching is performed automatically.
        Company names are normalized before lookup.
        
    See Also:
        - detect_tickers(): Find all tickers in a text
        - validate_ticker(): Check if a ticker is valid
    """
    if not company_name or not company_name.strip():
        raise ValueError("Company name cannot be empty")
    
    normalized = company_name.lower().strip()
    # ... implementation ...
```

### Type Hints

All functions include complete type hints:

```python
from typing import Dict, List, Optional, Tuple, Union

def analyze_sentiment(
    text: str,
    model: Optional[str] = None,
    threshold: float = 0.5
) -> Dict[str, Union[str, float]]:
    """Analyze sentiment of financial text."""
    ...
```

### Module Docstrings

Every file starts with a module docstring:

```python
"""
Ticker Resolution Module

This module provides functionality for resolving company names to ticker symbols.
It supports both traditional stocks and cryptocurrencies.

Key Features:
    - Case-insensitive company name matching
    - Support for common abbreviations ("JPM" → "JPM")
    - Cryptocurrency support ("Bitcoin" → "BTC-USD")
    - Fuzzy matching for typos (optional)

Example Usage:
    >>> from vestor.conversation import resolve_ticker
    >>> ticker = resolve_ticker("Apple")
    >>> print(ticker)
    "AAPL"

Dependencies:
    - re: For text pattern matching
    - typing: For type hints

Author: Vestor Team
Version: 2.0
Date: October 2025
"""
```

---

## 🔄 Migration Plan

### Phase 1: Setup & Security (Week 1)
- [x] Create folder structure
- [ ] Extract `security/input_validator.py`
- [ ] Extract `security/prompt_injection.py`
- [ ] Write unit tests for security modules
- [ ] Update imports in main codebase

### Phase 2: Knowledge Base (Week 2)
- [ ] Extract `knowledge/sectors.py`
- [ ] Extract `knowledge/indicators.py`
- [ ] Extract `knowledge/concepts.py`
- [ ] Extract `knowledge/resources.py`
- [ ] Write unit tests

### Phase 3: Conversation Layer (Week 2)
- [ ] Extract `conversation/context_manager.py`
- [ ] Extract `conversation/intent_detector.py`
- [ ] Extract `conversation/ticker_resolver.py`
- [ ] Write unit tests

### Phase 4: Response Generation (Week 3)
- [ ] Extract `responses/generator.py`
- [ ] Extract `responses/formatters.py`
- [ ] Write unit tests

### Phase 5: Core Refactor (Week 3)
- [ ] Create `core/vestor_bot.py`
- [ ] Create `core/ai_models.py`
- [ ] Update `vestor_service.py` to use new structure
- [ ] Integration tests

### Phase 6: Documentation (Week 4)
- [ ] Setup Sphinx
- [ ] Generate API documentation
- [ ] Write usage guides
- [ ] Create architecture diagrams

### Phase 7: Cleanup (Week 4)
- [ ] Remove old `stock_chat.py`
- [ ] Update all imports project-wide
- [ ] Run full test suite
- [ ] Update README

---

## ✅ Benefits

### Maintainability
- **Find code faster**: Know exactly where to look
- **Understand faster**: Small, focused files are easier to grasp
- **Change safely**: Isolated changes don't break unrelated features

### Testability
- **Unit tests**: Each file = one test file
- **Mock easily**: Clear interfaces make mocking simple
- **Test coverage**: Easier to ensure 100% coverage

### Collaboration
- **Parallel work**: Multiple people can work on different modules
- **Code review**: Smaller PRs, focused changes
- **Onboarding**: New developers can understand one module at a time

### Documentation
- **Auto-generated**: Sphinx creates beautiful docs from docstrings
- **Always updated**: Docs live with code
- **Easy to find**: Clear module structure

### Reusability
- **Components**: Each module can be used independently
- **Other projects**: Can reuse `security/`, `knowledge/` elsewhere
- **API creation**: Easy to expose modules as API endpoints

---

## 📊 Before vs After

### Before (Monolithic)
```
src/stock_chat.py (1,194 lines)
├─ Security checks
├─ Conversation handling
├─ Knowledge base (sectors, indicators, concepts)
├─ Response generation
├─ AI model management
└─ Everything else!

Problems:
❌ Hard to find specific code
❌ Difficult to test in isolation
❌ Can't work on features in parallel
❌ Unclear what depends on what
❌ Hard to document
```

### After (Modular)
```
src/vestor/ (17 files, ~2,600 lines)
├─ security/ (3 files, ~450 lines)
├─ knowledge/ (4 files, ~880 lines)
├─ conversation/ (3 files, ~400 lines)
├─ responses/ (3 files, ~470 lines)
└─ core/ (2 files, ~400 lines)

Benefits:
✅ Clear organization
✅ Easy to test each module
✅ Parallel development possible
✅ Clear dependencies
✅ Auto-generated docs
✅ Reusable components
```

---

## 🔗 Import Examples

### Old Way
```python
# Monolithic import
from src.stock_chat import StockChatAssistant

# Create instance
chat = StockChatAssistant()
chat.load_model()

# Use it
response = chat.answer_question(question, context, ticker)
```

### New Way
```python
# Clean, modular imports
from vestor import VestorBot
from vestor.security import validate_input
from vestor.conversation import resolve_ticker

# Validate input
if not validate_input(user_question):
    return "Invalid input"

# Resolve ticker
ticker = resolve_ticker("Apple")

# Ask Vestor
vestor = VestorBot()
response = vestor.ask(user_question, ticker=ticker)
```

**Benefits**:
- Clearer intent
- More testable
- Better separation of concerns

---

## 📚 Documentation Generation

### Setup Sphinx

```bash
# Install Sphinx and extensions
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Initialize Sphinx
cd docs/
sphinx-quickstart

# Configure conf.py
# (See docs/conf.py for full configuration)
```

### Generate Docs

```bash
# Auto-discover modules
cd docs/
sphinx-apidoc -f -o source/ ../src/vestor/

# Build HTML documentation
make html

# View documentation
open build/html/index.html
```

### Continuous Documentation

```bash
# Watch for changes and rebuild
sphinx-autobuild source/ build/html/
```

---

## 🧪 Testing Strategy

Each module has corresponding tests:

```
tests/
├── unit/                          # Unit tests (one per module)
│   ├── security/
│   │   ├── test_input_validator.py
│   │   └── test_prompt_injection.py
│   ├── conversation/
│   │   ├── test_context_manager.py
│   │   ├── test_intent_detector.py
│   │   └── test_ticker_resolver.py
│   ├── knowledge/
│   │   ├── test_sectors.py
│   │   ├── test_indicators.py
│   │   └── test_concepts.py
│   └── responses/
│       ├── test_generator.py
│       └── test_formatters.py
├── integration/                   # Integration tests
│   ├── test_vestor_bot.py
│   └── test_full_conversation.py
└── e2e/                          # End-to-end tests
    └── conversation_scenarios/
```

---

## 📈 Success Metrics

- **File Size**: All files < 300 lines ✅
- **Test Coverage**: > 80% across all modules
- **Documentation**: 100% of public APIs documented
- **Build Time**: Documentation builds < 30 seconds
- **Code Review**: PRs with < 200 lines of changes

---

## 🚀 Next Steps

1. **Start Phase 1**: Extract security modules this week
2. **Setup CI/CD**: Auto-generate docs on every commit
3. **Write Examples**: Create usage examples for each module
4. **Team Review**: Get feedback on architecture
5. **Iterate**: Refine based on real-world usage

---

## 📞 Questions?

For questions about this architecture, contact the Vestor team or review:
- `/docs/ARCHITECTURE.md` (this file)
- `/tests/README_SCENARIOS.md` (testing guide)
- `/src/vestor/README.md` (module overview)

---

**Document Version**: 2.0  
**Last Updated**: October 10, 2025  
**Status**: ⚠️ In Progress (Phase 1)
