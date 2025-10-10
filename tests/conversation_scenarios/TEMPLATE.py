"""
TEMPLATE for creating new conversation scenarios

Copy this file and rename it (e.g., my_scenario.py)
Fill in your conversation flow and it will be automatically discovered!
"""

from .base import ConversationScenario, ConversationSession


class TemplateScenario(ConversationScenario):
    """
    Brief description of what this scenario tests
    """
    
    def __init__(self):
        super().__init__(
            name="Your Scenario Name Here",
            description="What specific behavior or feature this tests",
            user_persona="Brief description of the user (optional)",
            tags=['beginner', 'stocks']  # Tags for filtering
        )
    
    def run(self) -> ConversationSession:
        """
        Implement your conversation flow here
        """
        # Print scenario header
        self.print_header()
        
        # Create session
        session = ConversationSession(self.name, self.description)
        
        # ============================================================
        # Your conversation flow starts here
        # ============================================================
        
        # 1. User says something
        session.say("Your first question or statement")
        
        # Optional: Check if response is good
        # session.check_response(
        #     question="Your first question",
        #     expected_keywords=['keyword1', 'keyword2'],
        #     should_not_contain=['would you like me to']
        # )
        
        # 2. Continue the conversation
        session.say("Follow-up question")
        
        # 3. Request stock analysis if needed
        # session.analyze_stock("AAPL")
        
        # 4. Ask about the analyzed stock
        # session.say("Should I buy Apple?")
        
        # 5. More follow-ups...
        session.say("Another question")
        
        # ============================================================
        # Conversation flow ends here
        # ============================================================
        
        # Print summary (automatically shows stats and pass/fail)
        session.print_summary()
        
        return session


# ============================================================
# EXAMPLE SCENARIOS - Delete these and create your own!
# ============================================================

class QuickSmokeTest(ConversationScenario):
    """
    Quick test to verify basic functionality
    Use this as a starting point for new scenarios
    """
    
    def __init__(self):
        super().__init__(
            name="Quick Smoke Test",
            description="Verifies basic greeting and educational question",
            tags=['quick', 'smoke']
        )
    
    def run(self) -> ConversationSession:
        self.print_header()
        
        session = ConversationSession(self.name, self.description)
        
        # Test greeting
        session.say("Hi!")
        
        # Test educational question
        session.say("What are consumer staples?")
        session.check_response(
            question="What are consumer staples?",
            expected_keywords=['consumer staples', 'products'],
            should_not_contain=['would you like me to', 'ask me about']
        )
        
        # Test stock question
        session.say("Tell me about Apple")
        
        session.print_summary()
        return session


class EdgeCaseTest(ConversationScenario):
    """
    Tests edge cases and unusual inputs
    """
    
    def __init__(self):
        super().__init__(
            name="Edge Case Test",
            description="Tests unusual inputs and edge cases",
            tags=['edge-case', 'robustness']
        )
    
    def run(self) -> ConversationSession:
        self.print_header()
        
        session = ConversationSession(self.name, self.description)
        
        # Very short question
        session.say("Hi")
        
        # One word
        session.say("Stocks?")
        
        # Vague question
        session.say("What do you think?")
        
        # Question with typos
        session.say("Whats the bst invesment?")
        
        # Empty-ish question
        session.say("...")
        
        session.print_summary()
        return session
