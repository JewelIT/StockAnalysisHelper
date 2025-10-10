"""
End-to-End Conversation Scenarios with Vestor
Tests realistic multi-turn conversations through the actual UI/API
"""
import requests
import time
import json
from typing import List, Dict

BASE_URL = "http://localhost:5000"
CHAT_ENDPOINT = f"{BASE_URL}/chat"
ANALYZE_ENDPOINT = f"{BASE_URL}/analyze"

class ConversationSession:
    """Represents a user's conversation session with Vestor"""
    
    def __init__(self, scenario_name: str):
        self.scenario_name = scenario_name
        self.messages = []
        self.context_ticker = None
        self.start_time = time.time()
        
    def say(self, message: str, wait_seconds: float = 1.5) -> Dict:
        """User sends a message and gets response"""
        print(f"\n{'='*80}")
        print(f"👤 USER: {message}")
        print(f"{'='*80}")
        
        try:
            # Send message to chat endpoint
            response = requests.post(
                CHAT_ENDPOINT,
                json={
                    "question": message,
                    "ticker": self.context_ticker
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            answer = data.get('answer', '')
            ticker = data.get('ticker')
            
            # Update context if ticker mentioned
            if ticker:
                self.context_ticker = ticker
            
            # Store message
            msg_record = {
                'user': message,
                'vestor': answer,
                'ticker': ticker,
                'timestamp': time.time() - self.start_time
            }
            self.messages.append(msg_record)
            
            # Print Vestor's response
            print(f"\n🤖 VESTOR: {answer[:800]}{'...' if len(answer) > 800 else ''}\n")
            
            # Wait before next message (simulate human typing)
            time.sleep(wait_seconds)
            
            return data
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}\n")
            msg_record = {
                'user': message,
                'vestor': None,
                'error': str(e),
                'timestamp': time.time() - self.start_time
            }
            self.messages.append(msg_record)
            return {'error': str(e)}
    
    def analyze_stock(self, ticker: str) -> Dict:
        """Request stock analysis"""
        print(f"\n{'='*80}")
        print(f"📊 ANALYZING: {ticker}")
        print(f"{'='*80}")
        
        try:
            response = requests.post(
                ANALYZE_ENDPOINT,
                json={"tickers": [ticker]},
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Analysis complete for {ticker}\n")
            self.context_ticker = ticker
            time.sleep(2)
            
            return data
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}\n")
            return {'error': str(e)}
    
    def print_summary(self):
        """Print conversation summary"""
        print(f"\n\n{'#'*80}")
        print(f"CONVERSATION SUMMARY: {self.scenario_name}")
        print(f"{'#'*80}")
        print(f"Duration: {time.time() - self.start_time:.1f} seconds")
        print(f"Messages: {len(self.messages)}")
        print(f"Final Context Ticker: {self.context_ticker}")
        
        # Count successful responses
        successful = sum(1 for m in self.messages if m.get('vestor') is not None)
        print(f"Successful Responses: {successful}/{len(self.messages)}")
        
        # Check for loops
        loop_phrases = ['would you like me to', 'ask me about', 'i can help you with']
        loop_count = sum(
            1 for m in self.messages 
            if m.get('vestor') and any(phrase in m['vestor'].lower() for phrase in loop_phrases)
        )
        print(f"Loop Responses: {loop_count} {'❌ FAIL' if loop_count > 0 else '✅ PASS'}")
        
        print(f"{'#'*80}\n\n")


# ============================================================================
# SCENARIO 1: Complete Beginner - Learning the Basics
# ============================================================================

def scenario_1_complete_beginner():
    """
    Sarah is 25, just got her first real job, wants to start investing
    She knows nothing about stocks or the market
    """
    print("\n" + "="*80)
    print("SCENARIO 1: Complete Beginner - Sarah's First Steps")
    print("="*80)
    print("Sarah (25) just got her first job and wants to learn about investing.")
    print("She's heard about stocks but doesn't understand how they work.")
    print("="*80 + "\n")
    
    session = ConversationSession("Complete Beginner")
    
    # Greeting
    session.say("Hi! I'm Sarah and I'm new to investing.")
    
    # Basic questions
    session.say("What exactly is a stock?")
    
    session.say("So if I buy Apple stock, I own part of Apple?")
    
    session.say("How do I actually make money from stocks?")
    
    session.say("What about dividends? I've heard that term.")
    
    # Getting practical
    session.say("Okay, I want to start. How much money do I need to begin investing?")
    
    session.say("What's the difference between a stock and a cryptocurrency?")
    
    # Ready to invest
    session.say("I have $1000 saved. Should I invest all of it?")
    
    session.say("What stocks would you recommend for a beginner like me?")
    
    session.say("Tell me about Apple. Is it good for beginners?")
    
    # Get analysis
    session.analyze_stock("AAPL")
    
    # Follow up on analysis
    session.say("Should I buy Apple stock now?")
    
    session.say("What if the price goes down after I buy it?")
    
    session.say("Thank you! This was really helpful. I feel more confident now.")
    
    session.print_summary()
    return session


# ============================================================================
# SCENARIO 2: Experienced Investor - Technical Analysis
# ============================================================================

def scenario_2_experienced_trader():
    """
    Mike is 35, has been trading for 5 years
    Wants technical analysis and specific signals
    """
    print("\n" + "="*80)
    print("SCENARIO 2: Experienced Trader - Mike's Technical Analysis")
    print("="*80)
    print("Mike (35) is an experienced trader looking for technical insights.")
    print("He wants specific signals and detailed analysis.")
    print("="*80 + "\n")
    
    session = ConversationSession("Experienced Trader")
    
    # Direct and knowledgeable
    session.say("Hey, I want to check NVIDIA's technical setup.")
    
    # Request analysis
    session.analyze_stock("NVDA")
    
    # Technical questions
    session.say("What's the RSI looking like?")
    
    session.say("Is NVDA overbought right now?")
    
    session.say("What about the MACD signal?")
    
    session.say("Are we seeing bullish or bearish divergence?")
    
    # Sentiment check
    session.say("What's the overall market sentiment on NVDA?")
    
    # Comparison
    session.say("How does NVDA compare to AMD right now?")
    
    # Get AMD analysis
    session.analyze_stock("AMD")
    
    session.say("Between NVDA and AMD, which has better momentum?")
    
    # Risk assessment
    session.say("What's the volatility like on these semiconductor stocks?")
    
    # Entry point
    session.say("If I'm looking to enter NVDA, what would be a good price level?")
    
    session.say("Thanks, that's exactly what I needed.")
    
    session.print_summary()
    return session


# ============================================================================
# SCENARIO 3: Market Overview - Daily Briefing
# ============================================================================

def scenario_3_market_overview():
    """
    Lisa checks in every morning for market overview
    Wants to understand what's happening in the markets
    """
    print("\n" + "="*80)
    print("SCENARIO 3: Market Overview - Lisa's Daily Briefing")
    print("="*80)
    print("Lisa (40) starts her day with a market overview.")
    print("She wants to understand sector trends and opportunities.")
    print("="*80 + "\n")
    
    session = ConversationSession("Market Overview")
    
    # Morning greeting
    session.say("Good morning! What's happening in the market today?")
    
    # Sector questions
    session.say("Which sectors are performing well?")
    
    session.say("Tell me about the technology sector.")
    
    session.say("What about consumer staples? Are they defensive right now?")
    
    # Specific interest
    session.say("I'm interested in healthcare stocks. Any recommendations?")
    
    # Check a specific stock
    session.say("What about Johnson & Johnson?")
    
    session.analyze_stock("JNJ")
    
    session.say("Is JNJ a good long-term hold?")
    
    # Diversification
    session.say("I already own tech stocks. Should I diversify into healthcare?")
    
    # Risk management
    session.say("With the current market volatility, what should I do?")
    
    # Check another sector
    session.say("What's happening with financial stocks like JPMorgan?")
    
    session.analyze_stock("JPM")
    
    session.say("Are banks a good play right now?")
    
    session.say("Thanks for the briefing. I'll check back tomorrow!")
    
    session.print_summary()
    return session


# ============================================================================
# SCENARIO 4: Value Investor - Finding Opportunities
# ============================================================================

def scenario_4_value_investor():
    """
    Robert is looking for undervalued stocks
    Wants fundamental analysis and valuation metrics
    """
    print("\n" + "="*80)
    print("SCENARIO 4: Value Investor - Robert's Stock Hunting")
    print("="*80)
    print("Robert (50) is a value investor looking for undervalued opportunities.")
    print("He focuses on fundamentals and long-term potential.")
    print("="*80 + "\n")
    
    session = ConversationSession("Value Investor")
    
    # Introduction
    session.say("I'm looking for undervalued stocks with strong fundamentals.")
    
    # Strategy discussion
    session.say("What's your approach to identifying value stocks?")
    
    # P/E ratio questions
    session.say("Can you explain P/E ratios? What's a good P/E?")
    
    # Check retail
    session.say("I'm interested in Walmart. Is it undervalued?")
    
    session.analyze_stock("WMT")
    
    session.say("What's the sentiment on Walmart?")
    
    session.say("Does WMT pay dividends?")
    
    # Compare with competitor
    session.say("How does Walmart compare to Costco?")
    
    session.analyze_stock("COST")
    
    session.say("Between WMT and COST, which is better value?")
    
    # Long-term perspective
    session.say("I'm thinking 10-year hold. Which is better for that?")
    
    # Risk assessment
    session.say("What are the risks with retail stocks right now?")
    
    # Final decision
    session.say("I think I'll go with Walmart. What do you think?")
    
    session.say("Great analysis. Thank you!")
    
    session.print_summary()
    return session


# ============================================================================
# SCENARIO 5: Crypto Curious - Exploring Digital Assets
# ============================================================================

def scenario_5_crypto_explorer():
    """
    Emma wants to understand cryptocurrency
    Curious about Bitcoin and altcoins but cautious
    """
    print("\n" + "="*80)
    print("SCENARIO 5: Crypto Explorer - Emma's Crypto Journey")
    print("="*80)
    print("Emma (28) is curious about cryptocurrency but doesn't understand it.")
    print("She's heard stories of huge gains and huge losses.")
    print("="*80 + "\n")
    
    session = ConversationSession("Crypto Explorer")
    
    # Opening
    session.say("Hi, I want to learn about cryptocurrency.")
    
    # Basic understanding
    session.say("What's the difference between Bitcoin and regular stocks?")
    
    session.say("Why is crypto so volatile?")
    
    # Specific crypto
    session.say("Should I invest in Bitcoin?")
    
    session.analyze_stock("BTC-USD")
    
    session.say("What's Bitcoin's price right now?")
    
    session.say("Is Bitcoin too expensive for me to buy?")
    
    session.say("How much should I invest in crypto?")
    
    # Alt coins
    session.say("What about Ethereum? Is it better than Bitcoin?")
    
    session.analyze_stock("ETH-USD")
    
    session.say("Between Bitcoin and Ethereum, which is safer?")
    
    # Risk concerns
    session.say("I heard people lose all their money in crypto. Is it really that risky?")
    
    session.say("How do I protect myself from losing everything?")
    
    # Diversification
    session.say("Should I have both crypto and stocks in my portfolio?")
    
    # Final thoughts
    session.say("Okay, I think I'll start small with Bitcoin. Good idea?")
    
    session.say("Thanks for making crypto less scary!")
    
    session.print_summary()
    return session


# ============================================================================
# RUN ALL SCENARIOS
# ============================================================================

def run_all_scenarios():
    """Execute all conversation scenarios"""
    print("\n\n" + "#"*80)
    print("VESTOR E2E CONVERSATION TEST SUITE")
    print("Testing realistic multi-turn conversations with follow-ups")
    print("#"*80 + "\n")
    
    scenarios = [
        ("Complete Beginner", scenario_1_complete_beginner),
        ("Experienced Trader", scenario_2_experienced_trader),
        ("Market Overview", scenario_3_market_overview),
        ("Value Investor", scenario_4_value_investor),
        ("Crypto Explorer", scenario_5_crypto_explorer),
    ]
    
    results = []
    
    for name, scenario_func in scenarios:
        print(f"\n{'*'*80}")
        print(f"Starting: {name}")
        print(f"{'*'*80}\n")
        
        try:
            session = scenario_func()
            
            # Analyze results
            successful = sum(1 for m in session.messages if m.get('vestor') is not None)
            loop_phrases = ['would you like me to', 'ask me about', 'i can help you with']
            loop_count = sum(
                1 for m in session.messages 
                if m.get('vestor') and any(phrase in m['vestor'].lower() for phrase in loop_phrases)
            )
            
            results.append({
                'name': name,
                'status': 'PASS' if loop_count == 0 else 'FAIL',
                'messages': len(session.messages),
                'successful': successful,
                'loops': loop_count,
                'duration': time.time() - session.start_time
            })
            
        except Exception as e:
            print(f"\n❌ SCENARIO FAILED: {str(e)}\n")
            results.append({
                'name': name,
                'status': 'ERROR',
                'error': str(e)
            })
    
    # Final summary
    print("\n\n" + "="*80)
    print("FINAL TEST RESULTS")
    print("="*80)
    print(f"{'Scenario':<30} {'Status':<10} {'Messages':<10} {'Loops':<10} {'Duration':<10}")
    print("-"*80)
    
    for result in results:
        name = result['name']
        status = result['status']
        messages = result.get('messages', 'N/A')
        loops = result.get('loops', 'N/A')
        duration = f"{result.get('duration', 0):.1f}s" if 'duration' in result else 'N/A'
        
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{name:<30} {status_icon} {status:<8} {messages:<10} {loops:<10} {duration:<10}")
    
    print("="*80)
    
    # Overall summary
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    print(f"\nOverall: {passed}/{total} scenarios passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL SCENARIOS PASSED! Vestor is conversing naturally!")
    else:
        print("\n⚠️ Some scenarios need improvement.")
    
    print("\n")


if __name__ == '__main__':
    """Run end-to-end conversation tests"""
    run_all_scenarios()
