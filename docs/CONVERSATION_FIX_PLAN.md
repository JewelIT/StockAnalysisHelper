# Vestor Conversation Improvements - Implementation Plan

## Current Issues (From User Report)

**User's Test Questions:**
1. "What is investment" → Response unclear
2. "should I buy apple?" → Needs better handling
3. "are people buying apple?" → Follow-up context lost
4. "what's the price of apple stock in euro?" → No currency conversion
5. "What's the ticker for Uniphar PLC" → Generic guidance, not specific answer

## Root Causes

### 1. **No Conversation Memory**
- Bot doesn't remember last analyzed stock
- Follow-up questions don't maintain context
- User has to re-specify ticker every time

### 2. **Missing Currency Conversion**
- Has price data but no EUR/GBP/etc conversion
- Should fetch live exchange rates

### 3. **Ticker Lookup Too Generic**
- Gives "go to Yahoo Finance" instead of actually looking up ticker
- Should attempt API lookup first

### 4. **Pattern Matching Too Rigid**
- "What is investment" might not trigger best response
- Needs more flexible natural language understanding

## Fix Strategy (Incremental with Tests)

### Phase 1: Add Conversation Memory (PRIORITY)
**What:** Remember last ticker and analysis
**Why:** Enables natural follow-ups like "are people buying it?"
**Test:** Ask about AAPL, then ask follow-up without mentioning Apple

```python
class StockChatAssistant:
    def __init__(self):
        self.last_ticker = None
        self.last_analysis_context = None
        self.last_analysis_time = None
```

**Commit:** "feat: add conversation memory for follow-up questions"

### Phase 2: Improve Company Name Detection
**What:** Better extraction of company names → tickers
**Why:** "should I buy apple?" should auto-detect AAPL
**Test:** Various phrasings with company names

```python
def _extract_ticker_from_question(self, question):
    # Map common names to tickers
    # Check if already a ticker (e.g., "AAPL")
    # Return None if no ticker found
```

**Commit:** "feat: auto-detect company names in questions"

### Phase 3: Add Currency Conversion
**What:** Convert USD prices to EUR/GBP/etc
**Why:** International users need local currency
**Test:** Ask for price in euros

```python
def _convert_currency(self, amount_usd, to_currency='EUR'):
    # Use exchangerate-api.com or similar
    # Cache rates for 1 hour
    # Return converted amount
```

**Commit:** "feat: add currency conversion for prices"

### Phase 4: Improve Educational Responses
**What:** Better pattern matching for basic questions
**Why:** "What is investment" should give clear, concise answer
**Test:** Ask basic finance questions

```python
# Add more patterns:
if any(pattern in question_lower for pattern in [
    'what is investment',
    'what are stocks',
    'what is a stock',
    'explain investing'
]):
    return concise_investment_definition()
```

**Commit:** "feat: improve educational response patterns"

### Phase 5: Smart Ticker Lookup
**What:** Try to find ticker via API before giving generic advice
**Why:** Better UX - give answer if possible
**Test:** Ask for tickers of various companies

```python
def _lookup_ticker_online(self, company_name):
    # Try yfinance search
    # Try Yahoo Finance API
    # Fall back to guidance if not found
```

**Commit:** "feat: add online ticker lookup"

## Testing Workflow

For each phase:
1. Write test case
2. Run test (should fail)
3. Implement fix
4. Run test (should pass)
5. Run ALL previous tests (regression check)
6. Commit if all pass

## Implementation Order

1. ✅ **Phase 1** - Conversation memory (biggest impact)
2. ✅ **Phase 2** - Company name detection (related to Phase 1)
3. ✅ **Phase 4** - Educational responses (quick win)
4. ⏳ **Phase 3** - Currency conversion (requires external API)
5. ⏳ **Phase 5** - Ticker lookup (requires external API)

## Success Criteria

After fixes, the test conversation should:
- ✅ "What is investment" → Clear, concise definition
- ✅ "should I buy apple?" → Recognizes AAPL, fetches analysis, provides recommendation
- ✅ "are people buying apple?" → Remembers context, provides sentiment
- ✅ "what's the price in euro?" → Converts USD to EUR
- ✅ "ticker for Uniphar PLC" → Attempts lookup, provides specific answer or helpful guidance

## Files to Modify

- `src/stock_chat.py` - Main chatbot logic
- `tests/test_conversation_flow.py` - Conversation tests
- `src/currency_converter.py` - NEW: Currency conversion utility
- `src/ticker_lookup.py` - NEW: Ticker search utility

## Next Steps

1. Create test file with all 5 questions
2. Run test → see failures
3. Implement Phase 1
4. Run test → see improvements
5. Commit
6. Repeat for other phases
