"""
Debug: Verify that timeframe data is being fetched correctly
"""
import yfinance as yf

def test_timeframe_data():
    """
    Test that different timeframes return appropriate data
    """
    ticker = "XRP-EUR"
    timeframes = ['1d', '5d', '1mo', '3mo']
    
    print(f"\n{'='*70}")
    print(f"TESTING: Timeframe Data Fetching for {ticker}")
    print(f"{'='*70}\n")
    
    for timeframe in timeframes:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=timeframe)
        
        if not hist.empty:
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            change = ((end_price - start_price) / start_price) * 100
            
            print(f"Timeframe: {timeframe:5} | Candles: {len(hist):3} | Change: {change:+7.2f}%")
            print(f"  Start: €{start_price:.4f} | End: €{end_price:.4f}")
        else:
            print(f"Timeframe: {timeframe:5} | NO DATA")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    test_timeframe_data()
