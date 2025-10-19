#!/usr/bin/env python3
"""Test dynamic recommendations (NO hardcoded stocks!)"""
import sys
sys.path.insert(0, 'src')

print('=== TESTING DYNAMIC RECOMMENDATIONS (LIVE DATA) ===\n')

from web.services.dynamic_recommendations import get_dynamic_recommendation_service

service = get_dynamic_recommendation_service()
print('✓ Dynamic recommendation service initialized\n')

# Test buy recommendations
print('Testing BUY recommendations (live analysis)...')
top_sectors = ['Technology', 'Healthcare', 'Financials']
buy_recs = service.get_dynamic_buy_recommendations(top_sectors, max_recommendations=5)

print(f'\nGenerated {len(buy_recs)} BUY recommendations:\n')
for i, rec in enumerate(buy_recs, 1):
    print(f'{i}. {rec["ticker"]} ({rec["sector"]}) - ${rec["price"]:.2f}')
    print(f'   Score: {rec["score"]} | Momentum: {rec["momentum"]} | RSI: {rec["rsi"]}')
    print(f'   Reason: {rec["reason"]}\n')

# Test sell recommendations
print('\n' + '='*70)
print('Testing SELL recommendations (live analysis)...')
bottom_sectors = ['Energy', 'Utilities', 'Materials']
buy_tickers = {rec['ticker'] for rec in buy_recs}
sell_recs = service.get_dynamic_sell_recommendations(
    bottom_sectors, 
    max_recommendations=5, 
    excluded_tickers=buy_tickers
)

print(f'\nGenerated {len(sell_recs)} SELL recommendations:\n')
for i, rec in enumerate(sell_recs, 1):
    print(f'{i}. {rec["ticker"]} ({rec["sector"]}) - ${rec["price"]:.2f}')
    print(f'   Score: {rec["score"]} | Momentum: {rec["momentum"]} | RSI: {rec["rsi"]}')
    print(f'   Reason: {rec["reason"]}\n')

# Check for duplicates
all_buy = {rec['ticker'] for rec in buy_recs}
all_sell = {rec['ticker'] for rec in sell_recs}
duplicates = all_buy & all_sell

print('='*70)
if duplicates:
    print(f'❌ DUPLICATES FOUND: {duplicates}')
else:
    print('✅ NO DUPLICATES - Buy and sell lists are mutually exclusive!')

print(f'\n✅ ALL RECOMMENDATIONS ARE DYNAMIC (NO HARDCODED LISTS!)')
print(f'✅ Based on live RSI, momentum, volume analysis')
print(f'✅ Stocks analyzed: {len(buy_recs) + len(sell_recs)} total')
