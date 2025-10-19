# Bug Fix: Crypto Price Change Not Respecting Timeframe - October 19, 2025

## Problem
When analyzing cryptocurrency (like XRP-EUR) with a specific timeframe selected (e.g., "1 Day"), the system was **always showing the 3-month price change (-33%)** instead of the selected timeframe's change.

**Example:**
- User selected: "1 Day" timeframe
- Yahoo Finance shows: +0.72% (1-day change)
- Our system displayed: ▼ -33.52% (3-month change) ❌

This was confusing because the label said "Day Change" but the value was from a 3-month analysis.

## Root Cause
The CoinGecko fetcher's `period_map` dictionary was missing entries for short timeframes (`'1d'` and `'1wk'`). 

When the system couldn't find the timeframe in the map, it defaulted to 90 days (3 months):

```python
# OLD CODE - Missing 1d and 1wk
period_map = {
    '1mo': 30,
    '3mo': 90,      # This was the default!
    '6mo': 180,
    '1y': 365,
    '5y': 1825,
    'max': 'max'
}
days = period_map.get(period, 90)  # ← Defaults to 90 if period not found
```

When `period='1d'` was passed, it wasn't in the map, so it defaulted to 90 days.

## Solution
Added the missing timeframe entries to the `period_map` in `src/data/coingecko_fetcher.py`:

```python
# NEW CODE - Includes all supported timeframes
period_map = {
    '1d': 1,        # ← NEW
    '1wk': 7,       # ← NEW
    '1mo': 30,
    '3mo': 90,
    '6mo': 180,
    '1y': 365,
    '5y': 1825,
    'max': 'max'
}
```

## Verification Results

Testing XRP-EUR with different timeframes:

| Timeframe | Data Points | Date Range | Change |
|-----------|-------------|-----------|--------|
| **1D** | 48 | Oct 18-19 | **+0.42%** ✅ |
| **1Week** | 42 | Oct 12-19 | **-2.08%** ✅ |
| **1Month** | 180 | Sep 19-Oct 19 | **-22.44%** ✅ |
| **3Months** | 23 | Jul 23-Oct 19 | **-33.52%** ✅ |

Now each timeframe correctly calculates the price change for that specific period!

## Files Modified
- `src/data/coingecko_fetcher.py` (line 151-153)
  - Added `'1d': 1` entry
  - Added `'1wk': 7` entry
  - Updated docstring to reflect supported periods

## Impact
✅ **Cryptocurrency Analysis** - Now correctly shows price changes for selected timeframe
✅ **Frontend Labels** - "Day Change", "Week Change", "Month Change" now display accurate values
✅ **Technical Analysis** - Price change calculations use correct timeframe data
✅ **Consistency** - Matches backend timeframe selection with frontend display

## Testing Notes
- Tested with XRP-EUR (cryptocurrency)
- Also works for stocks via Yahoo Finance (data_fetcher.py already had these mappings)
- CoinGecko API supports all timeframes via days parameter
