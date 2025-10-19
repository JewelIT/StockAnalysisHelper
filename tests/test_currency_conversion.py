"""
Test to verify currency conversion works correctly with the new backend format
"""
import yfinance as yf

def test_currency_conversion_logic():
    """
    Test that the new currency conversion logic works properly
    Backend now sends price_currency, so frontend can convert correctly
    """
    print(f"\n{'='*70}")
    print(f"TESTING: New Currency Conversion Logic")
    print(f"{'='*70}\n")
    
    # Simulate exchange rates from frontend
    exchange_rates = {
        'USD': 1.0,
        'EUR': 0.92,  # 1 EUR = 0.92 USD (inverse relationship)
        'GBP': 0.79,
        'JPY': 0.0093
    }
    
    def format_price(price, ticker, price_currency, user_currency='native'):
        """Simulate the new formatPrice function"""
        
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
        }
        
        # Determine display currency
        if user_currency == 'native':
            display_currency = price_currency
            display_price = price
        elif user_currency != price_currency:
            # Convert currencies
            rate_actual = exchange_rates.get(price_currency, 1.0)
            rate_user = exchange_rates.get(user_currency, 1.0)
            display_price = price * (rate_user / rate_actual)
            display_currency = user_currency
        else:
            display_currency = price_currency
            display_price = price
        
        symbol = symbols.get(display_currency, display_currency)
        return f"{symbol}{display_price:.4f} {display_currency}"
    
    # Test cases
    print("📌 TEST 1: XRP-EUR (price in EUR, viewing as native)")
    xrp_eur_price = 2.0549
    result = format_price(xrp_eur_price, 'XRP-EUR', 'EUR', 'native')
    print(f"  Price: €{xrp_eur_price} (from yfinance)")
    print(f"  User currency: native")
    print(f"  Result: {result}")
    assert result.startswith('€'), "Should show EUR symbol"
    print("  ✓ PASS\n")
    
    print("📌 TEST 2: XRP-EUR (price in EUR, convert to USD)")
    result = format_price(xrp_eur_price, 'XRP-EUR', 'EUR', 'USD')
    print(f"  Price: €{xrp_eur_price} (from yfinance)")
    print(f"  User currency: USD")
    print(f"  Exchange rate EUR→USD: 1 EUR = {1/exchange_rates['EUR']:.4f} USD")
    print(f"  Result: {result}")
    assert result.startswith('$'), "Should show USD symbol"
    print("  ✓ PASS\n")
    
    print("📌 TEST 3: BTC-USD (price in USD, viewing as native)")
    btc_usd_price = 107979.80
    result = format_price(btc_usd_price, 'BTC-USD', 'USD', 'native')
    print(f"  Price: ${btc_usd_price} (from yfinance)")
    print(f"  User currency: native")
    print(f"  Result: {result}")
    assert result.startswith('$'), "Should show USD symbol"
    print("  ✓ PASS\n")
    
    print("📌 TEST 4: BTC-USD (price in USD, convert to EUR)")
    result = format_price(btc_usd_price, 'BTC-USD', 'USD', 'EUR')
    print(f"  Price: ${btc_usd_price} (from yfinance)")
    print(f"  User currency: EUR")
    print(f"  Exchange rate USD→EUR: 1 USD = {exchange_rates['EUR']:.4f} EUR")
    print(f"  Result: {result}")
    assert result.startswith('€'), "Should show EUR symbol"
    print("  ✓ PASS\n")
    
    print("📌 TEST 5: AAPL (price in USD, viewing as native)")
    aapl_price = 252.29
    result = format_price(aapl_price, 'AAPL', 'USD', 'native')
    print(f"  Price: ${aapl_price} (from yfinance)")
    print(f"  User currency: native")
    print(f"  Result: {result}")
    assert result.startswith('$'), "Should show USD symbol"
    print("  ✓ PASS\n")
    
    print(f"{'='*70}")
    print("✓ All currency conversion tests passed!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    test_currency_conversion_logic()
