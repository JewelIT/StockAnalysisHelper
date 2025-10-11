#!/bin/bash
# Quick script to run app with specific logging level

# Function to show current settings
show_status() {
    echo "Current Environment:"
    echo "  LOG_LEVEL: ${LOG_LEVEL:-INFO (default)}"
    echo "  Log files: logs/"
    echo ""
    echo "Frontend Debug Mode (set in browser console):"
    echo "  localStorage.setItem('DEBUG_MODE', 'true');   // Enable"
    echo "  localStorage.removeItem('DEBUG_MODE');        // Disable"
    echo ""
}

# Parse arguments
case "$1" in
    "quiet"|"production")
        echo "🔇 Running in QUIET mode (ERROR level only)"
        LOG_LEVEL=ERROR python3 app.py
        ;;
    
    "normal"|"default")
        echo "📢 Running in NORMAL mode (INFO level)"
        LOG_LEVEL=INFO python3 app.py
        ;;
    
    "verbose"|"debug"|"development")
        echo "🔊 Running in VERBOSE mode (DEBUG level - everything)"
        LOG_LEVEL=DEBUG python3 app.py
        ;;
    
    "status")
        show_status
        ;;
    
    "help"|"--help"|"-h"|"")
        echo "=========================================="
        echo "FinBERT Logging Control"
        echo "=========================================="
        echo ""
        echo "Usage: $0 [mode]"
        echo ""
        echo "Modes:"
        echo "  quiet       - ERROR only (production)"
        echo "  normal      - INFO level (default)"
        echo "  verbose     - DEBUG level (development)"
        echo "  status      - Show current env settings"
        echo "  help        - Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 quiet                    # Run app in quiet mode"
        echo "  $0 verbose                  # Run app with debug logs"
        echo "  LOG_LEVEL=ERROR python3 app.py  # Direct method"
        echo ""
        echo "Frontend Debugging:"
        echo "  Open browser console (F12) and run:"
        echo "    localStorage.setItem('DEBUG_MODE', 'true');   // Enable"
        echo "    localStorage.removeItem('DEBUG_MODE');        // Disable"
        echo "    location.reload();                            // Apply changes"
        echo ""
        ;;
    
    *)
        echo "❌ Unknown mode: $1"
        echo "Run '$0 help' for usage"
        exit 1
        ;;
esac
