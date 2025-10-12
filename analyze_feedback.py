#!/usr/bin/env python3
"""
Chat Feedback Analyzer

Analyzes feedback from chat-trainer to identify:
- Low-rated responses (need improvement)
- High-rated responses (doing well)
- Common patterns in good/bad responses
- Questions that consistently get poor ratings
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

def load_feedback(feedback_file='logs/chat_feedback.jsonl'):
    """Load all feedback from JSONL file"""
    feedback_path = Path(feedback_file)
    
    if not feedback_path.exists():
        print(f"❌ Feedback file not found: {feedback_file}")
        print("   Start collecting feedback at /chat-trainer first!")
        return []
    
    feedbacks = []
    with open(feedback_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                feedbacks.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"⚠️  Warning: Skipping invalid JSON on line {line_num}: {e}")
    
    return feedbacks


def analyze_feedback(feedbacks):
    """Analyze feedback and generate insights"""
    if not feedbacks:
        print("\n📊 No feedback data available yet.")
        return
    
    print(f"\n{'='*80}")
    print(f"📊 CHAT FEEDBACK ANALYSIS REPORT")
    print(f"{'='*80}\n")
    
    # Basic stats
    total_feedback = len(feedbacks)
    print(f"📈 Total Feedback Entries: {total_feedback}\n")
    
    # Rating distribution
    ratings = []
    helpful_count = 0
    unhelpful_count = 0
    
    for fb in feedbacks:
        rating = fb.get('feedback', {}).get('rating')
        if rating is not None:
            ratings.append(rating)
        
        helpful = fb.get('feedback', {}).get('helpful')
        if helpful is True:
            helpful_count += 1
        elif helpful is False:
            unhelpful_count += 1
    
    print(f"{'='*80}")
    print(f"⭐ RATING DISTRIBUTION")
    print(f"{'='*80}\n")
    
    if ratings:
        rating_counts = Counter(ratings)
        avg_rating = sum(ratings) / len(ratings)
        print(f"Average Rating: {avg_rating:.2f}/5.0\n")
        
        for rating in range(6):
            count = rating_counts.get(rating, 0)
            pct = (count / len(ratings)) * 100
            bar = '█' * int(pct / 2)
            print(f"  {rating} ⭐: {bar:25s} {count:3d} ({pct:5.1f}%)")
        print()
    
    print(f"👍 Helpful: {helpful_count}")
    print(f"👎 Unhelpful: {unhelpful_count}\n")
    
    # Identify problematic responses
    print(f"{'='*80}")
    print(f"🔴 LOW-RATED RESPONSES (Need Improvement)")
    print(f"{'='*80}\n")
    
    low_rated = []
    for fb in feedbacks:
        rating = fb.get('feedback', {}).get('rating', 5)
        if rating <= 2:
            interaction = fb.get('interaction', {})
            if interaction:
                low_rated.append({
                    'rating': rating,
                    'question': interaction.get('question', 'N/A'),
                    'answer': interaction.get('answer', 'N/A'),
                    'comment': fb.get('feedback', {}).get('comment', '')
                })
    
    if low_rated:
        for i, item in enumerate(low_rated[:10], 1):  # Show top 10
            print(f"#{i} Rating: {item['rating']}/5")
            print(f"   Q: {item['question'][:100]}...")
            print(f"   A: {item['answer'][:150]}...")
            if item['comment']:
                print(f"   💬 Comment: {item['comment']}")
            print()
    else:
        print("✅ No low-rated responses! All feedback is positive.\n")
    
    # High-rated responses
    print(f"{'='*80}")
    print(f"🟢 HIGH-RATED RESPONSES (Doing Well)")
    print(f"{'='*80}\n")
    
    high_rated = []
    for fb in feedbacks:
        rating = fb.get('feedback', {}).get('rating', 0)
        if rating >= 4:
            interaction = fb.get('interaction', {})
            if interaction:
                high_rated.append({
                    'rating': rating,
                    'question': interaction.get('question', 'N/A'),
                    'answer': interaction.get('answer', 'N/A')
                })
    
    if high_rated:
        print(f"✅ {len(high_rated)} responses rated 4-5 stars\n")
        for i, item in enumerate(high_rated[:5], 1):  # Show top 5
            print(f"#{i} Rating: {item['rating']}/5")
            print(f"   Q: {item['question'][:100]}...")
            print()
    else:
        print("⚠️  No high-rated responses yet.\n")
    
    # Question patterns
    print(f"{'='*80}")
    print(f"🔍 QUESTION PATTERNS")
    print(f"{'='*80}\n")
    
    question_keywords = defaultdict(list)
    for fb in feedbacks:
        interaction = fb.get('interaction', {})
        question = interaction.get('question', '').lower()
        rating = fb.get('feedback', {}).get('rating')
        
        if question and rating is not None:
            # Extract key words
            words = [w for w in question.split() if len(w) > 4]
            for word in words[:3]:  # First 3 meaningful words
                question_keywords[word].append(rating)
    
    # Find keywords associated with low ratings
    low_rated_keywords = []
    for keyword, ratings in question_keywords.items():
        if len(ratings) >= 2:  # At least 2 occurrences
            avg = sum(ratings) / len(ratings)
            if avg < 3.0:
                low_rated_keywords.append((keyword, avg, len(ratings)))
    
    if low_rated_keywords:
        low_rated_keywords.sort(key=lambda x: x[1])
        print("Keywords in low-rated questions:")
        for keyword, avg, count in low_rated_keywords[:10]:
            print(f"  • '{keyword}' - Avg rating: {avg:.1f} ({count} occurrences)")
        print()
    
    # Timeline
    print(f"{'='*80}")
    print(f"📅 FEEDBACK TIMELINE")
    print(f"{'='*80}\n")
    
    dates = defaultdict(lambda: {'count': 0, 'total_rating': 0, 'ratings': []})
    for fb in feedbacks:
        timestamp = fb.get('timestamp', '')
        rating = fb.get('feedback', {}).get('rating')
        
        if timestamp and rating is not None:
            date = timestamp[:10]  # YYYY-MM-DD
            dates[date]['count'] += 1
            dates[date]['total_rating'] += rating
            dates[date]['ratings'].append(rating)
    
    if dates:
        for date in sorted(dates.keys()):
            data = dates[date]
            avg = data['total_rating'] / data['count']
            print(f"  {date}: {data['count']} feedback(s), Avg rating: {avg:.2f}")
        print()
    
    # Recommendations
    print(f"{'='*80}")
    print(f"💡 RECOMMENDATIONS")
    print(f"{'='*80}\n")
    
    if avg_rating < 3.0 if ratings else False:
        print("⚠️  CRITICAL: Average rating is below 3.0")
        print("   → Review low-rated responses and identify common issues")
        print("   → Consider expanding knowledge base for problematic topics\n")
    elif avg_rating < 4.0 if ratings else False:
        print("⚠️  WARNING: Average rating is below 4.0")
        print("   → Room for improvement - analyze patterns in feedback\n")
    else:
        print("✅ Good job! Average rating is 4.0 or higher")
        print("   → Continue monitoring feedback for any issues\n")
    
    if low_rated:
        print(f"📝 Action Items:")
        print(f"   1. Review {len(low_rated)} low-rated responses")
        print(f"   2. Identify common failure patterns")
        print(f"   3. Expand knowledge base for weak areas")
        print(f"   4. Test improved responses with users\n")
    
    print(f"{'='*80}\n")


def export_for_training(feedbacks, output_file='logs/training_data.json'):
    """Export structured data for model fine-tuning"""
    training_data = []
    
    for fb in feedbacks:
        interaction = fb.get('interaction', {})
        rating = fb.get('feedback', {}).get('rating')
        helpful = fb.get('feedback', {}).get('helpful')
        
        if interaction and rating is not None:
            training_data.append({
                'question': interaction.get('question'),
                'answer': interaction.get('answer'),
                'rating': rating,
                'helpful': helpful,
                'comment': fb.get('feedback', {}).get('comment'),
                'timestamp': fb.get('timestamp')
            })
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exported {len(training_data)} entries to {output_file}")


def main():
    """Main analysis function"""
    feedback_file = 'logs/chat_feedback.jsonl'
    
    # Check command line args
    if len(sys.argv) > 1:
        feedback_file = sys.argv[1]
    
    print(f"\n📂 Loading feedback from: {feedback_file}")
    
    feedbacks = load_feedback(feedback_file)
    
    if feedbacks:
        analyze_feedback(feedbacks)
        
        # Ask if user wants to export
        print("\n💾 Export training data? (y/n): ", end='')
        try:
            response = input().strip().lower()
            if response == 'y':
                export_for_training(feedbacks)
        except (EOFError, KeyboardInterrupt):
            print("\nSkipping export.")
    else:
        print("\n💡 Tip: Visit /chat-trainer to start collecting feedback!")
    
    print()


if __name__ == '__main__':
    main()
