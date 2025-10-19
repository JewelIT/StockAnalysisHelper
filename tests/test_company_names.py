"""
Test to verify company names are fetched correctly in recommendations
"""
import yfinance as yf

def test_company_names_fetching():
    """
    Test that we can fetch company names for tickers
    This will be used to display in recommendations
    """
    print(f"\n{'='*70}")
    print(f"TESTING: Company Name Fetching for Recommendations")
    print(f"{'='*70}\n")
    
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'XRP-EUR', 'BTC-USD', 'TSLA']
    
    for ticker in test_tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            long_name = info.get('longName')
            short_name = info.get('shortName')
            quote_type = info.get('quoteType', 'UNKNOWN')
            
            display_name = long_name or short_name or ticker
            
            print(f"📌 {ticker}")
            print(f"   Long Name: {long_name}")
            print(f"   Short Name: {short_name}")
            print(f"   Quote Type: {quote_type}")
            print(f"   → Display: {display_name}")
            print()
            
        except Exception as e:
            print(f"❌ {ticker}: {e}\n")
    
    print(f"{'='*70}")
    print("✓ Company name fetching test complete")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_company_names_fetching()
