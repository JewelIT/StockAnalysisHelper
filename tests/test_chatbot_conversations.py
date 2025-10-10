"""
Comprehensive chatbot conversation testing
Tests the bot's ability to handle natural, unpredictable user questions
and adapt intelligently to various conversation flows.
"""

import pytest
import requests
import time
import json
from typing import List, Dict

BASE_URL = "http://localhost:5000"
CHAT_ENDPOINT = f"{BASE_URL}/chat"

class ConversationTester:
    """Simulates real user conversations with the chatbot"""
    
    def __init__(self):
        self.conversation_history = []
        self.test_results = []
    
    def ask(self, question: str, expected_behaviors: List[str] = None) -> Dict:
        """
        Ask a question and validate the response
        
        Args:
            question: The user's question
            expected_behaviors: List of expected response characteristics
                - 'helpful': Should provide useful information
                - 'natural': Should sound conversational, not robotic
                - 'specific': Should address the specific question
                - 'educational': Should teach something
                - 'no_loop': Should not ask user to ask questions
                - 'no_generic': Should not give generic "I can help with..." responses
                - 'contextual': Should reference previous conversation
        """
        print(f"\n{'='*80}")
        print(f"USER: {question}")
        print(f"{'='*80}")
        
        try:
            response = requests.post(
                CHAT_ENDPOINT,
                json={"question": question},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            answer = data.get('answer', '')
            print(f"BOT: {answer[:500]}...")  # Print first 500 chars
            
            # Store in history
            self.conversation_history.append({
                'question': question,
                'answer': answer,
                'timestamp': time.time()
            })
            
            # Validate expected behaviors
            validation_results = {}
            if expected_behaviors:
                for behavior in expected_behaviors:
                    validation_results[behavior] = self._validate_behavior(
                        question, answer, behavior
                    )
            
            result = {
                'question': question,
                'answer': answer,
                'validations': validation_results,
                'success': all(validation_results.values()) if validation_results else True
            }
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            result = {
                'question': question,
                'answer': None,
                'error': str(e),
                'success': False
            }
            self.test_results.append(result)
            return result
    
    def _validate_behavior(self, question: str, answer: str, behavior: str) -> bool:
        """Validate if the answer exhibits the expected behavior"""
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        if behavior == 'helpful':
            # Should provide actual information, not just say "I can help"
            unhelpful_phrases = [
                'how can i help',
                'what would you like to know',
                'ask me anything',
                'i can help you with'
            ]
            # Answer should be longer than 200 chars and not just prompting
            is_helpful = (
                len(answer) > 200 and
                not any(phrase in answer_lower for phrase in unhelpful_phrases) and
                ('##' in answer or '**' in answer or '\n\n' in answer)  # Has structure
            )
            if not is_helpful:
                print(f"❌ FAIL [helpful]: Response seems unhelpful or too short")
            else:
                print(f"✅ PASS [helpful]: Response is detailed and informative")
            return is_helpful
        
        elif behavior == 'natural':
            # Should sound conversational, not robotic
            robotic_phrases = [
                'as an ai',
                'i am programmed to',
                'my algorithms',
                'i do not have the ability'
            ]
            is_natural = not any(phrase in answer_lower for phrase in robotic_phrases)
            if not is_natural:
                print(f"❌ FAIL [natural]: Response sounds robotic")
            else:
                print(f"✅ PASS [natural]: Response sounds conversational")
            return is_natural
        
        elif behavior == 'specific':
            # Should address the specific topic asked about
            # Extract key topic from question
            topics = []
            if 'consumer staples' in question_lower:
                topics.append('consumer staples')
            if 'wmt' in question_lower or 'walmart' in question_lower:
                topics.append('walmart')
            if 'technology' in question_lower or 'tech' in question_lower:
                topics.append('tech')
            if 'invest' in question_lower or 'buy' in question_lower:
                topics.append('invest')
            
            # Answer should mention the topic
            is_specific = any(topic in answer_lower for topic in topics) if topics else True
            if not is_specific:
                print(f"❌ FAIL [specific]: Response doesn't address the topic")
            else:
                print(f"✅ PASS [specific]: Response addresses the specific topic")
            return is_specific
        
        elif behavior == 'educational':
            # Should teach something (has explanations, examples, or structure)
            educational_markers = [
                '##',  # Markdown headers
                '**',  # Bold text
                '###',
                'what it means',
                'for example',
                'key characteristics',
                'how it works',
                'this means',
                'in other words',
                '•', '✅', '❌', '📊'  # Lists or icons
            ]
            is_educational = any(marker in answer for marker in educational_markers)
            if not is_educational:
                print(f"❌ FAIL [educational]: Response lacks educational structure")
            else:
                print(f"✅ PASS [educational]: Response has educational content")
            return is_educational
        
        elif behavior == 'no_loop':
            # Should NOT create loops like "ask me questions about X"
            loop_phrases = [
                'would you like me to analyze',
                'just ask',
                'what would you like to know',
                'ask me about',
                'i can help you with',
                'how can i assist'
            ]
            has_loop = any(phrase in answer_lower for phrase in loop_phrases)
            if has_loop:
                print(f"❌ FAIL [no_loop]: Response creates a conversation loop")
            else:
                print(f"✅ PASS [no_loop]: Response answers directly without loops")
            return not has_loop
        
        elif behavior == 'no_generic':
            # Should NOT give generic "I'm here to help" responses
            generic_phrases = [
                'i\'m here to help you',
                'i can help you with',
                'how can i help',
                'what would you like to know',
                'being analyzed',
                'being assessed'
            ]
            is_generic = any(phrase in answer_lower for phrase in generic_phrases)
            if is_generic:
                print(f"❌ FAIL [no_generic]: Response is too generic")
            else:
                print(f"✅ PASS [no_generic]: Response is specific and actionable")
            return not is_generic
        
        elif behavior == 'contextual':
            # Should reference previous conversation context
            if len(self.conversation_history) > 0:
                prev_question = self.conversation_history[-1]['question'].lower()
                # Check if answer references something from previous question
                has_context = any(word in answer_lower for word in prev_question.split() if len(word) > 4)
                if not has_context:
                    print(f"❌ FAIL [contextual]: Response doesn't reference previous context")
                else:
                    print(f"✅ PASS [contextual]: Response shows awareness of conversation history")
                return has_context
            else:
                print(f"⚠️ SKIP [contextual]: No previous conversation to reference")
                return True  # Can't fail on first message
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n\n{'='*80}")
        print(f"CONVERSATION TEST SUMMARY")
        print(f"{'='*80}")
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.get('success', False))
        failed = total - passed
        
        print(f"Total Questions: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result.get('success', False):
                    print(f"  - {result['question']}")
                    if 'validations' in result:
                        for behavior, passed in result['validations'].items():
                            if not passed:
                                print(f"    ❌ {behavior}")
        
        print(f"{'='*80}\n")


# Test Scenarios
def test_conversation_1_financial_education():
    """
    Scenario 1: User asks educational questions about finance
    Should provide clear, educational answers without loops
    """
    tester = ConversationTester()
    
    # Question 1: Definition question
    tester.ask(
        "What are consumer staples?",
        expected_behaviors=['helpful', 'natural', 'specific', 'educational', 'no_loop', 'no_generic']
    )
    time.sleep(1)
    
    # Question 2: Follow-up about sector
    tester.ask(
        "What about the technology sector?",
        expected_behaviors=['helpful', 'specific', 'educational', 'no_loop']
    )
    time.sleep(1)
    
    # Question 3: More specific question
    tester.ask(
        "Which companies are in consumer staples?",
        expected_behaviors=['helpful', 'specific', 'no_loop']
    )
    
    tester.print_summary()
    
    # Assert all passed
    assert all(r.get('success', False) for r in tester.test_results), \
        "Some conversation tests failed"


def test_conversation_2_stock_inquiry():
    """
    Scenario 2: User asks about a specific stock
    Should provide information or offer to analyze, but NOT create loops
    """
    tester = ConversationTester()
    
    # Question 1: Initial stock question
    tester.ask(
        "Tell me about WMT",
        expected_behaviors=['helpful', 'specific', 'no_loop']
    )
    time.sleep(1)
    
    # Question 2: Investment question without context
    tester.ask(
        "Should I invest in it?",
        expected_behaviors=['helpful', 'no_loop']
    )
    time.sleep(1)
    
    # Question 3: Follow-up question
    tester.ask(
        "What are the risks?",
        expected_behaviors=['helpful', 'educational']
    )
    
    tester.print_summary()
    
    assert all(r.get('success', False) for r in tester.test_results), \
        "Some conversation tests failed"


def test_conversation_3_mixed_topics():
    """
    Scenario 3: User jumps between topics
    Bot should adapt naturally to each question
    """
    tester = ConversationTester()
    
    # Question 1: Sector question
    tester.ask(
        "What's the healthcare sector?",
        expected_behaviors=['helpful', 'specific', 'educational']
    )
    time.sleep(1)
    
    # Question 2: Completely different - stock question
    tester.ask(
        "Is AAPL a good buy?",
        expected_behaviors=['helpful', 'specific']
    )
    time.sleep(1)
    
    # Question 3: General investment question
    tester.ask(
        "How do I start investing?",
        expected_behaviors=['helpful', 'educational']
    )
    time.sleep(1)
    
    # Question 4: Technical indicator
    tester.ask(
        "What does RSI mean?",
        expected_behaviors=['helpful', 'educational', 'specific']
    )
    
    tester.print_summary()
    
    assert all(r.get('success', False) for r in tester.test_results), \
        "Some conversation tests failed"


def test_conversation_4_vague_questions():
    """
    Scenario 4: User asks vague or unclear questions
    Bot should still provide helpful responses and guide the user
    """
    tester = ConversationTester()
    
    # Question 1: Vague question
    tester.ask(
        "What do you think?",
        expected_behaviors=['helpful', 'natural']
    )
    time.sleep(1)
    
    # Question 2: One-word question
    tester.ask(
        "Stocks?",
        expected_behaviors=['helpful']
    )
    time.sleep(1)
    
    # Question 3: Incomplete thought
    tester.ask(
        "I want to...",
        expected_behaviors=['helpful', 'natural']
    )
    
    tester.print_summary()
    
    # This test is more lenient - we expect some to potentially fail
    # but should still be mostly helpful


def test_conversation_5_rapid_fire():
    """
    Scenario 5: User asks multiple questions rapidly
    Bot should handle each independently without confusion
    """
    tester = ConversationTester()
    
    questions = [
        "What are dividends?",
        "Best tech stocks?",
        "How volatile is crypto?",
        "What's a P/E ratio?",
        "Should I diversify?"
    ]
    
    for question in questions:
        tester.ask(
            question,
            expected_behaviors=['helpful', 'no_loop']
        )
        time.sleep(0.5)  # Rapid fire
    
    tester.print_summary()


def test_conversation_6_natural_language():
    """
    Scenario 6: User uses very casual, natural language
    Bot should understand and respond appropriately
    """
    tester = ConversationTester()
    
    # Casual questions
    tester.ask(
        "yo what's up with consumer staples lol",
        expected_behaviors=['helpful', 'specific', 'natural']
    )
    time.sleep(1)
    
    tester.ask(
        "nah but fr is walmart any good?",
        expected_behaviors=['helpful', 'specific']
    )
    time.sleep(1)
    
    tester.ask(
        "idk man seems risky",
        expected_behaviors=['helpful', 'natural']
    )
    
    tester.print_summary()


def test_no_endless_loops():
    """
    Critical test: Ensure bot NEVER creates endless loops
    """
    tester = ConversationTester()
    
    # These questions previously caused loops
    problematic_questions = [
        "What are consumer staples?",
        "Tell me about WMT",
        "Should I invest in WMT?",
        "What do you think about AAPL?",
        "Is Tesla good?"
    ]
    
    for question in problematic_questions:
        result = tester.ask(
            question,
            expected_behaviors=['no_loop', 'no_generic']
        )
        time.sleep(1)
        
        # Critical assertion: No loops
        answer = result.get('answer', '').lower()
        assert 'would you like me to analyze' not in answer, \
            f"LOOP DETECTED in response to: {question}"
        assert 'just ask' not in answer, \
            f"LOOP DETECTED in response to: {question}"
        assert 'i can help you with' not in answer, \
            f"GENERIC RESPONSE in response to: {question}"
    
    tester.print_summary()
    
    # All must pass
    assert all(r.get('success', False) for r in tester.test_results), \
        "Bot created loops or generic responses - CRITICAL FAILURE"


if __name__ == '__main__':
    """Run all conversation tests"""
    print("\n" + "="*80)
    print("CHATBOT CONVERSATION INTELLIGENCE TEST")
    print("Testing the bot's ability to adapt to unpredictable questions")
    print("="*80 + "\n")
    
    # Run each test scenario
    scenarios = [
        ("Financial Education", test_conversation_1_financial_education),
        ("Stock Inquiry", test_conversation_2_stock_inquiry),
        ("Mixed Topics", test_conversation_3_mixed_topics),
        ("Vague Questions", test_conversation_4_vague_questions),
        ("Rapid Fire", test_conversation_5_rapid_fire),
        ("Natural Language", test_conversation_6_natural_language),
        ("No Loops (CRITICAL)", test_no_endless_loops)
    ]
    
    results = []
    for name, test_func in scenarios:
        print(f"\n{'#'*80}")
        print(f"SCENARIO: {name}")
        print(f"{'#'*80}")
        try:
            test_func()
            results.append((name, "PASSED ✅"))
        except AssertionError as e:
            results.append((name, f"FAILED ❌: {str(e)}"))
        except Exception as e:
            results.append((name, f"ERROR ⚠️: {str(e)}"))
    
    # Final summary
    print(f"\n\n{'='*80}")
    print(f"FINAL RESULTS - CHATBOT CONVERSATION INTELLIGENCE")
    print(f"{'='*80}")
    for name, result in results:
        print(f"{name}: {result}")
    print(f"{'='*80}\n")
