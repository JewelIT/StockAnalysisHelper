"""
Test to verify price_change calculation works correctly
This test will help debug why price_change shows wrong values
"""
import yfinance as yf

def test_xrp_eur_price_change_calculation():
    """
    Test the price_change calculation for XRP-EUR
    Should show ~1.2% daily change (as of Oct 19, 2025)
    """
    ticker = "XRP-EUR"
    
    print(f"\n{'='*70}")
    print(f"TESTING: {ticker} Price Change Calculation")
    print(f"{'='*70}\n")
    
    # Fetch data like the app does
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period='3mo')
    
    # Current price from last candle
    current_price = hist['Close'].iloc[-1]
    
    # Method 1: Using previousClose from info
    print("📊 METHOD 1: Using yfinance info.previousClose")
    previous_close = info.get('previousClose')
    print(f"  Current Price: €{current_price:.6f}")
    print(f"  Previous Close: €{previous_close:.6f}" if previous_close else "  Previous Close: N/A")
    
    if previous_close and previous_close > 0:
        change_method1 = ((current_price - previous_close) / previous_close) * 100
        print(f"  Daily Change: {change_method1:.2f}% ✓\n")
    else:
        print(f"  Daily Change: N/A (previousClose not available)\n")
    
    # Method 2: Using previous candle from historical data
    print("📊 METHOD 2: Using df['Close'].iloc[-2] (previous candle)")
    if len(hist) >= 2:
        previous_candle = hist['Close'].iloc[-2]
        change_method2 = ((current_price - previous_candle) / previous_candle) * 100
        print(f"  Current Price: €{current_price:.6f}")
        print(f"  Previous Candle: €{previous_candle:.6f}")
        print(f"  Daily Change: {change_method2:.2f}% ✓\n")
    else:
        print(f"  Not enough data\n")
    
    # Method 3: OLD METHOD - Using timeframe start/end (WRONG)
    print("📊 METHOD 3 (OLD/WRONG): Using df['Close'].iloc[0] (timeframe start)")
    timeframe_start = hist['Close'].iloc[0]
    change_method3 = ((current_price - timeframe_start) / timeframe_start) * 100
    print(f"  Current Price: €{current_price:.6f}")
    print(f"  Timeframe Start (3mo ago): €{timeframe_start:.6f}")
    print(f"  Timeframe Change: {change_method3:.2f}% ✗ (THIS IS THE BUG!)\n")
    
    # Comparison
    print("="*70)
    print("SUMMARY:")
    print(f"  Expected (from CoinGecko/Yahoo): ~1.2% (daily)")
    if previous_close:
        print(f"  Method 1 (previousClose): {change_method1:.2f}% - {'✓ CORRECT' if 0.5 < change_method1 < 2.0 else '✗ WRONG'}")
    if len(hist) >= 2:
        print(f"  Method 2 (prev candle):   {change_method2:.2f}% - {'✓ LIKELY CORRECT' if 0.5 < change_method2 < 2.0 else '✗ WRONG'}")
    print(f"  Method 3 (timeframe):     {change_method3:.2f}% - ✗ ALWAYS WRONG (3-month change)")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_xrp_eur_price_change_calculation()
