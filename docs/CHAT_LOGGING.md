# Chat Interaction Logging

## Overview

The Vestor chatbot now automatically logs all user interactions to help identify issues and improve responses. Logs are stored in JSONL format (JSON Lines) for easy processing and analysis.

## Log Location

```
logs/chat_interactions/conversations_YYYYMMDD.jsonl
```

Each day gets its own log file.

## Log Format

Each line in the JSONL file contains one conversation:

```json
{
  "timestamp": "2025-10-12T13:20:17.123456",
  "question": "What are dividends?",
  "answer": "## 💰 Dividends Explained\n\n**Dividends** are cash payments...",
  "answer_length": 1438,
  "ticker": null,
  "vestor_mode": "conversation",
  "metadata": {
    "mentioned_tickers": [],
    "is_conversational": true,
    "success": true
  }
}
```

## Analyzing Logs

### View All Conversations

```bash
python scripts/analyze_chat_logs.py
```

Output includes:
- Total conversations
- Time range
- Vestor modes distribution
- Most discussed tickers
- Question patterns
- Response length statistics
- Potential issues (generic responses, very short/long answers)
- Recent conversation samples

### Analyze Specific Date

```bash
python scripts/analyze_chat_logs.py --date 20251012
```

### Analyze Recent Conversations

```bash
python scripts/analyze_chat_logs.py --recent 100
```

### Export for Manual Review

```bash
python scripts/analyze_chat_logs.py --export review.md
```

This creates a Markdown file with all conversations in readable format.

## What Gets Logged

- **Question**: User's exact question
- **Answer**: Bot's response (truncated to 500 chars in log, full length recorded)
- **Ticker**: Stock symbol if mentioned
- **Vestor Mode**: Type of conversation (conversation, stock_analysis, ticker_lookup, etc.)
- **Metadata**: Additional context (mentioned tickers, success status, etc.)

## Identifying Issues

The analyzer automatically detects:

### Generic Responses
Responses containing phrases like:
- "I can help you with"
- "How can I help"
- "Being analyzed"

### Short Answers
Responses under 150 characters to "what", "how", "why" questions

### Very Long Responses
Responses over 2000 characters (potential information dumps)

## Privacy & Storage

- Logs are stored locally only
- No personal identification information is collected
- Logs rotate daily
- Old logs can be manually deleted if needed

## Using Logs for Improvement

1. **Run Analysis Regularly**
   ```bash
   python scripts/analyze_chat_logs.py --recent 50
   ```

2. **Look for Patterns**
   - Which questions get generic responses?
   - Which tickers are most discussed?
   - Are responses too long or too short?

3. **Export for Review**
   ```bash
   python scripts/analyze_chat_logs.py --export review.md
   ```
   Then manually review the exported file

4. **Identify Knowledge Gaps**
   - Questions that get poor responses
   - Topics that need better knowledge base entries
   - Tickers that should be added to company mapping

## Example Analysis Output

```
================================================================================
📊 CONVERSATION ANALYSIS
================================================================================

**Total Conversations:** 125
**Time Range:** 2025-10-12 09:00 to 2025-10-12 17:30

### Vestor Modes:
  - **conversation**: 78 (62.4%)
  - **stock_analysis**: 32 (25.6%)
  - **ticker_lookup**: 15 (12.0%)

### Tickers Discussed:
  - **AAPL**: 12 times
  - **TSLA**: 8 times
  - **MSFT**: 6 times

### Question Patterns:
  - **what**: 45 questions
  - **should**: 23 questions
  - **how**: 18 questions

### Response Lengths:
  - **Average**: 892 characters
  - **Min**: 145 characters
  - **Max**: 2341 characters

================================================================================
🔍 POTENTIAL ISSUES
================================================================================

Found 5 potential issues:

**Generic Response:** 2
  - Q: "What do you think about crypto?"
    Problem: Contains "i can help you with"

**Short Answer:** 3
  - Q: "What is RSI?"
    Length: 98 chars
```

## Future Enhancements

Potential additions:
- User ratings/feedback integration
- Automated issue categorization
- Response quality scoring
- A/B testing different responses
- Weekly analysis reports
