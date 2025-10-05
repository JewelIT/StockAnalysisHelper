#!/usr/bin/env python3
"""
Log Analysis Tool for FinBERT Chatbot
Analyzes unanswered questions to identify patterns and improve the bot
"""
import os
import sys
from datetime import datetime
from logging_config import analyze_unanswered_questions
import json

def get_latest_log_file():
    """Find the most recent log file"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        print(f"❌ Log directory '{log_dir}' not found")
        return None
    
    log_files = [f for f in os.listdir(log_dir) if f.startswith('finbert_app_') and f.endswith('.log')]
    if not log_files:
        print("❌ No log files found")
        return None
    
    # Sort by date (filename format: finbert_app_YYYYMMDD.log)
    log_files.sort(reverse=True)
    return os.path.join(log_dir, log_files[0])

def print_analysis_report(analysis):
    """Print a formatted analysis report"""
    print("\n" + "=" * 80)
    print("📊 UNANSWERED QUESTIONS ANALYSIS REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if 'error' in analysis:
        print(f"\n❌ Error: {analysis['error']}")
        return
    
    if 'message' in analysis:
        print(f"\n✅ {analysis['message']}")
        return
    
    print(f"\n📈 Total Unanswered Questions: {analysis['total_unanswered']}")
    
    print("\n🔤 Most Common Words in Unanswered Questions:")
    print("-" * 80)
    for word, count in analysis['common_words']:
        print(f"  • {word:20} - {count:3} occurrences")
    
    print("\n❓ Question Type Patterns:")
    print("-" * 80)
    for pattern, count in analysis['question_patterns'].items():
        if count > 0:
            percentage = (count / analysis['total_unanswered']) * 100
            print(f"  • {pattern.upper():15} - {count:3} questions ({percentage:.1f}%)")
    
    print("\n💡 Sample Unanswered Questions:")
    print("-" * 80)
    for i, question in enumerate(analysis['sample_questions'], 1):
        print(f"  {i}. {question}")
    
    print("\n" + "=" * 80)
    print("📝 RECOMMENDATIONS:")
    print("=" * 80)
    
    # Generate recommendations based on patterns
    recommendations = []
    
    if analysis['question_patterns'].get('what', 0) > 5:
        recommendations.append("• Consider adding more 'What is...' definition handlers")
    
    if analysis['question_patterns'].get('how', 0) > 5:
        recommendations.append("• Users want process explanations - add more 'How to...' guides")
    
    if analysis['question_patterns'].get('should', 0) > 5:
        recommendations.append("• Many decision-seeking questions - enhance recommendation logic")
    
    if any(word in ['crypto', 'bitcoin', 'ethereum'] for word, _ in analysis['common_words'][:10]):
        recommendations.append("• High interest in crypto - consider expanding cryptocurrency content")
    
    if any(word in ['tax', 'taxes'] for word, _ in analysis['common_words'][:10]):
        recommendations.append("• Tax questions detected - add tax strategy content")
    
    if recommendations:
        for rec in recommendations:
            print(rec)
    else:
        print("  ✅ No specific patterns detected yet. Continue monitoring.")
    
    print("\n" + "=" * 80)

def export_analysis_json(analysis, output_file='logs/unanswered_analysis.json'):
    """Export analysis to JSON for further processing"""
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"\n💾 Analysis exported to: {output_file}")

if __name__ == "__main__":
    print("🔍 Finding latest log file...")
    log_file = get_latest_log_file()
    
    if not log_file:
        sys.exit(1)
    
    print(f"📂 Analyzing: {log_file}")
    
    analysis = analyze_unanswered_questions(log_file)
    print_analysis_report(analysis)
    
    # Export to JSON
    if analysis and 'error' not in analysis and 'message' not in analysis:
        export_analysis_json(analysis)
    
    print("\n✨ Analysis complete!\n")
