#!/usr/bin/env python3
"""
Test market sentiment with today's real Fear & Greed Index = 29 (FEAR)
This should show BEARISH sentiment, NOT BULLISH
"""

import sys
sys.path.insert(0, '/home/rmjoia/projects/FinBertTest')

from src.web.services.market_sentiment_service import MarketSentimentService

def test_real_world_scenario():
    """Test with current market conditions (Fear & Greed = 29)"""
    
    print("=" * 80)
    print("TESTING MARKET SENTIMENT WITH REAL FEAR & GREED = 29 (FEAR)")
    print("=" * 80)
    
    service = MarketSentimentService()
    
    # Clear cache to force fresh fetch
    import os
    cache_file = 'cache/market_sentiment_cache.json'
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print("✓ Cache cleared - will fetch live data\n")
    
    # Get live sentiment
    print("Fetching live market data...\n")
    sentiment_data = service.get_daily_sentiment(force_refresh=True)
    
    # Display results
    print("RESULTS:")
    print("-" * 80)
    print(f"Sentiment: {sentiment_data['sentiment']}")
    print(f"Confidence: {sentiment_data['confidence']}%")
    print(f"\nSummary:")
    print(f"  {sentiment_data['summary']}")
    print(f"\nReasoning:")
    print(f"  {sentiment_data['reasoning']}")
    
    print(f"\nKey Factors:")
    for i, factor in enumerate(sentiment_data.get('key_factors', []), 1):
        print(f"  {i}. {factor}")
    
    # Check market indices
    print(f"\nMarket Indices:")
    for name, data in sentiment_data.get('market_indices', {}).items():
        change = data.get('change_pct', 0)
        symbol = "📈" if change > 0 else "📉"
        print(f"  {symbol} {name}: {change:+.2f}%")
    
    # Validate expectations
    print("\n" + "=" * 80)
    print("VALIDATION:")
    print("=" * 80)
    
    sentiment = sentiment_data['sentiment']
    key_factors = sentiment_data.get('key_factors', [])
    
    # Check 1: Sentiment should NOT be BULLISH with Fear & Greed = 29
    if sentiment == "BULLISH":
        print("❌ FAIL: Sentiment is BULLISH but Fear & Greed Index shows FEAR (29)")
        print("   This is WRONG - we cannot be bullish when market fear is high!")
    elif sentiment == "BEARISH":
        print("✅ PASS: Sentiment correctly shows BEARISH (Fear & Greed = 29)")
    elif sentiment == "NEUTRAL":
        print("⚠️  ACCEPTABLE: Sentiment shows NEUTRAL (should ideally be BEARISH with Fear=29)")
    
    # Check 2: Fear & Greed should be mentioned in key factors
    fear_greed_mentioned = any('Fear' in factor or 'Greed' in factor for factor in key_factors)
    if fear_greed_mentioned:
        print("✅ PASS: Fear & Greed Index mentioned in key factors")
    else:
        print("❌ FAIL: Fear & Greed Index NOT mentioned in key factors")
    
    # Check 3: Risk warnings should be present when Fear & Greed = 29
    risk_mentioned = any(
        'risk' in factor.lower() or 
        'fear' in factor.lower() or 
        'caution' in factor.lower() or
        'defensive' in factor.lower() or
        'volatility' in factor.lower()
        for factor in key_factors
    )
    if risk_mentioned:
        print("✅ PASS: Risk warnings present in key factors")
    else:
        print("❌ FAIL: No risk warnings despite Fear & Greed showing FEAR")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if sentiment in ["BEARISH", "NEUTRAL"] and fear_greed_mentioned and risk_mentioned:
        print("✅ SYSTEM WORKING CORRECTLY")
        print("   - Sentiment is appropriate for Fear & Greed = 29")
        print("   - Risk warnings are present")
        print("   - Being pragmatic, not overly optimistic")
    else:
        print("❌ SYSTEM NEEDS FIXES")
        print("   - Review sentiment calculation logic")
        print("   - Ensure Fear & Greed Index has highest priority")
        print("   - Add explicit risk warnings")
    
    print("=" * 80)

if __name__ == "__main__":
    test_real_world_scenario()
