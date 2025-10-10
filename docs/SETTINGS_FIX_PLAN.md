# Settings/LocalStorage Fix Plan

## Issues Identified

1. ❌ **`loadConfigToUI()` not called when modal opens**
   - Function exists but no event listener for modal show
   - Result: Settings modal shows default values, not saved ones

2. ❌ **Currency dropdown defaults to "Native Currency"**  
   - HTML has `native` as first option
   - When modal opens without loading config, shows first option
   
3. ❌ **No currency conversion in Market Sentiment Service**
   - Prices always in USD
   - No conversion to EUR/GBP based on user preference

## Fix Strategy

### Fix 1: Load Config When Modal Opens ✅
Add Bootstrap modal event listener to call `loadConfigToUI()`:

```javascript
// Listen for modal show event
document.getElementById('settingsModal').addEventListener('show.bs.modal', function() {
    loadConfigToUI();  // Reload settings from localStorage when opening
});
```

###  Fix 2: Ensure Config Loads on Page Load ✅
Already exists in `DOMContentLoaded`:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    loadAppConfig();  // ✅ Already loads from localStorage
    // ...
});
```

### Fix 3: Add Currency Conversion Utility 
Create reusable currency converter:

```javascript
// Fetch live exchange rates
async function fetchExchangeRates() {
    try {
        const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
        const data = await response.json();
        exchangeRates = {
            USD: 1.0,
            EUR: data.rates.EUR || 0.92,
            GBP: data.rates.GBP || 0.79
        };
        localStorage.setItem('exchange_rates', JSON.stringify({
            rates: exchangeRates,
            timestamp: Date.now()
        }));
    } catch (error) {
        console.error('Failed to fetch exchange rates:', error);
        // Use cached or fallback values
    }
}

// Convert price to user's preferred currency
function convertPrice(priceUSD, targetCurrency = null) {
    const currency = targetCurrency || appConfig.currency;
    if (currency === 'native' || currency === 'USD') {
        return priceUSD;
    }
    const rate = exchangeRates[currency] || 1.0;
    return priceUSD * rate;
}
```

### Fix 4: Apply Currency in Daily Market Sentiment
Modify backend or frontend to convert recommendation prices:

**Frontend Approach** (simpler):
```javascript
// When rendering daily sentiment
function renderDailySentiment(data) {
    const buyRecs = data.buy_recommendations.map(rec => ({
        ...rec,
        price: convertPrice(rec.price),  // Convert from USD
        currency: appConfig.currency
    }));
    // ... render with converted prices
}
```

**Backend Approach** (proper):
Modify `market_sentiment_service.py` to accept currency parameter and convert prices.

## Testing Checklist

- [ ] Open settings modal → verify USD is selected if saved as USD
- [ ] Change to EUR → save → refresh page → verify EUR persists
- [ ] Change currency → verify all prices update
- [ ] Daily market sentiment → verify prices in correct currency
- [ ] Chat responses about prices → verify currency conversion

## Files to Modify

1. `static/js/app.js` - Add modal listener, improve currency conversion
2. `app/services/market_sentiment_service.py` - Add currency parameter (optional)
3. `templates/index.html` - Maybe update currency dropdown help text

## Implementation Order

1. ✅ Fix settings modal not loading config
2. ✅ Test that settings persist correctly
3. ✅ Add live exchange rate fetching
4. ✅ Apply currency conversion to all price displays
5. ✅ Update daily sentiment to use user currency
6. 🧪 Test complete user flow
7. 💾 Commit: "fix: settings persistence and currency conversion"
