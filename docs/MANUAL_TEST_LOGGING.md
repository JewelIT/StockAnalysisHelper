# Manual Testing Instructions - Logging System & Developer Menu

## Test Date: October 11, 2025
## Feature: Logging Control System & Developer UI

---

## Prerequisites
- App running at http://localhost:5000
- Browser with Developer Tools (F12)

---

## Test 1: Developer Menu Visibility (with DEBUG_MODE)

### Steps:
1. Open browser to http://localhost:5000
2. Open Developer Console (F12)
3. In console, type:
   ```javascript
   localStorage.setItem('DEBUG_MODE', 'true');
   location.reload();
   ```
4. Click Settings icon (⚙️) in top navigation
5. Look for "Developer" tab in settings modal

### Expected Results:
- ✅ Developer tab should be VISIBLE in settings
- ✅ Tab should have code icon (</>) 
- ✅ Console should show "🐛 DEBUG MODE ENABLED 🐛" message

---

## Test 2: Developer Menu Content

### Steps:
1. With DEBUG_MODE enabled (from Test 1)
2. Open Settings > Developer tab
3. Review the content

### Expected Results:
- ✅ Frontend Debug toggle switch (should be ON)
- ✅ Current Status badge shows "Enabled" in green
- ✅ Backend Log Level selector (5 options)
- ✅ Command display field with copy button
- ✅ Quick reference table
- ✅ Documentation link

---

## Test 3: Frontend Debug Toggle

### Steps:
1. In Developer tab, toggle debug switch OFF
2. Check the toast notification
3. Reload page
4. Open console (F12)
5. Try clicking "Add Ticker" or other actions

### Expected Results:
- ✅ Toast says "Debug mode disabled. Reload page to apply."
- ✅ After reload, console should have NO debug.log messages
- ✅ Developer tab should be HIDDEN (no longer in settings)
- ✅ Only errors/warnings show in console

---

## Test 4: Backend Log Level Command

### Steps:
1. Enable DEBUG_MODE again (Test 1 steps)
2. Go to Settings > Developer
3. Change log level dropdown to "ERROR"
4. Click copy button
5. Check clipboard contains command

### Expected Results:
- ✅ Command updates to: `LOG_LEVEL=ERROR python3 app.py`
- ✅ Copy button shows success toast
- ✅ Command is in clipboard (paste in text editor to verify)

---

## Test 5: Toast Notifications Theme

### Steps:
1. Add a ticker (e.g., AAPL)
2. Check toast notification appearance
3. Go to Settings > Display
4. Change theme to Dark
5. Add another ticker (e.g., MSFT)
6. Compare toast appearance

### Expected Results:
- ✅ Light theme: Toast has light background with colored left border
- ✅ Dark theme: Toast has dark background with colored left border
- ✅ Success toast: Green border
- ✅ Error toast: Red border
- ✅ Info toast: Blue border
- ✅ Toast text is readable in both themes

---

## Test 6: Duplicate Toast Bug Fix

### Steps:
1. Open Market Sentiment section
2. Find a "Top Pick to Buy"
3. Click the "+" button to add to analysis
4. Count how many toast notifications appear

### Expected Results:
- ✅ Only ONE toast notification appears
- ✅ Toast says "[TICKER] added to analysis session"
- ✅ Ticker appears in analysis list

---

## Test 7: Developer Menu Hidden (without DEBUG_MODE)

### Steps:
1. Clear DEBUG_MODE:
   ```javascript
   localStorage.removeItem('DEBUG_MODE');
   location.reload();
   ```
2. Open Settings modal
3. Count tabs

### Expected Results:
- ✅ Developer tab is NOT visible
- ✅ Only 5 tabs show: Display, Charts, Newsfeeds, Portfolio, About
- ✅ No error in console about missing elements

---

## Test 8: Log Level Script

### Steps:
1. Stop the running app (Ctrl+C in terminal)
2. Run: `./set-log-level.sh help`
3. Run: `./set-log-level.sh quiet` (in background)
4. Check app console output
5. Try: `./set-log-level.sh verbose`

### Expected Results:
- ✅ Help shows all modes
- ✅ Quiet mode: App starts with "Log Level: ERROR"
- ✅ Verbose mode: App starts with "Log Level: DEBUG"
- ✅ App runs successfully in each mode

---

## Test 9: Console Log Filtering

### Steps:
1. Enable DEBUG_MODE
2. Reload page
3. Open console, count debug messages
4. Disable DEBUG_MODE
5. Reload page
6. Check console again

### Expected Results:
- ✅ With DEBUG_MODE: Many debug.log() messages visible
- ✅ Without DEBUG_MODE: No debug.log() messages
- ✅ Errors/warnings always visible regardless of DEBUG_MODE

---

## Test 10: Settings Persistence

### Steps:
1. Set DEBUG_MODE to true
2. Change backend log level to WARNING
3. Close browser completely
4. Reopen browser to app
5. Check localStorage

### Expected Results:
- ✅ DEBUG_MODE persists (Developer tab visible)
- ✅ Backend log level command remembered in UI
- ✅ All settings remembered across sessions

---

## Regression Tests

### Quick checks to ensure nothing broke:
- ✅ Add ticker still works
- ✅ Remove ticker still works
- ✅ Analyze button works
- ✅ Chart displays correctly
- ✅ Market sentiment loads
- ✅ Portfolio management works
- ✅ Theme switching works
- ✅ Chat panel opens/closes

---

## Test Results Summary

| Test | Status | Notes |
|------|--------|-------|
| 1. Developer Menu Visibility | ⬜ | |
| 2. Developer Menu Content | ⬜ | |
| 3. Frontend Debug Toggle | ⬜ | |
| 4. Backend Log Command | ⬜ | |
| 5. Toast Theme | ⬜ | |
| 6. No Duplicate Toast | ⬜ | |
| 7. Menu Hidden (no debug) | ⬜ | |
| 8. Log Level Script | ⬜ | |
| 9. Console Log Filtering | ⬜ | |
| 10. Settings Persistence | ⬜ | |

---

## Issues Found

_(Document any issues discovered during testing)_

1. 
2. 
3. 

---

## Sign-off

- Tester: ________________
- Date: ________________
- Build: feature/chatbot branch
- Result: ⬜ PASS  ⬜ FAIL  ⬜ PARTIAL

---

## Notes for Next Steps

After all tests pass:
1. Commit logging system changes
2. Commit developer menu changes
3. Commit toast fixes
4. Commit test files
5. Push to remote
6. Move to next reorganization phase
