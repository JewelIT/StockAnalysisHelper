#!/usr/bin/env python3
"""Test multi-source market data integration"""
import sys
import os
sys.path.insert(0, 'src')

# Check environment variables
finnhub_key = os.getenv('FINNHUB_API_KEY')
alpha_key = os.getenv('ALPHAVANTAGE_API_KEY')

print('=== ENVIRONMENT CHECK ===')
print(f'FINNHUB_API_KEY: {"✓ Set" if finnhub_key else "✗ Not set"} ({finnhub_key[:10] if finnhub_key else "N/A"}...)')
print(f'ALPHAVANTAGE_API_KEY: {"✓ Set" if alpha_key else "✗ Not set"} ({alpha_key[:10] if alpha_key else "N/A"}...)')

print('\n=== TESTING MULTI-SOURCE SERVICE ===')
try:
    from web.services.multi_source_market_data import get_multi_source_service
    
    service = get_multi_source_service()
    print('✓ Multi-source service initialized')
    
    # Check enabled sources
    sources = service.get_enabled_sources()
    print(f'Enabled sources ({len(sources)}): {sources}')
    
    # Try to fetch consensus data
    print('\nFetching consensus market data...')
    data = service.get_consensus_market_data()
    
    for index_name, consensus in data.items():
        sources_used = consensus.get('sources_used', [])
        price = consensus.get('consensus_price', 0)
        change = consensus.get('consensus_change_pct', 0)
        confidence = consensus.get('confidence', 'UNKNOWN')
        has_disc = consensus.get('has_discrepancy', False)
        
        print(f'\n{index_name}:')
        print(f'  Price: {price:.2f}')
        print(f'  Change: {change:+.2f}%')
        print(f'  Sources: {len(sources_used)} ({", ".join(sources_used)})')
        print(f'  Confidence: {confidence}')
        if has_disc:
            print(f'  ⚠️ DISCREPANCY: {consensus.get("severity", "UNKNOWN")}')
            
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()

print('\n=== TESTING MARKET SENTIMENT SERVICE ===')
try:
    from web.services.market_sentiment_service import get_market_sentiment_service
    
    service = get_market_sentiment_service()
    print('✓ Market sentiment service initialized')
    
    # Force refresh to get fresh data
    print('\nFetching fresh market sentiment (force_refresh=True)...')
    sentiment = service.get_daily_sentiment(force_refresh=True)
    
    print(f'\nSentiment: {sentiment.get("sentiment", "N/A")} (Confidence: {sentiment.get("confidence", 0)}%)')
    print(f'Summary: {sentiment.get("summary", "N/A")}')
    
    # Check market indices
    indices = sentiment.get('market_indices', {})
    print(f'\nMarket Indices ({len(indices)}):')
    for name, data in indices.items():
        multi = data.get('multi_source', False)
        source_label = 'MULTI-SOURCE' if multi else 'Yahoo only'
        print(f'  {name:20s} {data.get("current", 0):>10.2f}  {data.get("change_pct", 0):>+7.2f}%  [{source_label}]')
    
    # Check recommendations
    buy_recs = sentiment.get('buy_recommendations', [])
    sell_recs = sentiment.get('sell_recommendations', [])
    
    print(f'\nRecommendations:')
    print(f'  Buy: {len(buy_recs)} stocks')
    print(f'  Sell: {len(sell_recs)} stocks')
    
    if sell_recs:
        print(f'\nSell recommendations:')
        for i, rec in enumerate(sell_recs[:3], 1):
            print(f'  {i}. {rec.get("ticker", "N/A")} ({rec.get("sector", "N/A")}) - ${rec.get("price", 0):.2f}')
    else:
        print('\n⚠️ NO SELL RECOMMENDATIONS GENERATED!')
    
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
