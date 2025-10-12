#!/usr/bin/env python3
"""
Test runner for FinBERT Portfolio Analyzer / Vestor AI
Runs all test suites and provides summary
"""
import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """Run all test suites"""
    print("="*80)
    print("🧪 FINBERT PORTFOLIO ANALYZER - TEST SUITE")
    print("="*80)
    print()
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"✅ Tests run: {result.testsRun}")
    print(f"{'✅' if result.wasSuccessful() else '❌'} Successful: {result.wasSuccessful()}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"❌ Errors: {len(result.errors)}")
    print("="*80)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
