"""
Real-world conversation test based on actual user session
Tests the specific issues reported:
1. "What is investment" - Educational response
2. "should I buy apple?" - Recommendation with context
3. "are people buying apple?" - Follow-up sentiment question
4. "what's the price of apple stock in euro?" - Currency conversion
5. "What's the ticker for Uniphar PLC" - Ticker lookup
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.stock_chat import StockChatAssistant
from stock_analysis import StockAnalysis

class ConversationTester:
    """Test real conversation flows"""
    
    def __init__(self):
        self.chat = StockChatAssistant()
        self.analyzer = StockAnalysis()
        self.chat.load_model()
        self.conversation_context = None
        self.last_ticker = None
        
    def test_conversation(self):
        """Run the exact conversation from user report"""
        print("=" * 80)
        print("TESTING REAL USER CONVERSATION")
        print("=" * 80)
        print()
        
        # Q1: Educational question
        self.ask("What is investment")
        
        # Q2: Buy recommendation
        self.ask("should I buy apple?")
        
        # Q3: Follow-up sentiment
        self.ask("are people buying apple?")
        
        # Q4: Currency conversion
        self.ask("what's the price of apple stock in euro?")
        
        # Q5: Ticker lookup
        self.ask("What's the ticker for Uniphar PLC")
        
        print("\n" + "=" * 80)
        print("CONVERSATION TEST COMPLETE")
        print("=" * 80)
    
    def ask(self, question):
        """Ask a question and analyze the response"""
        print(f"\n{'─' * 80}")
        print(f"👤 USER: {question}")
        print(f"{'─' * 80}")
        
        # Detect if question is about a specific stock
        ticker = self._extract_ticker(question)
        
        # If we have a ticker and it changed, get new analysis
        if ticker and ticker != self.last_ticker:
            print(f"📊 Analyzing {ticker}...")
            analysis = self.analyzer.full_stock_analysis(ticker)
            if analysis['success']:
                self.conversation_context = self.chat.generate_context_from_analysis(analysis)
                self.last_ticker = ticker
            else:
                print(f"❌ Failed to analyze {ticker}: {analysis.get('error', 'Unknown error')}")
                self.conversation_context = None
        elif not ticker and self.last_ticker:
            # User might be asking follow-up about same stock
            ticker = self.last_ticker
        
        # Get chatbot response
        if self.conversation_context and ticker:
            result = self.chat.answer_question(question, self.conversation_context, ticker)
        else:
            result = self.chat.get_educational_response(question)
        
        print(f"\n🤖 ASSISTANT:\n")
        print(result.get('answer', 'No answer provided'))
        
        # Analyze response quality
        self._analyze_response_quality(question, result, ticker)
        
        return result
    
    def _extract_ticker(self, question):
        """Extract ticker from question"""
        question_lower = question.lower()
        
        # Common company name to ticker mapping
        company_map = {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'tesla': 'TSLA',
            'amazon': 'AMZN',
            'google': 'GOOGL',
            'meta': 'META',
            'nvidia': 'NVDA',
            'netflix': 'NFLX'
        }
        
        # Check for company names
        for company, ticker in company_map.items():
            if company in question_lower:
                return ticker
        
        # Check for explicit ticker patterns
        import re
        ticker_match = re.search(r'\b([A-Z]{1,5})\b', question)
        if ticker_match:
            return ticker_match.group(1)
        
        return None
    
    def _analyze_response_quality(self, question, result, ticker):
        """Analyze if response quality is acceptable"""
        print(f"\n{'┄' * 80}")
        print("📋 RESPONSE ANALYSIS:")
        
        answer = result.get('answer', '').lower()
        question_lower = question.lower()
        
        issues = []
        
        # Check for common issues
        if 'investment' in question_lower and 'what is' in question_lower:
            # Should provide educational content
            if len(answer) < 100:
                issues.append("❌ Educational response too short")
            if 'capital' not in answer and 'asset' not in answer:
                issues.append("⚠️  Missing key investment concepts")
            else:
                print("✅ Provided educational content")
        
        if 'should i buy' in question_lower:
            # Should provide recommendation with caveats
            if 'i recommend' in answer or 'you should' in answer:
                issues.append("⚠️  Too directive (should be more cautious)")
            if 'risk' not in answer and 'research' not in answer:
                issues.append("❌ Missing risk warnings")
            if ticker and ticker.lower() not in answer:
                issues.append(f"❌ Doesn't mention ticker {ticker}")
            if not issues:
                print("✅ Provided balanced recommendation")
        
        if 'people buying' in question_lower or 'sentiment' in question_lower:
            # Should provide sentiment analysis
            if ticker and any(word in answer for word in ['bullish', 'bearish', 'neutral', 'sentiment']):
                print("✅ Provided sentiment analysis")
            else:
                issues.append("❌ Missing sentiment analysis")
        
        if 'price' in question_lower and 'euro' in question_lower:
            # Should provide currency conversion
            if '€' in answer or 'euro' in answer:
                print("✅ Provided currency conversion")
            else:
                issues.append("❌ Missing currency conversion")
            if ticker:
                # Should mention current price
                import re
                has_price = bool(re.search(r'\$?\d+\.?\d*', answer))
                if has_price:
                    print("✅ Includes price information")
                else:
                    issues.append("⚠️  No price numbers found")
        
        if 'ticker for' in question_lower or 'ticker symbol' in question_lower:
            # Should explain how to find tickers
            if 'yahoo finance' in answer or 'google' in answer or 'search' in answer:
                print("✅ Provided ticker lookup guidance")
            else:
                issues.append("❌ Doesn't explain how to find ticker")
        
        # Print issues
        if issues:
            print("\n🔴 ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n🟢 Response quality: GOOD")
        
        # Confidence check
        confidence = result.get('confidence', 0)
        if confidence < 0.5:
            print(f"\n⚠️  Low confidence: {confidence:.2f}")
        
        print(f"{'┄' * 80}")


if __name__ == '__main__':
    print("\n🧪 Starting real-world conversation test...\n")
    tester = ConversationTester()
    tester.test_conversation()
