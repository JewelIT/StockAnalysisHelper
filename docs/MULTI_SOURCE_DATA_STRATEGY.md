# 🎯 Multi-Source Market Data Strategy

**Problem:** Yahoo Finance (yfinance) showing different data than real-time market indicators
**Solution:** Aggregate data from multiple sources and find consensus

---

## 📊 Available Free/Low-Cost Market Data Sources

### 1. **Alpha Vantage** (FREE - 500 calls/day)
- **API:** https://www.alphavantage.co/
- **Data:** Real-time & historical stock prices, technical indicators, forex, crypto
- **Pros:** Reliable, good documentation, free tier
- **Cons:** Rate limited (5 calls/minute on free tier)
- **Python:** `pip install alpha-vantage`

```python
from alpha_vantage.timeseries import TimeSeries
ts = TimeSeries(key='YOUR_API_KEY', output_format='pandas')
data, meta_data = ts.get_intraday(symbol='SPY', interval='5min')
```

### 2. **Finnhub** (FREE - 60 calls/minute)
- **API:** https://finnhub.io/
- **Data:** Real-time stock prices, market news, sentiment
- **Pros:** Fast, real-time data, good free tier
- **Cons:** Limited historical data on free tier
- **Python:** `pip install finnhub-python`

```python
import finnhub
client = finnhub.Client(api_key="YOUR_API_KEY")
quote = client.quote('SPY')  # Real-time quote
```

### 3. **Twelve Data** (FREE - 800 calls/day)
- **API:** https://twelvedata.com/
- **Data:** Real-time & historical, 4000+ exchanges
- **Pros:** Good free tier, WebSocket support
- **Cons:** Rate limits on free tier
- **Python:** `pip install twelvedata`

```python
from twelvedata import TDClient
td = TDClient(apikey="YOUR_API_KEY")
quote = td.quote(symbol="SPY").as_json()
```

### 4. **Polygon.io** (FREE - 5 calls/minute)
- **API:** https://polygon.io/
- **Data:** Real-time & historical market data
- **Pros:** Professional-grade data, good free tier
- **Cons:** Limited calls on free tier
- **Python:** `pip install polygon-api-client`

```python
from polygon import RESTClient
client = RESTClient("YOUR_API_KEY")
aggs = client.get_aggs("SPY", 1, "minute", "2025-10-14", "2025-10-14")
```

### 5. **Yahoo Finance (yfinance)** - Current
- **Library:** Already using
- **Pros:** Free, unlimited, no API key
- **Cons:** Unreliable, may show stale/wrong data, no official support

### 6. **Fear & Greed Index** (FREE - Scraping)
- **Source:** https://production.dataviz.cnn.io/index/fearandgreed/graphdata
- **Data:** CNN Fear & Greed Index (0-100)
- **Pros:** Authoritative sentiment indicator
- **Cons:** May need scraping or unofficial API

### 7. **Financial Modeling Prep** (FREE - 250 calls/day)
- **API:** https://financialmodelingprep.com/
- **Data:** Real-time quotes, fundamentals, news
- **Pros:** Good free tier, comprehensive data
- **Cons:** Rate limited

```python
import requests
url = f"https://financialmodelingprep.com/api/v3/quote/SPY?apikey=YOUR_KEY"
response = requests.get(url).json()
```

---

## 🎯 RECOMMENDED STRATEGY: Multi-Source Consensus

### Approach:
1. **Fetch from 3-4 sources simultaneously**
2. **Compare values** (price, change %)
3. **Calculate median/average** to filter outliers
4. **Flag discrepancies** when sources disagree significantly
5. **Weight sources** by reliability (premium sources > free sources)

### Implementation Plan:

```python
class MultiSourceMarketData:
    """Aggregate market data from multiple sources for accuracy"""
    
    def __init__(self):
        self.sources = {
            'yfinance': {'weight': 1.0, 'enabled': True},
            'alphavantage': {'weight': 1.5, 'enabled': True, 'key': 'YOUR_KEY'},
            'finnhub': {'weight': 1.5, 'enabled': True, 'key': 'YOUR_KEY'},
            'twelvedata': {'weight': 1.2, 'enabled': True, 'key': 'YOUR_KEY'},
        }
    
    def get_consensus_quote(self, symbol: str) -> dict:
        """Fetch quote from multiple sources and return consensus"""
        results = []
        
        # Fetch from all enabled sources in parallel
        for source, config in self.sources.items():
            if config['enabled']:
                try:
                    data = self._fetch_from_source(source, symbol, config)
                    if data:
                        results.append({
                            'source': source,
                            'price': data['price'],
                            'change_pct': data['change_pct'],
                            'weight': config['weight'],
                            'timestamp': data['timestamp']
                        })
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source}: {e}")
        
        if not results:
            raise Exception("No sources returned data")
        
        # Calculate weighted consensus
        total_weight = sum(r['weight'] for r in results)
        consensus_price = sum(r['price'] * r['weight'] for r in results) / total_weight
        consensus_change = sum(r['change_pct'] * r['weight'] for r in results) / total_weight
        
        # Detect outliers (sources that disagree by >5%)
        outliers = []
        for r in results:
            if abs(r['change_pct'] - consensus_change) > 5:
                outliers.append(r['source'])
        
        return {
            'symbol': symbol,
            'consensus_price': round(consensus_price, 2),
            'consensus_change_pct': round(consensus_change, 2),
            'sources_used': [r['source'] for r in results],
            'outliers': outliers,
            'confidence': 'HIGH' if len(results) >= 3 and not outliers else 'MEDIUM',
            'raw_data': results  # For debugging
        }
    
    def _fetch_from_source(self, source: str, symbol: str, config: dict) -> dict:
        """Fetch data from specific source"""
        if source == 'yfinance':
            return self._fetch_yfinance(symbol)
        elif source == 'alphavantage':
            return self._fetch_alphavantage(symbol, config['key'])
        elif source == 'finnhub':
            return self._fetch_finnhub(symbol, config['key'])
        elif source == 'twelvedata':
            return self._fetch_twelvedata(symbol, config['key'])
        return None
```

---

## 🚀 Quick Win: Start with 2 Sources

**Phase 1 (This Week):**
1. Keep Yahoo Finance as fallback
2. Add **Finnhub** (free, 60 calls/min, real-time)
3. Compare the two, log discrepancies
4. Use Finnhub if available, fallback to Yahoo

**Phase 2 (Next Week):**
5. Add **Alpha Vantage** (500 calls/day)
6. Implement 3-source consensus
7. Weight by reliability

**Phase 3 (Future):**
8. Add **Twelve Data** or **Polygon**
9. Full multi-source aggregation
10. ML model to predict which source is most accurate

---

## 📝 Configuration File

Create `config/data_sources.json`:

```json
{
  "market_data_sources": {
    "yfinance": {
      "enabled": true,
      "weight": 1.0,
      "priority": 3,
      "requires_key": false
    },
    "finnhub": {
      "enabled": true,
      "weight": 1.5,
      "priority": 1,
      "requires_key": true,
      "api_key_env": "FINNHUB_API_KEY",
      "rate_limit": "60/minute"
    },
    "alphavantage": {
      "enabled": true,
      "weight": 1.5,
      "priority": 2,
      "requires_key": true,
      "api_key_env": "ALPHAVANTAGE_API_KEY",
      "rate_limit": "5/minute"
    },
    "twelvedata": {
      "enabled": false,
      "weight": 1.2,
      "priority": 4,
      "requires_key": true,
      "api_key_env": "TWELVEDATA_API_KEY"
    }
  },
  "consensus_strategy": {
    "min_sources": 2,
    "outlier_threshold_pct": 5.0,
    "use_weighted_average": true,
    "fallback_to_single_source": true
  }
}
```

---

## 🔍 Discrepancy Detection & Alerting

```python
def detect_data_discrepancy(results: list) -> dict:
    """Analyze if sources disagree significantly"""
    
    if len(results) < 2:
        return {'has_discrepancy': False, 'severity': 'NONE'}
    
    changes = [r['change_pct'] for r in results]
    max_change = max(changes)
    min_change = min(changes)
    spread = max_change - min_change
    
    # Check for sign disagreement (one says up, another says down)
    has_sign_disagreement = (max_change > 0) and (min_change < 0)
    
    severity = 'NONE'
    if spread > 10 or has_sign_disagreement:
        severity = 'CRITICAL'  # Sources completely disagree
    elif spread > 5:
        severity = 'HIGH'      # Significant disagreement
    elif spread > 2:
        severity = 'MEDIUM'    # Minor disagreement
    
    return {
        'has_discrepancy': spread > 2,
        'severity': severity,
        'spread': spread,
        'sign_disagreement': has_sign_disagreement,
        'message': f"Sources disagree by {spread:.2f}%"
    }
```

---

## 🎯 Action Items

### IMMEDIATE (Today):
1. **Sign up for Finnhub** - Free API key (60 calls/min)
   - https://finnhub.io/register
2. **Install finnhub-python**: `pip install finnhub-python`
3. **Create simple 2-source comparison** (Yahoo vs Finnhub)
4. **Log discrepancies** when they disagree by >2%

### THIS WEEK:
5. **Sign up for Alpha Vantage** - Free API key (500 calls/day)
6. **Implement 3-source consensus** (Yahoo, Finnhub, Alpha Vantage)
7. **Add discrepancy alerts** to logs
8. **Use consensus in sentiment calculation**

### NEXT SPRINT:
9. **Add Fear & Greed Index** scraping
10. **Add pre-market futures** data
11. **Implement caching per source** (not global)
12. **Add data quality metrics** dashboard

---

## 📊 Expected Outcome

**Before (Single Source):**
```
Yahoo Finance: SPY +0.37%
System: BULLISH ✅
Reality: Markets down -2.7% ❌
```

**After (Multi-Source Consensus):**
```
Yahoo Finance: SPY +0.37%
Finnhub: SPY -2.6%
Alpha Vantage: SPY -2.8%

⚠️ DISCREPANCY DETECTED: Yahoo disagrees by 3%
Consensus: SPY -2.4% (weighted average)
System: BEARISH ✅
Reality: Markets down -2.7% ✅
```

---

## 💰 Cost Analysis

| Source | Free Tier | Cost if Exceeded |
|--------|-----------|------------------|
| Yahoo Finance | Unlimited | Free |
| Finnhub | 60 calls/min | $59/month |
| Alpha Vantage | 500 calls/day | $49/month |
| Twelve Data | 800 calls/day | $29/month |
| Polygon | 5 calls/min | $29/month |

**Recommendation:** Start with free tiers, monitor usage, upgrade if needed.

**Estimated Usage:** 
- 3 indices (SPY, DIA, QQQ) × 4 sources = 12 calls per refresh
- Refresh every 15 min during market hours (6.5 hours) = 26 refreshes
- Total: ~312 calls/day (WELL within free tiers)

---

## ⚠️ Critical Consideration

**Yahoo Finance may be showing DELAYED data:**
- Free data often 15-20 minutes delayed
- Intraday bars may not be real-time
- Some symbols may have wrong/stale data

**Premium sources (Finnhub, Alpha Vantage):**
- Real-time or near real-time (few seconds delay)
- More reliable and accurate
- Better for volatility detection

---

## 🎯 DECISION: Let's implement Finnhub + Alpha Vantage TODAY

This will give us:
- ✅ 2-3 source consensus
- ✅ Real-time data (not delayed 15-20 min)
- ✅ Discrepancy detection
- ✅ Higher confidence in sentiment
- ✅ All within FREE tiers
