# 🚀 Quick Setup: Multi-Source Market Data

## What Changed?

Your system now uses **multiple data sources** instead of just Yahoo Finance to get more accurate, real-time market data. This fixes the issue where Yahoo Finance showed markets up when they were actually down.

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Get FREE API Keys

#### **Finnhub** (Recommended - Real-time data)
1. Go to: https://finnhub.io/register
2. Sign up with email
3. Copy your API key from dashboard
4. **Free tier: 60 calls/minute** (more than enough!)

#### **Alpha Vantage** (Recommended - Reliable data)
1. Go to: https://www.alphavantage.co/support/#api-key
2. Fill out simple form
3. Get instant API key via email
4. **Free tier: 500 calls/day** (plenty!)

### Step 2: Configure Environment

Set your API keys as environment variables in your shell or `.env` file:

```bash
# Option 1: Export directly in shell
export FINNHUB_API_KEY=your_actual_key_here
export ALPHAVANTAGE_API_KEY=your_actual_key_here

# Option 2: Or create .env file in project root
echo "FINNHUB_API_KEY=your_actual_key_here" > .env
echo "ALPHAVANTAGE_API_KEY=your_actual_key_here" >> .env
```

### Step 3: Install New Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `finnhub-python` - Finnhub client
- `alpha-vantage` - Alpha Vantage client
- `twelvedata` - Twelve Data client (optional)

### Step 4: Restart Application

```bash
python src/web/app.py
```

---

## ✅ How It Works Now

### Before (Single Source):
```
┌─────────────────┐
│  Yahoo Finance  │ ← Only source (potentially wrong!)
└────────┬────────┘
         │
         ▼
    Your System
```

**Problem:** If Yahoo Finance has stale/wrong data, your entire system is wrong.

### After (Multi-Source Consensus):
```
┌─────────────────┐
│  Yahoo Finance  │ Weight: 1.0
└────────┬────────┘
         │
┌────────┴────────┐
│    Finnhub      │ Weight: 1.5 (more reliable)
└────────┬────────┘
         │
┌────────┴────────┐
│ Alpha Vantage   │ Weight: 1.5 (more reliable)
└────────┬────────┘
         │
         ▼
    CONSENSUS       ← Weighted average of all sources
         │
         ▼
    Your System    ← More accurate!
```

**Solution:** 
- Fetches from 2-3 sources simultaneously
- Calculates weighted consensus (median/average)
- Detects outliers (sources that disagree)
- Logs warnings when sources disagree by >5%
- Falls back to Yahoo Finance if APIs unavailable

---

## 🎯 Example Output

### Scenario: Markets are actually DOWN

**Without API keys** (Yahoo Finance only):
```
⚠️ Using single source (Yahoo Finance)
S&P 500: +0.37% (UP)   ← WRONG!
Sentiment: BULLISH     ← WRONG!
```

**With API keys** (Multi-source consensus):
```
✓ Using 3 sources
Yahoo Finance: +0.37% (UP)
Finnhub: -2.6% (DOWN)
Alpha Vantage: -2.8% (DOWN)

⚠️ DISCREPANCY DETECTED: Yahoo Finance is an outlier
Consensus: -2.4% (DOWN)  ← CORRECT!
Confidence: HIGH
Sentiment: BEARISH       ← CORRECT!
```

---

## 🔍 Verification

### Check if API keys are loaded:

```bash
# Run test script
python3 -c "
import os
from src.web.services.multi_source_market_data import get_multi_source_service

service = get_multi_source_service()
status = service.get_source_status()

print('=== DATA SOURCE STATUS ===')
for source, info in status.items():
    enabled = '✓' if info['enabled'] else '✗'
    print(f'{enabled} {source:15s} Weight: {info[\"weight\"]:.1f}  Priority: {info[\"priority\"]}')

enabled_sources = service.get_enabled_sources()
print(f'\nTotal enabled sources: {len(enabled_sources)}')
print(f'Sources: {', '.join(enabled_sources)}')

if len(enabled_sources) == 1:
    print('\n⚠️ WARNING: Only 1 source enabled! Add API keys for better accuracy.')
elif len(enabled_sources) >= 2:
    print(f'\n✅ GOOD: {len(enabled_sources)} sources will be used for consensus!')
"
```

Expected output with API keys:
```
=== DATA SOURCE STATUS ===
✓ yfinance       Weight: 1.0  Priority: 3
✓ finnhub        Weight: 1.5  Priority: 1
✓ alphavantage   Weight: 1.5  Priority: 2

Total enabled sources: 3
Sources: yfinance, finnhub, alphavantage

✅ GOOD: 3 sources will be used for consensus!
```

---

## 📊 Monitoring & Debugging

### Check logs for discrepancies:

```bash
tail -f logs/market_sentiment.log | grep "DISCREPANCY"
```

You'll see warnings like:
```
⚠️ S&P 500: Data sources disagree by 3.17% (Severity: MEDIUM)
⚠️ Outlier detected: yfinance deviates by 3.05% from consensus
```

This tells you:
- Which sources disagree
- How much they disagree by
- Which source is the outlier

---

## 🚨 Troubleshooting

### "No data available"
- **Cause:** API keys not set or invalid
- **Solution:** Check `.env` file, verify keys are correct

### "Rate limit exceeded"
- **Cause:** Too many API calls
- **Solution:** 
  - Cache is set to 15 minutes (should be fine)
  - Free tiers allow plenty of calls
  - If still hitting limits, increase cache duration

### "Finnhub/AlphaVantage not available"
- **Cause:** Library not installed or import error
- **Solution:** 
  ```bash
  pip install finnhub-python alpha-vantage
  ```

### System still shows wrong sentiment
- **Check:** Are API keys loaded? Run verification script above
- **Check:** Look at logs for "Using X sources"
- **Check:** If only 1 source, consensus won't work
- **Solution:** Add at least 1 additional API key

---

## 💡 Optional: Add More Sources

### Twelve Data (800 calls/day free)
```bash
# Add to .env
TWELVEDATA_API_KEY=your_key_here
```

### Polygon.io (5 calls/min free)
- More complex setup, professional-grade data
- Good for future upgrade

---

## 🎯 Success Criteria

After setup, you should see:

✅ **At least 2 data sources enabled**  
✅ **Consensus calculations in logs**  
✅ **Discrepancy warnings when sources disagree**  
✅ **Sentiment matches real market conditions**  

If you see these, your multi-source system is working! 🎉

---

## 📝 Next Steps

1. **Get API keys** (5 min) - Finnhub + Alpha Vantage
2. **Configure .env** (1 min) - Add keys
3. **Install deps** (1 min) - `pip install -r requirements.txt`
4. **Test** (2 min) - Run verification script
5. **Monitor** (ongoing) - Check logs for discrepancies

**Total time: ~10 minutes for significantly more accurate data!**
