# Enhanced Chat Endpoint - Add this to app.py

@app.route('/chat', methods=['POST'])
def chat():
    """AI chat endpoint - Educational and conversational"""
    global chat_assistant, analysis_cache
    
    data = request.get_json()
    question = data.get('question', '')
    ticker = data.get('ticker', '')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    # Initialize chat assistant if needed
    if chat_assistant is None:
        try:
            chat_assistant = StockChatAssistant()
            chat_assistant.load_model()
        except Exception as e:
            return jsonify({'error': f'Could not load chat model: {str(e)}'}), 500
    
    question_lower = question.lower()
    
    # Detect if it's an educational/general question (priority)
    educational_keywords = [
        'learn', 'beginner', 'start', 'how to invest', 'what is', 'explain',
        'diversif', 'risk', 'safe', 'protect', 'scam', 'ethical', 'book',
        'resource', 'course', 'understand', 'technical analysis', 'fundamental'
    ]
    
    is_educational = any(keyword in question_lower for keyword in educational_keywords)
    
    # If it's clearly educational, provide educational response
    if is_educational and not ticker:
        educational_response = chat_assistant.get_educational_response(question)
        return jsonify({
            'question': question,
            'answer': educational_response,
            'ticker': '',
            'success': True,
            'educational': True
        })
    
    # Extract ticker from question if none provided
    if not ticker:
        import re
        ticker_pattern = r'\b([A-Z]{2,5}(?:[-\.][A-Z]{2,4})?)\b'
        potential_tickers = re.findall(ticker_pattern, question)
        
        if potential_tickers:
            ticker = potential_tickers[0]
    
    # If ticker found but not analyzed, offer background analysis
    if ticker and ticker not in analysis_cache:
        return jsonify({
            'question': question,
            'answer': f'🔍 I can analyze **{ticker}** for you!\n\nWould you like me to:\n\n1️⃣ **Analyze in background** - I\'ll fetch the data quietly and answer your question\n2️⃣ **Full analysis with charts** - Display complete analysis on the main screen\n\nJust reply with "background" or "full analysis" (or I\'ll do background by default).',
            'ticker': ticker,
            'success': True,
            'needs_confirmation': True,
            'pending_ticker': ticker
        })
    
    # If no ticker and no educational intent, check if they have analyzed stocks
    if not ticker:
        if analysis_cache:
            available_tickers = ', '.join(analysis_cache.keys())
            return jsonify({
                'question': question,
                'answer': f'💡 I have analysis for: **{available_tickers}**\n\nYour question "{question}" - which stock were you asking about? Or mention any ticker to analyze!\n\n*Tip: I can also answer general investment questions!*',
                'ticker': '',
                'success': True,
                'general_response': True
            })
        else:
            return jsonify({
                'question': question,
                'answer': '👋 I can help in two ways:\n\n**📚 General Investment Education:**\nAsk me about investing basics, risk management, technical analysis, or recommend books and resources.\n\n**📊 Specific Stock Analysis:**\nMention any ticker (e.g., "What about AAPL?") and I\'ll analyze it for you!\n\nWhat would you like to know?',
                'ticker': '',
                'success': True,
                'general_response': True
            })
    
    # We have a ticker and it's analyzed - answer the question
    cached_result = analysis_cache[ticker]['result']
    context = chat_assistant.generate_context_from_analysis(cached_result)
    
    # Answer the question
    result = chat_assistant.answer_question(question, context, ticker)
    
    return jsonify({
        'question': question,
        'answer': result['answer'],
        'ticker': ticker,
        'success': result['success'],
        'confidence': result.get('confidence', 0)
    })
