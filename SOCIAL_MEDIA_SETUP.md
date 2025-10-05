# Social Media Sentiment Analysis Setup

## Overview

The app now supports **multi-source sentiment analysis** using different HuggingFace models:

- **📰 News Sentiment**: FinBERT (`yiyanghkust/finbert-tone`) - optimized for financial news
- **💬 Social Media Sentiment**: Twitter-RoBERTa (`cardiffnlp/twitter-roberta-base-sentiment-latest`) - optimized for social media

## Data Sources

### 1. StockTwits (Free, No Auth Required)
- **Status**: Partially working (may require headers)
- **Rate Limit**: Public API limits apply
- **Data**: Recent messages about stocks with optional user sentiment tags

### 2. Reddit (Requires Free API Credentials)
- **Status**: Optional, needs setup
- **Rate Limit**: ~60 requests/minute
- **Subreddits**: r/wallstreetbets, r/stocks, r/investing
- **Data**: Posts mentioning ticker symbols

## Setup Instructions

### Option 1: Run Without Social Media (Default)
The app works fine without social media data. It will only analyze news sentiment.

### Option 2: Enable Reddit Sentiment (Recommended)

1. **Create Reddit App**:
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Fill in:
     - Name: `FinBertPortfolioAnalyzer`
     - Type: Select "script"
     - Description: `Portfolio sentiment analysis tool`
     - About URL: Leave blank
     - Redirect URI: `http://localhost:8080`
   - Click "Create app"

2. **Get Credentials**:
   - After creation, you'll see:
     - `client_id`: String under "personal use script"
     - `client_secret`: The "secret" field

3. **Set Environment Variables**:

   **Linux/Mac**:
   ```bash
   export REDDIT_CLIENT_ID="your_client_id_here"
   export REDDIT_CLIENT_SECRET="your_client_secret_here"
   ```

   **Windows (PowerShell)**:
   ```powershell
   $env:REDDIT_CLIENT_ID="your_client_id_here"
   $env:REDDIT_CLIENT_SECRET="your_client_secret_here"
   ```

   **Permanent (Linux/Mac)** - Add to `~/.bashrc` or `~/.zshrc`:
   ```bash
   echo 'export REDDIT_CLIENT_ID="your_client_id"' >> ~/.bashrc
   echo 'export REDDIT_CLIENT_SECRET="your_secret"' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Restart the Flask app**:
   ```bash
   python3 app.py
   ```

## How It Works

### Sentiment Analysis Pipeline

1. **News Analysis** (FinBERT):
   - Fetches recent news from Yahoo Finance
   - Analyzes with FinBERT (formal financial language model)
   - Weight: 60% of overall sentiment

2. **Social Media Analysis** (Twitter-RoBERTa):
   - Fetches posts from StockTwits and/or Reddit
   - Analyzes with Twitter-RoBERTa (informal social media model)
   - Weight: 40% of overall sentiment

3. **Combined Sentiment**:
   ```
   Overall Sentiment = (News * 0.6) + (Social * 0.4)
   ```

### Model Selection

The app automatically uses the best model for each data source:

| Data Source | Model | Why? |
|-------------|-------|------|
| Yahoo Finance News | FinBERT | Optimized for formal financial text |
| StockTwits | Twitter-RoBERTa | Trained on Twitter data, handles informal language |
| Reddit | Twitter-RoBERTa | Good with casual discussions and slang |

## Available Models

You can extend the app with these HuggingFace models:

1. **yiyanghkust/finbert-tone** ✅ (Current - News)
   - Best for: Financial news, earnings reports, analyst reports
   - Size: ~440MB

2. **cardiffnlp/twitter-roberta-base-sentiment-latest** ✅ (Current - Social)
   - Best for: Twitter, Reddit, StockTwits, casual discussions
   - Size: ~500MB

3. **ProsusAI/finbert** (Alternative)
   - Best for: General financial text
   - Size: ~440MB

## Troubleshooting

### "No social media data available"
- **Cause**: APIs are not accessible or not configured
- **Solution**: 
  - Set up Reddit credentials (see above)
  - The app will work fine with news sentiment only

### "Reddit API not configured"
- **Cause**: Missing environment variables
- **Solution**: Set `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`

### StockTwits returns 403
- **Cause**: API rate limiting or blocking
- **Solution**: 
  - App will gracefully skip StockTwits
  - Focus on Reddit for social sentiment
  - The code includes fallback handling

### Models take long to download
- **First Run**: Models will download (~1GB total)
- **Subsequent Runs**: Models are cached locally in `~/.cache/huggingface/`

## Metrics Display

The frontend now shows:

- **Overall Sentiment**: Combined news + social media score
- **News Sentiment**: Score from financial news analysis
- **Social Sentiment**: Score from social media analysis
- **Source Counts**: Number of news articles and social posts analyzed

## Cost

✅ **100% Free**:
- HuggingFace models: Free
- Reddit API: Free (requires registration)
- StockTwits API: Free public endpoints
- Yahoo Finance: Free

## Privacy

- All sentiment analysis runs **locally** on your machine
- No data is sent to external APIs except for fetching public data
- Reddit credentials stay on your machine
- Models are downloaded once and cached

## Next Steps

To customize further:
1. Adjust sentiment weights in `src/portfolio_analyzer.py`
2. Add more subreddits in `src/social_media_fetcher.py`
3. Try different HuggingFace models in `src/multi_model_sentiment.py`
