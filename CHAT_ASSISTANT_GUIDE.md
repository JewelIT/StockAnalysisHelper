# AI Chat Assistant Guide

## Overview
The AI Stock Chat Assistant uses DistilBERT Q&A model to answer questions about analyzed stocks. It provides intelligent responses based on the analysis data available.

---

## How It Works

### 1. **Stock Selection (Optional)**
- You can select a stock from the dropdown OR
- Mention a ticker in your question (e.g., "What about MSFT?")
- Or ask general questions without selecting a stock

### 2. **Analysis Required**
⚠️ **Important**: You must analyze a stock before asking questions about it.
- Use the "Analyze Portfolio" button first
- The chat needs analysis data to answer questions accurately

### 3. **Confidence Scoring**
The AI shows confidence percentage only when:
- ✅ Confidence >= 30%
- ✅ Direct answer found in analysis data
- ❌ Hidden for helpful messages and warnings

---

## What You Can Ask

### ✅ **Supported Questions**

#### Price & Performance
- "What's the current price?"
- "What's the price change?"
- "How did it perform over 3 months?"
- "Is it going up or down?"

#### Technical Analysis
- "What's the RSI value?"
- "What are the technical indicators?"
- "Is it overbought or oversold?"
- "What's the MACD showing?"
- "What's the technical signal?"

#### Recommendations
- "Should I buy this stock?"
- "What's the recommendation?"
- "Is it a good time to buy?"
- "What does the analysis suggest?"

#### Sentiment
- "What's the sentiment?"
- "Is the news positive or negative?"
- "What are people saying about it?"
- "Is social media sentiment bullish?"

#### Company Info
- "What sector is it in?"
- "What industry?"
- "What's the company name?"

---

## ❌ **Current Limitations**

### Not Yet Supported:
1. **Currency Conversion**
   - ❌ "What's the price in euros?"
   - ❌ "Convert to GBP"
   - **Workaround**: Prices shown in USD (or ticker's native currency)
   - **Coming Soon**: Currency conversion feature

2. **Future Predictions**
   - ❌ "What will the price be tomorrow?"
   - ❌ "Will it go up next week?"
   - **Why**: The AI only analyzes historical data and current indicators

3. **Comparison Between Stocks**
   - ❌ "Is MSFT better than AAPL?"
   - ❌ "Compare these two stocks"
   - **Workaround**: Ask about each stock separately

4. **Real-Time Data**
   - ❌ "What's the price right now?"
   - **Note**: Data is from the most recent analysis (3-month historical)

5. **External Information**
   - ❌ "What's the CEO's name?"
   - ❌ "When is the earnings report?"
   - **Why**: Only analyzes data from Yahoo Finance/CoinGecko APIs

---

## Smart Features

### 🎯 **Auto-Ticker Detection**
Ask questions like:
- "What about MSFT?" → Auto-selects Microsoft
- "Tell me about BTC-USD" → Auto-selects Bitcoin

### 📊 **Helpful Responses**
When confidence is low, the AI provides:
- Summary of available data
- List of questions it CAN answer
- Current price and recommendation
- Technical signals

### ⚠️ **Clear Warnings**
- "Please analyze this stock first" → Stock not yet analyzed
- "Select a stock from dropdown" → No stock selected
- Low confidence → Shows what data IS available

---

## Examples

### ✅ Good Questions

```
User: "What's the current price?"
AI: "$150.25 USD (Confidence: 95%)"

User: "What's the recommendation?"
AI: "BUY - Based on positive sentiment and strong technical indicators (Confidence: 87%)"

User: "What are the technical indicators showing?"
AI: "RSI: 65 (neutral), MACD: Bullish crossover, Price above 50-day SMA (Confidence: 92%)"
```

### ⚠️ Questions Needing Improvement

```
User: "What's the price in euros?"
AI: I'm not confident about that specific question (confidence: 6%), but here's what I know about UPR.IR:

📊 Current Price: $3.75 USD
📈 3-Month Change: +8.5%
💡 Recommendation: BUY

Note: Currency conversions may not be available yet.
```

---

## Tips for Best Results

1. **Analyze First**
   - Always analyze stocks before chatting
   - Re-analyze for updated data

2. **Be Specific**
   - ✅ "What's the RSI?" instead of "How's the indicator?"
   - ✅ "What's the recommendation?" instead of "Should I invest?"

3. **Use Stock Names**
   - ✅ "What about MSFT stock?"
   - ✅ "Tell me about Bitcoin"

4. **Check Available Data**
   - If confidence is low, the AI will tell you what it CAN answer
   - Rephrase your question based on the suggestions

5. **One Stock at a Time**
   - Ask about one stock per question
   - For comparisons, ask separately

---

## Future Enhancements

### 🚀 Coming Soon:
- [ ] Currency conversion (EUR, GBP, JPY, etc.)
- [ ] Multi-stock comparison
- [ ] Conversation history (follow-up questions)
- [ ] Chart references ("Show me the chart")
- [ ] News summarization
- [ ] Custom alerts ("Tell me when RSI drops below 30")

### 🔮 Planned:
- [ ] Voice input/output
- [ ] Real-time data integration
- [ ] Portfolio-level questions ("What's my total return?")
- [ ] Risk analysis
- [ ] Dividend information
- [ ] Earnings calendar integration

---

## Technical Details

### Model
- **DistilBERT** (distilbert-base-cased-distilled-squad)
- Trained on SQuAD (Stanford Question Answering Dataset)
- ~66M parameters, runs on GPU if available

### Context Window
The AI receives:
- Current price and 3-month change
- Technical indicators (RSI, MACD, SMA, Bollinger Bands)
- Sentiment scores (news + social media)
- Recommendation and technical signal
- Recent news headlines
- Sector and industry info

### Confidence Threshold
- **High** (≥50%): Direct answer with confidence shown
- **Medium** (30-50%): Answer with confidence shown
- **Low** (<30%): Helpful message with available data summary

---

## Troubleshooting

### "Please analyze this stock first"
**Solution**: Click "Analyze Portfolio" button to run analysis

### "Select a stock from the dropdown"
**Solution**: Either select from dropdown or mention ticker in question

### Low Confidence Responses
**Reason**: Question can't be answered with available data
**Solution**: Check the helpful message for what CAN be answered

### "Sorry, there was an error"
**Reason**: Network issue or backend problem
**Solution**: 
1. Check Flask is running (http://localhost:5000)
2. Check browser console for errors
3. Try refreshing the page

---

## API Response Format

```json
{
  "question": "What's the current price?",
  "answer": "$150.25 USD",
  "confidence": 0.95,
  "ticker": "MSFT",
  "success": true,
  "needs_analysis": false,
  "low_confidence": false
}
```

### Response Fields:
- `answer`: The AI's response
- `confidence`: 0.0 to 1.0 score
- `needs_analysis`: true if stock must be analyzed first
- `low_confidence`: true if showing helpful fallback message
- `success`: true if request processed successfully

---

## Support

For issues or feature requests:
1. Check this guide first
2. Review `INTERNATIONAL_TICKERS.md` for ticker format
3. Check Flask console for errors
4. Open an issue with:
   - Your question
   - Selected ticker
   - Screenshot of response
   - Browser console errors (F12)
