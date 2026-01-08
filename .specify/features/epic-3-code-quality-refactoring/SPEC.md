# Feature Specification: Code Quality Refactoring

**Feature Branch**: `feature/code-quality-refactoring`  
**Created**: 2026-01-08  
**Status**: Not Started  
**Epic**: Epic 3 - Code Quality Refactoring  
**Priority**: MEDIUM  
**Estimated Effort**: 4-6 days  
**Dependencies**: Epic 1 and Epic 2 complete (to avoid refactoring code that's about to change)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Unified Repository Pattern (Priority: P1)

All data access (market data, crypto data, news) follows the Repository Pattern with clear interface contracts.

**Why this priority**: Foundational architectural pattern. Makes code testable, maintainable, and consistent with auth system.

**Independent Test**: Can be tested by mocking repository interfaces in unit tests and verifying services don't directly call external APIs.

**Acceptance Scenarios**:

1. **Given** a service needs market data, **When** it calls `market_data_repo.get_stock_price("AAPL")`, **Then** repository handles API calls and returns domain model
2. **Given** a unit test, **When** testing service logic, **Then** in-memory repository can be injected without external API calls
3. **Given** a repository interface, **When** reviewing code, **Then** no implementation details (API keys, HTTP clients) are exposed
4. **Given** a new data source, **When** adding it, **Then** new repository implementation can be added without changing service code

---

### User Story 2 - Dependency Injection Everywhere (Priority: P1)

All services receive dependencies via constructor injection (no global singletons or direct instantiation).

**Why this priority**: Enables testing, makes dependencies explicit, prevents tight coupling.

**Independent Test**: Can be tested by instantiating services with mock dependencies and verifying they work in isolation.

**Acceptance Scenarios**:

1. **Given** a service class, **When** reviewing constructor, **Then** all dependencies are passed as parameters (no `self.repo = Repository()` inside)
2. **Given** a Flask route, **When** instantiating service, **Then** factory pattern or DI container provides dependencies
3. **Given** a unit test, **When** testing service, **Then** mock dependencies can be injected without patching globals
4. **Given** app initialization, **When** app starts, **Then** dependency graph is constructed in one place (app factory or DI container)

---

### User Story 3 - Type Hints & Static Analysis (Priority: P2)

All functions have type hints and mypy passes with ≥80% coverage.

**Why this priority**: Catches bugs at development time, improves IDE autocomplete, serves as documentation.

**Independent Test**: Can be tested by running `mypy .` and verifying zero type errors.

**Acceptance Scenarios**:

1. **Given** a function definition, **When** reviewing code, **Then** all parameters and return types are annotated
2. **Given** mypy configuration, **When** running `mypy .`, **Then** zero type errors reported
3. **Given** IDE (VS Code), **When** hovering over function, **Then** full type signature is displayed
4. **Given** a function call with wrong type, **When** mypy runs, **Then** type mismatch is flagged before runtime

---

### User Story 4 - Code Coverage ≥90% (Priority: P2)

Critical business logic has ≥90% test coverage, measured and enforced in CI/CD.

**Why this priority**: Ensures refactoring doesn't break functionality, gives confidence in changes.

**Independent Test**: Can be tested by running `pytest --cov` and reviewing coverage report.

**Acceptance Scenarios**:

1. **Given** a new commit, **When** CI/CD runs, **Then** coverage report is generated and checked
2. **Given** coverage below 90%, **When** PR is created, **Then** CI/CD fails with coverage report
3. **Given** untested code path, **When** reviewing coverage report, **Then** missing lines are highlighted
4. **Given** critical service (AuthenticationService, AnalysisService), **When** checking coverage, **Then** coverage is ≥95%

---

### User Story 5 - Linting & Code Style (Priority: P3)

Code passes linting (flake8, pylint) and follows PEP 8 conventions.

**Why this priority**: Code consistency, readability, catches common bugs. Lower priority than functional refactoring.

**Independent Test**: Can be tested by running `flake8 .` and `pylint src/` and verifying zero high-severity issues.

**Acceptance Scenarios**:

1. **Given** a new commit, **When** CI/CD runs, **Then** flake8 executes with project config
2. **Given** linting violations, **When** PR is created, **Then** CI/CD fails with violation list
3. **Given** existing code, **When** running pylint, **Then** code quality score is ≥8.0/10
4. **Given** pre-commit hook, **When** committing code, **Then** linter runs automatically and blocks commit if failures

---

### User Story 6 - Comprehensive Docstrings (Priority: P3)

All public classes and functions have docstrings following Google or NumPy style.

**Why this priority**: Improves maintainability and onboarding. Lower priority than structural refactoring.

**Independent Test**: Can be tested by running pydocstyle or interrogate and checking coverage.

**Acceptance Scenarios**:

1. **Given** a public function, **When** reviewing code, **Then** docstring includes description, args, returns, raises
2. **Given** a class, **When** reviewing code, **Then** class docstring includes purpose and usage examples
3. **Given** documentation generator (Sphinx), **When** running `make html`, **Then** API docs are generated from docstrings
4. **Given** IDE hover, **When** hovering over function, **Then** docstring is displayed as tooltip

---

### Edge Cases

- What happens when repository fails to connect to external API? → Repository raises domain exception, service handles gracefully
- How are circular dependencies prevented in DI? → Use factory pattern or dependency graph analyzer
- What if type hints conflict with dynamic Python features? → Use `typing.Any` or `typing.Union` sparingly, prefer explicit types
- How are legacy services migrated without breaking existing functionality? → Strangler fig pattern (new code alongside old, gradual migration)
- What if coverage drops during refactoring? → Temporarily lower threshold, but create tickets to restore coverage

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All data access MUST go through Repository interfaces (no direct API calls in services)
- **FR-002**: All services MUST receive dependencies via constructor injection
- **FR-003**: All repository implementations MUST implement defined interfaces
- **FR-004**: All functions MUST have type hints for parameters and return values
- **FR-005**: All public classes/functions MUST have docstrings (Google or NumPy style)
- **FR-006**: Test coverage MUST be ≥90% for critical paths (auth, analysis, market data)
- **FR-007**: Code MUST pass flake8 with max-line-length=120, max-complexity=10
- **FR-008**: Code MUST pass pylint with score ≥8.0/10
- **FR-009**: mypy MUST pass with ≥80% type coverage
- **FR-010**: All repository implementations MUST have in-memory variants for testing

### Non-Functional Requirements

- **NFR-001**: Refactoring MUST NOT change external API contracts (backwards compatibility)
- **NFR-002**: Refactoring MUST NOT degrade performance (benchmark critical paths)
- **NFR-003**: CI/CD pipeline MUST run all quality checks (linting, types, coverage) on every commit
- **NFR-004**: Quality gates MUST fail build if thresholds not met
- **NFR-005**: Refactoring MUST be done incrementally (feature flags if needed)

### Key Entities *(include if feature involves data)*

- **RepositoryInterface**: Abstract base class defining data access contracts
- **ServiceInterface**: Abstract base class defining business logic contracts (optional, for complex services)
- **DomainModel**: Pure Python dataclasses representing business entities (Stock, MarketData, NewsArticle, etc.)

## Technical Architecture

### Components to Refactor

#### 1. Data Layer - Repository Pattern

**Current State**: 
- `src/data/data_fetcher.py` - Direct API calls to yfinance, Finnhub, Alpha Vantage
- `src/data/coingecko_fetcher.py` - Direct CoinGecko API calls
- No abstraction, hard to test

**Target State**:
```python
# app/repositories/market_data_repository.py
class MarketDataRepositoryInterface(ABC):
    @abstractmethod
    def get_stock_price(self, ticker: str) -> Optional[StockPrice]:
        pass
    
    @abstractmethod
    def get_stock_fundamentals(self, ticker: str) -> Optional[StockFundamentals]:
        pass

class MultiSourceMarketDataRepository(MarketDataRepositoryInterface):
    """Aggregates data from yfinance, Finnhub, Alpha Vantage"""
    def __init__(self, yfinance_client, finnhub_client, alpha_vantage_client):
        self._yfinance = yfinance_client
        self._finnhub = finnhub_client
        self._alpha_vantage = alpha_vantage_client
    
    def get_stock_price(self, ticker: str) -> Optional[StockPrice]:
        # Consensus algorithm with multi-source data
        pass

class InMemoryMarketDataRepository(MarketDataRepositoryInterface):
    """For testing - returns mock data"""
    pass
```

**Files to Create**:
- app/repositories/market_data_repository.py
- app/repositories/crypto_repository.py
- app/repositories/news_repository.py

**Files to Refactor**:
- src/data/data_fetcher.py → Extract logic into repository implementations
- src/data/coingecko_fetcher.py → Extract logic into CryptoRepository

#### 2. Service Layer - Dependency Injection

**Current State**:
- `src/services/vestor_service.py` - Direct instantiation of dependencies
- `src/services/market_sentiment_service.py` - Global state, direct API calls
- `src/services/analysis_service.py` - Tightly coupled to data fetchers

**Target State**:
```python
# app/services/market_sentiment_service.py
class MarketSentimentService:
    def __init__(
        self,
        market_data_repo: MarketDataRepositoryInterface,
        news_repo: NewsRepositoryInterface,
        sentiment_analyzer: SentimentAnalyzer
    ):
        self._market_data = market_data_repo
        self._news = news_repo
        self._sentiment_analyzer = sentiment_analyzer
    
    def analyze_market_sentiment(self, sector: Optional[str] = None) -> MarketSentiment:
        # Uses injected dependencies, easy to test
        pass
```

**Files to Refactor**:
- src/services/vestor_service.py
- src/services/market_sentiment_service.py
- src/services/analysis_service.py

**Files to Create**:
- app/di_container.py or app/factory.py (Dependency Injection setup)

#### 3. Domain Models

**Current State**:
- Data structures mixed with logic (dicts, mixed concerns)
- No clear domain boundaries

**Target State**:
```python
# app/models/market.py
@dataclass(frozen=True)
class StockPrice:
    ticker: str
    price: Decimal
    timestamp: datetime
    source: str
    
    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "price": float(self.price),
            "timestamp": self.timestamp.isoformat(),
            "source": self.source
        }

@dataclass(frozen=True)
class MarketSentiment:
    sector: str
    sentiment_score: float  # -1 to 1
    top_stocks: List[StockRecommendation]
    analyzed_at: datetime
```

**Files to Create**:
- app/models/market.py
- app/models/stock.py
- app/models/news.py

#### 4. Type Hints

**Strategy**:
- Add type hints to all new code
- Gradually add to existing code (start with public APIs)
- Configure mypy in pyproject.toml or mypy.ini

**mypy Configuration**:
```ini
# mypy.ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False  # Start lenient, tighten over time
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_unreachable = True
strict_equality = True

[mypy-pytest.*]
ignore_missing_imports = True

[mypy-flask.*]
ignore_missing_imports = True
```

**Files to Update**:
- All Python files (gradual migration)

#### 5. Testing Infrastructure

**Coverage Configuration**:
```ini
# .coveragerc or pyproject.toml
[coverage:run]
source = app,src
omit = 
    */tests/*
    */venv/*
    */__pycache__/*

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
fail_under = 90

[coverage:html]
directory = htmlcov
```

**CI/CD Integration**:
```yaml
# .github/workflows/quality-checks.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: flake8 . --count --max-line-length=120 --statistics
      - run: pylint src/ app/ --fail-under=8.0
      - run: mypy . --ignore-missing-imports
      - run: pytest --cov --cov-fail-under=90
```

**Files to Create**:
- requirements-dev.txt (flake8, pylint, mypy, pytest-cov, etc.)
- .github/workflows/quality-checks.yml
- .coveragerc or update pyproject.toml
- mypy.ini or update pyproject.toml
- .flake8 or update pyproject.toml

#### 6. Linting Configuration

**.flake8**:
```ini
[flake8]
max-line-length = 120
max-complexity = 10
exclude = 
    .git,
    __pycache__,
    venv,
    .venv,
    migrations
ignore = 
    E203,  # Whitespace before ':' (conflicts with black)
    W503   # Line break before binary operator (PEP 8 updated)
```

**.pylintrc** (generate with `pylint --generate-rcfile > .pylintrc`, then customize):
```ini
[MASTER]
ignore=tests,venv,.venv
max-line-length=120

[MESSAGES CONTROL]
disable=
    C0111,  # Missing docstring (too strict initially)
    R0903,  # Too few public methods (not always bad)
    
[DESIGN]
max-args=7
max-locals=20
```

## Success Criteria

### Phase 1: Repository Pattern Migration (Days 1-2)
- [ ] MarketDataRepositoryInterface defined with 5+ methods
- [ ] MultiSourceMarketDataRepository implemented (yfinance + Finnhub + Alpha Vantage)
- [ ] InMemoryMarketDataRepository implemented for testing
- [ ] CryptoRepositoryInterface defined
- [ ] CryptoRepository implemented (CoinGecko)
- [ ] NewsRepositoryInterface defined (if applicable)
- [ ] ≥20 repository unit tests passing
- [ ] No direct API calls in service layer (verified with grep)

### Phase 2: Service Layer Refactoring (Days 3-4)
- [ ] MarketSentimentService refactored with DI
- [ ] AnalysisService refactored with DI
- [ ] VestorService refactored with DI
- [ ] Dependency factory/container implemented
- [ ] Flask routes updated to use factory pattern
- [ ] All 231 existing tests still passing
- [ ] ≥15 new service tests with mocked dependencies

### Phase 3: Type Hints & Static Analysis (Day 5)
- [ ] Type hints added to all repository interfaces
- [ ] Type hints added to all service classes
- [ ] Type hints added to ≥80% of functions
- [ ] mypy configured and passing
- [ ] mypy integration in CI/CD
- [ ] Zero critical type errors

### Phase 4: Quality Gates (Day 6)
- [ ] Coverage reporting configured
- [ ] Coverage ≥90% for app/ (auth + new code)
- [ ] Coverage ≥80% for src/ (legacy code)
- [ ] flake8 configured and passing
- [ ] pylint configured with score ≥8.0
- [ ] CI/CD quality checks passing
- [ ] Pre-commit hooks configured (optional)

### Overall Completion
- [ ] All repository pattern implementations complete
- [ ] All services use dependency injection
- [ ] mypy passing with ≥80% coverage
- [ ] Test coverage ≥90% for critical paths
- [ ] Linting passing (flake8 + pylint)
- [ ] Zero high-severity code quality issues
- [ ] Documentation updated (architecture diagrams)

## Out of Scope (Future Improvements)

- Full black/autopep8 formatting enforcement (can conflict with existing style)
- 100% type coverage (diminishing returns, ≥80% is sufficient)
- Complete docstring coverage (target public APIs first)
- Complexity metrics monitoring (can be added later)
- Performance profiling (separate epic)
- Database ORM migration (SQLAlchemy) - staying with pure Python for now

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Refactoring introduces regressions | High | Critical | Run full test suite after each phase; use feature flags |
| Type hints reveal existing type bugs | Medium | Medium | Fix incrementally; use `# type: ignore` temporarily if needed |
| Coverage targets are too ambitious | Medium | Low | Start with 80%, increase to 90% over time |
| DI container adds complexity | Low | Medium | Use simple factory pattern initially; avoid over-engineering |
| Linting fails on legacy code | High | Low | Fix incrementally; use pylint/flake8 disable comments sparingly |

## Refactoring Strategy: Strangler Fig Pattern

1. **Create new alongside old** - Don't delete old code immediately
2. **Route new requests to new code** - Use feature flags or gradual rollout
3. **Test thoroughly** - Both old and new code paths
4. **Monitor for differences** - Log discrepancies during transition
5. **Remove old code** - Only when new code is stable and proven

**Example**:
```python
# Gradual migration approach
def get_market_data(ticker: str):
    if USE_NEW_REPOSITORY:  # Feature flag
        repo = get_market_data_repository()
        return repo.get_stock_price(ticker)
    else:
        return legacy_data_fetcher.get_stock_price(ticker)
```

## Implementation Notes

- Prioritize repository pattern (biggest architectural win)
- Don't refactor everything at once (incremental migration)
- Keep existing tests passing (green CI/CD throughout)
- Use type hints as documentation (not just for static analysis)
- Set realistic coverage targets (90% for new code, 70-80% for legacy)
- Review linting violations manually (don't blindly auto-fix)

---

**Next Steps**: Generate PLAN.md with detailed implementation tasks
