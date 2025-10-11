"""
Phase 1 Test: Conversation Memory
Tests that bot remembers context between questions
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.ai.stock_chat import StockChatAssistant

def test_conversation_memory():
    """Test conversation memory works"""
    print("\n" + "=" * 80)
    print("PHASE 1 TEST: CONVERSATION MEMORY")
    print("=" * 80)
    
    chat = StockChatAssistant()
    chat.load_model()
    
    # Create mock analysis context for AAPL
    mock_context = """
    Stock Analysis for AAPL (Apple Inc.)
    Current Price: $175.50
    Market Sentiment: BULLISH (78% confidence)
    Technical Analysis: RSI at 65 (neutral), MACD showing positive momentum
    People are buying: Strong institutional buying detected
    Recent Performance: Up 5.2% this week
    """
    
    # Q1: Initial question with explicit ticker
    print("\n📝 TEST 1: Initial Question (Explicit Ticker)")
    print("─" * 80)
    print("❓ 'What do you think about Apple stock?'")
    
    result1 = chat.answer_question(
        "What do you think about Apple stock?",
        mock_context,
        ticker="AAPL"
    )
    
    answer1 = result1.get('answer', '')
    print(f"✅ Got response ({len(answer1)} chars)")
    
    # Check if bot stored the context
    if hasattr(chat, 'last_ticker'):
        if chat.last_ticker == "AAPL":
            print("✅ PASS: Bot remembered ticker 'AAPL'")
        else:
            print(f"❌ FAIL: Bot stored wrong ticker: '{chat.last_ticker}'")
    else:
        print("❌ FAIL: Bot has no 'last_ticker' attribute")
    
    if hasattr(chat, 'last_analysis_context'):
        if chat.last_analysis_context:
            print("✅ PASS: Bot stored analysis context")
        else:
            print("❌ FAIL: Bot didn't store analysis context")
    else:
        print("❌ FAIL: Bot has no 'last_analysis_context' attribute")
    
    # Q2: Follow-up WITHOUT mentioning ticker
    print("\n📝 TEST 2: Follow-up Question (No Ticker Mentioned)")
    print("─" * 80)
    print("❓ 'are people buying it?'")
    print("⚠️  Should use context from previous question about AAPL")
    
    result2 = chat.answer_question(
        "are people buying it?",
        "",  # Empty context - should use remembered context
        ticker=None  # No ticker - should use last_ticker
    )
    
    answer2 = result2.get('answer', '')
    print(f"✅ Got response ({len(answer2)} chars)")
    
    # Check if response mentions Apple/AAPL
    answer2_lower = answer2.lower()
    if 'apple' in answer2_lower or 'aapl' in answer2_lower:
        print("✅ PASS: Response mentions Apple/AAPL")
    else:
        print("❌ FAIL: Response doesn't mention Apple/AAPL")
    
    # Check if response has sentiment info
    if any(word in answer2_lower for word in ['buying', 'bullish', 'sentiment', 'institutional']):
        print("✅ PASS: Response includes sentiment/buying information")
    else:
        print("❌ FAIL: Response missing sentiment information")
    
    print(f"\n🤖 Response preview:\n{answer2[:300]}...")
    
    # Q3: Another follow-up
    print("\n📝 TEST 3: Second Follow-up")
    print("─" * 80)
    print("❓ 'what's the current price?'")
    
    result3 = chat.answer_question(
        "what's the current price?",
        "",
        ticker=None
    )
    
    answer3 = result3.get('answer', '')
    print(f"✅ Got response ({len(answer3)} chars)")
    
    # Check if response mentions price
    if '$175' in answer3 or '175' in answer3:
        print("✅ PASS: Response includes the price")
    else:
        print("❌ FAIL: Response doesn't include price information")
    
    # Q4: Switch to different stock
    print("\n📝 TEST 4: Switch to Different Stock")
    print("─" * 80)
    print("❓ 'What about Microsoft?'")
    
    mock_context_msft = """
    Stock Analysis for MSFT (Microsoft Corporation)
    Current Price: $380.25
    Market Sentiment: BULLISH (82% confidence)
    """
    
    result4 = chat.answer_question(
        "What about Microsoft?",
        mock_context_msft,
        ticker="MSFT"
    )
    
    answer4 = result4.get('answer', '')
    print(f"✅ Got response ({len(answer4)} chars)")
    
    # Check if context switched
    if hasattr(chat, 'last_ticker'):
        if chat.last_ticker == "MSFT":
            print("✅ PASS: Bot switched to MSFT")
        else:
            print(f"❌ FAIL: Bot didn't switch ticker: '{chat.last_ticker}'")
    
    # Q5: Follow-up should now be about MSFT
    print("\n📝 TEST 5: Follow-up After Switch")
    print("─" * 80)
    print("❓ 'is it a good buy?'")
    print("⚠️  Should refer to MSFT, not AAPL")
    
    result5 = chat.answer_question(
        "is it a good buy?",
        "",
        ticker=None
    )
    
    answer5 = result5.get('answer', '')
    print(f"✅ Got response ({len(answer5)} chars)")
    
    answer5_lower = answer5.lower()
    if 'microsoft' in answer5_lower or 'msft' in answer5_lower:
        print("✅ PASS: Response refers to Microsoft")
        if 'apple' in answer5_lower or 'aapl' in answer5_lower:
            print("⚠️  WARNING: Response mentions both stocks (context confusion)")
    else:
        print("❌ FAIL: Response doesn't refer to Microsoft")
        if 'apple' in answer5_lower:
            print("❌ FAIL: Response still talking about Apple (didn't switch context)")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("\n📊 What we're testing:")
    print("1. Bot stores last ticker and context")
    print("2. Follow-up questions use stored context")
    print("3. Bot can switch between different stocks")
    print("4. Pronouns like 'it' refer to last mentioned stock")
    print("\n💡 If tests fail, implement conversation memory in stock_chat.py")
    print("=" * 80)

if __name__ == '__main__':
    test_conversation_memory()
