"""
Quick Conversation Test - Fast validation of core flows
Run this before the full E2E suite for rapid feedback
"""
import requests
import time

BASE_URL = "http://localhost:5000"
CHAT_ENDPOINT = f"{BASE_URL}/chat"

def quick_chat(message: str) -> str:
    """Send message and get response"""
    try:
        response = requests.post(
            CHAT_ENDPOINT,
            json={"question": message},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get('answer', '')
    except Exception as e:
        return f"ERROR: {str(e)}"

def check_for_loops(answer: str) -> bool:
    """Check if response contains loop-generating phrases"""
    loop_phrases = [
        'would you like me to',
        'ask me about',
        'i can help you with',
        'just ask',
        'how can i help',
        'want to know more'
    ]
    return any(phrase in answer.lower() for phrase in loop_phrases)

def test_quick_scenarios():
    """Run quick smoke tests"""
    print("\n" + "="*80)
    print("QUICK CONVERSATION TEST - Smoke Testing Vestor")
    print("="*80 + "\n")
    
    tests = [
        {
            'name': 'Educational Question',
            'message': 'What are consumer staples?',
            'expect': ['consumer staples', 'defensive', 'products'],
            'no_loops': True
        },
        {
            'name': 'Greeting',
            'message': 'Hi, I want to learn about investing',
            'expect': ['invest', 'help'],
            'no_loops': True
        },
        {
            'name': 'Stock Inquiry',
            'message': 'Tell me about Apple',
            'expect': ['apple', 'aapl'],
            'no_loops': True
        },
        {
            'name': 'Technical Question',
            'message': 'What is RSI?',
            'expect': ['rsi', 'momentum', 'overbought'],
            'no_loops': True
        },
        {
            'name': 'Investment Advice',
            'message': 'Should I invest in WMT?',
            'expect': ['invest', 'wmt', 'walmart'],
            'no_loops': True
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"Testing: {test['name']}")
        print(f"Message: {test['message']}")
        
        answer = quick_chat(test['message'])
        
        # Check expectations
        has_expected = any(word in answer.lower() for word in test['expect'])
        has_loops = check_for_loops(answer)
        
        passed = has_expected and (not has_loops if test['no_loops'] else True)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"Status: {status}")
        
        if not has_expected:
            print(f"  ⚠️ Missing expected keywords: {test['expect']}")
        if has_loops and test['no_loops']:
            print(f"  ⚠️ Contains loop-generating phrases")
        
        print(f"Response preview: {answer[:200]}...\n")
        
        results.append({
            'name': test['name'],
            'passed': passed,
            'has_loops': has_loops
        })
        
        time.sleep(1)
    
    # Summary
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    
    passed_count = sum(1 for r in results if r['passed'])
    total = len(results)
    
    for result in results:
        icon = "✅" if result['passed'] else "❌"
        print(f"{icon} {result['name']}")
    
    print(f"\nPassed: {passed_count}/{total} ({passed_count/total*100:.0f}%)")
    
    if passed_count == total:
        print("\n🎉 All quick tests passed! Ready for full E2E testing.")
    else:
        print("\n⚠️ Some tests failed. Check responses above.")
    
    print("="*80 + "\n")

if __name__ == '__main__':
    test_quick_scenarios()
