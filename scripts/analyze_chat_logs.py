#!/usr/bin/env python3
"""
Analyze chat logs to understand user interactions and identify issues

Usage:
    python scripts/analyze_chat_logs.py
    python scripts/analyze_chat_logs.py --date 20251012
    python scripts/analyze_chat_logs.py --recent 100
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict


def load_conversations(log_dir, date_filter=None, recent=None):
    """Load conversations from JSONL files"""
    conversations = []
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"❌ Log directory not found: {log_dir}")
        return conversations
    
    # Find log files
    if date_filter:
        files = [log_path / f'conversations_{date_filter}.jsonl']
    else:
        files = sorted(log_path.glob('conversations_*.jsonl'), reverse=True)
    
    # Load conversations
    for file in files:
        if file.exists():
            print(f"📂 Reading: {file.name}")
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        conv = json.loads(line.strip())
                        conversations.append(conv)
                    except json.JSONDecodeError:
                        continue
    
    # Return most recent if specified
    if recent:
        conversations = conversations[-recent:]
    
    return conversations


def analyze_conversations(conversations):
    """Analyze conversation patterns"""
    if not conversations:
        print("❌ No conversations to analyze")
        return
    
    print(f"\n{'='*80}")
    print(f"📊 CONVERSATION ANALYSIS")
    print(f"{'='*80}\n")
    
    # Basic stats
    total = len(conversations)
    print(f"**Total Conversations:** {total}")
    
    # Time range
    if total > 0:
        timestamps = [datetime.fromisoformat(c['timestamp']) for c in conversations]
        earliest = min(timestamps)
        latest = max(timestamps)
        print(f"**Time Range:** {earliest.strftime('%Y-%m-%d %H:%M')} to {latest.strftime('%Y-%m-%d %H:%M')}")
    
    # Vestor modes
    print(f"\n### Vestor Modes:")
    modes = Counter(c['vestor_mode'] for c in conversations)
    for mode, count in modes.most_common():
        pct = (count/total)*100
        print(f"  - **{mode}**: {count} ({pct:.1f}%)")
    
    # Tickers mentioned
    print(f"\n### Tickers Discussed:")
    tickers = Counter(c['ticker'] for c in conversations if c.get('ticker'))
    if tickers:
        for ticker, count in tickers.most_common(10):
            print(f"  - **{ticker}**: {count} times")
    else:
        print("  - No tickers mentioned")
    
    # Question types (analyze first words)
    print(f"\n### Question Patterns:")
    question_starters = Counter()
    for c in conversations:
        question = c['question'].lower().strip()
        first_word = question.split()[0] if question else ''
        if first_word:
            question_starters[first_word] += 1
    
    for word, count in question_starters.most_common(10):
        print(f"  - **{word}**: {count} questions")
    
    # Answer lengths
    print(f"\n### Response Lengths:")
    lengths = [c['answer_length'] for c in conversations]
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    min_length = min(lengths) if lengths else 0
    max_length = max(lengths) if lengths else 0
    print(f"  - **Average**: {avg_length:.0f} characters")
    print(f"  - **Min**: {min_length} characters")
    print(f"  - **Max**: {max_length} characters")
    
    # Short responses (potential issues)
    short_responses = [c for c in conversations if c['answer_length'] < 200]
    if short_responses:
        print(f"\n⚠️ **Short Responses ({len(short_responses)} found):**")
        for c in short_responses[:5]:  # Show first 5
            print(f"  - Q: \"{c['question'][:60]}...\"")
            print(f"    A: \"{c['answer'][:60]}...\" ({c['answer_length']} chars)")
    
    # Sample recent conversations
    print(f"\n### Recent Conversations (last 5):")
    for c in conversations[-5:]:
        ts = datetime.fromisoformat(c['timestamp']).strftime('%H:%M:%S')
        ticker_info = f" [{c['ticker']}]" if c.get('ticker') else ""
        print(f"\n  **[{ts}]{ticker_info} User:** {c['question'][:70]}...")
        print(f"  **Vestor:** {c['answer'][:150]}...")


def find_problematic_responses(conversations):
    """Identify potentially problematic responses"""
    print(f"\n{'='*80}")
    print(f"🔍 POTENTIAL ISSUES")
    print(f"{'='*80}\n")
    
    issues = []
    
    for c in conversations:
        question = c['question'].lower()
        answer = c['answer'].lower()
        
        # Check for generic/unhelpful responses
        generic_phrases = [
            'i can help you with',
            'how can i help',
            'what would you like to know',
            'being analyzed',
            'being assessed'
        ]
        
        for phrase in generic_phrases:
            if phrase in answer:
                issues.append({
                    'type': 'Generic Response',
                    'question': c['question'][:60],
                    'answer': c['answer'][:100],
                    'phrase': phrase
                })
                break
        
        # Check for very short answers to specific questions
        if len(c['answer']) < 150 and any(word in question for word in ['what', 'how', 'why', 'explain']):
            issues.append({
                'type': 'Short Answer',
                'question': c['question'][:60],
                'answer': c['answer'][:100],
                'length': c['answer_length']
            })
        
        # Check for information dumps (very long responses)
        if c['answer_length'] > 2000:
            issues.append({
                'type': 'Very Long Response',
                'question': c['question'][:60],
                'length': c['answer_length']
            })
    
    if issues:
        print(f"Found {len(issues)} potential issues:\n")
        
        issue_types = Counter(i['type'] for i in issues)
        for issue_type, count in issue_types.most_common():
            print(f"**{issue_type}:** {count}")
            # Show examples
            examples = [i for i in issues if i['type'] == issue_type][:3]
            for ex in examples:
                print(f"  - Q: \"{ex['question']}...\"")
                if 'phrase' in ex:
                    print(f"    Problem: Contains \"{ex['phrase']}\"")
                if 'length' in ex:
                    print(f"    Length: {ex['length']} chars")
                print()
    else:
        print("✅ No obvious issues detected")


def export_for_review(conversations, output_file):
    """Export conversations in readable format for manual review"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# CHAT CONVERSATION REVIEW\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Conversations: {len(conversations)}\n\n")
        f.write("="*80 + "\n\n")
        
        for i, c in enumerate(conversations, 1):
            ts = datetime.fromisoformat(c['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"## Conversation {i}\n\n")
            f.write(f"**Time:** {ts}\n")
            f.write(f"**Mode:** {c['vestor_mode']}\n")
            if c.get('ticker'):
                f.write(f"**Ticker:** {c['ticker']}\n")
            f.write(f"\n**USER:** {c['question']}\n\n")
            f.write(f"**VESTOR:** {c['answer']}\n\n")
            f.write("="*80 + "\n\n")
    
    print(f"✅ Exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Analyze chat conversation logs')
    parser.add_argument('--date', help='Analyze specific date (YYYYMMDD)')
    parser.add_argument('--recent', type=int, help='Analyze N most recent conversations')
    parser.add_argument('--export', help='Export conversations to file for review')
    parser.add_argument('--log-dir', default='logs/chat_interactions', help='Log directory path')
    
    args = parser.parse_args()
    
    # Load conversations
    conversations = load_conversations(args.log_dir, args.date, args.recent)
    
    if not conversations:
        print("❌ No conversations found")
        return
    
    # Analyze
    analyze_conversations(conversations)
    find_problematic_responses(conversations)
    
    # Export if requested
    if args.export:
        export_for_review(conversations, args.export)


if __name__ == '__main__':
    main()
