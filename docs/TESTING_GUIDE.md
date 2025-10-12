# Testing Guide for Developers

## Overview
This guide explains how to write and run tests for the FinBertTest application.

## Test Structure

```
tests/
├── unit/                          # Unit tests (isolated component testing)
│   └── test_currency_conversion.py
├── integration/                   # Integration tests (API endpoint testing)
│   └── test_market_sentiment_api.py
└── e2e/                          # End-to-end tests (full user flow) - Future
```

## Running Tests

### All Tests
```bash
python3 -m pytest tests/ -v
```

### Specific Test File
```bash
python3 -m pytest tests/unit/test_currency_conversion.py -v
```

### Specific Test Class
```bash
python3 -m pytest tests/unit/test_currency_conversion.py::TestCurrencyConversion -v
```

### Specific Test Method
```bash
python3 -m pytest tests/unit/test_currency_conversion.py::TestCurrencyConversion::test_convert_price_usd_to_eur -v
```

### With Coverage Report
```bash
python3 -m pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Watch Mode (auto-run on file changes)
```bash
pip install pytest-watch
ptw tests/
```

## Writing Unit Tests

### Template
```python
"""
Unit tests for [component name]
"""
import pytest
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.your_service import YourService


class TestYourFeature:
    """Test [feature description]"""
    
    def setup_method(self):
        """Setup test fixtures - runs before each test"""
        self.service = YourService()
    
    def teardown_method(self):
        """Cleanup after test - runs after each test"""
        pass
    
    def test_feature_basic_functionality(self):
        """Test [what this tests]"""
        # Arrange
        input_value = 100
        
        # Act
        result = self.service.process(input_value)
        
        # Assert
        assert result == 200
        assert isinstance(result, int)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

### Unit Test Best Practices
1. **Isolate**: Test one component at a time
2. **Mock dependencies**: Use `unittest.mock` or `pytest-mock`
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Test edge cases**: Null, empty, invalid inputs
5. **Descriptive names**: `test_convert_price_with_invalid_currency`

### Example: Testing Service Methods
```python
def test_currency_conversion_handles_none_price(self):
    """Test that conversion handles None price gracefully"""
    service = MarketSentimentService()
    
    # Should not crash with None
    result = service._convert_price(None, 'EUR')
    
    assert result is None  # Or handle as appropriate
```

## Writing Integration Tests

### Template
```python
"""
Integration tests for [API endpoint or feature]
"""
import pytest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import create_app


class TestYourAPI:
    """Integration tests for [endpoint name]"""
    
    def setup_method(self):
        """Setup test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_endpoint_returns_success(self):
        """Test [what this tests]"""
        # Make request
        response = self.client.get('/your-endpoint?param=value')
        
        # Check status
        assert response.status_code == 200
        
        # Parse JSON
        data = json.loads(response.data)
        
        # Validate response
        assert data['success'] is True
        assert 'data' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

### Integration Test Best Practices
1. **Test real HTTP requests**: Use Flask test client
2. **Check status codes**: 200, 400, 404, 500
3. **Validate JSON structure**: Required fields, types
4. **Test parameters**: Query params, POST data
5. **Test error handling**: Invalid inputs, edge cases

### Example: Testing API with Different Parameters
```python
def test_api_with_various_currencies(self):
    """Test API accepts different currency parameters"""
    currencies = ['USD', 'EUR', 'GBP', 'NATIVE']
    
    for currency in currencies:
        response = self.client.get(f'/market-sentiment?currency={currency}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['data']['currency'] == currency
```

## Pytest Features

### Fixtures
```python
@pytest.fixture
def sample_data():
    """Reusable test data"""
    return {
        'ticker': 'AAPL',
        'price': 175.50,
        'reason': 'Test'
    }

def test_with_fixture(sample_data):
    """Use fixture as parameter"""
    assert sample_data['ticker'] == 'AAPL'
```

### Parametrize (test multiple inputs)
```python
@pytest.mark.parametrize("currency,expected_rate", [
    ('USD', 1.0),
    ('EUR', 0.92),
    ('GBP', 0.79),
])
def test_exchange_rates(currency, expected_rate):
    """Test different exchange rates"""
    service = MarketSentimentService()
    rate = service.exchange_rates[currency]
    assert rate == expected_rate
```

### Markers
```python
@pytest.mark.slow
def test_expensive_operation():
    """This test takes a long time"""
    pass

@pytest.mark.skip(reason="API not available")
def test_external_api():
    """Skip this test"""
    pass

# Run specific markers:
# pytest -v -m slow
# pytest -v -m "not slow"
```

### Exception Testing
```python
def test_raises_exception_on_invalid_input():
    """Test that invalid input raises ValueError"""
    service = YourService()
    
    with pytest.raises(ValueError) as exc_info:
        service.process_invalid_data(None)
    
    assert "Invalid input" in str(exc_info.value)
```

## Continuous Integration

### GitHub Actions Example
```yaml
# .github/workflows/test.yml
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
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

## Test-Driven Development (TDD)

### TDD Workflow
1. **Write test first** (it will fail - RED)
2. **Write minimal code** to make it pass (GREEN)
3. **Refactor** while keeping tests green (REFACTOR)

### Example TDD Process
```python
# Step 1: Write failing test
def test_convert_price_to_jpy():
    """Test USD to JPY conversion"""
    service = MarketSentimentService()
    result = service._convert_price(100.0, 'JPY')
    assert result == 14900.0  # Rate: 149.0

# Step 2: Run test (fails - JPY not implemented)
# pytest tests/unit/test_currency_conversion.py::test_convert_price_to_jpy

# Step 3: Implement minimal code
# In market_sentiment_service.py:
# self.exchange_rates['JPY'] = 149.0

# Step 4: Run test (passes)
# Step 5: Refactor if needed
```

## Common Testing Patterns

### Testing Database Operations
```python
@pytest.fixture
def test_db():
    """Create test database"""
    db = create_test_database()
    yield db
    db.cleanup()

def test_save_to_database(test_db):
    """Test saving data to database"""
    record = {'name': 'Test'}
    test_db.save(record)
    
    retrieved = test_db.find_by_name('Test')
    assert retrieved == record
```

### Testing Async Functions
```python
@pytest.mark.asyncio
async def test_async_fetch():
    """Test async API call"""
    result = await fetch_data_async()
    assert result is not None
```

### Testing with Mock
```python
from unittest.mock import Mock, patch

def test_external_api_call():
    """Test with mocked API"""
    with patch('app.services.requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'rate': 0.92}
        
        service = MarketSentimentService()
        rate = service.fetch_live_rate('EUR')
        
        assert rate == 0.92
        mock_get.assert_called_once()
```

## Debugging Tests

### Print Debug Info
```python
def test_with_debug():
    """Test with debug output"""
    result = calculate_something()
    print(f"\nResult: {result}")  # Use -s flag to see output
    assert result > 0

# Run with: pytest tests/unit/test_file.py -s
```

### Drop into Debugger
```python
def test_with_debugger():
    """Test with debugger"""
    result = calculate_something()
    
    import pdb; pdb.set_trace()  # Breakpoint
    
    assert result > 0

# Or run with: pytest tests/unit/test_file.py --pdb
```

### Use pytest's Built-in Debugging
```bash
# Drop into debugger on failures
pytest tests/ --pdb

# Drop into debugger on first failure
pytest tests/ -x --pdb
```

## Test Coverage Goals

### Coverage Targets
- **Critical paths**: 100% coverage
- **Business logic**: 90-100% coverage
- **API endpoints**: 90-100% coverage
- **Utility functions**: 80-90% coverage
- **Overall target**: 80%+

### Checking Coverage
```bash
# Generate coverage report
pytest tests/ --cov=app --cov-report=term-missing

# See which lines are not covered
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

## Resources

### Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### Best Practices
- Test behavior, not implementation
- Keep tests independent
- Use descriptive test names
- Test one thing per test
- Make tests fast
- Don't test external dependencies directly

---
*Last Updated: January 2024*
