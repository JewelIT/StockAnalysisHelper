"""
Natural response generator for chatbot
Handles questions without analysis data
CRITICAL: NO LOOPS - Answer questions directly, don't ask user to ask more questions
"""

def generate_smart_response(question: str, ticker: str = None) -> str:
    """
    Generate intelligent, natural responses based on question type
    This method is smart enough to adapt to ANY user question
    """
    question_lower = question.lower()
    ticker_str = ticker.upper() if ticker else None
    
    # Don't treat technical indicators as tickers
    technical_terms = ['rsi', 'macd', 'p/e', 'pe', 'ema', 'sma', 'eps', 'roe', 'roa']
    if ticker_str and ticker_str.lower() in technical_terms:
        ticker_str = None
    
    # 1. SECTOR EDUCATION QUESTIONS
    if 'consumer staples' in question_lower:
        return """## 🛒 Consumer Staples Sector

**Consumer Staples** are essential products people buy regularly regardless of economic conditions - groceries, household items, personal care products.

### What's Included:
- 🥫 **Food & Beverages**: Grocery items, snacks, drinks (Coca-Cola, PepsiCo)
- 🏠 **Household Products**: Cleaning supplies, paper goods (Procter & Gamble)
- 🛒 **Retail**: Walmart, Costco, CVS
- 💊 **Personal Care**: Shampoo, soap, cosmetics

### Why Investors Like Them:
✅ **Recession-Resistant**: People still buy groceries during downturns
✅ **Stable Revenue**: Predictable demand creates steady cash flow
✅ **Dividend Payers**: Many offer reliable 2-4% dividend yields
✅ **Low Volatility**: Safer than tech stocks, less dramatic price swings

### Investment Perspective:
**Defensive Play**: Perfect for conservative portfolios or during market uncertainty. You won't get explosive growth, but you won't see dramatic crashes either. Think "boring but reliable."

### Famous Examples:
- **WMT** (Walmart) - World's largest retailer
- **PG** (Procter & Gamble) - Gillette, Tide, Pampers
- **KO** (Coca-Cola) - Global beverage giant
- **PEP** (PepsiCo) - Snacks and beverages
- **COST** (Costco) - Warehouse club with loyal customers"""
    
    if 'technology' in question_lower or 'tech sector' in question_lower:
        return """## 💻 Technology Sector

The **Technology Sector** includes companies that develop hardware, software, internet services, and semiconductors.

### Major Categories:
- 📱 **Hardware**: Apple (iPhone), Dell, HP
- 💾 **Software**: Microsoft (Windows, Office), Oracle, Adobe
- 🌐 **Internet Giants**: Google, Meta, Amazon
- 🔌 **Semiconductors**: NVIDIA (AI chips), AMD, Intel
- ☁️ **Cloud Services**: AWS, Azure, Google Cloud

### Investment Characteristics:
🚀 **High Growth**: Innovation creates rapid revenue expansion
⚡ **High Volatility**: Can swing 20-30% in months
💰 **Premium Valuations**: Often trade at 25-50+ P/E ratios
📈 **Market Dominance**: Top 5 tech stocks = 25% of S&P 500

### Risk vs Reward:
**Aggressive Growth**: High potential returns but significant risk. Great for long-term investors who can handle volatility. During bull markets, tech leads. During bear markets, tech often falls hardest.

### Popular Picks:
- **AAPL** (Apple) - iPhone, services ecosystem
- **MSFT** (Microsoft) - Cloud, software, AI
- **GOOGL** (Google) - Search, ads, cloud
- **NVDA** (NVIDIA) - AI chip leader
- **META** (Meta) - Social media, ads"""
    
    if 'healthcare' in question_lower or 'health care' in question_lower:
        return """## ⚕️ Healthcare Sector

The **Healthcare Sector** covers pharmaceuticals, biotechnology, medical devices, and healthcare services.

### Sub-Sectors:
- 💊 **Big Pharma**: Pfizer, Johnson & Johnson, Merck (established drugs)
- 🧬 **Biotechnology**: Moderna, Amgen (cutting-edge treatments)
- 🏥 **Healthcare Services**: UnitedHealth, CVS (insurance, pharmacies)
- 🔬 **Medical Devices**: Medtronic, Abbott Labs (equipment, diagnostics)

### Why Healthcare?
🛡️ **Defensive**: People need medicine in any economy
💰 **Stable Cash Flows**: Recurring revenue from prescriptions
🧪 **Innovation Potential**: Breakthrough drugs = huge profits
⚖️ **Regulated**: FDA approvals provide moats

### Investment Approach:
**Balanced Strategy**: Big pharma offers stability and dividends. Biotech offers explosive growth (but high risk). Good sector for diversification.

### Key Players:
- **JNJ** (Johnson & Johnson) - Diversified healthcare giant
- **UNH** (UnitedHealth) - Health insurance leader
- **PFE** (Pfizer) - Major pharmaceutical company
- **MRNA** (Moderna) - mRNA vaccine technology"""
    
    if 'financials' in question_lower or 'financial sector' in question_lower:
        return """## 🏦 Financial Sector

The **Financial Sector** includes banks, investment firms, insurance companies, and payment processors.

### Categories:
- 🏦 **Banks**: JPMorgan, Bank of America (lending, deposits)
- 💼 **Investment Banks**: Goldman Sachs, Morgan Stanley (trading, M&A)
- 🛡️ **Insurance**: Berkshire Hathaway, MetLife
- 💳 **Payments**: Visa, Mastercard (transaction networks)

### Key Factors:
📊 **Interest Rate Sensitive**: Higher rates = higher profits (usually)
📉 **Economic Cycle**: Thrive in booms, suffer in recessions
💸 **Dividend Income**: Many banks pay 3-5% yields
⚖️ **Regulated**: Government oversight limits risk-taking

### Investment View:
**Cyclical Play**: Performance tied to economy. Good when rates are rising and economy is strong. Risky during recessions or financial crises.

### Top Names:
- **JPM** (JPMorgan Chase) - Largest US bank
- **BAC** (Bank of America) - Major retail bank
- **GS** (Goldman Sachs) - Premier investment bank
- **V** (Visa) - Payment network (not a bank!)"""
    
    # 2. TECHNICAL INDICATOR EXPLANATIONS
    if 'rsi' in question_lower or 'relative strength' in question_lower:
        return """## 📊 RSI (Relative Strength Index)

**RSI** is a momentum indicator that measures if a stock is **overbought** or **oversold** on a scale of 0-100.

### How to Read It:
- **Above 70**: 🔴 **Overbought** - Stock may have risen too fast, potential pullback
- **Below 30**: 🟢 **Oversold** - Stock may have fallen too much, potential bounce
- **30-70**: ⚪ **Neutral** - No extreme signals

### What It Means:
RSI doesn't predict the future, but shows **momentum exhaustion**. If RSI is 85, it doesn't mean "sell now!" - it means "be cautious, the rally might pause."

### Real Example:
Imagine a stock rockets from $100 to $150 in 2 weeks. RSI hits 82 (overbought). This suggests:
- Short-term traders might take profits
- Stock could consolidate or dip before continuing
- BUT in strong bull markets, stocks can stay overbought for weeks

### Pro Tips:
✅ **Combine with other indicators** - Don't use RSI alone
✅ **Watch for divergence** - Price makes new high, RSI doesn't = warning
✅ **Adjust timeframe** - 14-day RSI is standard, but you can use 7 or 21 days

### The Math (Optional):
RSI = 100 - [100 / (1 + RS)]  
where RS = Average Gain / Average Loss over 14 periods

**Bottom Line**: RSI helps identify extreme momentum, but markets can stay overbought/oversold longer than you'd expect."""
    
    if 'macd' in question_lower:
        return """## 📈 MACD (Moving Average Convergence Divergence)

**MACD** is a trend-following indicator that shows the relationship between two moving averages.

### Components:
1. **MACD Line**: 12-day EMA minus 26-day EMA
2. **Signal Line**: 9-day EMA of the MACD line
3. **Histogram**: Difference between MACD and Signal lines

### How to Use It:
**🟢 Bullish Signal**: MACD crosses above Signal line → Potential uptrend starting  
**🔴 Bearish Signal**: MACD crosses below Signal line → Potential downtrend starting  
**📊 Histogram**: Bigger bars = stronger momentum

### What It Tells You:
- **Trend Direction**: Is momentum bullish or bearish?
- **Trend Strength**: How strong is the trend?
- **Potential Reversals**: When lines cross

### Real Example:
Stock is falling, MACD is negative. Then MACD crosses above Signal line → Early sign downtrend might be ending. Time to watch for entry.

### Common Mistakes:
❌ **False Signals**: MACD can whipsaw in sideways markets
❌ **Lagging**: It's based on past prices, not predictive
✅ **Best Use**: Confirming trends, not catching exact tops/bottoms

**Bottom Line**: MACD is great for identifying trend changes and momentum shifts, but use it with price action and other indicators."""
    
    if 'p/e' in question_lower or 'pe ratio' in question_lower or 'price to earnings' in question_lower:
        return """## 💰 P/E Ratio (Price-to-Earnings)

**P/E Ratio** tells you how much investors are willing to pay for $1 of a company's earnings.

### The Formula:
**P/E = Stock Price / Earnings Per Share (EPS)**

### Example:
- Stock trading at $100
- Company earns $5 per share
- P/E = 100 / 5 = **20x**

This means: You're paying $20 for every $1 of annual profit.

### What's a "Good" P/E?
- **Low P/E (5-15)**: 🏦 Value stocks, banks, mature companies
- **Medium P/E (15-25)**: 📊 S&P 500 average (~18-20)
- **High P/E (25-50+)**: 🚀 Growth stocks, tech companies
- **No P/E (negative)**: 🔴 Company is losing money

### Interpretation:
**High P/E**: Market expects strong future growth (or stock is overvalued)  
**Low P/E**: Market expects slow growth (or stock is undervalued)

### Real Examples:
- **NVDA** (NVIDIA): P/E ~65 → Investors bet on AI growth
- **JPM** (JPMorgan): P/E ~12 → Stable bank, lower growth expectations
- **TSLA** (Tesla): P/E ~45-80 → Priced for future potential

### Limitations:
❌ **Doesn't work for negative earnings** (unprofitable companies)
❌ **Can be manipulated** by accounting tricks
❌ **Ignores growth rate** (use PEG ratio for that)

**Bottom Line**: P/E is a quick valuation check. Compare it to sector averages and company's own history, not absolute numbers."""
    
    if 'dividend' in question_lower:
        return """## 💵 Dividends Explained

**Dividends** are cash payments companies make to shareholders from profits.

### How It Works:
Company makes profit → Board decides to share some with investors → You get cash (usually quarterly)

### Example:
- You own 100 shares of Stock XYZ at $50/share = $5,000 invested
- Company announces $1/share annual dividend (2% yield)
- You receive $100/year ($25 per quarter)

### Key Terms:
- **Dividend Yield**: Annual dividend ÷ stock price (e.g., 3%)
- **Payout Ratio**: % of earnings paid as dividends
- **Ex-Dividend Date**: Must own stock BEFORE this date to get dividend

### Why Companies Pay Dividends:
✅ **Mature Businesses**: Stable profits, less growth opportunities
✅ **Shareholder Returns**: Reward long-term investors
✅ **Signal of Health**: Regular dividends = company confidence

### High Dividend Sectors:
- 🏦 **Financials**: Banks pay 3-5% yields
- ⚡ **Utilities**: 3-6% yields, very stable
- 🛒 **Consumer Staples**: 2-4% yields, reliable

### Growth vs Income:
**Growth Stocks** (AAPL, GOOGL): Reinvest profits → No/low dividends  
**Income Stocks** (JPM, VZ): Distribute profits → High dividends

### Dividend Reinvestment (DRIP):
Automatically use dividends to buy more shares → Compound growth over time

### Tax Note:
Qualified dividends taxed at 0-20% (capital gains rates), better than ordinary income.

**Bottom Line**: Dividends provide passive income and reduce volatility. Great for retirement portfolios or risk-averse investors."""
    
    # 3. INVESTMENT STRATEGY QUESTIONS
    if 'diversif' in question_lower:
        return """## 🎯 Diversification: Don't Put All Eggs in One Basket

**Diversification** means spreading investments across different assets to reduce risk.

### The Core Idea:
If you own 10 stocks and one crashes -50%, you lose 5% total. If you own just that one stock, you lose 50%. Simple math, massive impact.

### How to Diversify:

**1. Across Sectors** 🏗️
Don't buy only tech stocks. Mix:
- Technology (AAPL, MSFT)
- Healthcare (JNJ, UNH)
- Financials (JPM, V)
- Consumer Staples (WMT, PG)
- Energy, Industrials, etc.

**2. Across Market Caps** 📏
- Large-cap (stable): AAPL, MSFT
- Mid-cap (balanced): Growth potential + some stability
- Small-cap (risky): Higher growth, higher risk

**3. Across Asset Classes** 💼
- Stocks (growth)
- Bonds (stability)
- Real Estate (REITs)
- Cash (safety buffer)
- Commodities (inflation hedge)

**4. Geographic Diversification** 🌍
- US stocks
- International developed (Europe, Japan)
- Emerging markets (India, Brazil)

### Example Portfolio (Moderate Risk):
- 60% US stocks (mix of sectors)
- 20% International stocks
- 15% Bonds
- 5% Cash

### Common Mistakes:
❌ **Over-diversification**: Owning 100 stocks dilutes returns
❌ **False Diversification**: Buying 10 tech stocks isn't diversified
❌ **No Diversification**: YOLO into one meme stock

### The Sweet Spot:
**15-25 stocks** across different sectors provides excellent diversification without over-complication.

**Bottom Line**: Diversification is the only free lunch in investing. It reduces risk without necessarily reducing returns."""
    
    if 'start investing' in question_lower or 'how to invest' in question_lower or 'begin investing' in question_lower:
        return """## 🚀 How to Start Investing: Step-by-Step Guide

### Step 1: Get Your Finances in Order 💰
**BEFORE investing**:
- ✅ Pay off high-interest debt (credit cards >10%)
- ✅ Build emergency fund (3-6 months expenses)
- ✅ Have stable income
- ❌ Don't invest money you need in 5 years

### Step 2: Choose a Brokerage 🏦
**Popular Options**:
- **Fidelity**: Great research, no fees
- **Charles Schwab**: Excellent customer service
- **Interactive Brokers**: Best for active traders
- **Vanguard**: Low-cost index funds

**What to Look For**:
- Zero commission stock trades
- No account minimums
- Easy-to-use app
- Good customer support

### Step 3: Decide Your Strategy 🎯

**Option A: Passive (Recommended for Beginners)**
Buy index funds that track the market:
- **VTI** - Total US stock market
- **VOO** or **SPY** - S&P 500
- **VXUS** - International stocks

**Pros**: Low fees, diversification, historically ~10% annual returns  
**Cons**: Can't beat the market, boring

**Option B: Active Stock Picking**
Research and buy individual stocks
**Pros**: Potential to beat market, more exciting  
**Cons**: Requires research, higher risk, time-consuming

### Step 4: Start Small 📈
- **First $1,000**: Put in S&P 500 index fund (VOO)
- **Next $2,000**: Add 3-5 individual stocks you understand
- **Ongoing**: Invest consistently (dollar-cost averaging)

### Step 5: Key Principles ⚡
1. **Time in Market > Timing the Market**: Start now, stay invested
2. **Don't Panic Sell**: Markets drop 10-20% regularly, it's normal
3. **Reinvest Dividends**: Compounding is powerful
4. **Keep Learning**: Read, watch, analyze
5. **Avoid Hype**: Meme stocks and crypto are NOT for beginners

### Realistic Expectations:
- **Good Year**: +15-25%
- **Average Year**: +8-12%
- **Bad Year**: -10 to -30%
- **20-Year Average**: ~10% annually

### Common Beginner Mistakes:
❌ Investing money needed for bills
❌ Panic selling during market drops
❌ Chasing hot stocks
❌ Not diversifying
❌ Trying to time the market

**Bottom Line**: Start simple with index funds, learn as you go, invest regularly, and be patient. Wealth builds slowly."""
    
    if 'volatile' in question_lower or 'volatility' in question_lower:
        if 'crypto' in question_lower:
            return """## ⚡ Cryptocurrency Volatility

**Crypto is EXTREMELY volatile** - that's the short answer.

### How Volatile?
**Bitcoin** (least volatile crypto):
- ✅ **Good day**: +5-10%
- 🔴 **Bad day**: -10-20%
- 🎢 **Yearly swings**: Can go +200% or -70%

**Altcoins** (even more volatile):
- Can swing 20-50% in a day
- Many go to zero (90%+ drop)

### Why So Volatile?
1. **No Regulation**: No circuit breakers like stock market
2. **24/7 Trading**: Never stops, news hits anytime
3. **Speculation-Driven**: Most people buy hoping price goes up, not for utility
4. **Low Liquidity**: Easier for whales to move prices
5. **Sentiment-Based**: One Elon tweet can swing market 15%

### Real Examples:
- **Bitcoin 2021**: $65K → $30K → $69K → $20K (all in 18 months)
- **Luna 2022**: $116 → $0.0001 in 2 days (total collapse)
- **Ethereum**: Regularly sees 30-40% monthly swings

### Stock vs Crypto Volatility:
**S&P 500**: ~15-20% annual volatility  
**Bitcoin**: ~80-100% annual volatility  
**Most Altcoins**: 150-300%+ annual volatility

### Should You Invest in Crypto?
**Only if**:
- You can afford to lose 100% of it
- You understand blockchain technology
- You have strong conviction
- It's <5% of your portfolio
- You won't panic sell at -50%

### Risk Management:
- **Never go all-in**: Crypto should be 2-10% max of portfolio
- **Expect crashes**: -50% drops happen regularly
- **Don't use leverage**: You'll get liquidated
- **Dollar-cost average**: Buy small amounts over time

**Bottom Line**: Crypto is like stocks on steroids. If you can't handle seeing -30% in a week, stick to traditional investments."""
        else:
            return """## 📊 Volatility Explained

**Volatility** measures how much and how fast a stock's price moves up and down.

### High Volatility:
🎢 **Big swings**: Stock moves 5-10% in a day  
**Examples**: TSLA, NVDA, small-cap growth stocks  
**Risk/Reward**: High potential gains, high potential losses

### Low Volatility:
📉 **Small moves**: Stock moves 0.5-1% in a day  
**Examples**: WMT, JNJ, utility stocks  
**Risk/Reward**: Steady, boring, safer

### Measuring Volatility:
**VIX ("Fear Index")**: Measures S&P 500 volatility
- VIX below 15: Market is calm
- VIX above 30: Market is panicking

**Beta**: Compares stock to market
- Beta = 1: Moves with market
- Beta = 1.5: 50% more volatile than market
- Beta = 0.5: 50% less volatile than market

### Why Does Volatility Matter?
**High Volatility** = Higher risk, but also more opportunity to:
- Buy dips
- Sell rallies
- Swing trade

**Low Volatility** = Lower risk, better for:
- Retirement accounts
- Conservative investors
- Sleep-at-night money

### Real Examples:
**Tesla (TSLA)**: Beta ~2.0
- If S&P drops 5%, TSLA might drop 10%
- If S&P rises 5%, TSLA might rise 10%

**Walmart (WMT)**: Beta ~0.6
- If S&P drops 5%, WMT might only drop 3%
- If S&P rises 5%, WMT might only rise 3%

### Managing Volatility:
✅ **Diversification**: Mix high and low volatility stocks
✅ **Position Sizing**: Smaller positions in volatile stocks
✅ **Time Horizon**: Volatility matters less if you hold 10+ years
✅ **Stop Losses**: Protect against big drops

**Bottom Line**: Volatility isn't good or bad - it's a tool. Match volatility to your risk tolerance and time horizon."""
    
    # 4. STOCK-SPECIFIC QUESTIONS
    if ticker_str and any(word in question_lower for word in ['good', 'invest', 'buy', 'worth', 'recommend']):
        return f"""## 🤔 Should You Invest in {ticker_str}?

I can help you make an **informed decision** about {ticker_str}, but I need to analyze it first.

### What My Analysis Includes:
📈 **Technical Indicators**
- RSI: Is it overbought (>70) or oversold (<30)?
- MACD: What's the momentum trend?
- Moving Averages: Support/resistance levels

🎭 **Market Sentiment**
- FinBERT AI analysis of recent financial news
- Are investors bullish, bearish, or neutral?

💹 **Price Action**
- Recent performance and trends
- Volume analysis
- Key technical levels

### After Analysis, You'll Get:
✅ Clear **Buy/Sell/Hold** recommendation  
✅ **Confidence score** (0-100%)  
✅ **Reasoning** behind the recommendation  
✅ **Risk factors** to consider  
✅ **Key price levels** to watch

### IMPORTANT: Due Diligence Checklist
Before investing in ANY stock, make sure you:
- 📚 Understand the company's business model
- 💰 Check their financial health (earnings, debt)
- 🎯 Know your investment timeline (1 year? 10 years?)
- ⚖️ Assess your risk tolerance
- 🔍 Read multiple analyst opinions
- 💼 Consider how it fits your portfolio

### Remember:
⚠️ **Capital is at Risk**: You can lose money  
⚠️ **DYOR**: Do Your Own Research  
⚠️ **Diversify**: Don't put everything in one stock  
⚠️ **Only invest what you can afford to lose**

**Ready for me to analyze {ticker_str}?**"""
    
    if ticker_str and ('tell me about' in question_lower or 'what about' in question_lower):
        return f"""## 📊 {ticker_str} Analysis Overview

I can provide a comprehensive analysis of **{ticker_str}** using advanced AI and technical indicators.

### What I'll Analyze:
1. **📈 Technical Setup**
   - Current price and trend direction
   - RSI (momentum indicator)
   - MACD (trend strength)
   - Moving averages (support/resistance)

2. **🎭 Market Sentiment**
   - FinBERT AI analysis of financial news
   - Investor sentiment (bullish/bearish/neutral)
   - Recent news impact

3. **📊 Investment Perspective**
   - Buy/Sell/Hold recommendation
   - Confidence level
   - Risk assessment
   - Key levels to watch

### What You Need to Know First:
**Company Research** (do this yourself):
- What does {ticker_str} do? (business model)
- Revenue and earnings trends
- Competitive position
- Debt levels
- Management quality

**Your Investment Goals**:
- Time horizon (short-term trade or long-term hold?)
- Risk tolerance (can you handle -20% drops?)
- Portfolio allocation (how much to invest?)

### After My Analysis:
You'll understand:
✅ Current market momentum
✅ Technical buy/sell signals
✅ Sentiment from news and social media
✅ Risk/reward profile

**Would you like me to run a full technical and sentiment analysis on {ticker_str}?**"""
    
    # 5. VAGUE OR GENERAL QUESTIONS
    if any(phrase in question_lower for phrase in ['what do you think', 'your opinion', 'thoughts on']):
        if ticker_str:
            return f"""To give you my analysis on **{ticker_str}**, I would need to run my technical and sentiment analysis tools.

### Here's What I Do:
I analyze stocks using:
- **FinBERT AI**: Trained on 50,000+ financial texts to gauge sentiment
- **Technical Indicators**: RSI, MACD, moving averages
- **Price Action**: Trends, support/resistance, volume

This gives you a **data-driven perspective**, not just gut feelings.

### What I DON'T Do:
❌ Make guarantees or promises
❌ Give advice without analysis
❌ Predict the future with certainty

### What I CAN Do:
✅ Show you what the data says RIGHT NOW
✅ Provide clear Buy/Sell/Hold recommendation
✅ Explain the reasoning
✅ Highlight risks

**Want me to analyze {ticker_str}? Just let me know and I'll run the full analysis.**"""
        else:
            return """I'm here to help with **data-driven stock analysis** and **financial education**.

### How I Can Help:

**📊 Analyze Specific Stocks**
Give me a ticker (e.g., AAPL, MSFT, TSLA) and I'll provide:
- Technical indicators (RSI, MACD)
- Market sentiment (FinBERT AI)
- Buy/Sell/Hold recommendation

**📚 Explain Financial Concepts**
Ask me about:
- Market sectors (technology, healthcare, etc.)
- Technical indicators (What is RSI? MACD?)
- Investment strategies (diversification, value investing)
- Risk management

**💬 Discuss Investment Topics**
- "Should I invest in [stock]?"
- "What's the best strategy for beginners?"
- "How volatile is [sector/stock]?"
- "Explain P/E ratios"

**What's on your mind about investing?**"""
    
    # 6. SHORT/CASUAL QUESTIONS
    if len(question_lower.split()) <= 3 and not ticker_str:  # Very short questions
        # Handle common short questions
        if 'stock' in question_lower:
            return """**Stocks** represent ownership in a company. When you buy a stock, you own a tiny piece of that business.

### Quick Facts:
- **How You Make Money**: Stock price goes up, or company pays dividends
- **Risk**: Stock can go down, you can lose money
- **Long-term Average**: ~10% annual returns historically (S&P 500)
- **Where to Buy**: Through brokerages like Fidelity, Schwab, Interactive Brokers

### Get Started:
Tell me what you want to know:
- "How do I start investing?"
- "What's a good beginner stock?"
- "Should I buy [ticker]?"
- "What are the risks?"

**What specific aspect of stocks interests you?**"""
        
        elif 'crypto' in question_lower:
            return """**Cryptocurrency** is digital currency secured by blockchain technology.

### Key Points:
🎢 **Extremely Volatile**: Can swing 20%+ in a day
🔐 **Decentralized**: No government or bank control
⚡ **24/7 Trading**: Never stops
🎰 **High Risk**: Many cryptos go to zero

### Major Cryptos:
- **Bitcoin (BTC)**: "Digital gold", most established
- **Ethereum (ETH)**: Smart contracts platform
- **Others**: Thousands of altcoins, most are speculation

### Reality Check:
- Most people lose money in crypto
- Only invest what you can afford to lose completely
- Keep it <5% of your portfolio
- Understand it before investing

**Want to know about crypto volatility, risks, or how to start?**"""
        
        elif 'invest' in question_lower:
            return """**Investing** is putting money to work to grow wealth over time.

### Core Principles:
💰 **Start Early**: Time in market beats timing the market
📈 **Be Consistent**: Invest regularly (dollar-cost averaging)
🎯 **Diversify**: Don't put all eggs in one basket
⏳ **Be Patient**: Wealth builds slowly, not overnight
📚 **Keep Learning**: Markets evolve, so should you

### First Steps:
1. Build emergency fund (3-6 months expenses)
2. Pay off high-interest debt
3. Open brokerage account (Fidelity, Schwab)
4. Start with index funds (S&P 500)
5. Learn as you go

**Want details on "How to start investing?" Just ask!**"""
        
        else:
            return """I can help you with:

**📊 Stock Analysis**: Give me a ticker (e.g., AAPL) for technical analysis and sentiment  
**📚 Financial Education**: Ask about sectors, indicators, strategies  
**💬 Investment Discussions**: "Should I buy X?", "How to start investing?"  

**What would you like to explore?**"""
    
    # 7. FOLLOW-UP OR CONTEXT-BASED QUESTIONS
    if any(word in question_lower for word in ['it', 'that', 'this', 'them', 'those']):
        # User is referring to something from previous context
        return """I want to give you the best answer! However, I need a bit more context.

**Could you be more specific?**  
For example:
- Which stock are you asking about? (ticker symbol)
- Which concept do you want explained? (RSI, diversification, etc.)
- What's your main question?

**Example**: Instead of "Is it good?", try "Is AAPL a good buy?"

**What specifically are you asking about?**"""
    
    # 8. FALLBACK - FOR TRULY UNRECOGNIZED QUESTIONS
    return f"""I'm here to help with investing and stock market questions!

### Quick Response:
Your question: "{question}"

I can help you better if you ask about:
- **Specific stocks**: "Analyze AAPL", "Should I buy TSLA?"
- **Financial concepts**: "What is RSI?", "Explain P/E ratio"
- **Investment strategies**: "How to diversify?", "Best stocks for beginners?"
- **Market sectors**: "What are consumer staples?", "Tech sector overview"

**Could you rephrase your question to be more specific? What aspect of investing are you most interested in?**"""


# Helper function to detect question intent
def detect_intent(question: str) -> str:
    """Detect what the user is really asking about"""
    q = question.lower()
    
    if any(word in q for word in ['what is', 'what are', 'define', 'explain']):
        return 'education'
    if any(word in q for word in ['should i', 'recommend', 'good buy', 'worth it']):
        return 'recommendation'
    if any(word in q for word in ['risk', 'volatile', 'safe', 'dangerous']):
        return 'risk'
    if any(word in q for word in ['how to', 'start', 'begin']):
        return 'guidance'
    if any(word in q for word in ['tell me about', 'information on', 'what about']):
        return 'overview'
    
    return 'general'
