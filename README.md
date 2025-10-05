# Portfolio Analysis with FinBERT

AI-Powered stock portfolio analysis using FinBERT sentiment analysis and technical indicators.

## Features

- 📊 **FinBERT Sentiment Analysis** - Analyzes news sentiment using state-of-the-art financial NLP
- 📈 **Technical Analysis** - RSI, MACD, Moving Averages, Bollinger Bands
- 🎨 **Interactive Charts** - Candlestick charts with technical indicators inline
- 💾 **LocalStorage Support** - Save your portfolio tickers in the browser
- 🌐 **Web Interface** - Modern, responsive Flask web application
- 📁 **Organized Exports** - All analysis results saved to `exports/` folder

## Project Structure

```
FinBertTest/
├── app.py                      # Flask web application
├── requirements.txt            # Python dependencies
├── src/                        # Source modules
│   ├── __init__.py
│   ├── sentiment_analyzer.py  # FinBERT sentiment analysis
│   ├── technical_analyzer.py  # Technical indicators (RSI, MACD, etc.)
│   ├── data_fetcher.py         # Yahoo Finance data fetching
│   ├── chart_generator.py      # Plotly chart generation
│   └── portfolio_analyzer.py   # Main analysis orchestration
├── templates/                  # HTML templates
│   └── index.html
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── exports/                    # Generated analysis files
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Application (Recommended)

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser to: `http://localhost:5000`

3. Add ticker symbols (e.g., AAPL, MSFT, GOOGL)

4. Click "Analyze Portfolio"

5. View results with inline interactive charts

### Features

- **Custom Portfolio**: Add/remove tickers with the interface
- **LocalStorage**: Your ticker list is saved in your browser
- **Default Portfolio**: Quick load common tech stocks
- **Interactive Charts**: Zoom, pan, and explore candlestick charts with indicators
- **Export Results**: Analysis saved as JSON in `exports/` folder

## Technical Analysis Indicators

- **RSI (Relative Strength Index)**: Identifies overbought/oversold conditions
- **MACD (Moving Average Convergence Divergence)**: Trend following momentum
- **Moving Averages**: SMA(20), SMA(50), EMA(12)
- **Bollinger Bands**: Volatility and price levels

## Scoring System

- **Combined Score** = 40% Sentiment + 60% Technical Analysis
- **STRONG BUY**: > 0.65
- **BUY**: 0.55 - 0.65
- **HOLD**: 0.45 - 0.55
- **SELL**: 0.35 - 0.45
- **STRONG SELL**: < 0.35

## Legacy Scripts

- `script.py` - Original simple script
- `enhanced_script.py` - Standalone enhanced version

## Requirements

- Python 3.8+
- Internet connection (for fetching stock data and news)
- ~2GB RAM (for FinBERT model)

## Notes

- First analysis will take longer as it downloads the FinBERT model
- Model is cached for subsequent runs
- Charts are generated inline using Plotly CDN
- All generated files go to `exports/` folder, never mixed with source code

## License

MIT
