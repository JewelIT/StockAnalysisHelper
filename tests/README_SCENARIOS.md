# Vestor Conversation Test Framework

A modular, extensible framework for testing realistic multi-turn conversations with Vestor.

## 🎯 Overview

This framework allows you to:
- Test realistic user conversations with Vestor
- Verify that responses don't create conversation loops
- Ensure educational content is helpful and specific
- Validate technical analysis accuracy
- Add new test scenarios easily

## 📁 Structure

```
tests/
├── conversation_scenarios/          # Scenario modules
│   ├── __init__.py                 # Package initialization
│   ├── base.py                     # Base classes and framework
│   ├── TEMPLATE.py                 # Template for new scenarios
│   ├── beginner_first_steps.py     # Scenario: Complete beginner
│   ├── experienced_trader.py       # Scenario: Technical analysis
│   ├── market_overview.py          # Scenario: Market briefing
│   ├── value_investor.py           # Scenario: Value investing
│   ├── crypto_explorer.py          # Scenario: Crypto education
│   └── [your_scenario.py]          # Add your own!
├── run_scenarios.py                # Main test runner
├── quick_conversation_test.py      # Quick smoke tests
└── README_SCENARIOS.md             # This file
```

## 🚀 Quick Start

### Running Tests

```bash
# Run all scenarios
python3 tests/run_scenarios.py

# Run quick smoke tests only
python3 tests/run_scenarios.py --quick

# Run scenarios with specific tags
python3 tests/run_scenarios.py --tags beginner
python3 tests/run_scenarios.py --tags crypto stocks

# List all available scenarios
python3 tests/run_scenarios.py --list
```

### Quick Smoke Test

For rapid feedback during development:

```bash
python3 tests/quick_conversation_test.py
```

## 📝 Creating New Scenarios

### Step 1: Copy the Template

```bash
cp tests/conversation_scenarios/TEMPLATE.py tests/conversation_scenarios/my_scenario.py
```

### Step 2: Define Your Scenario

```python
from .base import ConversationScenario, ConversationSession


class MyScenario(ConversationScenario):
    """
    Brief description of what this tests
    """
    
    def __init__(self):
        super().__init__(
            name="My Scenario Name",
            description="What this tests",
            user_persona="User description (optional)",
            tags=['tag1', 'tag2']  # For filtering
        )
    
    def run(self) -> ConversationSession:
        self.print_header()
        
        session = ConversationSession(self.name, self.description)
        
        # Your conversation flow
        session.say("Hello Vestor!")
        session.say("What are stocks?")
        session.analyze_stock("AAPL")
        session.say("Should I buy Apple?")
        
        session.print_summary()
        return session
```

### Step 3: Run Your Scenario

Your scenario will be automatically discovered and run!

```bash
python3 tests/run_scenarios.py
```

## 🛠️ Available Methods

### ConversationSession Methods

#### `say(message, wait_seconds=1.5, expect_ticker=None)`
User sends a message to Vestor.

```python
session.say("Tell me about Apple")
session.say("What's the RSI?", wait_seconds=2.0)
```

#### `analyze_stock(ticker, wait_seconds=2.0)`
Request stock analysis.

```python
session.analyze_stock("AAPL")
session.analyze_stock("BTC-USD")
```

#### `check_response(question, expected_keywords, should_not_contain=None)`
Validate that response contains expected content.

```python
session.say("What are consumer staples?")
session.check_response(
    question="What are consumer staples?",
    expected_keywords=['consumer', 'staples', 'defensive'],
    should_not_contain=['would you like me to', 'ask me about']
)
```

#### `get_stats()`
Get conversation statistics.

```python
stats = session.get_stats()
print(f"Messages: {stats['total_messages']}")
print(f"Loops: {stats['loops_detected']}")
```

#### `print_summary()`
Print detailed conversation summary with pass/fail verdict.

```python
session.print_summary()
```

## 🏷️ Scenario Tags

Use tags to organize and filter scenarios:

- **`beginner`**: For users new to investing
- **`advanced`**: For experienced traders
- **`stocks`**: Stock-related scenarios
- **`crypto`**: Cryptocurrency scenarios
- **`technical`**: Technical analysis focus
- **`educational`**: Educational content focus
- **`quick`** or **`smoke`**: Quick validation tests
- **`edge-case`**: Edge cases and unusual inputs

Example:
```python
tags=['beginner', 'stocks', 'educational']
```

Filter by tags:
```bash
python3 tests/run_scenarios.py --tags beginner educational
```

## 📊 Understanding Results

### Test Output

```
================================================================================
SCENARIO: Complete Beginner - First Steps
================================================================================
Description: User learning about investing from scratch
User Persona: Sarah (25) - First job, wants to start investing
Tags: beginner, educational, stocks, basics
================================================================================

================================================================================
👤 USER: Hi! I'm Sarah and I'm new to investing.
================================================================================

🤖 VESTOR: [Response...]

📊 Context Ticker: AAPL
```

### Summary Report

```
################################################################################
CONVERSATION SUMMARY: Complete Beginner - First Steps
################################################################################
Description: User learning about investing from scratch
Duration: 42.3 seconds
Messages: 13
Successful Responses: 13/13
Errors: 0
Final Context Ticker: AAPL
✅ Loop Responses: 0 ✅ PASS

🎉 SCENARIO PASSED
################################################################################
```

### Pass/Fail Criteria

A scenario **PASSES** if:
- ✅ All messages get responses (no errors)
- ✅ No loop-generating phrases detected
  - "Would you like me to..."
  - "Ask me about..."
  - "I can help you with..."

A scenario **FAILS** if:
- ❌ Errors occur during conversation
- ❌ Loop-generating phrases detected
- ❌ Server timeouts or connection issues

## 💡 Best Practices

### 1. Realistic Conversations

Mimic how real users would interact:

```python
# ✅ Good: Natural flow
session.say("Hi, I'm new to investing")
session.say("What exactly is a stock?")
session.say("So if I buy Apple, I own part of it?")

# ❌ Bad: Unnatural, robotic
session.say("Define stock")
session.say("List benefits")
```

### 2. Follow-Up Questions

Test contextual understanding:

```python
session.say("Tell me about Apple")
session.say("Should I buy it?")        # Uses context
session.say("What if it goes down?")   # Continues topic
```

### 3. Mixed Topics

Test topic switching:

```python
session.say("What are consumer staples?")
session.say("Is NVDA a good buy?")         # Jump to different topic
session.say("How volatile is crypto?")     # Another jump
```

### 4. Validation

Check responses meet expectations:

```python
session.say("What is RSI?")
session.check_response(
    question="What is RSI?",
    expected_keywords=['rsi', 'momentum', 'overbought'],
    should_not_contain=['would you like me to']
)
```

### 5. Naming Conventions

- **File names**: `snake_case.py` (e.g., `my_scenario.py`)
- **Class names**: `PascalCase` (e.g., `MyScenario`)
- **Descriptive names**: Indicate what's being tested

## 🐛 Troubleshooting

### Server Not Running

```
❌ Flask server is not running on http://localhost:5000

Please start the server first:
  python3 app.py
```

**Solution**: Start Flask server in another terminal

### No Scenarios Found

```
❌ No scenarios found in conversation_scenarios directory
```

**Solution**: 
- Make sure your scenario file is in `tests/conversation_scenarios/`
- Class must inherit from `ConversationScenario`
- File name shouldn't start with `_`

### Import Errors

```
⚠️ Warning: Could not load scenario from my_scenario.py: No module named 'requests'
```

**Solution**: Install dependencies
```bash
pip install requests
```

### Timeouts

```
❌ ERROR: Connection timeout
```

**Solution**:
- Check server is running
- Increase timeout in `say()`: `session.say("...", wait_seconds=5.0)`
- Check network/firewall settings

## 📈 Examples

### Example 1: Simple Educational Test

```python
class BasicEducation(ConversationScenario):
    def __init__(self):
        super().__init__(
            name="Basic Education",
            description="Tests basic financial education",
            tags=['beginner', 'educational', 'quick']
        )
    
    def run(self) -> ConversationSession:
        self.print_header()
        session = ConversationSession(self.name, self.description)
        
        session.say("What are stocks?")
        session.check_response(
            question="What are stocks?",
            expected_keywords=['stock', 'company', 'ownership']
        )
        
        session.say("What's the difference between stocks and bonds?")
        
        session.print_summary()
        return session
```

### Example 2: Technical Analysis Test

```python
class TechnicalIndicators(ConversationScenario):
    def __init__(self):
        super().__init__(
            name="Technical Indicators",
            description="Tests RSI and MACD explanations",
            tags=['advanced', 'technical']
        )
    
    def run(self) -> ConversationSession:
        self.print_header()
        session = ConversationSession(self.name, self.description)
        
        session.say("What is RSI?")
        session.check_response(
            question="What is RSI?",
            expected_keywords=['rsi', 'momentum', 'overbought', 'oversold']
        )
        
        session.say("What about MACD?")
        session.check_response(
            question="What is MACD?",
            expected_keywords=['macd', 'moving average', 'convergence']
        )
        
        session.print_summary()
        return session
```

### Example 3: Edge Case Test

```python
class EdgeCases(ConversationScenario):
    def __init__(self):
        super().__init__(
            name="Edge Cases",
            description="Tests unusual inputs",
            tags=['edge-case', 'robustness']
        )
    
    def run(self) -> ConversationSession:
        self.print_header()
        session = ConversationSession(self.name, self.description)
        
        # Very short
        session.say("Hi")
        
        # One word
        session.say("Stocks?")
        
        # Typos
        session.say("Whats the bst invesment?")
        
        # Vague
        session.say("What do you think?")
        
        session.print_summary()
        return session
```

## 🔄 Continuous Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Conversation Tests
  run: |
    python3 app.py &
    sleep 5  # Wait for server
    python3 tests/run_scenarios.py --quick
```

## 📚 Additional Resources

- **Framework Code**: `tests/conversation_scenarios/base.py`
- **Example Scenarios**: `tests/conversation_scenarios/*.py`
- **Template**: `tests/conversation_scenarios/TEMPLATE.py`
- **Main Runner**: `tests/run_scenarios.py`

## 🤝 Contributing Scenarios

When you find issues or want to test new features:

1. Create a new scenario file
2. Add descriptive tags
3. Test it: `python3 tests/run_scenarios.py`
4. Commit: `git add tests/conversation_scenarios/my_scenario.py`

Your scenarios help improve Vestor! 🚀
