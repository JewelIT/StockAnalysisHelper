"""
Test to verify currency handling is correct
This will expose where currency conversion is wrong
"""
import yfinance as yf

def test_currency_handling():
    """
    Test that prices are correctly handled in their native currency
    and conversion rates are applied properly
    """
    print(f"\n{'='*70}")
    print(f"TESTING: Currency Handling & Exchange Rates")
    print(f"{'='*70}\n")
    
    # Example 1: XRP-EUR (native currency is EUR)
    print("📌 SCENARIO 1: XRP-EUR (Cryptocurrency pair, native currency = EUR)")
    print("-" * 70)
    
    ticker_eur = "XRP-EUR"
    stock_eur = yf.Ticker(ticker_eur)
    info_eur = stock_eur.info
    hist_eur = stock_eur.history(period='1d')
    
    price_eur = hist_eur['Close'].iloc[-1] if not hist_eur.empty else None
    currency_eur = info_eur.get('currency')
    
    print(f"Ticker: {ticker_eur}")
    print(f"  yfinance returns currency: {currency_eur}")
    print(f"  yfinance returns price: €{price_eur:.4f}")
    print()
    
    # What happens if we want to display this in USD?
    print("  If user wants to see in USD:")
    eur_to_usd_rate = 1.0 / 0.92  # 1 EUR = 1.09 USD (approximate)
    price_in_usd = price_eur * eur_to_usd_rate
    print(f"    Exchange rate (EUR→USD): 1 EUR = {eur_to_usd_rate:.4f} USD")
    print(f"    Price in USD: ${price_in_usd:.4f}")
    print()
    
    # Example 2: BTC-USD (native currency is USD)
    print("📌 SCENARIO 2: BTC-USD (Cryptocurrency pair, native currency = USD)")
    print("-" * 70)
    
    ticker_usd = "BTC-USD"
    stock_usd = yf.Ticker(ticker_usd)
    info_usd = stock_usd.info
    hist_usd = stock_usd.history(period='1d')
    
    price_usd = hist_usd['Close'].iloc[-1] if not hist_usd.empty else None
    currency_usd = info_usd.get('currency')
    
    print(f"Ticker: {ticker_usd}")
    print(f"  yfinance returns currency: {currency_usd}")
    print(f"  yfinance returns price: ${price_usd:.2f}")
    print()
    
    # What happens if we want to display this in EUR?
    print("  If user wants to see in EUR:")
    usd_to_eur_rate = 0.92  # 1 USD = 0.92 EUR (approximate)
    price_in_eur = price_usd * usd_to_eur_rate
    print(f"    Exchange rate (USD→EUR): 1 USD = {usd_to_eur_rate:.4f} EUR")
    print(f"    Price in EUR: €{price_in_eur:.2f}")
    print()
    
    # Example 3: AAPL (US stock, native currency is USD)
    print("📌 SCENARIO 3: AAPL (US stock, native currency = USD)")
    print("-" * 70)
    
    ticker_stock = "AAPL"
    stock_stock = yf.Ticker(ticker_stock)
    info_stock = stock_stock.info
    hist_stock = stock_stock.history(period='1d')
    
    price_stock = hist_stock['Close'].iloc[-1] if not hist_stock.empty else None
    currency_stock = info_stock.get('currency')
    
    print(f"Ticker: {ticker_stock}")
    print(f"  yfinance returns currency: {currency_stock}")
    print(f"  yfinance returns price: ${price_stock:.2f}")
    print()
    
    # ================================================================
    print(f"\n{'='*70}")
    print("🔍 CRITICAL INSIGHT:")
    print("="*70)
    print()
    print("1. yfinance ALREADY returns prices in the CORRECT native currency")
    print("   - XRP-EUR: Returns price in EUR")
    print("   - BTC-USD: Returns price in USD")
    print("   - AAPL: Returns price in USD")
    print()
    print("2. The 'current_price' from backend is ALREADY in native currency")
    print()
    print("3. App config has: appConfig.currency = 'native' or 'USD' or 'EUR'")
    print()
    print("4. CONVERSION LOGIC SHOULD BE:")
    print("   ┌─────────────────────────────────────────────────────┐")
    print("   │ IF appConfig.currency == 'native':                  │")
    print("   │   - Display price as-is (it's already native)       │")
    print("   │   - Show correct symbol (€ for EUR, $ for USD, etc) │")
    print("   │                                                       │")
    print("   │ ELSE IF appConfig.currency != native_currency:      │")
    print("   │   - Convert: price_converted = price × rate          │")
    print("   │   - Show converted symbol                            │")
    print("   └─────────────────────────────────────────────────────┘")
    print()
    print("5. CURRENT BUG IN formatPrice():")
    print("   When currency='native', the function:")
    print("   - Extracts currency from ticker ✓")
    print("   - Shows correct symbol ✓")
    print("   - BUT: Does NOT know what currency price is in!")
    print("   - If backend sends EUR price but frontend thinks it's USD")
    print("     → Price will be WRONG by ~9x!")
    print()
    print("6. FIX NEEDED:")
    print("   - Backend must send currency code along with price")
    print("   - Frontend must convert IF user currency ≠ price currency")
    print()
    
    print(f"{'='*70}\n")

if __name__ == "__main__":
    test_currency_handling()
