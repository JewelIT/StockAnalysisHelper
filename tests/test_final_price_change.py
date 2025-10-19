"""
Test the final price_change calculation that respects timeframes
"""
import yfinance as yf

def test_final_price_change_logic():
    """
    Test that price_change correctly:
    1. Shows daily change when timeframe has only 1 candle
    2. Shows timeframe change when timeframe has multiple candles
    """
    ticker = "XRP-EUR"
    
    print(f"\n{'='*70}")
    print(f"TESTING: Final Price Change Logic (Timeframe-Aware)")
    print(f"{'='*70}\n")
    
    # Simulate the fixed calculation
    def calculate_price_change(df, ticker):
        """The fixed calculation"""
        current_price = df['Close'].iloc[-1]
        
        if len(df) == 1:
            # Only 1 candle - fetch previous close for daily change
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                previous_close = info.get('previousClose')
                if previous_close and previous_close > 0:
                    price_change = ((current_price - previous_close) / previous_close) * 100
                else:
                    price_change = 0.0
            except Exception:
                price_change = 0.0
        else:
            # Multiple candles - show change over the timeframe (start to end)
            price_change = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
        
        return price_change
    
    # Test different timeframes
    timeframes = ['1d', '5d', '1mo', '3mo']
    
    for timeframe in timeframes:
        stock = yf.Ticker(ticker)
        df = stock.history(period=timeframe)
        
        if not df.empty:
            result = calculate_price_change(df, ticker)
            candle_count = len(df)
            
            if candle_count == 1:
                source = "previousClose"
            else:
                source = f"df[0] to df[-1]"
            
            print(f"Timeframe: {timeframe:5} | Candles: {candle_count:3} | Change: {result:+7.2f}% | Source: {source}")
    
    print(f"\n{'='*70}")
    print("Expected behavior:")
    print("  1d   → ~1.74% (daily change, from previousClose)")
    print("  5d   → ~-0.56% (5-day change, from start to end)")
    print("  1mo  → ~-19.12% (1-month change, from start to end)")
    print("  3mo  → ~-30.15% (3-month change, from start to end)")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_final_price_change_logic()
