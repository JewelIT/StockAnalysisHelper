# 🎛️ Logging Control

Quick commands to control console/log output:

## Backend (Python Server)

```bash
# Quiet mode (production) - Only show errors
LOG_LEVEL=ERROR python3 app.py

# Normal mode (default) - Show info and above  
python3 app.py

# Verbose mode (development) - Show everything
LOG_LEVEL=DEBUG python3 app.py
```

Or use the helper script:
```bash
./set-log-level.sh quiet      # Production mode
./set-log-level.sh normal     # Default mode
./set-log-level.sh verbose    # Debug mode
./set-log-level.sh status     # Show current settings
```

## Frontend (Browser Console)

Open browser DevTools (F12) and run:

```javascript
// Enable debug logs
localStorage.setItem('DEBUG_MODE', 'true');
location.reload();

// Disable debug logs (quiet mode)
localStorage.removeItem('DEBUG_MODE');
location.reload();

// Check current status
localStorage.getItem('DEBUG_MODE')
```

## Log Files

All logs are saved to files regardless of console output level:

- **Application logs**: `logs/finbert_app_YYYYMMDD.log`
- **Security logs**: `logs/security_YYYYMMDD.log`

View recent logs:
```bash
tail -f logs/finbert_app_$(date +%Y%m%d).log
```

📖 **Full Documentation**: See [docs/LOGGING_CONTROL.md](docs/LOGGING_CONTROL.md)
