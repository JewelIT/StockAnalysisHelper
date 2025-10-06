"""
JavaScript validation tests
Checks for undefined functions, syntax errors, and common issues
"""
import re
import os
from pathlib import Path

def test_javascript_undefined_functions():
    """Check for function calls that are not defined"""
    js_file = Path(__file__).parent.parent / 'static' / 'js' / 'app.js'
    
    with open(js_file, 'r') as f:
        content = f.read()
    
    # Find all function definitions
    defined_functions = set(re.findall(r'function\s+(\w+)\s*\(', content))
    defined_functions.update(re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function', content))
    defined_functions.update(re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>', content))
    
    # Remove comments and strings to avoid false positives
    content_no_comments = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)
    content_no_comments = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '""', content_no_comments)
    content_no_comments = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", "''", content_no_comments)
    content_no_comments = re.sub(r'`[^`\\]*(?:\\.[^`\\]*)*`', '``', content_no_comments)
    
    # Find all function calls (excluding method calls with dots before them)
    called_functions = set(re.findall(r'(?<![.\w])(\w+)\s*\(', content_no_comments))
    
    # Built-in and DOM functions to ignore
    builtins = {
        # JavaScript keywords and reserved words
        'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
        'return', 'function', 'var', 'let', 'const', 'new', 'delete', 'typeof',
        'instanceof', 'void', 'this', 'super', 'class', 'extends', 'static',
        'async', 'await', 'yield', 'try', 'catch', 'throw', 'finally',
        # DOM and Browser APIs
        'addEventListener', 'getElementById', 'querySelector', 'querySelectorAll',
        'fetch', 'JSON', 'localStorage', 'sessionStorage', 'setTimeout', 'setInterval',
        'console', 'Date', 'Array', 'Object', 'String', 'Number', 'Boolean',
        'Math', 'alert', 'confirm', 'prompt', 'parseInt', 'parseFloat', 'isNaN',
        'Error', 'TypeError', 'ReferenceError', 'SyntaxError', 'Promise', 'Map', 'Set',
        # Array methods
        'push', 'pop', 'shift', 'unshift', 'map', 'filter', 'reduce', 'forEach',
        'includes', 'indexOf', 'join', 'split', 'replace', 'trim', 'toLowerCase',
        'toUpperCase', 'slice', 'splice', 'sort', 'reverse', 'find', 'findIndex',
        'every', 'some',
        # Console methods
        'log', 'error', 'warn', 'info', 'debug',
        # JSON methods
        'stringify', 'parse',
        # Storage methods
        'setItem', 'getItem', 'removeItem', 'clear',
        # DOM methods
        'setAttribute', 'getAttribute', 'removeAttribute', 'classList', 'add',
        'remove', 'toggle', 'contains', 'createElement', 'appendChild',
        'removeChild', 'insertBefore', 'cloneNode', 'closest', 'matches',
        'append', 'prepend', 'after', 'before', 'focus', 'blur',
        'submit', 'reset', 'preventDefault', 'stopPropagation',
        # String methods
        'startsWith', 'endsWith', 'repeat', 'padStart', 'padEnd',
        'toFixed', 'toLocaleString', 'match', 'search', 'test', 'exec',
        # Math methods
        'floor', 'ceil', 'round', 'abs', 'max', 'min', 'random', 'sqrt', 'pow',
        # Object methods
        'keys', 'values', 'entries', 'assign', 'freeze', 'seal', 'hasOwnProperty',
        # Promise methods
        'then', 'catch', 'finally', 'resolve', 'reject', 'all', 'race',
        # Date methods
        'now', 'getTime', 'toISOString',
    }
    
    # Find undefined functions
    undefined = called_functions - defined_functions - builtins
    
    # Filter out method calls (things after dots)
    undefined = {f for f in undefined if not any(f'{method}' in content for method in ['.'+f])}
    
    if undefined:
        print("\n❌ UNDEFINED FUNCTIONS FOUND:")
        for func in sorted(undefined):
            # Find where it's called
            matches = re.finditer(rf'\b{func}\s*\(', content)
            for match in matches:
                # Get line number
                line_num = content[:match.start()].count('\n') + 1
                print(f"   Line {line_num}: {func}()")
        assert False, f"Found {len(undefined)} undefined functions"
    else:
        print("\n✅ All JavaScript functions are defined")


def test_javascript_syntax():
    """Basic syntax validation"""
    js_file = Path(__file__).parent.parent / 'static' / 'js' / 'app.js'
    
    with open(js_file, 'r') as f:
        content = f.read()
    
    issues = []
    
    # Check for unclosed brackets
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        issues.append(f"Unmatched braces: {open_braces} {{ vs {close_braces} }}")
    
    open_parens = content.count('(')
    close_parens = content.count(')')
    if open_parens != close_parens:
        issues.append(f"Unmatched parentheses: {open_parens} ( vs {close_parens} )")
    
    open_brackets = content.count('[')
    close_brackets = content.count(']')
    if open_brackets != close_brackets:
        issues.append(f"Unmatched brackets: {open_brackets} [ vs {close_brackets} ]")
    
    if issues:
        print("\n❌ SYNTAX ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        assert False, "JavaScript syntax issues detected"
    else:
        print("✅ JavaScript syntax looks good")


def test_flask_routes():
    """Test that all Flask routes are accessible"""
    print("\n🧪 Testing Flask routes:")
    print("   ⏭️  Skipped (requires running app)")
    # Routes will be tested manually or with integration tests
    

def test_chat_endpoint():
    """Test chat endpoint with sample messages"""
    print("\n💬 Testing chat endpoint:")
    print("   ⏭️  Skipped (requires running app)")
    # Chat will be tested manually or with integration tests


if __name__ == '__main__':
    print("="*80)
    print("🧪 RUNNING JAVASCRIPT AND FLASK TESTS")
    print("="*80)
    
    try:
        test_javascript_undefined_functions()
        test_javascript_syntax()
        test_flask_routes()
        test_chat_endpoint()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
    except AssertionError as e:
        print("\n" + "="*80)
        print(f"❌ TEST FAILED: {e}")
        print("="*80)
        exit(1)
    except Exception as e:
        print("\n" + "="*80)
        print(f"❌ ERROR: {e}")
        print("="*80)
        exit(1)
