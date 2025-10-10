"""
Scenario: Market Overview

Lisa checks in every morning for a market overview and sector analysis.
"""

from .base import ConversationScenario, ConversationSession


class MarketOverview(ConversationScenario):
    """
    Tests sector analysis and market overview capabilities
    """
    
    def __init__(self):
        super().__init__(
            name="Market Overview - Daily Briefing",
            description="User wants market overview and sector performance",
            user_persona="Lisa (40) - Daily market check-in routine",
            tags=['market', 'sectors', 'diversification', 'overview']
        )
    
    def run(self) -> ConversationSession:
        self.print_header()
        
        session = ConversationSession(self.name, self.description)
        
        # Morning briefing
        session.say("Good morning! What's happening in the market today?")
        
        # Sector performance
        session.say("Which sectors are performing well?")
        
        # Sector deep dive
        session.say("Tell me about the technology sector.")
        session.check_response(
            question="Tell me about tech sector",
            expected_keywords=['technology', 'tech'],
            should_not_contain=['would you like me to']
        )
        
        session.say("What about consumer staples? Are they defensive right now?")
        
        # Healthcare interest
        session.say("I'm interested in healthcare stocks. Any recommendations?")
        
        # Specific stock
        session.say("What about Johnson & Johnson?")
        
        session.analyze_stock("JNJ")
        
        session.say("Is JNJ a good long-term hold?")
        
        # Diversification question
        session.say("I already own tech stocks. Should I diversify into healthcare?")
        
        # Risk management
        session.say("With the current market volatility, what should I do?")
        
        # Financial sector
        session.say("What's happening with financial stocks like JPMorgan?")
        
        session.analyze_stock("JPM")
        
        session.say("Are banks a good play right now?")
        
        # Closing
        session.say("Thanks for the briefing. I'll check back tomorrow!")
        
        session.print_summary()
        return session
