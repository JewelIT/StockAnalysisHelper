#!/usr/bin/env python3
"""
Test script to verify analyst consensus integration
Tests both COUR (with analyst coverage) and a stock without coverage
"""

from src.core.portfolio_analyzer import PortfolioAnalyzer
import json

def test_analyst_integration():
    print("=" * 80)
    print("ANALYST CONSENSUS INTEGRATION TEST")
    print("=" * 80)
    
    analyzer = PortfolioAnalyzer(enable_social_media=False)
    
    # Test 1: Stock with analyst coverage (COUR)
    print("\n📊 TEST 1: Stock with Analyst Coverage (COUR)")
    print("-" * 80)
    result1 = analyzer.analyze_stock('COUR', max_news=2, timeframe='3mo')
    
    if result1['success']:
        print(f"✓ Analysis completed successfully")
        print(f"\n  Company: {result1['name']}")
        print(f"  Recommendation: {result1['recommendation']}")
        print(f"  Combined Score: {result1['combined_score']:.3f}")
        
        print(f"\n  Score Breakdown:")
        print(f"    - Sentiment: {result1['sentiment_score']:.3f}")
        print(f"    - Technical: {result1['technical_score']:.3f}")
        if result1.get('analyst_score'):
            print(f"    - Analyst: {result1['analyst_score']:.3f}")
        
        if result1.get('analyst_consensus'):
            ac = result1['analyst_consensus']
            print(f"\n  Analyst Consensus:")
            print(f"    - Signal: {ac['signal']}")
            print(f"    - Number of Analysts: {ac['num_analysts']}")
            print(f"    - Recommendation Mean: {ac['recommendation_mean']:.2f}")
            
            if result1.get('analyst_data'):
                ad = result1['analyst_data']
                if ad.get('target_mean_price') and ad.get('current_price'):
                    upside = ((ad['target_mean_price'] - ad['current_price']) / ad['current_price']) * 100
                    print(f"    - Target Price: ${ad['target_mean_price']:.2f}")
                    print(f"    - Current Price: ${ad['current_price']:.2f}")
                    print(f"    - Upside Potential: {upside:+.1f}%")
            
            print(f"\n  ✓ Analyst data successfully integrated!")
        else:
            print(f"\n  ✗ ERROR: No analyst consensus found (expected for COUR)")
            return False
        
        # Check formula
        exp = result1['recommendation_explanation']
        print(f"\n  Formula: {exp['formula']}")
        print(f"  Weights: Sentiment={exp['sentiment_weight']}, Technical={exp['technical_weight']}, Analyst={exp['analyst_weight']}")
        
        if exp['analyst_weight'] != '30%':
            print(f"\n  ✗ ERROR: Expected analyst weight of 30%, got {exp['analyst_weight']}")
            return False
    else:
        print(f"✗ Analysis failed: {result1.get('error')}")
        return False
    
    # Test 2: Stock without sufficient analyst coverage
    print("\n\n📊 TEST 2: Stock with Insufficient Analyst Coverage")
    print("-" * 80)
    
    # Try to find a stock with less than 3 analysts
    test_tickers = ['GME', 'HOOD', 'PLTR']
    found_no_coverage = False
    
    for ticker in test_tickers:
        result2 = analyzer.analyze_stock(ticker, max_news=1, timeframe='1mo')
        
        if result2['success']:
            has_analyst = result2.get('analyst_score') is not None
            num_analysts = result2.get('analyst_consensus', {}).get('num_analysts', 0) if has_analyst else 0
            
            print(f"\n  Testing {ticker}:")
            print(f"    - Recommendation: {result2['recommendation']}")
            print(f"    - Has Analyst Data: {has_analyst}")
            
            if has_analyst:
                print(f"    - Number of Analysts: {num_analysts}")
                print(f"    - Analyst Score: {result2['analyst_score']:.3f}")
            else:
                print(f"    - Fallback to sentiment + technical only")
                exp2 = result2['recommendation_explanation']
                print(f"    - Formula: {exp2['formula']}")
                
                if 'Analyst Consensus' in exp2['formula']:
                    print(f"\n  ✗ ERROR: Formula shouldn't include analyst data")
                    return False
                
                found_no_coverage = True
                print(f"\n  ✓ Fallback logic working correctly!")
                break
    
    if not found_no_coverage:
        print(f"\n  Note: All tested stocks have analyst coverage, fallback not tested")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Analyst Integration Working Correctly")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_analyst_integration()
    exit(0 if success else 1)
