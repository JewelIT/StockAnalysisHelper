# Newsfeed Age Filters - Implementation Summary

## Date: October 6, 2025

## Overview
Completed implementation of age-based filtering for news articles and social media posts, with robust timestamp handling and logging for unknown date formats.

## Changes Made

### 1. Frontend (UI Layer)

#### `templates/index.html`
- ✅ Already has newsfeed configuration UI with age filter dropdowns
- Options: 1, 3, 7, 14, 30 days
- Slider badges show current values
- "Save & Close" button to persist settings

#### `static/js/app.js`
- ✅ Already updated: All 3 fetch('/analyze') calls include `news_days` and `social_days` parameters
- ✅ localStorage persistence with `newsDays: 3` and `socialDays: 7` defaults

### 2. Backend (API Layer)

#### `app/routes/analysis.py`
- ✅ Already extracts `news_days` and `social_days` from request
- ✅ Passes to analysis service

#### `app/services/analysis_service.py`
- ✅ Already updated: `analyze()` method accepts and passes through age filter parameters

### 3. Core Analysis Layer

#### `src/portfolio_analyzer.py`
- ✅ **UPDATED**: `analyze_stock()` signature now includes:
  - `news_days=3` parameter
  - `social_days=7` parameter
- ✅ Input validation: clamps days to 1-30 range
- ✅ Passes parameters to data fetchers:
  ```python
  news_articles = self.data_fetcher.fetch_news(ticker, max_news, days=news_days)
  social_posts = self.social_media_fetcher.fetch_all_social_media(ticker, max_per_source=max_social, days=social_days)
  ```

### 4. Data Fetching Layer

#### `src/data_fetcher.py`
- ✅ **NEW**: `fetch_news()` now accepts `days` parameter (default: 3)
- ✅ **NEW**: Implements intelligent date filtering with multiple format support:
  - **Unix timestamps** (int/float): `datetime.fromtimestamp()`
  - **ISO 8601** (e.g., "2025-10-06T13:19:18Z")
  - **Common formats**: "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", etc.
- ✅ **NEW**: Logging for unrecognized date formats
- ✅ **NEW**: Graceful fallback: includes articles if date parsing fails
- ✅ Filters before limiting: fetches all, filters by age, then returns up to `max_articles`

#### `src/social_media_fetcher.py`
- ✅ **NEW**: `fetch_all_social_media()` now accepts `days` parameter (default: 7)
- ✅ **NEW**: Implements intelligent date filtering with multiple format support:
  - **Unix timestamps** (int/float)
  - **ISO 8601** strings
  - **Common datetime formats**
- ✅ **NEW**: Logging for unrecognized date formats
- ✅ **NEW**: Graceful fallback: includes posts if date parsing fails

## Date Format Support

### Supported Formats

**Priority 1 - Direct Detection:**
1. **Unix Timestamp** (int/float): `1696607958`
2. **ISO 8601** (with 'T', '+', or 'Z'): `"2025-10-06T13:19:18Z"`, `"2025-10-06T13:19:18+00:00"`

**Priority 2 - Format Matching:**
3. `"%Y-%m-%d %H:%M:%S"` → "2025-10-06 13:19:18"
4. `"%Y-%m-%d"` → "2025-10-06"
5. `"%d/%m/%Y"` → "06/10/2025"
6. `"%m/%d/%Y"` → "10/06/2025"
7. `"%d/%m/%Y %H:%M:%S"` → "06/10/2025 13:19:18"
8. `"%m/%d/%Y %H:%M:%S"` → "10/06/2025 13:19:18"

### Logging Unknown Formats

When an unrecognized format is encountered:
```python
logger.warning(f"Unrecognized date format for news article: '{pub_time}' (type: {type(pub_time).__name__})")
```

This allows us to:
- ✅ Identify new formats in production logs
- ✅ Add support for additional formats as needed
- ✅ Include the content anyway (graceful degradation)
- ✅ Maintain service availability

## Testing Instructions

### Manual Testing
1. Open settings modal → Newsfeeds tab
2. Set news age to "Last 24 hours" (1 day)
3. Set social age to "Last week" (7 days)
4. Click "Save & Close"
5. Analyze a stock (e.g., AAPL)
6. Verify only recent news/social media appears
7. Check logs for any date format warnings

### Check Logs
```bash
tail -f logs/finbert_app_20251006.log | grep "Unrecognized date format"
```

### Unit Testing
Run the test suite:
```bash
python3 tests/run_tests.py
```

## Known Issues & Solutions

### Issue 1: Server Restart Required
**Problem**: Changes to Python files require server restart
**Solution**: Flask debug mode auto-reloads, or manually restart:
```bash
pkill -f "python3 run.py"
python3 run.py
```

### Issue 2: Cached Responses
**Problem**: Browser may cache API responses
**Solution**: Hard refresh (Ctrl+Shift+R) or clear browser cache

### Issue 3: Old Template Files
**Status**: ✅ Cleaned up
- Deleted: `index-modern.html`, `modern.css`
- Kept: `index.html`, `style.css`, `style-old.css` (backup)

## File Structure

```
FinBertTest/
├── templates/
│   └── index.html                    ✅ Single template
├── static/
│   ├── css/
│   │   ├── style.css                ✅ Active
│   │   └── style-old.css            (backup)
│   └── js/
│       └── app.js                   ✅ Updated
├── app/
│   ├── routes/
│   │   └── analysis.py              ✅ Updated
│   └── services/
│       └── analysis_service.py      ✅ Updated
├── src/
│   ├── portfolio_analyzer.py        ✅ Updated
│   ├── data_fetcher.py              ✅ NEW: Date filtering
│   └── social_media_fetcher.py      ✅ NEW: Date filtering
└── logs/
    └── finbert_app_YYYYMMDD.log     (check for warnings)
```

## Configuration Defaults

```javascript
// Frontend (localStorage)
{
  newsDays: 3,          // Last 3 days of news
  socialDays: 7,        // Last week of social media
  maxNews: 5,           // Up to 5 articles
  maxSocial: 5,         // Up to 5 posts
  newsSort: 'relevance',
  socialSort: 'relevance'
}
```

```python
# Backend (function defaults)
def analyze_stock(..., news_days=3, social_days=7):
def fetch_news(..., days=3):
def fetch_all_social_media(..., days=7):
```

## Next Steps

1. ✅ **COMPLETED**: Parameter chain from UI to fetchers
2. ✅ **COMPLETED**: Date filtering implementation
3. ✅ **COMPLETED**: Logging for unknown formats
4. ⏳ **TODO**: Monitor logs for new date formats
5. ⏳ **TODO**: Add unit tests for date filtering
6. ⏳ **TODO**: Implement sort order logic (currently accepted but not used)
7. ⏳ **TODO**: Consider adding real-time preview of filtered results

## Performance Notes

- **News fetching**: Fetches all available, then filters by age, then limits by count
- **Social media**: Same approach - filter by age before limiting count
- **Impact**: Slight overhead from parsing timestamps, but ensures accurate filtering
- **Optimization**: Could cache parsed timestamps if performance becomes an issue

## Security Considerations

- ✅ Input validation: Days clamped to 1-30 range
- ✅ Type checking: Validates int/float/str before processing
- ✅ Error handling: Try-except blocks prevent crashes from malformed dates
- ✅ Logging: Non-sensitive information only (date formats, not user data)

## Success Criteria

- ✅ UI settings persist across sessions
- ✅ Settings are sent to backend in all analysis requests
- ✅ Backend validates and uses age filter parameters
- ✅ Data fetchers filter content by age
- ✅ Multiple date formats supported
- ✅ Unknown formats logged for future support
- ✅ Graceful degradation when date parsing fails
- ⏳ No errors in production logs (monitoring required)

---

**Implementation Status**: ✅ **COMPLETE**
**Server Status**: ✅ **RUNNING** (http://localhost:5000)
**Ready for Testing**: ✅ **YES**
