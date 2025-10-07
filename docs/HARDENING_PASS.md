# Hardening Pass - Code Cleanup & Organization

**Date**: October 7, 2025  
**Branch**: feature/chatbot

## 1. Files to Remove/Clean

### ✅ Backup Files to Remove
- [ ] `static/js/app.js.backup` - Created during development, no longer needed

### ✅ Root-Level Test Files to Move
- [ ] `test_analyst_integration.py` → `tests/test_analyst_integration.py`
- [ ] `test_selenium_stocktwits.py` → `tests/test_selenium_stocktwits.py`

### ✅ Documentation to Consolidate (Move to docs/)
- [ ] `ANALYST_CONSENSUS_IMPLEMENTATION.md` → `docs/features/`
- [ ] `BUGFIX_SUMMARY.md` → `docs/changelog/`
- [ ] `CHANGELOG_newsfeed_filters.md` → `docs/changelog/`
- [ ] `COMPACT_UI_GUIDE.md` → `docs/features/`
- [ ] `FILE_STATE_INVESTIGATION.md` → `docs/troubleshooting/` (or delete if obsolete)
- [ ] `SELENIUM_STOCKTWITS_IMPLEMENTATION.md` → `docs/features/`
- [ ] `UI_IMPROVEMENTS.md` → `docs/features/`

### ✅ Logs to Ignore (Already in .gitignore)
- [x] `flask.log` - Runtime log, should not be committed
- [x] `logs/` directory - Already ignored

## 2. .gitignore Improvements

### Add Missing Patterns
```gitignore
# Backup files
*.backup
*.bak

# Test output
.pytest_cache/
htmlcov/
.coverage
*.cover

# Jupyter Notebooks (if any)
*.ipynb_checkpoints/

# Environment files
.env.local
.env.*.local

# IDE specific
*.code-workspace
```

## 3. Test Coverage Gaps

### Current Coverage: 50 tests

### Missing Test Cases to Add

#### A. Pre-Market Data Tests
**File**: `tests/test_premarket_data.py` (NEW)
```python
- test_premarket_data_available()
- test_premarket_data_unavailable()
- test_premarket_data_crypto_247()
- test_premarket_data_formatting()
```

#### B. Chart Generator Tests
**File**: `tests/test_chart_generator.py` (NEW)
```python
- test_1day_intraday_intervals()
- test_1week_hourly_intervals()
- test_adaptive_indicators_short_timeframe()
- test_adaptive_indicators_long_timeframe()
- test_xaxis_formatting_intraday()
- test_xaxis_formatting_weekly()
- test_xaxis_formatting_monthly()
- test_chart_title_with_timerange()
```

#### C. Analyst Consensus Tests (Expand Existing)
**File**: `tests/test_analyst_consensus.py` (NEW)
```python
- test_analyst_minimum_threshold_2()
- test_analyst_coverage_level_limited()
- test_analyst_coverage_level_standard()
- test_analyst_coverage_level_strong()
- test_gauge_chart_calculation()
- test_no_analyst_data_fallback()
```

#### D. Technical Analyzer Tests (Expand)
**File**: `tests/test_technical_analyzer.py` (NEW)
```python
- test_adaptive_windows_5_points()
- test_adaptive_windows_20_points()
- test_adaptive_windows_50_points()
- test_minimum_data_requirement()
- test_macd_fallback_on_insufficient_data()
- test_bollinger_bands_fallback()
```

#### E. Data Fetcher Tests
**File**: `tests/test_data_fetcher.py` (NEW)
```python
- test_fetch_1day_with_30min_interval()
- test_fetch_1week_with_1hour_interval()
- test_fetch_longer_period_daily_interval()
- test_crypto_vs_stock_detection()
```

#### F. UI Integration Tests
**File**: `tests/test_ui_layout.py` (NEW)
```python
- test_2column_layout_structure()
- test_gauge_chart_render_called()
- test_premarket_display_side_by_side()
- test_analyst_coverage_badge_display()
- test_no_analyst_fallback_message()
```

### Target Coverage: 80+ tests (60% increase)

## 4. Code Organization Refactoring

### A. Create Config Module
**File**: `src/config.py` (NEW)
```python
class Config:
    # Data fetching intervals
    INTRADAY_INTERVAL = "30m"
    WEEKLY_INTERVAL = "1h"
    DAILY_INTERVAL = "1d"
    
    # Technical indicator windows
    MIN_DATA_POINTS = 5
    ADAPTIVE_WINDOWS = {
        'sma_short': lambda n: min(20, max(5, n // 3)),
        'sma_long': lambda n: min(50, max(10, n // 2)),
        'rsi': lambda n: min(14, max(5, n // 4)),
        'macd_fast': lambda n: min(12, max(3, n // 5)),
        'macd_slow': lambda n: min(26, max(6, n // 3)),
        'macd_signal': lambda n: min(9, max(3, n // 6)),
    }
    
    # Analyst coverage thresholds
    ANALYST_MIN_COVERAGE = 2
    ANALYST_LIMITED = 4
    ANALYST_STANDARD = 9
    ANALYST_STRONG = 10
    
    # Chart dimensions
    GAUGE_WIDTH = 280
    GAUGE_HEIGHT = 180
    CHART_HEIGHT_STANDARD = 800
    CHART_HEIGHT_VOLUME = 900
```

### B. Extract Constants from Files
- [ ] Move magic numbers from `technical_analyzer.py` to `config.py`
- [ ] Move chart dimensions from `chart_generator.py` to `config.py`
- [ ] Move analyst thresholds from `portfolio_analyzer.py` to `config.py`

### C. Create Utility Module
**File**: `src/utils.py` (NEW)
```python
def format_timeframe_display(time_delta):
    """Convert timedelta to human-readable format"""
    
def format_price(price, ticker):
    """Format price with appropriate decimal places"""
    
def calculate_percentage_change(old, new):
    """Calculate percentage change with safety checks"""
```

### D. Improve Module Structure
```
src/
├── __init__.py
├── config.py          # NEW - Configuration constants
├── utils.py           # NEW - Utility functions
├── core/              # NEW - Core analysis modules
│   ├── __init__.py
│   ├── sentiment_analyzer.py
│   ├── technical_analyzer.py
│   └── analyst_consensus.py
├── data/              # NEW - Data fetching
│   ├── __init__.py
│   ├── data_fetcher.py
│   └── coingecko_fetcher.py
├── visualization/     # NEW - Charts and UI
│   ├── __init__.py
│   └── chart_generator.py
└── chat/              # NEW - AI chat functionality
    ├── __init__.py
    └── stock_chat.py
```

## 5. Documentation Structure

### Reorganize docs/
```
docs/
├── README.md
├── features/
│   ├── analyst_consensus.md
│   ├── compact_ui.md
│   ├── pre_market_data.md
│   ├── social_media_integration.md
│   └── adaptive_indicators.md
├── changelog/
│   ├── 2024-Q4.md
│   ├── newsfeed_filters.md
│   └── bugfixes.md
├── api/
│   ├── endpoints.md
│   └── data_structures.md
├── troubleshooting/
│   ├── common_issues.md
│   └── debugging.md
└── architecture/
    ├── overview.md
    ├── data_flow.md
    └── testing_strategy.md
```

## 6. Security & Performance

### A. Add Input Validation
**File**: `src/validators.py` (NEW)
```python
def validate_ticker(ticker: str) -> bool:
    """Validate ticker symbol format"""
    
def validate_timeframe(timeframe: str) -> bool:
    """Validate timeframe parameter"""
    
def sanitize_user_input(text: str) -> str:
    """Sanitize user input for chat"""
```

### B. Add Rate Limiting
**File**: `app/middleware/rate_limiter.py` (NEW)
```python
from flask_limiter import Limiter

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### C. Add Caching
**File**: `app/middleware/cache.py` (NEW)
```python
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})
```

## 7. Error Handling Improvements

### A. Custom Exception Classes
**File**: `src/exceptions.py` (NEW)
```python
class DataFetchError(Exception):
    """Raised when data fetching fails"""
    
class AnalysisError(Exception):
    """Raised when analysis computation fails"""
    
class ChartGenerationError(Exception):
    """Raised when chart generation fails"""
    
class InsufficientDataError(Exception):
    """Raised when not enough data for indicators"""
```

### B. Centralized Error Handler
**File**: `app/error_handlers.py` (NEW)
```python
@app.errorhandler(DataFetchError)
def handle_data_fetch_error(error):
    return jsonify({'error': str(error)}), 503
```

## 8. Logging Improvements

### A. Structured Logging
**File**: Update `logging_config.py`
```python
import logging
import json

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'module': record.module,
            'message': record.getMessage(),
            'ticker': getattr(record, 'ticker', None),
            'timeframe': getattr(record, 'timeframe', None)
        }
        return json.dumps(log_data)
```

## 9. Performance Optimizations

### A. Database for Caching (Optional)
- [ ] Consider SQLite for caching analyst data
- [ ] Cache historical data for frequently accessed tickers
- [ ] Store pre-computed indicators

### B. Async Data Fetching
- [ ] Parallelize news, social media, and analyst data fetching
- [ ] Use `asyncio` for concurrent API calls

## 10. CI/CD Setup

### A. GitHub Actions Workflow
**File**: `.github/workflows/test.yml` (NEW)
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v
      - name: Run linter
        run: flake8 src/ app/
```

## Implementation Priority

### Phase 1: Immediate (This Session)
1. ✅ Remove backup files
2. ✅ Move root-level test files to tests/
3. ✅ Update .gitignore
4. ✅ Create config.py with constants

### Phase 2: Testing (Next Session)
5. Add missing test cases
6. Achieve 80+ test coverage

### Phase 3: Refactoring (Future)
7. Reorganize module structure
8. Add validators and error handlers
9. Implement caching

### Phase 4: DevOps (Future)
10. Set up CI/CD
11. Add performance monitoring
12. Database integration

## Success Metrics

- ✅ Test coverage: 50 → 80+ tests
- ✅ Code organization: flat → modular structure
- ✅ Documentation: scattered → organized
- ✅ Security: basic → validated inputs
- ✅ Performance: baseline → cached + optimized

## Notes

- Keep backward compatibility during refactoring
- Update README.md with new structure
- Document all breaking changes
- Maintain test suite during reorganization
