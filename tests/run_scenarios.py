#!/usr/bin/env python3
"""
Vestor E2E Conversation Test Runner

Automatically discovers and runs all conversation scenarios in the
conversation_scenarios directory.

Usage:
    python run_scenarios.py                    # Run all scenarios
    python run_scenarios.py --quick            # Run only quick/smoke tests
    python run_scenarios.py --tags beginner    # Run scenarios with 'beginner' tag
    python run_scenarios.py --list             # List all available scenarios
"""

import sys
import os
import time
import importlib
import inspect
from pathlib import Path
from typing import List, Dict
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conversation_scenarios.base import ConversationScenario


def discover_scenarios() -> List[ConversationScenario]:
    """
    Automatically discover all scenario classes in the conversation_scenarios directory
    """
    scenarios = []
    scenarios_dir = Path(__file__).parent / "conversation_scenarios"
    
    # Get all Python files in the directory
    for file_path in scenarios_dir.glob("*.py"):
        if file_path.name.startswith("_") or file_path.name == "base.py":
            continue  # Skip __init__.py and base.py
        
        # Import the module
        module_name = file_path.stem
        try:
            module = importlib.import_module(f"conversation_scenarios.{module_name}")
            
            # Find all classes that inherit from ConversationScenario
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, ConversationScenario) and 
                    obj is not ConversationScenario and
                    not inspect.isabstract(obj)):
                    
                    # Instantiate the scenario
                    scenario_instance = obj()
                    scenarios.append(scenario_instance)
                    
        except Exception as e:
            print(f"⚠️ Warning: Could not load scenario from {file_path.name}: {str(e)}")
    
    return scenarios


def list_scenarios(scenarios: List[ConversationScenario]):
    """List all available scenarios"""
    print("\n" + "="*80)
    print("AVAILABLE CONVERSATION SCENARIOS")
    print("="*80 + "\n")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario.name}")
        if scenario.description:
            print(f"   Description: {scenario.description}")
        if scenario.user_persona:
            print(f"   Persona: {scenario.user_persona}")
        if scenario.tags:
            print(f"   Tags: {', '.join(scenario.tags)}")
        print()
    
    print(f"Total: {len(scenarios)} scenarios")
    print("="*80 + "\n")


def filter_scenarios(scenarios: List[ConversationScenario], 
                     tags: List[str] = None,
                     quick_only: bool = False) -> List[ConversationScenario]:
    """Filter scenarios by tags"""
    filtered = scenarios
    
    if quick_only:
        filtered = [s for s in filtered if 'quick' in s.tags or 'smoke' in s.tags]
    
    if tags:
        filtered = [s for s in filtered 
                   if any(tag in s.tags for tag in tags)]
    
    return filtered


def run_scenarios(scenarios: List[ConversationScenario]) -> Dict:
    """
    Run all provided scenarios and collect results
    """
    print("\n\n" + "#"*80)
    print("VESTOR E2E CONVERSATION TEST SUITE")
    print("Testing realistic multi-turn conversations with follow-ups")
    print("#"*80 + "\n")
    
    results = []
    start_time = time.time()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'*'*80}")
        print(f"[{i}/{len(scenarios)}] Starting: {scenario.name}")
        print(f"{'*'*80}\n")
        
        try:
            # Run the scenario
            session = scenario.run()
            
            # Collect stats
            stats = session.get_stats()
            
            results.append({
                'name': scenario.name,
                'status': 'PASS' if stats['loops_detected'] == 0 and stats['errors'] == 0 else 'FAIL',
                'messages': stats['total_messages'],
                'successful': stats['successful_responses'],
                'errors': stats['errors'],
                'loops': stats['loops_detected'],
                'duration': stats['duration_seconds'],
                'tags': scenario.tags
            })
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Test interrupted by user (Ctrl+C)")
            break
            
        except Exception as e:
            print(f"\n❌ SCENARIO FAILED WITH EXCEPTION: {str(e)}\n")
            results.append({
                'name': scenario.name,
                'status': 'ERROR',
                'error': str(e),
                'tags': scenario.tags
            })
    
    total_duration = time.time() - start_time
    
    # Print final summary
    print("\n\n" + "="*80)
    print("FINAL TEST RESULTS")
    print("="*80)
    print(f"{'Scenario':<40} {'Status':<8} {'Msgs':<6} {'Loops':<7} {'Time':<8}")
    print("-"*80)
    
    for result in results:
        name = result['name'][:38]
        status = result['status']
        messages = result.get('messages', 'N/A')
        loops = result.get('loops', 'N/A')
        duration = f"{result.get('duration', 0):.1f}s" if 'duration' in result else 'N/A'
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{name:<40} {status_icon} {status:<6} {messages:<6} {loops:<7} {duration:<8}")
    
    print("="*80)
    
    # Overall statistics
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    total = len(results)
    
    print(f"\nTotal Duration: {total_duration:.1f}s")
    print(f"Scenarios Run: {total}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  ⚠️ Errors: {errors}")
    print(f"Success Rate: {passed/total*100:.0f}%")
    
    if passed == total:
        print("\n🎉 ALL SCENARIOS PASSED! Vestor is conversing naturally!")
    elif errors > 0:
        print(f"\n⚠️ {errors} scenario(s) encountered errors.")
    else:
        print(f"\n❌ {failed} scenario(s) failed. See details above.")
    
    print("="*80 + "\n")
    
    return {
        'results': results,
        'passed': passed,
        'failed': failed,
        'errors': errors,
        'total': total,
        'duration': total_duration
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Run Vestor E2E conversation scenarios',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scenarios.py                   # Run all scenarios
  python run_scenarios.py --list            # List available scenarios
  python run_scenarios.py --quick           # Run quick smoke tests only
  python run_scenarios.py --tags beginner   # Run beginner scenarios
  python run_scenarios.py --tags crypto stocks  # Run crypto OR stock scenarios
        """
    )
    
    parser.add_argument('--list', action='store_true',
                       help='List all available scenarios and exit')
    parser.add_argument('--quick', action='store_true',
                       help='Run only quick/smoke test scenarios')
    parser.add_argument('--tags', nargs='+',
                       help='Run only scenarios with these tags')
    
    args = parser.parse_args()
    
    # Check if server is running
    print("🔍 Checking if Flask server is running...")
    import requests
    try:
        requests.get("http://localhost:5000/health", timeout=2)
        print("✅ Server is running\n")
    except:
        print("❌ Flask server is not running on http://localhost:5000")
        print("\nPlease start the server first:")
        print("  python3 app.py\n")
        sys.exit(1)
    
    # Discover all scenarios
    print("🔍 Discovering conversation scenarios...")
    scenarios = discover_scenarios()
    print(f"✅ Found {len(scenarios)} scenario(s)\n")
    
    if not scenarios:
        print("❌ No scenarios found in conversation_scenarios directory")
        print("Make sure you have scenario files that inherit from ConversationScenario")
        sys.exit(1)
    
    # Handle --list
    if args.list:
        list_scenarios(scenarios)
        sys.exit(0)
    
    # Filter scenarios
    filtered_scenarios = filter_scenarios(
        scenarios,
        tags=args.tags,
        quick_only=args.quick
    )
    
    if not filtered_scenarios:
        print(f"❌ No scenarios match the filters")
        if args.tags:
            print(f"   Tags: {', '.join(args.tags)}")
        if args.quick:
            print(f"   Quick only: Yes")
        sys.exit(1)
    
    if len(filtered_scenarios) < len(scenarios):
        print(f"🎯 Running {len(filtered_scenarios)} of {len(scenarios)} scenarios")
        if args.tags:
            print(f"   Filtered by tags: {', '.join(args.tags)}")
        if args.quick:
            print(f"   Quick tests only")
        print()
    
    # Run scenarios
    summary = run_scenarios(filtered_scenarios)
    
    # Exit with appropriate code
    if summary['errors'] > 0:
        sys.exit(2)  # Errors occurred
    elif summary['failed'] > 0:
        sys.exit(1)  # Tests failed
    else:
        sys.exit(0)  # All passed


if __name__ == '__main__':
    main()
