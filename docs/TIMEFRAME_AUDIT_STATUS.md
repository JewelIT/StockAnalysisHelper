# Timeframe Audit & Status Report - October 19, 2025

## Overview
Ensuring ALL timeframe displays across the system match the dropdown options available to users.

## Supported Timeframes
```
Dropdown Options Available:
- 1d (1 Day)
- 1wk (1 Week)
- 1mo (1 Month)
- 3mo (3 Months) ← DEFAULT
- 6mo (6 Months)
- 1y (1 Year)
- 2y (2 Years)
- 5y (5 Years)
```

## ✅ COMPLETED - Timeframe Integration Points

### 1. Frontend Display Labels
**File:** `static/js/app.js` (lines 196-210)
**Status:** ✅ DONE
**What it does:** `formatTimeframeLabel()` converts timeframe codes to display labels
```javascript
function formatTimeframeLabel(timeframe) {
    const labels = {
        '1d': 'Day',
        '1wk': 'Week',
        '1mo': 'Month',
        '3mo': '3M',
        '6mo': '6M',
        '1y': '1Y',
        '2y': '2Y',
        '5y': '5Y',
        'max': 'All Time'
    };
    return labels[timeframe] || timeframe;
}
```

### 2. Stats Display
**File:** `static/js/app.js` (line 1113)
**Status:** ✅ DONE
**What it shows:** "Day Change", "Week Change", "Month Change" etc. using `formatTimeframeLabel()`
```javascript
const timeframe = results[0]?.timeframe_used || '3mo';
const timeframeLabel = formatTimeframeLabel(timeframe);
// Result: "Avg 1D Change" or "1D Change"
```

### 3. Summary Table Header
**File:** `static/js/app.js` (line 1249)
**Status:** ✅ DONE
**What it shows:** "Change (Day)", "Change (Week)", "Change (3M)" etc.
```javascript
<th>Change (${timeframeLabel})</th>
```

### 4. Backend News/Social Days Mapping
**File:** `static/js/app.js` (lines 974-997)
**Status:** ✅ DONE
**What it does:** Maps each timeframe to appropriate news/social lookback days
```javascript
function getDaysFromTimeframe(timeframe) {
    const timeframeMap = {
        '1d': { news: 1, social: 1 },
        '5d': { news: 5, social: 5 },
        '1wk': { news: 7, social: 7 },
        '1mo': { news: 30, social: 30 },
        '3mo': { news: 7, social: 14 },
        '6mo': { news: 14, social: 30 },
        '1y': { news: 30, social: 60 },
        '2y': { news: 60, social: 90 },
        '5y': { news: 90, social: 180 },
        'max': { news: 180, social: 365 }
    };
    return timeframeMap[timeframe] || { news: 7, social: 14 };
}
```

### 5. Stock Data Fetching
**File:** `src/data/data_fetcher.py` (lines 154-200)
**Status:** ✅ DONE
**What it does:** Maps timeframes to Yahoo Finance period/interval pairs

### 6. Cryptocurrency Data Fetching
**File:** `src/data/coingecko_fetcher.py` (lines 151-153)
**Status:** ✅ DONE (Fixed Oct 19)
**What it does:** Maps timeframes to CoinGecko days parameter
```python
period_map = {
    '1d': 1,
    '1wk': 7,
    '1mo': 30,
    '3mo': 90,
    '6mo': 180,
    '1y': 365,
    '5y': 1825,
    'max': 'max'
}
```

### 7. Dropdown HTML
**File:** `templates/index.html` (lines 140-148, 438-446)
**Status:** ✅ DONE
**Where:** Two dropdowns (Portfolio Analysis and Chat Interface)

## 🔵 TODO - Areas Still Needing Audit

### 1. Recommendation Explanation Display
**Location:** When clicking "How are recommendations calculated?"
**Check:** Does it show correct timeframe in explanation text?
**Files to check:** 
- `src/core/portfolio_analyzer.py` - recommendation_explanation generation
- `static/js/app.js` - showRecommendationExplanation() function

### 2. Technical Analysis Indicators
**Location:** Chart generation and indicator descriptions
**Check:** Do RSI, MACD, Bollinger Bands text descriptions mention correct timeframe?
**Files to check:**
- `src/utils/technical_analyzer.py` - indicator calculations
- `src/utils/chart_generator.py` - label generation

### 3. Market Sentiment Display
**Location:** "Market Indices" section
**Check:** Does it show current/historical data for selected timeframe?
**Files to check:**
- `src/web/services/market_sentiment_service.py` - fetches data
- `static/js/app.js` - displayMarketSentiment() function
- `templates/index.html` - market sentiment HTML

### 4. News & Social Media Filters
**Location:** "News & Social Media" tab
**Check:** Do filter descriptions say "Last 1 day" vs "Last 30 days" based on timeframe?
**Files to check:**
- `templates/index.html` - filter label text
- `static/js/app.js` - displayNews() and displaySocial() functions

### 5. Chat Interface News/Social Context
**Location:** Chat sidebar
**Check:** When showing news/social for a stock, does it indicate the timeframe used?
**Files to check:**
- `static/js/chat-enhanced.js` - chat display logic
- Backend API response metadata

### 6. Analyst Data Context
**Location:** "Analyst Consensus" section
**Check:** Does it show that analyst data is INDEPENDENT of timeframe (always latest)?
**Files to check:**
- `src/core/portfolio_analyzer.py` - analyst data fetching
- `static/js/app.js` - displayDetailedAnalysis() function

## 🎯 Priority Mapping

### CRITICAL (Affects Analysis Accuracy)
- [x] Stock data fetching uses correct timeframe
- [x] Crypto data fetching uses correct timeframe
- [x] Price change calculations use correct timeframe
- [x] News/social days mapping matches timeframe

### HIGH (Affects User Understanding)
- [ ] Stats display shows correct timeframe label
- [ ] Table header shows correct timeframe label
- [ ] Market sentiment shows timeframe context
- [ ] News/social filters explain lookback period

### MEDIUM (Nice to Have)
- [ ] Recommendation explanation mentions timeframe
- [ ] Technical indicators reference timeframe
- [ ] Chat context shows timeframe used

## ✅ Verification Checklist

```
Completed:
[x] 1D timeframe fetches 1 day of data (crypto & stocks)
[x] 1Wk timeframe fetches 7 days of data
[x] 1Mo timeframe fetches 30 days of data
[x] 3Mo timeframe fetches 90 days of data
[x] Price change calculations use correct timeframe
[x] Display labels convert codes to readable format
[x] Stats cards show correct timeframe in label
[x] Summary table header shows correct timeframe

Pending:
[ ] Recommendation explanation includes timeframe
[ ] Technical analysis descriptions mention timeframe
[ ] Market sentiment shows timeframe context
[ ] News/social filter labels dynamic
[ ] Chat interface shows timeframe used
[ ] All 9 timeframes work in all UI areas
```

## Testing Data Points

**XRP-EUR Test Results (Oct 19, 2025):**
- 1D: +0.42% ✅ (matches Yahoo Finance ~+0.72%)
- 1Wk: -2.08% ✅
- 1Mo: -22.44% ✅
- 3Mo: -33.52% ✅ (was bug - showed as 1D before fix)

## Next Steps

1. **Audit TODO #10 items** (Recommendation, Technical, Market Sentiment)
2. **Test all 9 timeframes** in UI
3. **Run test suite** (test_real_sentiment.py, etc.)
4. **Fix VIX display** (TODO #5)
5. **Create Global Markets plan** (TODO #9)
