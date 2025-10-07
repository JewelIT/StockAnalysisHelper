#!/usr/bin/env python3
"""
Quick test script for ticker lookup functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vestor_service import VestorService

def test_ticker_lookups():
    """Test various ticker lookup questions"""
    vestor = VestorService()
    
    test_questions = [
        "what's the ticker for boeing",
        "what's the ticker for Boeing?",
        "What is the ticker for Apple",
        "ticker for Microsoft",
        "what's the stock symbol for Tesla",
        "tell me the ticker for Google",
        "what's the ticker for xyz company",  # Not in database
        "what companies do you know",
        "list the tickers you support",
        "what stocks can you analyze",
    ]
    
    print("\n" + "="*80)
    print("TESTING TICKER LOOKUP FUNCTIONALITY")
    print("="*80 + "\n")
    
    for question in test_questions:
        print(f"❓ Question: {question}")
        print("-" * 80)
        
        # Test the ticker lookup directly
        result = vestor._handle_ticker_lookup(question, question.lower())
        
        if result:
            print(f"✅ MATCHED - Mode: {result['vestor_mode']}")
            print(f"📊 Ticker: {result.get('ticker', 'None')}")
            print(f"\n📝 Response:\n{result['answer'][:200]}...")
        else:
            # Try list companies
            list_result = vestor._handle_list_companies(question.lower())
            if list_result:
                print(f"✅ MATCHED - Mode: {list_result['vestor_mode']}")
                print(f"\n📝 Response:\n{list_result['answer'][:200]}...")
            else:
                print("❌ NO MATCH - Would fall through to regular conversation")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_ticker_lookups()
