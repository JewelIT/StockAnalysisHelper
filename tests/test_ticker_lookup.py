#!/usr/bin/env python3
"""
Quick test script for ticker lookup functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.services.vestor_service import VestorService

def test_ticker_lookups():
    """Test various ticker lookup questions - now handled by AI"""
    vestor = VestorService()
    
    test_questions = [
        ("what's the ticker for boeing", True),  # Any company
        ("what's the ticker for random startup", True),  # Unknown company
        ("What is the ticker for some company", True),  # Generic
        ("what about Apple", False),  # Stock mention (should detect AAPL)
        ("tell me about Microsoft", False),  # Stock mention
        ("how do I invest", False),  # General question
    ]
    
    print("\n" + "="*80)
    print("TESTING TICKER LOOKUP FUNCTIONALITY")
    print("="*80 + "\n")
    
    for question, is_ticker_lookup in test_questions:
        print(f"❓ Question: {question}")
        print(f"   Expected: {'Ticker lookup guidance' if is_ticker_lookup else 'Stock analysis or conversation'}")
        print("-" * 80)
        
        result = vestor.process_chat(question, '', '', [])
        
        if is_ticker_lookup:
            # Should go to conversation mode with ticker lookup guidance
            if result['vestor_mode'] == 'conversation' and 'ticker' in result['answer'].lower():
                print(f"✅ CORRECT - Returns ticker lookup guidance")
                print(f"📝 Response preview: {result['answer'][:150]}...")
            else:
                print(f"❌ UNEXPECTED - Mode: {result['vestor_mode']}")
                print(f"📝 Answer: {result['answer'][:200]}")
        else:
            # Should detect ticker or handle as conversation
            print(f"✅ Mode: {result['vestor_mode']}")
            if result.get('ticker') or result.get('pending_ticker'):
                print(f"📊 Ticker detected: {result.get('ticker') or result.get('pending_ticker')}")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_ticker_lookups()
