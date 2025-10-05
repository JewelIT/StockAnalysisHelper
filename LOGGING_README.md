# Logging & Analytics System

This application includes comprehensive logging to help improve the chatbot over time through data-driven insights.

## Log Files

All logs are stored in the `logs/` directory (automatically created):

- `finbert_app_YYYYMMDD.log` - General application logs
- `security_YYYYMMDD.log` - Security events (prompt injection attempts, etc.)

## Log Categories

### 1. Security Events (HIGH Priority)
- **Prompt Injection Attempts**: Users trying to override system instructions
- **Legal Manipulation**: Attempts to change liability statements
- **Persona Override**: Attempts to change the financial advisor role
- **Data Extraction**: Attempts to reveal internal prompts

All security events are logged with:
- Timestamp
- Severity level (HIGH/MEDIUM)
- Attack type
- User question
- IP address and user agent

### 2. Unanswered Questions (IMPROVEMENT Priority)
Questions that the bot couldn't properly answer are logged for analysis:
- Educational questions without matching patterns
- Questions without identifiable tickers
- Too broad or ambiguous questions

### 3. Chat Interactions
All successful and failed chat interactions are logged for quality monitoring.

## Analyzing Unanswered Questions

### Automatic Analysis

Run the analysis tool to identify patterns:

```bash
python3 analyze_questions.py
```

This will:
- Find the latest log file
- Extract all unanswered questions
- Identify common words and patterns
- Provide recommendations for bot improvements
- Export analysis to `logs/unanswered_analysis.json`

### Sample Output

```
📊 UNANSWERED QUESTIONS ANALYSIS REPORT
================================================================================
📈 Total Unanswered Questions: 45

🔤 Most Common Words in Unanswered Questions:
  • microsoft           -   8 occurrences
  • investment          -   7 occurrences
  • crypto              -   6 occurrences
  • portfolio           -   5 occurrences

❓ Question Type Patterns:
  • WHAT              -  15 questions (33.3%)
  • HOW               -  12 questions (26.7%)
  • SHOULD            -   8 questions (17.8%)

📝 RECOMMENDATIONS:
  • Consider adding more 'What is...' definition handlers
  • Users want process explanations - add more 'How to...' guides
  • High interest in crypto - consider expanding cryptocurrency content
```

## Improving the Bot

### Step 1: Analyze Logs Periodically

Run the analysis tool weekly or after significant user activity:

```bash
python3 analyze_questions.py
```

### Step 2: Identify Patterns

Look for:
- **Common topics**: Words that appear frequently (e.g., "tax", "dividend", "crypto")
- **Question types**: "What is", "How do I", "Should I", etc.
- **Specific tickers**: Users asking about stocks not in keyword lists

### Step 3: Add New Handlers

Based on patterns, add new response handlers in `src/stock_chat.py`:

```python
# Example: Adding a new handler for dividend questions
if any(word in question_lower for word in ['dividend', 'dividends', 'yield', 'payout']):
    matched_pattern = True
    return """💰 **Understanding Dividends**
    
    Dividends are cash payments companies make to shareholders...
    """
```

### Step 4: Expand Keywords

Update educational keywords in `app.py` to catch more question types:

```python
educational_keywords = [
    'learn', 'beginner', 'start',
    # Add new keywords based on analysis
    'dividend', 'option', 'future', 'margin'
]
```

## Security Monitoring

### Reviewing Security Logs

Check security logs regularly:

```bash
cat logs/security_*.log
```

Look for patterns:
- Repeated attempts from same IP
- Coordinated attacks
- New attack vectors

### Responding to Security Events

1. **High-Severity Events**: Review immediately
2. **Pattern Detection**: If multiple users try similar bypasses, strengthen defenses
3. **Update Patterns**: Add new detection patterns in `src/stock_chat.py._detect_prompt_injection()`

## Best Practices

1. **Regular Analysis**: Run `analyze_questions.py` at least weekly
2. **Iterative Improvement**: Add 2-3 new handlers per analysis cycle
3. **Test New Handlers**: Verify new patterns don't conflict with existing ones
4. **Monitor Success Rate**: Track if unanswered questions decrease over time
5. **User Privacy**: Never log personally identifiable information

## Privacy & Security

- Questions are truncated in logs (max 200 chars)
- No personal user data is logged
- IP addresses are only logged for security events
- Logs are excluded from git (see `.gitignore`)
- Logs should be regularly archived and cleaned

## File Structure

```
logs/
├── finbert_app_20251005.log      # Application logs
├── security_20251005.log          # Security events
└── unanswered_analysis.json       # Latest analysis results
```

## Continuous Improvement Cycle

```
┌─────────────────┐
│  Users Ask      │
│  Questions      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Bot Responds   │
│  (some unsure)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Log Unanswered │
│  Questions      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analyze Logs   │
│  Find Patterns  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Add New        │
│  Handlers       │
└────────┬────────┘
         │
         └──────► (Cycle repeats with improved bot)
```

---

**Remember**: The goal is continuous improvement based on real user questions, not assumptions about what users might ask!
