# Analyst Consensus Integration

## Overview
Enhanced the recommendation engine to incorporate professional analyst ratings and price targets from Yahoo Finance, providing more balanced and accurate stock recommendations.

## Problem Statement
The application was showing contradictory recommendations compared to professional analysts. For example:
- **COUR**: App recommended SELL, but 13 analysts recommended BUY with 19.6% upside potential
- Root cause: Recommendation algorithm only used sentiment analysis + technical indicators, ignoring professional analyst consensus

## Solution Implemented

### 1. New Module: `src/analyst_consensus.py`
Created a comprehensive analyst consensus fetcher with the following features:

**Key Methods:**
- `fetch_analyst_data(ticker)` - Retrieves analyst recommendations and price targets from Yahoo Finance
- `calculate_analyst_score(analyst_data)` - Converts Yahoo's 1-5 recommendation scale to 0-1 score
- `calculate_price_target_score(analyst_data)` - Scores based on upside/downside potential
- `get_analyst_consensus_signal(analyst_data)` - Human-readable consensus (STRONG BUY, BUY, HOLD, SELL, STRONG SELL)
- `format_analyst_summary(analyst_data)` - Formats data for UI display

**Scoring Logic:**
```python
# Yahoo Finance Scale: 1=Strong Buy, 2=Buy, 3=Hold, 4=Sell, 5=Strong Sell
analyst_score = (5.0 - recommendation_mean) / 4.0  # Convert to 0-1 (higher is better)

# Price Target Scoring
upside_pct = ((target - current) / current) * 100
# -20% or worse → 0.0, 0% → 0.5, +20% or better → 1.0

# Combined Score (weighted)
final_score = recommendation_score * 0.7 + price_target_score * 0.3
```

### 2. Enhanced Recommendation Algorithm

**Previous Formula:**
```
Combined Score = (Sentiment × 40%) + (Technical × 60%)
```

**New Formula (with analyst data available):**
```
Combined Score = (Sentiment × 25%) + (Technical × 45%) + (Analyst Consensus × 30%)
```

**Fallback (insufficient analyst coverage):**
```
Combined Score = (Sentiment × 40%) + (Technical × 60%)  # Original formula
```

**Requirements for Analyst Integration:**
- Minimum 3 analyst opinions
- Valid recommendation mean (1-5 scale)
- Either recommendation data or price target available

### 3. UI Enhancements

**Recommendation Explanation Modal:**
- Added "Analyst Consensus" section showing:
  - Consensus signal (STRONG BUY / BUY / HOLD / SELL / STRONG SELL)
  - Number of analysts providing coverage
  - Recommendation mean (1-5 scale)
  - Price target and upside potential
  - Analyst score contribution

**Stock Detail Cards:**
- Added "Analyst Score" metric box
- New "Analyst Consensus" section displaying:
  - Consensus signal with analyst count
  - Price targets (mean, high, low)
  - Upside potential percentage with color coding
  - Recommendation mean with scale explanation

**No Coverage Handling:**
- Shows warning when analyst coverage unavailable
- Explains fallback to sentiment + technical only
- Maintains consistent user experience

### 4. Data Sources

**Yahoo Finance API (via yfinance):**
- `info.recommendationKey` - Consensus key (buy, hold, sell)
- `info.recommendationMean` - Numerical mean (1-5 scale)
- `info.numberOfAnalystOpinions` - Coverage count
- `info.targetMeanPrice` - Average price target
- `info.targetHighPrice` - Highest price target
- `info.targetLowPrice` - Lowest price target
- `info.currentPrice` - Current market price
- `recommendations` - Historical breakdown (strongBuy, buy, hold, sell, strongSell counts)

## Test Results

### COUR (With Analyst Coverage)
```
Recommendation: HOLD
Combined Score: 0.498

Score Breakdown:
  - Sentiment: 0.506
  - Technical: 0.300
  - Analyst: 0.787

Analyst Consensus:
  - Signal: BUY (13 analysts)
  - Recommendation Mean: 2.20
  - Target Price: $12.31 (Current: $10.29)
  - Upside Potential: +19.6%

Formula: (Sentiment × 25%) + (Technical × 45%) + (Analyst × 30%)
```

**Analysis:** The high analyst score (0.787) reflects the strong BUY consensus with significant upside. The HOLD recommendation balances this against weak technical indicators (0.300), providing a more nuanced view than the previous SELL recommendation.

### GME (Without Analyst Coverage)
```
Recommendation: BUY
Has Analyst Data: False
Fallback: Sentiment + Technical only

Formula: (Sentiment × 40%) + (Technical × 60%)
```

**Analysis:** Graceful fallback when insufficient analyst coverage. No degradation in user experience.

## Benefits

1. **More Accurate Recommendations**: Incorporates professional analyst research
2. **Better Trust**: Aligns with industry consensus when available
3. **Transparency**: Shows analyst data and how it influences recommendations
4. **Flexibility**: Gracefully handles stocks without analyst coverage
5. **Data-Driven**: Uses multiple data points (consensus + price targets)

## Code Changes

**Modified Files:**
- `src/portfolio_analyzer.py` - Integrated analyst consensus into recommendation logic
- `static/js/app.js` - Added analyst data display to UI

**New Files:**
- `src/analyst_consensus.py` - Analyst data fetching and scoring
- `test_analyst_integration.py` - Integration testing

## Future Enhancements

1. **Historical Tracking**: Track analyst recommendation changes over time
2. **Analyst Accuracy**: Weight recommendations by analyst track record
3. **Earnings Integration**: Factor in earnings estimate revisions
4. **Consensus Trends**: Show if consensus is improving or deteriorating
5. **Analyst Details**: Display individual analyst recommendations and firms

## Configuration

**Minimum Analysts Required**: 3 (configurable in `analyst_consensus.py`)
**Weighting**: 30% analyst, 45% technical, 25% sentiment (configurable in `portfolio_analyzer.py`)

## Dependencies

No new dependencies required. Uses existing `yfinance` package for Yahoo Finance API access.

## Testing

All 50 existing tests pass. Integration verified with:
- COUR (with coverage): ✅ Analyst data integrated
- GME (without coverage): ✅ Fallback working
- JavaScript syntax: ✅ Valid
- UI rendering: ✅ Functional

## Deployment Notes

- No database migrations required
- No API keys or credentials needed
- Yahoo Finance API rate limits apply (same as existing stock data)
- Backwards compatible with existing data
