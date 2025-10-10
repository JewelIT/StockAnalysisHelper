"""
Simplified conversation test - tests actual issues without complex dependencies
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_conversation_issues():
    """Test the specific problems reported"""
    
    print("=" * 80)
    print("VESTOR CONVERSATION ISSUES - DIAGNOSTIC TEST")
    print("=" * 80)
    print("\nThis test identifies issues with:")
    print("1. Educational responses")
    print("2. Follow-up context")
    print("3. Currency conversion")
    print("4. Price extraction")
    print("5. Ticker lookup\n")
    
    from stock_chat import StockChatAssistant
    
    chat = StockChatAssistant()
    chat.load_model()
    
    # Test 1: Educational question
    print("\n" + "─" * 80)
    print("TEST 1: Educational Question")
    print("─" * 80)
    print("❓ QUESTION: 'What is investment'")
    
    result = chat.get_educational_response("What is investment")
    answer = result.get('answer', '')
    
    print(f"\n✅ Got response ({len(answer)} chars)")
    print(f"📊 Confidence: {result.get('confidence', 0)}")
    
    # Check quality
    if len(answer) < 100:
        print("❌ ISSUE: Response too short for educational content")
    if 'capital' not in answer.lower() and 'asset' not in answer.lower():
        print("⚠️  WARNING: Missing key investment concepts")
    
    print(f"\n🤖 ANSWER:\n{answer[:500]}...")
    
    # Test 2: Buy recommendation WITHOUT analysis (common issue)
    print("\n\n" + "─" * 80)
    print("TEST 2: Buy Recommendation (NO CONTEXT)")
    print("─" * 80)
    print("❓ QUESTION: 'should I buy apple?'")
    print("⚠️  This tests what happens when user asks without prior analysis\n")
    
    result2 = chat.answer_question("should I buy apple?", "", ticker=None)
    answer2 = result2.get('answer', '')
    
    print(f"✅ Got response ({len(answer2)} chars)")
    print(f"📊 Confidence: {result2.get('confidence', 0)}")
    
    # Check if it gracefully handles missing context
    if 'cannot' in answer2.lower() or 'unable' in answer2.lower() or 'need' in answer2.lower():
        print("✅ GOOD: Bot explains it needs to analyze first")
    elif 'aapl' not in answer2.lower() and 'apple' not in answer2.lower():
        print("❌ ISSUE: Doesn't mention Apple at all")
    
    print(f"\n🤖 ANSWER:\n{answer2[:500]}...")
    
    # Test 3: Currency conversion question
    print("\n\n" + "─" * 80)
    print("TEST 3: Currency Conversion")
    print("─" * 80)
    print("❓ QUESTION: 'what's the price of apple stock in euro?'")
    print("⚠️  This requires both price lookup AND currency conversion\n")
    
    # Create minimal context with price
    mock_context = """
    Stock: AAPL (Apple Inc.)
    Current Price: $175.50
    The stock is currently trading at $175.50 per share.
    """
    
    result3 = chat.answer_question("what's the price of apple stock in euro?", mock_context, ticker="AAPL")
    answer3 = result3.get('answer', '')
    
    print(f"✅ Got response ({len(answer3)} chars)")
    print(f"📊 Confidence: {result3.get('confidence', 0)}")
    
    # Check if it handles currency
    has_euro_symbol = '€' in answer3
    has_euro_word = 'euro' in answer3.lower()
    has_price = any(char.isdigit() for char in answer3)
    
    if has_euro_symbol or has_euro_word:
        print("✅ GOOD: Mentions euros")
    else:
        print("❌ ISSUE: Doesn't convert to euros")
    
    if has_price:
        print("✅ GOOD: Includes price numbers")
    else:
        print("❌ ISSUE: No price information")
    
    print(f"\n🤖 ANSWER:\n{answer3[:500]}...")
    
    # Test 4: Ticker lookup
    print("\n\n" + "─" * 80)
    print("TEST 4: Ticker Lookup")
    print("─" * 80)
    print("❓ QUESTION: 'What's the ticker for Uniphar PLC'")
    print("⚠️  This tests ticker lookup for unknown company\n")
    
    result4 = chat.answer_question("What's the ticker for Uniphar PLC", "", ticker=None)
    answer4 = result4.get('answer', '')
    
    print(f"✅ Got response ({len(answer4)} chars)")
    print(f"📊 Confidence: {result4.get('confidence', 0)}")
    
    # Check if it provides guidance
    has_guidance = any(word in answer4.lower() for word in ['yahoo', 'google', 'search', 'find', 'look up'])
    
    if has_guidance:
        print("✅ GOOD: Provides guidance on finding ticker")
    else:
        print("❌ ISSUE: Doesn't explain how to find ticker")
    
    print(f"\n🤖 ANSWER:\n{answer4[:500]}...")
    
    # Summary
    print("\n\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    print("\n🔍 KEY FINDINGS:")
    print("1. Educational responses - Check length and concept coverage")
    print("2. Buy recommendations need proper context/analysis")
    print("3. Currency conversion requires exchange rate API")
    print("4. Ticker lookup for unknown companies needs guidance")
    print("\n💡 RECOMMENDATIONS:")
    print("• Add context awareness (remember last analyzed stock)")
    print("• Add currency conversion utility")
    print("• Improve price extraction from context")
    print("• Better ticker lookup guidance")
    print("=" * 80)

if __name__ == '__main__':
    test_conversation_issues()
