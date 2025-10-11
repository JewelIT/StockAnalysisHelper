# Logging Control Guide

This document explains how to control logging output in both the backend (Python) and frontend (JavaScript).

## 🎯 Overview

The application has two types of logging:
1. **Backend Logging** (Python) - Server-side logs, security events, errors
2. **Frontend Logging** (JavaScript) - Browser console output for debugging

---

## 🐍 Backend Logging (Python)

### Quick Start

Control Python logging level via environment variable:

```bash
# Show only errors (production mode)
LOG_LEVEL=ERROR python3 app.py

# Show warnings and above (recommended for production)
LOG_LEVEL=WARNING python3 app.py

# Show info and above (default)
LOG_LEVEL=INFO python3 app.py

# Show everything including debug messages (development)
LOG_LEVEL=DEBUG python3 app.py
```

### Log Levels (from least to most verbose)

| Level | Description | Use Case |
|-------|-------------|----------|
| `CRITICAL` | Critical errors only | Emergency situations |
| `ERROR` | Errors and critical | **Production (recommended)** |
| `WARNING` | Warnings, errors, critical | Production with monitoring |
| `INFO` | General info + above | **Default** |
| `DEBUG` | Everything | Development/troubleshooting |

### Permanent Configuration

Add to your `.env` file or shell profile:

```bash
# .env file
LOG_LEVEL=ERROR
```

Or in `~/.bashrc` / `~/.zshrc`:

```bash
export LOG_LEVEL=ERROR
```

### Per-Session Override

```bash
# Temporarily set for one command
LOG_LEVEL=DEBUG python3 app.py

# Set for current shell session
export LOG_LEVEL=DEBUG
python3 app.py
```

### Log Files

Logs are always written to files (regardless of console level):
- **Application logs**: `logs/finbert_app_YYYYMMDD.log`
- **Security logs**: `logs/security_YYYYMMDD.log`

---

## 🌐 Frontend Logging (JavaScript)

### Quick Start - Browser Console

Control JavaScript console output via browser localStorage:

```javascript
// Enable debug mode (in browser console)
localStorage.setItem('DEBUG_MODE', 'true');
// Refresh page to see debug logs

// Disable debug mode
localStorage.removeItem('DEBUG_MODE');
// Refresh page - logs will stop
```

### What Gets Logged?

| Log Type | Always Shown | Debug Mode Only |
|----------|--------------|-----------------|
| `debug.log()` | ❌ | ✅ |
| `debug.info()` | ❌ | ✅ |
| `debug.warn()` | ✅ | ✅ |
| `debug.error()` | ✅ | ✅ |

**Important**: Warnings and errors are **always** shown, regardless of DEBUG_MODE.

### Example Usage in Code

```javascript
// This only shows when DEBUG_MODE is enabled
debug.log('Chart rendered successfully');

// This always shows (important warnings)
debug.warn('API rate limit approaching');

// This always shows (errors need attention)
debug.error('Failed to fetch data', error);
```

### Checking Current State

```javascript
// In browser console
localStorage.getItem('DEBUG_MODE')
// Returns: "true" (enabled) or null (disabled)
```

---

## 🛠️ Common Scenarios

### Scenario 1: Production Deployment

```bash
# Backend: Only show errors
export LOG_LEVEL=ERROR

# Frontend: Disable debug
# (Users should run in console):
localStorage.removeItem('DEBUG_MODE');
```

### Scenario 2: Development

```bash
# Backend: Show everything
export LOG_LEVEL=DEBUG

# Frontend: Enable debug
# (In browser console):
localStorage.setItem('DEBUG_MODE', 'true');
```

### Scenario 3: Troubleshooting Production Issue

```bash
# Temporarily enable verbose logging
LOG_LEVEL=DEBUG python3 app.py

# In affected user's browser console:
localStorage.setItem('DEBUG_MODE', 'true');
// Have them refresh and reproduce the issue
```

### Scenario 4: Performance Testing

```bash
# Backend: Minimal logging to reduce overhead
LOG_LEVEL=CRITICAL python3 app.py

# Frontend: Disabled
localStorage.removeItem('DEBUG_MODE');
```

---

## 📊 What Gets Logged?

### Backend (Python)

| Component | Info Logged |
|-----------|-------------|
| Security | Prompt injection attempts, validation failures |
| Chat | User questions, response types, success/failure |
| Analysis | Stock analysis requests, tickers analyzed |
| Market Data | API calls, rate limits, cache hits |
| Errors | Exceptions, stack traces, error context |

### Frontend (JavaScript)

| Component | Info Logged (Debug Mode) |
|-----------|--------------------------|
| Charts | Rendering, updates, indicator changes |
| Theme | Theme switches, chart refreshes |
| Exchange Rates | API calls, cache status |
| Chat | Message sending, history loading |
| Market Sentiment | Data fetching, recommendations |

---

## 🔍 Finding What You Need

### View Recent Backend Logs

```bash
# Last 50 lines of today's log
tail -n 50 logs/finbert_app_$(date +%Y%m%d).log

# Follow logs in real-time
tail -f logs/finbert_app_$(date +%Y%m%d).log

# Search for errors
grep ERROR logs/finbert_app_$(date +%Y%m%d).log

# Search for specific ticker
grep "AAPL" logs/finbert_app_$(date +%Y%m%d).log
```

### View Security Events

```bash
# Security log (only warnings and errors)
cat logs/security_$(date +%Y%m%d).log

# Recent security events
tail -n 20 logs/security_$(date +%Y%m%d).log
```

### Browser Console Filtering

In browser DevTools (F12):
- Click the filter icon
- Enter search terms like: `Chart`, `Error`, `Market`
- Use log level filters: All, Info, Warnings, Errors

---

## ⚙️ Advanced Configuration

### Custom Log Format

Edit `src/logging_config.py`:

```python
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# Change to:
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'  # Simpler format
```

### Module-Specific Log Levels

```python
# In app.py or any module
import logging

# Set specific logger to DEBUG
logging.getLogger('market_sentiment').setLevel(logging.DEBUG)

# Quiet a noisy module
logging.getLogger('yfinance').setLevel(logging.ERROR)
```

### Disable Specific Console Logs

To keep some console.logs even when DEBUG_MODE is off:

```javascript
// Current (respects DEBUG_MODE):
debug.log('Something happened');

// Always show (bypass DEBUG_MODE):
console.log('Critical system message');
```

---

## 🚨 Troubleshooting

### "Logs are still verbose even with LOG_LEVEL=ERROR"

**Check:**
1. Environment variable is set: `echo $LOG_LEVEL`
2. Restart the Flask app after changing
3. Some libraries (like yfinance) may log independently

**Solution:**
```python
# Add to app.py
import logging
logging.getLogger('yfinance').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
```

### "Browser console still shows logs after disabling DEBUG_MODE"

**Check:**
1. Did you refresh the page? (`Cmd/Ctrl + R`)
2. Check the value: `localStorage.getItem('DEBUG_MODE')`
3. Hard refresh to clear cache: `Cmd/Ctrl + Shift + R`

**Solution:**
```javascript
// Clear and verify
localStorage.removeItem('DEBUG_MODE');
location.reload(true);  // Force reload
```

### "Can't find log files"

**Check:**
```bash
# List log directory
ls -la logs/

# Check if logs directory exists
test -d logs && echo "Exists" || echo "Missing"
```

**Solution:**
```bash
# Create logs directory
mkdir -p logs
chmod 755 logs

# Restart app
python3 app.py
```

---

## 📋 Quick Reference

```bash
# Backend
LOG_LEVEL=ERROR   # Production (quiet)
LOG_LEVEL=INFO    # Default
LOG_LEVEL=DEBUG   # Development (verbose)

# Frontend (in browser console)
localStorage.setItem('DEBUG_MODE', 'true');    // Enable
localStorage.removeItem('DEBUG_MODE');         // Disable

# Check logs
tail -f logs/finbert_app_$(date +%Y%m%d).log   // Follow backend
grep ERROR logs/*.log                           // Find errors
```

---

## 💡 Best Practices

1. **Production**: Use `LOG_LEVEL=ERROR` or `WARNING`
2. **Development**: Use `LOG_LEVEL=DEBUG` with frontend DEBUG_MODE enabled
3. **Review Security Logs**: Check `logs/security_*.log` regularly
4. **Rotate Logs**: Set up log rotation (e.g., logrotate on Linux)
5. **Monitor Disk Usage**: Log files can grow large over time

---

## 🔗 Related Files

- **Backend Logging**: `src/logging_config.py`
- **Backend Config**: `src/config.py`
- **Frontend Debug**: `static/js/app.js` (lines 1-16)
- **Log Files**: `logs/` directory

---

**Last Updated**: October 2025  
**Version**: 1.0
