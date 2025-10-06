"""
Integration tests for Vestor chatbot
Tests complete conversation flows and multi-turn interactions
"""
import unittest
from app import create_app
import json


class TestChatbotIntegration(unittest.TestCase):
    """Integration tests for complete chatbot flows"""
    
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clear chat history before each test
        with self.client.session_transaction() as sess:
            sess.clear()
    
    def _send_chat(self, question, ticker="", context_ticker=""):
        """Helper to send chat message"""
        return self.client.post('/chat', 
            json={
                'question': question,
                'ticker': ticker,
                'context_ticker': context_ticker
            }
        )
    
    def test_simple_greeting_flow(self):
        """Test: User greets → Vestor responds"""
        response = self._send_chat("Hello")
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('Vestor', data['answer'])
        self.assertIn('financial advisor', data['answer'].lower())
    
    def test_stock_question_needs_analysis(self):
        """Test: User asks about stock → Vestor requests analysis"""
        response = self._send_chat("What can you tell me about AMD?")
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        # Should request analysis since AMD not analyzed yet
        self.assertTrue(
            data.get('needs_background_analysis') or 
            'analyze' in data['answer'].lower()
        )
    
    def test_thank_you_flow(self):
        """Test: User says thanks → Vestor responds warmly"""
        response = self._send_chat("Thanks!")
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('welcome', data['answer'].lower())
    
    def test_conversation_continuity(self):
        """Test: Multiple messages maintain context"""
        # Message 1: Greeting
        response1 = self._send_chat("Hi")
        data1 = response1.get_json()
        self.assertTrue(data1['success'])
        
        # Message 2: Ask about stock
        response2 = self._send_chat("Tell me about Apple")
        data2 = response2.get_json()
        self.assertTrue(data2['success'])
        self.assertEqual(data2.get('ticker') or data2.get('pending_ticker'), 'AAPL')
        
        # Message 3: Thank you
        response3 = self._send_chat("Thank you")
        data3 = response3.get_json()
        self.assertTrue(data3['success'])
    
    def test_company_name_detection(self):
        """Test: Vestor detects company names correctly"""
        test_cases = [
            ("How is Apple doing?", "AAPL"),
            ("Tell me about Microsoft", "MSFT"),
            ("What about Tesla?", "TSLA"),
            ("Thoughts on Amazon", "AMZN"),
            ("Should I buy Bitcoin?", "BTC-USD"),
        ]
        
        for question, expected_ticker in test_cases:
            with self.subTest(question=question):
                response = self._send_chat(question)
                data = response.get_json()
                
                self.assertEqual(response.status_code, 200)
                self.assertTrue(data['success'])
                # Check ticker is detected (either in ticker or pending_ticker)
                detected_ticker = data.get('ticker') or data.get('pending_ticker')
                self.assertEqual(detected_ticker, expected_ticker)
    
    def test_multiple_greetings(self):
        """Test: Various greeting formats work"""
        greetings = ["hello", "hi", "hey", "good morning", "hey there"]
        
        for greeting in greetings:
            with self.subTest(greeting=greeting):
                # Clear session between tests
                with self.client.session_transaction() as sess:
                    sess.clear()
                
                response = self._send_chat(greeting)
                data = response.get_json()
                
                self.assertEqual(response.status_code, 200)
                self.assertTrue(data['success'])
                self.assertIn('Vestor', data['answer'])
    
    def test_session_persistence(self):
        """Test: Chat history is maintained in session"""
        # Send first message
        response1 = self._send_chat("Hello")
        self.assertEqual(response1.status_code, 200)
        
        # Check session has conversation history
        with self.client.session_transaction() as sess:
            history = sess.get('conversation_history', [])
            self.assertGreater(len(history), 0)
            # Should have user message and bot response
            self.assertGreaterEqual(len(history), 2)


class TestChatbotFollowUpQuestions(unittest.TestCase):
    """Test follow-up question scenarios"""
    
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clear chat history
        with self.client.session_transaction() as sess:
            sess.clear()
    
    def _send_chat(self, question, ticker="", context_ticker=""):
        """Helper to send chat message"""
        return self.client.post('/chat', 
            json={
                'question': question,
                'ticker': ticker,
                'context_ticker': context_ticker
            }
        )
    
    def test_follow_up_with_context(self):
        """Test: Ask about stock, then follow-up question"""
        # First question: Establish context
        response1 = self._send_chat("What about AMD?")
        data1 = response1.get_json()
        self.assertTrue(data1['success'])
        
        # Get the ticker from response
        ticker = data1.get('ticker') or data1.get('pending_ticker')
        self.assertIsNotNone(ticker)
        self.assertEqual(ticker, 'AMD')
        
        # Second question: Follow-up using context
        response2 = self._send_chat(
            "Is it a good investment?",
            context_ticker=ticker
        )
        data2 = response2.get_json()
        self.assertTrue(data2['success'])
        # Response should provide investment advice
        # (may refer to ticker or "this asset")
        self.assertTrue(
            'AMD' in data2['answer'].upper() or 
            'investment' in data2['answer'].lower() or
            'this asset' in data2['answer'].lower()
        )
    
    def test_switching_topics(self):
        """Test: Switch from one stock to another"""
        # Ask about AMD
        response1 = self._send_chat("Tell me about AMD")
        data1 = response1.get_json()
        self.assertTrue(data1['success'])
        
        # Switch to AAPL
        response2 = self._send_chat("What about Apple?")
        data2 = response2.get_json()
        self.assertTrue(data2['success'])
        ticker2 = data2.get('ticker') or data2.get('pending_ticker')
        self.assertEqual(ticker2, 'AAPL')


class TestChatbotErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def _send_chat(self, question):
        """Helper to send chat message"""
        return self.client.post('/chat', json={'question': question})
    
    def test_empty_question(self):
        """Test: Empty question returns error"""
        response = self.client.post('/chat', json={'question': ''})
        self.assertEqual(response.status_code, 400)
    
    def test_no_question_field(self):
        """Test: Missing question field returns error"""
        response = self.client.post('/chat', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_very_long_question(self):
        """Test: Very long question is handled"""
        long_question = "What about AMD? " * 100
        response = self._send_chat(long_question)
        data = response.get_json()
        
        # Should still work, not crash
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
    
    def test_special_characters(self):
        """Test: Special characters don't break the system"""
        response = self._send_chat("What about $AAPL & $MSFT?")
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])


class TestChatEndpoints(unittest.TestCase):
    """Test chat-related HTTP endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_clear_chat_endpoint(self):
        """Test: Clear chat history endpoint"""
        # Send a message first
        self.client.post('/chat', json={'question': 'Hello'})
        
        # Clear chat
        response = self.client.post('/clear-chat')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        
        # Verify session is cleared
        with self.client.session_transaction() as sess:
            history = sess.get('conversation_history', [])
            self.assertEqual(len(history), 0)
    
    def test_get_chat_history_endpoint(self):
        """Test: Get chat history endpoint"""
        # Send some messages
        self.client.post('/chat', json={'question': 'Hello'})
        self.client.post('/chat', json={'question': 'What about AAPL?'})
        
        # Get history
        response = self.client.get('/get-chat-history')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('history', data)
        self.assertGreater(len(data['history']), 0)


if __name__ == '__main__':
    unittest.main()
