"""
Scenario: Complete Beginner

Sarah is 25, just got her first real job, and wants to start investing.
She knows nothing about stocks or the market.
"""

from .base import ConversationScenario, ConversationSession


class CompleteBeginner(ConversationScenario):
    """
    Tests the experience for a user with zero investment knowledge
    """
    
    def __init__(self):
        super().__init__(
            name="Complete Beginner - First Steps",
            description="User learning about investing from scratch",
            user_persona="Sarah (25) - First job, wants to start investing",
            tags=['beginner', 'educational', 'stocks', 'basics']
        )
    
    def run(self) -> ConversationSession:
        self.print_header()
        
        session = ConversationSession(self.name, self.description)
        
        # Greeting and introduction
        session.say("Hi! I'm Sarah and I'm new to investing.")
        
        # Basic stock education
        session.say("What exactly is a stock?")
        session.check_response(
            question="What exactly is a stock?",
            expected_keywords=['stock', 'company', 'own'],
            should_not_contain=['would you like me to']
        )
        
        session.say("So if I buy Apple stock, I own part of Apple?")
        
        # Understanding returns
        session.say("How do I actually make money from stocks?")
        session.check_response(
            question="How do I make money?",
            expected_keywords=['price', 'dividend'],
            should_not_contain=['ask me about']
        )
        
        session.say("What about dividends? I've heard that term.")
        
        # Getting practical
        session.say("Okay, I want to start. How much money do I need to begin investing?")
        
        session.say("What's the difference between a stock and a cryptocurrency?")
        
        # Investment decision
        session.say("I have $1000 saved. Should I invest all of it?")
        
        session.say("What stocks would you recommend for a beginner like me?")
        
        # Specific stock interest
        session.say("Tell me about Apple. Is it good for beginners?")
        
        # Get detailed analysis
        session.analyze_stock("AAPL")
        
        # Follow up on analysis
        session.say("Should I buy Apple stock now?")
        
        # Risk management
        session.say("What if the price goes down after I buy it?")
        
        # Closing
        session.say("Thank you! This was really helpful. I feel more confident now.")
        
        session.print_summary()
        return session
