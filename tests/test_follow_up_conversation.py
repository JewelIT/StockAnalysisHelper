#!/usr/bin/env python3
"""
Test ticker lookup and follow-up conversation flow
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.services.vestor_service import VestorService

def test_follow_up_flow():
    """Test that follow-up questions use the context ticker"""
    vestor = VestorService()
    
    print("\n" + "="*80)
    print("TEST: Follow-up Question Flow")
    print("="*80 + "\n")
    
    # First question mentions Boeing
    print("1️⃣  User asks: 'what's the ticker for boeing'")
    result1 = vestor.process_chat(
        question="what's the ticker for boeing",
        ticker="",
        context_ticker="",
        conversation_history=[]
    )
    print(f"✅ Mode: {result1['vestor_mode']}")
    print(f"✅ Ticker: {result1.get('ticker', 'None')}")
    assert result1['ticker'] == 'BA', f"Expected BA, got {result1.get('ticker')}"
    print(f"✅ Answer preview: {result1['answer'][:100]}...")
    
    # Second question is a follow-up (assumes BA from context)
    print("\n2️⃣  User asks: 'should I buy it?' (follow-up)")
    result2 = vestor.process_chat(
        question="should I buy it?",
        ticker="",
        context_ticker="BA",  # BA from previous question
        conversation_history=[
            {'role': 'user', 'content': "what's the ticker for boeing", 'ticker': 'BA'},
            {'role': 'assistant', 'content': result1['answer'], 'ticker': 'BA'}
        ]
    )
    print(f"✅ Mode: {result2['vestor_mode']}")
    print(f"✅ Should use ticker from context")
    
    # Check if it's trying to use stock analysis mode (not just conversation)
    if result2['vestor_mode'] == 'conversation':
        print("❌ ERROR: Follow-up went to conversation mode instead of stock analysis")
        print(f"   Answer: {result2['answer'][:200]}")
        return False
    elif result2['vestor_mode'] == 'needs_analysis':
        print("✅ Correctly identified need for analysis")
        print(f"✅ Pending ticker: {result2.get('pending_ticker')}")
        return True
    elif result2['vestor_mode'] == 'stock_advice':
        print("✅ Correctly used cached analysis for stock advice")
        # Check if answer contains "BA" or "Boeing" (not "this asset")
        answer_lower = result2['answer'].lower()
        if 'this asset' in answer_lower:
            print("⚠️  WARNING: Answer contains 'this asset' instead of ticker name")
            print(f"   Answer preview: {result2['answer'][:300]}")
        else:
            print("✅ Answer uses proper ticker reference")
        return True
    else:
        print(f"✅ Mode: {result2['vestor_mode']}")
        return True

def test_ticker_resolution():
    """Test ticker resolution logic"""
    vestor = VestorService()
    
    print("\n" + "="*80)
    print("TEST: Ticker Resolution")
    print("="*80 + "\n")
    
    # Test explicit ticker takes priority
    ticker1 = vestor._resolve_ticker("AAPL", ["MSFT"], "TSLA", "should i buy")
    assert ticker1 == "AAPL", "Explicit ticker should take priority"
    print("✅ Explicit ticker takes priority")
    
    # Test mentioned ticker is used
    ticker2 = vestor._resolve_ticker("", ["MSFT", "GOOGL"], "TSLA", "what about microsoft")
    assert ticker2 == "MSFT", "Mentioned ticker should be used"
    print("✅ Mentioned ticker is used")
    
    # Test context ticker for follow-ups
    ticker3 = vestor._resolve_ticker("", [], "BA", "should i buy it")
    assert ticker3 == "BA", "Context ticker should be used for follow-ups"
    print("✅ Context ticker used for follow-ups")
    
    # Test no ticker found
    ticker4 = vestor._resolve_ticker("", [], "", "hello there")
    assert ticker4 is None, "Should return None when no ticker found"
    print("✅ Returns None when no ticker found")
    
    return True

if __name__ == "__main__":
    success = True
    
    try:
        if not test_ticker_resolution():
            success = False
        
        if not test_follow_up_flow():
            success = False
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    if success:
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("❌ SOME TESTS FAILED")
        print("="*80)
        sys.exit(1)
