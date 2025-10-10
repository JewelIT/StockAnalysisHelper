"""
Scenario: Value Investor

Robert is looking for undervalued stocks with strong fundamentals.
"""

from .base import ConversationScenario, ConversationSession


class ValueInvestor(ConversationScenario):
    """
    Tests fundamental analysis and value investing guidance
    """
    
    def __init__(self):
        super().__init__(
            name="Value Investor - Stock Hunting",
            description="User seeking undervalued stocks with strong fundamentals",
            user_persona="Robert (50) - Value investor, long-term focus",
            tags=['value', 'fundamentals', 'long-term', 'stocks']
        )
    
    def run(self) -> ConversationSession:
        self.print_header()
        
        session = ConversationSession(self.name, self.description)
        
        # Introduction
        session.say("I'm looking for undervalued stocks with strong fundamentals.")
        
        # Strategy discussion
        session.say("What's your approach to identifying value stocks?")
        
        # Valuation metrics
        session.say("Can you explain P/E ratios? What's a good P/E?")
        session.check_response(
            question="Explain P/E ratios",
            expected_keywords=['p/e', 'earnings', 'price'],
            should_not_contain=['would you like me to']
        )
        
        # Specific stock interest - retail
        session.say("I'm interested in Walmart. Is it undervalued?")
        
        session.analyze_stock("WMT")
        
        session.say("What's the sentiment on Walmart?")
        
        # Dividends
        session.say("Does WMT pay dividends?")
        
        # Competitor comparison
        session.say("How does Walmart compare to Costco?")
        
        session.analyze_stock("COST")
        
        session.say("Between WMT and COST, which is better value?")
        
        # Long-term perspective
        session.say("I'm thinking 10-year hold. Which is better for that?")
        
        # Risk assessment
        session.say("What are the risks with retail stocks right now?")
        
        # Final decision
        session.say("I think I'll go with Walmart. What do you think?")
        
        # Closing
        session.say("Great analysis. Thank you!")
        
        session.print_summary()
        return session
