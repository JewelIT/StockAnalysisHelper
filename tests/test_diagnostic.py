#!/usr/bin/env python3
"""
Quick diagnostic test for dynamic recommendations
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.services.dynamic_recommendations import DynamicRecommendationService

print("=" * 80)
print("DYNAMIC RECOMMENDATIONS DIAGNOSTIC TEST")
print("=" * 80)

service = DynamicRecommendationService()

# Test S&P 500 fetch for a single sector
print("\n1. Testing S&P 500 fetch for Technology sector...")
try:
    tech_stocks = service._get_sp500_stocks_by_sector('Technology')
    print(f"   Result: {len(tech_stocks)} stocks")
    if tech_stocks:
        print(f"   Sample: {tech_stocks[:5]}")
    else:
        print("   ❌ NO STOCKS RETURNED")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test live sector stocks
print("\n2. Testing _get_live_sector_stocks for Healthcare...")
try:
    healthcare_stocks = service._get_live_sector_stocks('Healthcare', limit=10)
    print(f"   Result: {len(healthcare_stocks)} stocks")
    if healthcare_stocks:
        print(f"   Sample: {healthcare_stocks[:5]}")
    else:
        print("   ❌ NO STOCKS RETURNED")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test buy recommendations
print("\n3. Testing get_dynamic_buy_recommendations...")
try:
    top_sectors = ['Technology', 'Healthcare']
    recommendations = service.get_dynamic_buy_recommendations(top_sectors, max_recommendations=3)
    print(f"   Result: {len(recommendations)} recommendations")
    for rec in recommendations:
        print(f"   - {rec['ticker']} ({rec['sector']}): ${rec.get('price', 'N/A')}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
