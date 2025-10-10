"""
Scenario: Crypto Explorer

Emma is curious about cryptocurrency but doesn't understand it.
She's heard stories of huge gains and losses.
"""

from .base import ConversationScenario, ConversationSession


class CryptoExplorer(ConversationScenario):
    """
    Tests cryptocurrency education and risk guidance
    """
    
    def __init__(self):
        super().__init__(
            name="Crypto Explorer - Digital Assets",
            description="User learning about cryptocurrency and its risks",
            user_persona="Emma (28) - Curious about crypto but cautious",
            tags=['crypto', 'beginner', 'risk', 'education']
        )
    
    def run(self) -> ConversationSession:
        self.print_header()
        
        session = ConversationSession(self.name, self.description)
        
        # Opening - crypto curiosity
        session.say("Hi, I want to learn about cryptocurrency.")
        
        # Basic understanding
        session.say("What's the difference between Bitcoin and regular stocks?")
        session.check_response(
            question="Difference between Bitcoin and stocks",
            expected_keywords=['crypto', 'bitcoin', 'stock'],
            should_not_contain=['would you like me to']
        )
        
        session.say("Why is crypto so volatile?")
        
        # Specific crypto interest
        session.say("Should I invest in Bitcoin?")
        
        session.analyze_stock("BTC-USD")
        
        session.say("What's Bitcoin's price right now?")
        
        # Affordability concern
        session.say("Is Bitcoin too expensive for me to buy?")
        
        # Risk assessment
        session.say("How much should I invest in crypto?")
        
        # Altcoins
        session.say("What about Ethereum? Is it better than Bitcoin?")
        
        session.analyze_stock("ETH-USD")
        
        session.say("Between Bitcoin and Ethereum, which is safer?")
        
        # Risk concerns
        session.say("I heard people lose all their money in crypto. Is it really that risky?")
        
        # Protection
        session.say("How do I protect myself from losing everything?")
        
        # Portfolio strategy
        session.say("Should I have both crypto and stocks in my portfolio?")
        
        # Final decision
        session.say("Okay, I think I'll start small with Bitcoin. Good idea?")
        
        # Closing
        session.say("Thanks for making crypto less scary!")
        
        session.print_summary()
        return session
