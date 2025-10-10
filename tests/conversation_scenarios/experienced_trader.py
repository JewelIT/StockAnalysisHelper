"""
Scenario: Experienced Trader

Mike is 35, has been trading for 5 years, and wants technical analysis
with specific signals.
"""

from .base import ConversationScenario, ConversationSession


class ExperiencedTrader(ConversationScenario):
    """
    Tests technical analysis depth for experienced users
    """
    
    def __init__(self):
        super().__init__(
            name="Experienced Trader - Technical Analysis",
            description="User seeking detailed technical indicators and signals",
            user_persona="Mike (35) - 5 years trading experience",
            tags=['advanced', 'technical', 'indicators', 'stocks']
        )
    
    def run(self) -> ConversationSession:
        self.print_header()
        
        session = ConversationSession(self.name, self.description)
        
        # Direct approach - experienced user
        session.say("Hey, I want to check NVIDIA's technical setup.")
        
        # Get analysis
        session.analyze_stock("NVDA")
        
        # Technical indicator questions
        session.say("What's the RSI looking like?")
        session.check_response(
            question="What's the RSI?",
            expected_keywords=['rsi'],
            should_not_contain=['would you like me to']
        )
        
        session.say("Is NVDA overbought right now?")
        
        session.say("What about the MACD signal?")
        
        session.say("Are we seeing bullish or bearish divergence?")
        
        # Sentiment analysis
        session.say("What's the overall market sentiment on NVDA?")
        
        # Comparison with competitor
        session.say("How does NVDA compare to AMD right now?")
        
        # Analyze competitor
        session.analyze_stock("AMD")
        
        session.say("Between NVDA and AMD, which has better momentum?")
        
        # Risk assessment
        session.say("What's the volatility like on these semiconductor stocks?")
        
        # Entry strategy
        session.say("If I'm looking to enter NVDA, what would be a good price level?")
        
        # Closing
        session.say("Thanks, that's exactly what I needed.")
        
        session.print_summary()
        return session
