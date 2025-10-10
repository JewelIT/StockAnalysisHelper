"""
Base classes for conversation scenarios

To create a new scenario:
1. Create a new file in this directory (e.g., my_scenario.py)
2. Import ConversationScenario
3. Create a class that inherits from ConversationScenario
4. Implement the run() method with your conversation flow
5. The scenario will be automatically discovered and run
"""
import requests
import time
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


BASE_URL = "http://localhost:5000"
CHAT_ENDPOINT = f"{BASE_URL}/chat"
ANALYZE_ENDPOINT = f"{BASE_URL}/analyze"


class ConversationSession:
    """
    Represents a user's conversation session with Vestor
    Tracks messages, context, and provides helper methods
    """
    
    def __init__(self, scenario_name: str, description: str = ""):
        self.scenario_name = scenario_name
        self.description = description
        self.messages = []
        self.context_ticker = None
        self.start_time = time.time()
        self.loop_count = 0
        self.error_count = 0
        
    def say(self, message: str, wait_seconds: float = 1.5, expect_ticker: str = None) -> Dict:
        """
        User sends a message and gets response
        
        Args:
            message: What the user says
            wait_seconds: How long to wait before next message (simulates human typing)
            expect_ticker: Optional ticker you expect to be mentioned
            
        Returns:
            Dict with response data
        """
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
            
            # Check for loops (phrases that redirect back to user)
            loop_phrases = ['would you like me to', 'ask me about', 'i can help you with', 
                          'just ask', 'how can i help', 'want to know more']
            if any(phrase in answer.lower() for phrase in loop_phrases):
                self.loop_count += 1
                print(f"⚠️ LOOP DETECTED in response!")
            
            # Store message
            msg_record = {
                'user': message,
                'vestor': answer,
                'ticker': ticker,
                'timestamp': time.time() - self.start_time,
                'expected_ticker': expect_ticker,
                'has_loop': any(phrase in answer.lower() for phrase in loop_phrases)
            }
            self.messages.append(msg_record)
            
            # Print Vestor's response (truncated for readability)
            max_length = 800
            if len(answer) > max_length:
                print(f"\n🤖 VESTOR: {answer[:max_length]}...")
                print(f"(... {len(answer) - max_length} more characters)")
            else:
                print(f"\n🤖 VESTOR: {answer}")
            
            if ticker:
                print(f"\n📊 Context Ticker: {ticker}")
            
            print()
            
            # Wait before next message (simulate human typing)
            time.sleep(wait_seconds)
            
            return data
            
        except Exception as e:
            self.error_count += 1
            print(f"\n❌ ERROR: {str(e)}\n")
            msg_record = {
                'user': message,
                'vestor': None,
                'error': str(e),
                'timestamp': time.time() - self.start_time
            }
            self.messages.append(msg_record)
            return {'error': str(e)}
    
    def analyze_stock(self, ticker: str, wait_seconds: float = 2.0) -> Dict:
        """
        Request stock analysis
        
        Args:
            ticker: Stock ticker to analyze (e.g., 'AAPL')
            wait_seconds: How long to wait after analysis
            
        Returns:
            Dict with analysis results
        """
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
            time.sleep(wait_seconds)
            
            return data
            
        except Exception as e:
            self.error_count += 1
            print(f"❌ Analysis failed: {str(e)}\n")
            return {'error': str(e)}
    
    def check_response(self, question: str, expected_keywords: List[str], 
                      should_not_contain: List[str] = None) -> bool:
        """
        Check if the last response contains expected content
        
        Args:
            question: The question that was asked (for error reporting)
            expected_keywords: List of keywords that should appear in response
            should_not_contain: List of phrases that should NOT appear
            
        Returns:
            True if response meets expectations, False otherwise
        """
        if not self.messages:
            print(f"⚠️ No messages to check")
            return False
        
        last_msg = self.messages[-1]
        answer = last_msg.get('vestor', '').lower()
        
        if not answer:
            print(f"❌ No answer received for: {question}")
            return False
        
        # Check for expected keywords
        missing_keywords = [kw for kw in expected_keywords if kw.lower() not in answer]
        if missing_keywords:
            print(f"⚠️ Response missing expected keywords: {missing_keywords}")
            return False
        
        # Check for phrases that should not be there
        if should_not_contain:
            unwanted_found = [phrase for phrase in should_not_contain if phrase.lower() in answer]
            if unwanted_found:
                print(f"⚠️ Response contains unwanted phrases: {unwanted_found}")
                return False
        
        return True
    
    def get_stats(self) -> Dict:
        """Get conversation statistics"""
        successful = sum(1 for m in self.messages if m.get('vestor') is not None)
        
        return {
            'total_messages': len(self.messages),
            'successful_responses': successful,
            'errors': self.error_count,
            'loops_detected': self.loop_count,
            'duration_seconds': time.time() - self.start_time,
            'final_ticker': self.context_ticker
        }
    
    def print_summary(self):
        """Print conversation summary"""
        stats = self.get_stats()
        
        print(f"\n\n{'#'*80}")
        print(f"CONVERSATION SUMMARY: {self.scenario_name}")
        print(f"{'#'*80}")
        
        if self.description:
            print(f"Description: {self.description}")
        
        print(f"Duration: {stats['duration_seconds']:.1f} seconds")
        print(f"Messages: {stats['total_messages']}")
        print(f"Successful Responses: {stats['successful_responses']}/{stats['total_messages']}")
        print(f"Errors: {stats['errors']}")
        print(f"Final Context Ticker: {stats['final_ticker']}")
        
        # Check for loops
        if stats['loops_detected'] > 0:
            print(f"⚠️ Loop Responses: {stats['loops_detected']} ❌ FAIL")
        else:
            print(f"✅ Loop Responses: 0 ✅ PASS")
        
        # Overall verdict
        if stats['errors'] == 0 and stats['loops_detected'] == 0:
            print(f"\n🎉 SCENARIO PASSED")
        elif stats['errors'] > 0:
            print(f"\n❌ SCENARIO FAILED (Errors detected)")
        else:
            print(f"\n⚠️ SCENARIO PASSED WITH WARNINGS (Loops detected)")
        
        print(f"{'#'*80}\n\n")


class ConversationScenario(ABC):
    """
    Base class for conversation scenarios
    
    To create a new scenario:
    1. Inherit from this class
    2. Set name and description in __init__
    3. Implement run() method with conversation flow
    
    Example:
        class MyScenario(ConversationScenario):
            def __init__(self):
                super().__init__(
                    name="My Test Scenario",
                    description="Testing specific feature X"
                )
            
            def run(self) -> ConversationSession:
                session = ConversationSession(self.name, self.description)
                session.say("Hello Vestor!")
                session.say("Tell me about stocks")
                return session
    """
    
    def __init__(self, name: str, description: str = "", 
                 user_persona: str = "", tags: List[str] = None):
        """
        Initialize scenario
        
        Args:
            name: Scenario name (e.g., "Complete Beginner")
            description: What this scenario tests
            user_persona: Who the user is (optional, for documentation)
            tags: Tags for filtering scenarios (e.g., ['beginner', 'stocks'])
        """
        self.name = name
        self.description = description
        self.user_persona = user_persona
        self.tags = tags or []
    
    @abstractmethod
    def run(self) -> ConversationSession:
        """
        Run the conversation scenario
        
        Returns:
            ConversationSession with the completed conversation
        """
        pass
    
    def print_header(self):
        """Print scenario header"""
        print("\n" + "="*80)
        print(f"SCENARIO: {self.name}")
        print("="*80)
        if self.description:
            print(f"Description: {self.description}")
        if self.user_persona:
            print(f"User Persona: {self.user_persona}")
        if self.tags:
            print(f"Tags: {', '.join(self.tags)}")
        print("="*80 + "\n")
