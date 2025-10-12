# Chat Trainer - Feedback Collection System

## Overview

The Chat Trainer is a feedback collection system that allows users to rate chatbot responses and help improve the AI over time.

## Features

### 1. Training Interface (`/chat-trainer`)
- Beautiful, interactive chat interface
- Ask questions and get responses from the bot
- Rate each response with:
  - **Thumbs up/down** (binary feedback)
  - **0-5 star rating** (detailed feedback)
- Track statistics (total chats, total feedback)

### 2. Feedback Collection
All feedback is logged to `logs/chat_feedback.jsonl` in JSON Lines format (one JSON object per line).

Each feedback entry contains:
```json
{
  "interaction_id": "20251012_131151_228430",
  "timestamp": "2025-10-12T13:12:00.123456",
  "feedback": {
    "thumbs": "up",
    "helpful": true,
    "rating": 4
  },
  "metadata": {
    "user_agent": "Mozilla/5.0...",
    "ip_hash": 1234
  },
  "interaction": {
    "question": "What are dividends?",
    "answer": "Dividends are...",
    "ticker": "",
    "vestor_mode": "conversation"
  }
}
```

### 3. Feedback Analysis (`analyze_feedback.py`)

Run the analyzer to get insights:

```bash
python3 analyze_feedback.py
```

Or specify a custom feedback file:

```bash
python3 analyze_feedback.py logs/custom_feedback.jsonl
```

**Analysis Report Includes:**
- 📈 Total feedback count
- ⭐ Rating distribution (0-5 stars)
- 🔴 Low-rated responses (need improvement)
- 🟢 High-rated responses (doing well)
- 🔍 Question patterns (what topics get low ratings)
- 📅 Timeline of feedback over time
- 💡 Actionable recommendations

**Export Training Data:**
The analyzer can export structured data to `logs/training_data.json` for future model fine-tuning.

## Usage

### For Users (Collect Feedback)

1. Open your browser to: `http://localhost:5000/chat-trainer`
2. Ask the chatbot questions
3. Rate each response with thumbs up/down or 0-5 stars
4. Your feedback is automatically saved

### For Developers (Analyze Feedback)

```bash
# View analysis report
python3 analyze_feedback.py

# Export training data when prompted
# This creates logs/training_data.json
```

### API Endpoints

#### POST `/chat-trainer`
Chat with feedback collection enabled.

**Request:**
```json
{
  "question": "What are dividends?",
  "ticker": "",  // optional
  "context_ticker": ""  // optional
}
```

**Response:**
```json
{
  "answer": "Dividends are...",
  "interaction_id": "20251012_131151_228430",
  "feedback_enabled": true,
  "success": true,
  "ticker": null,
  "vestor_mode": "conversation"
}
```

#### POST `/chat-trainer/feedback`
Submit feedback for an interaction.

**Request (Thumbs):**
```json
{
  "interaction_id": "20251012_131151_228430",
  "thumbs": "up"  // or "down"
}
```

**Request (Rating):**
```json
{
  "interaction_id": "20251012_131151_228430",
  "rating": 4  // 0-5
}
```

**Request (With Comment):**
```json
{
  "interaction_id": "20251012_131151_228430",
  "rating": 2,
  "comment": "Answer was too technical for a beginner"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback received! Thank you for helping improve the chatbot.",
  "interaction_id": "20251012_131151_228430"
}
```

## Workflow

1. **Collect Feedback** → Users interact with `/chat-trainer`
2. **Feedback Logged** → Data saved to `logs/chat_feedback.jsonl`
3. **Analyze** → Run `python3 analyze_feedback.py`
4. **Identify Issues** → Review low-rated responses
5. **Improve Bot** → Update knowledge base or patterns
6. **Test** → Have users test improved responses
7. **Repeat** → Continuous improvement cycle

## Continuous Improvement

### Finding Weak Areas

Run analysis regularly:
```bash
# Daily analysis
python3 analyze_feedback.py

# Look for patterns in low-rated responses:
# - Which topics get poor ratings?
# - What type of questions fail?
# - Are there specific keywords in bad responses?
```

### Improving Responses

1. **Identify Pattern**: "Questions about P/E ratio get low ratings"
2. **Update Knowledge Base**: Improve `_get_knowledge_based_answer()` in `src/ai/stock_chat.py`
3. **Test Manually**: Test the new response
4. **Collect More Feedback**: Monitor improvement

### Export for Training

If you collect enough high-quality feedback (100+ entries), you can:

1. Export training data: `python3 analyze_feedback.py` → yes to export
2. Use `logs/training_data.json` to fine-tune models
3. Train a better response ranker or classifier

## Privacy & Ethics

- **IP Addresses**: Hashed and anonymized
- **User Agent**: Stored for debugging, not identification
- **Questions**: Stored for analysis, no PII should be in questions
- **Purpose**: Educational improvement only

## File Locations

```
logs/
├── chat_feedback.jsonl          # Raw feedback (JSONL format)
└── training_data.json           # Exported training data

templates/
└── chat_trainer.html            # Training interface

src/web/routes/
└── chat.py                      # Endpoints: /chat-trainer, /chat-trainer/feedback

analyze_feedback.py              # Analysis script
```

## Tips

### For Testers
- Test edge cases and unusual questions
- Provide detailed ratings (0-5 preferred over thumbs)
- Add comments to explain why you rated something low
- Test the same question multiple times to check consistency

### For Developers
- Run analysis weekly during development
- Focus on questions with rating ≤ 2 first
- Look for patterns, not individual failures
- Export data when you have 50+ feedback entries

## Example Analysis Output

```
================================================================================
📊 CHAT FEEDBACK ANALYSIS REPORT
================================================================================

📈 Total Feedback Entries: 47

⭐ RATING DISTRIBUTION
Average Rating: 3.82/5.0

  5 ⭐: ███████████████ 15 (31.9%)
  4 ⭐: ████████████ 12 (25.5%)
  3 ⭐: ██████ 8 (17.0%)
  2 ⭐: ████ 6 (12.8%)
  1 ⭐: ████ 6 (12.8%)

👍 Helpful: 27
👎 Unhelpful: 12

🔴 LOW-RATED RESPONSES (Need Improvement)
#1 Rating: 1/5
   Q: How do I start investing with $100?
   A: ## 📊 Investment Analysis
      To give you a proper investment recommendation...
```

## Future Enhancements

- [ ] A/B testing different response strategies
- [ ] Sentiment analysis of comments
- [ ] Automatic knowledge base updates
- [ ] Dashboard for real-time feedback monitoring
- [ ] Model fine-tuning pipeline
- [ ] Comparison of response quality over time

## Questions?

Check `src/web/routes/chat.py` for implementation details or run:

```bash
python3 analyze_feedback.py --help
```
