#!/bin/bash
# Run Vestor Conversation Tests
# This script runs all conversation test suites

echo "=============================================================================="
echo "VESTOR CONVERSATION TEST SUITE"
echo "=============================================================================="
echo ""

# Check if server is running
echo "🔍 Checking if Flask server is running..."
if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "❌ Flask server is not running on http://localhost:5000"
    echo ""
    echo "Please start the server first:"
    echo "  python3 app.py"
    echo ""
    exit 1
fi

echo "✅ Server is running"
echo ""

# Parse arguments
RUN_QUICK=true
RUN_FULL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            RUN_FULL=true
            shift
            ;;
        --quick-only)
            RUN_QUICK=true
            RUN_FULL=false
            shift
            ;;
        --help)
            echo "Usage: ./run_conversation_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --quick-only    Run only quick smoke tests (default)"
            echo "  --full          Run full E2E conversation scenarios"
            echo "  --help          Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run quick tests
if [ "$RUN_QUICK" = true ]; then
    echo "=============================================================================="
    echo "RUNNING QUICK CONVERSATION TESTS (Smoke Test)"
    echo "=============================================================================="
    echo ""
    python3 tests/quick_conversation_test.py
    QUICK_EXIT=$?
    echo ""
    
    if [ $QUICK_EXIT -ne 0 ]; then
        echo "⚠️ Quick tests encountered errors. Skipping full tests."
        echo "Fix the issues and try again."
        exit $QUICK_EXIT
    fi
fi

# Run full E2E tests if requested
if [ "$RUN_FULL" = true ]; then
    echo "=============================================================================="
    echo "RUNNING FULL E2E CONVERSATION SCENARIOS"
    echo "This will take several minutes..."
    echo "=============================================================================="
    echo ""
    python3 tests/e2e_conversation_scenarios.py
    FULL_EXIT=$?
    echo ""
    
    if [ $FULL_EXIT -ne 0 ]; then
        echo "❌ Full E2E tests encountered errors."
        exit $FULL_EXIT
    fi
fi

echo "=============================================================================="
echo "TEST RUN COMPLETE"
echo "=============================================================================="
echo ""

if [ "$RUN_FULL" = true ]; then
    echo "✅ Both quick and full tests completed successfully!"
else
    echo "✅ Quick tests completed successfully!"
    echo ""
    echo "💡 To run full E2E scenarios with realistic conversations, use:"
    echo "   ./run_conversation_tests.sh --full"
fi

echo ""
