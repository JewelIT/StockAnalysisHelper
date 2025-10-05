#!/usr/bin/env python3
"""
Quick test script for the chat system
"""
from src.stock_chat import StockChatAssistant

# Initialize chat assistant
chat = StockChatAssistant()
chat.load_model()

# Test educational questions
test_questions = [
    "I'm just starting investing, what do you suggest?",
    "Can you tell me about Microsoft investment stock?",
    "What books should I read?",
    "How do I manage risk?",
    "Explain what RSI means"
]

print("=" * 80)
print("TESTING EDUCATIONAL RESPONSES")
print("=" * 80)

for q in test_questions:
    print(f"\n📝 Question: {q}")
    print("-" * 80)
    response = chat.get_educational_response(q)
    print(response[:500] + "..." if len(response) > 500 else response)
    print("\n")
