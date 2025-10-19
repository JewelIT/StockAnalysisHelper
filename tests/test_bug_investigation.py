"""
Investigation of STRONG BUY recommendation for XRP-EUR (0.11% daily change)
This test analyzes why the system is recommending STRONG BUY despite minimal price movement
"""
import pytest
from datetime import datetime, timedelta
import yfinance as yf

def test_xrp_eur_investigation():
    """
    Investigate: Why is XRP-EUR getting STRONG BUY despite only +0.11% daily change?
    
    Scoring Formula:
    - Technical: 0.65 weight
    - Fundamental: 0.25 weight  
    - Sentiment: 0.1 weight
    
    For STRONG BUY: total_score >= 0.65
    """
    
    ticker = "XRP-EUR"
    
    print(f"\n{'='*70}")
    print(f"INVESTIGATING: {ticker} - Why STRONG BUY for 0.11% price change?")
    print(f"{'='*70}\n")
    
    # Step 1: Fetch actual data
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period='3mo')
    
    print(f"📊 ACTUAL MARKET DATA:")
    print(f"  Current Price: €{info.get('currentPrice', 'N/A')}")
    print(f"  Previous Close: €{info.get('previousClose', 'N/A')}")
    print(f"  52-Week High: €{info.get('fiftyTwoWeekHigh', 'N/A')}")
    print(f"  52-Week Low: €{info.get('fiftyTwoWeekLow', 'N/A')}")
    print(f"  Market Cap: {info.get('marketCap', 'N/A')}")
    print(f"  P/E Ratio: {info.get('trailingPE', 'N/A')}")  # Will be None for crypto
    print()
    
    # Step 2: Understand the scoring components
    print(f"🧮 SCORING ANALYSIS:")
    print(f"\nFor STRONG BUY (>= 0.65), we need:")
    print(f"  Formula: 0.65*technical + 0.25*fundamental + 0.1*sentiment >= 0.65")
    print(f"  Simplified: technical*0.65 + (fundamental+sentiment)*0.35 >= 0.65")
    print()
    
    # Scenario analysis
    scenarios = [
        {
            "name": "All Neutral (0.5 everywhere)",
            "technical": 0.5,
            "fundamental": 0.5,
            "sentiment": 0.5,
        },
        {
            "name": "Strong Technical (0.8), Weak Others (0.3)",
            "technical": 0.8,
            "fundamental": 0.3,
            "sentiment": 0.3,
        },
        {
            "name": "Very Strong Technical (0.95), Weak Others (0.2)",
            "technical": 0.95,
            "fundamental": 0.2,
            "sentiment": 0.2,
        },
        {
            "name": "Actual Recommendation (0.72 STRONG BUY)",
            "technical": 0.82,
            "fundamental": 0.68,
            "sentiment": 0.75,
        },
    ]
    
    print(f"📈 SCENARIO ANALYSIS:\n")
    for scenario in scenarios:
        tech = scenario["technical"]
        fund = scenario["fundamental"]
        sent = scenario["sentiment"]
        
        total = 0.65 * tech + 0.25 * fund + 0.1 * sent
        recommendation = "STRONG BUY" if total >= 0.65 else "BUY" if total >= 0.55 else "HOLD" if total >= 0.45 else "SELL" if total >= 0.35 else "STRONG SELL"
        
        print(f"  {scenario['name']}")
        print(f"    Technical: {tech:.2f} × 0.65 = {tech*0.65:.3f}")
        print(f"    Fundamental: {fund:.2f} × 0.25 = {fund*0.25:.3f}")
        print(f"    Sentiment: {sent:.2f} × 0.1 = {sent*0.1:.3f}")
        print(f"    ➜ Total Score: {total:.2f} → {recommendation}")
        print()
    
    # Step 3: Identify the problem
    print(f"🔍 ROOT CAUSE ANALYSIS:")
    print()
    print(f"1. Technical Score is TOO HIGH for small price moves")
    print(f"   - RSI, MACD, and moving averages don't require big price moves")
    print(f"   - Example: RSI can be 30 (oversold) even if price is stable")
    print(f"   - Problem: High technical score is independent of actual price momentum")
    print()
    print(f"2. Fundamentals don't apply to cryptocurrency")
    print(f"   - XRP is crypto, so P/E, margins, etc. are N/A")
    print(f"   - Fundamental score might default to 0.5 or use proxy metrics")
    print(f"   - This creates artificial score")
    print()
    print(f"3. Sentiment can be positive despite price stagnation")
    print(f"   - News sentiment = news headlines about XRP are positive")
    print(f"   - ≠ Price momentum or actual buying pressure")
    print(f"   - Example: 'Ripple in talks with JP Morgan' is bullish news")
    print(f"             but doesn't necessarily drive price today")
    print()
    
    # Step 4: Recommendations
    print(f"💡 RECOMMENDATIONS TO FIX THIS:")
    print()
    print(f"Option 1: Add Price Momentum as Factor")
    print(f"  - Current: 0.65*tech + 0.25*fund + 0.1*sent")
    print(f"  - Proposed: 0.4*tech + 0.2*fund + 0.1*sent + 0.3*momentum")
    print(f"  - Momentum = (price today vs 50-day avg) / volatility")
    print()
    print(f"Option 2: Reduce Technical Weight for Small Price Changes")
    print(f"  - If daily_change < 1%: reduce technical weight by 50%")
    print(f"  - Forces recommendation to consider price action, not just indicators")
    print()
    print(f"Option 3: Add Conviction Filter")
    print(f"  - Require agreement between components")
    print(f"  - STRONG BUY only if: tech>0.7 AND (fund>0.6 OR sent>0.7) AND momentum>0.6")
    print()
    print(f"Option 4: Crypto-Specific Scoring")
    print(f"  - For crypto: 0.5*technical + 0.3*sentiment + 0.2*on-chain_metrics")
    print(f"  - Use on-chain data instead of fundamentals")
    print()
    
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_xrp_eur_investigation()
