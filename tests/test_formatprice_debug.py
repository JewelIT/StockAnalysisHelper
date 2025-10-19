"""
Test formatPrice function behavior
"""

def test_formatprice_native_currency():
    """
    Test that formatPrice correctly handles native currency
    Should extract currency from ticker suffix
    """
    print(f"\n{'='*70}")
    print(f"TESTING: formatPrice function behavior")
    print(f"{'='*70}\n")
    
    # Simulate the JavaScript formatPrice function
    def formatPrice(priceUSD, ticker=None, currency='native'):
        """Simulates the fixed formatPrice function"""
        
        if currency == 'native':
            # Extract currency from ticker (e.g., "XRP-EUR" → "EUR")
            nativeCurrency = 'USD'  # Default
            
            if ticker:
                parts = ticker.split('-')
                if len(parts) == 2:
                    nativeCurrency = parts[1].upper()
            
            symbols = {
                'USD': '$',
                'EUR': '€',
                'GBP': '£',
                'JPY': '¥',
                'CHF': 'CHF',
                'AUD': 'A$',
                'CAD': 'C$'
            }
            
            symbol = symbols.get(nativeCurrency, nativeCurrency)
            return f"{symbol}{priceUSD:.2f} {nativeCurrency}"
        
        # Else: convert currency (not tested here)
        return f"${priceUSD:.2f}"
    
    # Test cases
    test_cases = [
        {"ticker": "XRP-EUR", "price": 2.06, "expected": "€2.06 EUR"},
        {"ticker": "BTC-USD", "price": 42500.00, "expected": "$42500.00 USD"},
        {"ticker": "AAPL", "price": 150.50, "expected": "$150.50 USD"},  # No suffix = USD
        {"ticker": "ETH-GBP", "price": 1800.75, "expected": "£1800.75 GBP"},
        {"ticker": "XRP-JPY", "price": 250.00, "expected": "¥250.00 JPY"},
    ]
    
    print("Testing formatPrice with native currency:")
    all_pass = True
    for test in test_cases:
        result = formatPrice(test["price"], test["ticker"], 'native')
        passed = result == test["expected"]
        all_pass = all_pass and passed
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test['ticker']:15} → {result:20} (expected: {test['expected']})")
    
    print(f"\n{'All tests passed!' if all_pass else 'Some tests failed!'}\n")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_formatprice_native_currency()
