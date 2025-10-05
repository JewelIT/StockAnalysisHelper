// Enhanced Conversational Chat System
// Track conversation context for fluid, mentor-style interactions

let conversationContext = {
    lastTicker: null,
    lastTopic: null,
    analyzedTickers: [],
    conversationHistory: []
};

// Override the existing sendChatMessage function
window.sendChatMessage = async function() {
    const input = document.getElementById('chatInput');
    const tickerSelect = document.getElementById('chatTicker');
    const question = input.value.trim();
    let ticker = tickerSelect.value;
    
    if (!question) {
        return;
    }
    
    // Add user message
    addChatMessage(question, true);
    input.value = '';
    
    // Update context with analyzed tickers
    if (window.analysisResults) {
        conversationContext.analyzedTickers = window.analysisResults.map(r => r.ticker);
    }
    
    // Add to conversation history
    conversationContext.conversationHistory.push({
        type: 'user',
        question: question,
        timestamp: Date.now()
    });
    
    // Try to extract ticker from question
    const tickerMatch = question.match(/\b([A-Z]{2,5}(?:[-\.][A-Z]{2,4})?)\b/);
    const extractedTicker = tickerMatch ? tickerMatch[1] : null;
    
    // Determine which ticker to use based on context
    if (!ticker) {
        // 1. Check if extracted ticker is already analyzed
        if (extractedTicker && conversationContext.analyzedTickers.includes(extractedTicker)) {
            ticker = extractedTicker;
        }
        // 2. Use conversation context (continuing discussion about last ticker)
        else if (conversationContext.lastTicker && conversationContext.analyzedTickers.includes(conversationContext.lastTicker)) {
            ticker = conversationContext.lastTicker;
        }
        // 3. If ticker mentioned but not analyzed, trigger auto-analysis
        else if (extractedTicker) {
            addChatMessage(`🔍 Great question! Let me analyze **${extractedTicker}** for you...`, false);
            
            if (!sessionTickers.includes(extractedTicker)) {
                sessionTickers.push(extractedTicker);
                saveSessionTickers();
                updateTickerChips();
            }
            
            addChatMessage(`📊 Running comprehensive analysis... This includes technical indicators, sentiment analysis, and recent news.`, false);
            
            try {
                await analyzePortfolio();
                addChatMessage(`✅ Analysis complete! Here's what I found...`, false);
                
                conversationContext.lastTicker = extractedTicker;
                if (!conversationContext.analyzedTickers.includes(extractedTicker)) {
                    conversationContext.analyzedTickers.push(extractedTicker);
                }
                
                setTimeout(async () => {
                    await sendChatWithTicker(question, extractedTicker);
                }, 800);
                
            } catch (error) {
                addChatMessage(`❌ I apologize, but I encountered an error analyzing ${extractedTicker}. This could be due to:\n\n` +
                    `• Invalid ticker symbol\n` +
                    `• Network connectivity issues\n` +
                    `• Data provider limitations\n\n` +
                    `Please verify the ticker symbol and try again.`, false);
            }
            return;
        }
        // 4. No ticker, but have analyzed stocks - provide conversational response
        else if (conversationContext.analyzedTickers.length > 0) {
            await sendContextualResponse(question);
            return;
        }
        // 5. No context at all - friendly onboarding
        else {
            addChatMessage(`👋 Hello! I'm your AI investment advisor. I'm here to help you make informed decisions.\n\n` +
                `🎯 **Let's get started!**\n` +
                `You can ask me about any stock or cryptocurrency by mentioning its ticker symbol. For example:\n` +
                `• "What do you think about AAPL?"\n` +
                `• "Should I invest in BTC-USD?"\n` +
                `• "How is TSLA performing?"\n\n` +
                `I'll automatically analyze it and provide you with:\n` +
                `• 📊 Technical analysis (RSI, MACD, trends)\n` +
                `• 🎭 Sentiment from news and social media\n` +
                `• 💡 Buy/sell/hold recommendations\n` +
                `• ⚠️ Risk assessment\n\n` +
                `**⚖️ Important Disclaimer:**\n` +
                `My analysis is for educational and informational purposes only. I cannot be held responsible for investment outcomes. Always:\n` +
                `• Do your own thorough research (DYOR)\n` +
                `• Consult with licensed financial advisors\n` +
                `• Only invest what you can afford to lose\n` +
                `• Verify all information independently\n` +
                `What would you like to know?`, false);
            return;
        }
    }
    
    // Update conversation context
    if (ticker) {
        conversationContext.lastTicker = ticker;
    }
    
    await sendChatWithTicker(question, ticker);
};

// Handle contextual responses when no specific ticker is mentioned
async function sendContextualResponse(question) {
    const questionLower = question.toLowerCase();
    
    // Detect question intent
    const intents = {
        comparison: /compare|versus|vs|better|difference/i.test(question),
        general: /is it|should i|good investment|worth|recommend/i.test(question),
        sentiment: /sentiment|feel|opinion|think/i.test(question),
        price: /price|cost|worth|expensive|cheap/i.test(question),
        risk: /risk|safe|dangerous|volatile/i.test(question)
    };
    
    // If asking about last discussed ticker
    if (intents.general && conversationContext.lastTicker) {
        addChatMessage(`I understand you're asking about **${conversationContext.lastTicker}**. Let me provide you with insights...`, false);
        await sendChatWithTicker(question, conversationContext.lastTicker);
        return;
    }
    
    // If comparing stocks
    if (intents.comparison && conversationContext.analyzedTickers.length >= 2) {
        const tickers = conversationContext.analyzedTickers.slice(-2).join(' and ');
        addChatMessage(`Let me help you compare your analyzed stocks: **${tickers}**\n\n` +
            `For a detailed comparison, please ask specific questions like:\n` +
            `• "Which has better technical indicators?"\n` +
            `• "Which has more positive sentiment?"\n` +
            `• "Which is less risky?"`, false);
        return;
    }
    
    // Conversational response about available tickers
    if (conversationContext.analyzedTickers.length > 0) {
        const tickersList = conversationContext.analyzedTickers.join(', ');
        addChatMessage(`📊 **Your Portfolio Overview**\n\n` +
            `I have analysis data for: **${tickersList}**\n\n` +
            `To help you better, could you:\n` +
            `• Specify which ticker you're asking about?\n` +
            `• Or select one from the dropdown above?\n\n` +
            `I'll remember the context and can continue our conversation about any of these stocks!\n\n` +
            `💡 **Tip:** If you're asking "${question}", I assume you mean **${conversationContext.lastTicker || conversationContext.analyzedTickers[conversationContext.analyzedTickers.length - 1]}**. Is that correct?`, false);
        
        // Set a temporary flag to use last ticker on next question
        setTimeout(() => {
            if (!conversationContext.lastTicker && conversationContext.analyzedTickers.length > 0) {
                conversationContext.lastTicker = conversationContext.analyzedTickers[conversationContext.analyzedTickers.length - 1];
            }
        }, 2000);
    } else {
        addChatMessage(`I'd love to help answer that question! However, I need to analyze some stocks first.\n\n` +
            `📝 **Quick Start:**\n` +
            `Just mention any ticker symbol in your question, and I'll analyze it automatically. For example:\n` +
            `• "Tell me about MSFT"\n` +
            `• "Is AAPL a good buy?"\n` +
            `• "Analyze BTC-USD for me"`, false);
    }
}

console.log('✅ Enhanced conversational chat system loaded');
