#!/usr/bin/env python3
"""
Test script to verify Selenium can fetch StockTwits data
"""
from src.data.social_media_fetcher import SocialMediaFetcher

def test_stocktwits_selenium():
    print("=" * 80)
    print("Testing StockTwits fetch with Selenium")
    print("=" * 80)
    
    fetcher = SocialMediaFetcher()
    ticker = "HIVE"
    
    print(f"\n📊 Fetching StockTwits data for {ticker}...")
    messages = fetcher.fetch_stocktwits_messages(ticker, max_messages=5)
    
    print(f"\n✅ Retrieved {len(messages)} messages")
    
    if messages:
        print("\n📝 Sample messages:")
        for i, msg in enumerate(messages[:3], 1):
            print(f"\n{i}. {msg.get('source', 'Unknown')} - {msg.get('user', 'Unknown')}")
            print(f"   {msg.get('text', '')[:150]}...")
            print(f"   Link: {msg.get('link', 'N/A')}")
    else:
        print("\n❌ No messages retrieved")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_stocktwits_selenium()
