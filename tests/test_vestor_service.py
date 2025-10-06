"""
Unit tests for VestorService
Tests the core chatbot conversation logic
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from app.services.vestor_service import VestorService


class TestVestorServiceGreetings(unittest.TestCase):
    """Test greeting detection and responses"""
    
    def setUp(self):
        """Initialize VestorService for each test"""
        self.vestor = VestorService()
    
    def test_greeting_hello(self):
        """Test that 'hello' triggers greeting response"""
        result = self.vestor.process_chat(
            question="hello",
            ticker="",
            context_ticker="",
            conversation_history=[]
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Vestor', result['answer'])
        self.assertIn('financial advisor', result['answer'].lower())
        self.assertEqual(result['vestor_mode'], 'conversation')
    
    def test_greeting_hi(self):
        """Test that 'hi' triggers greeting response"""
        result = self.vestor.process_chat(
            question="hi",
            ticker="",
            context_ticker="",
            conversation_history=[]
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Vestor', result['answer'])
    
    def test_greeting_hey_there(self):
        """Test that 'hey there' triggers greeting response"""
        result = self.vestor.process_chat(
            question="hey there",
            ticker="",
            context_ticker="",
            conversation_history=[]
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Vestor', result['answer'])
    
    def test_greeting_case_insensitive(self):
        """Test that greetings are case insensitive"""
        result = self.vestor.process_chat(
            question="HELLO",
            ticker="",
            context_ticker="",
            conversation_history=[]
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Vestor', result['answer'])


class TestVestorServiceThankYou(unittest.TestCase):
    """Test thank you message handling"""
    
    def setUp(self):
        self.vestor = VestorService()
    
    def test_thank_you(self):
        """Test 'thank you' response"""
        result = self.vestor.process_chat(
            question="thank you",
            ticker="",
            context_ticker="",
            conversation_history=[]
        )
        
        self.assertTrue(result['success'])
        self.assertIn('welcome', result['answer'].lower())
    
    def test_thanks(self):
        """Test 'thanks' response"""
        result = self.vestor.process_chat(
            question="thanks",
            ticker="",
            context_ticker="",
            conversation_history=[]
        )
        
        self.assertTrue(result['success'])
        self.assertIn('welcome', result['answer'].lower())


class TestVestorServiceTickerDetection(unittest.TestCase):
    """Test ticker symbol and company name detection"""
    
    def setUp(self):
        self.vestor = VestorService()
    
    def test_detect_ticker_aapl(self):
        """Test detection of AAPL ticker"""
        tickers = self.vestor._detect_tickers("What about AAPL?", "what about aapl?")
        self.assertIn('AAPL', tickers)
    
    def test_detect_company_apple(self):
        """Test detection of Apple company name"""
        tickers = self.vestor._detect_tickers("Tell me about Apple", "tell me about apple")
        self.assertIn('AAPL', tickers)
    
    def test_detect_company_microsoft(self):
        """Test detection of Microsoft company name"""
        tickers = self.vestor._detect_tickers("How is Microsoft doing?", "how is microsoft doing?")
        self.assertIn('MSFT', tickers)
    
    def test_detect_crypto_bitcoin(self):
        """Test detection of Bitcoin"""
        tickers = self.vestor._detect_tickers("What about Bitcoin?", "what about bitcoin?")
        self.assertIn('BTC-USD', tickers)
    
    def test_detect_multiple_tickers(self):
        """Test detection of multiple tickers in one question"""
        tickers = self.vestor._detect_tickers(
            "Compare AAPL and MSFT", 
            "compare aapl and msft"
        )
        self.assertIn('AAPL', tickers)
        self.assertIn('MSFT', tickers)


class TestVestorServiceTickerResolution(unittest.TestCase):
    """Test ticker resolution logic"""
    
    def setUp(self):
        self.vestor = VestorService()
    
    def test_explicit_ticker_priority(self):
        """Test that explicit ticker has highest priority"""
        result = self.vestor._resolve_ticker(
            explicit_ticker="TSLA",
            mentioned=['AAPL'],
            context_ticker="MSFT",
            question_lower="what about the stock?"
        )
        self.assertEqual(result, 'TSLA')
    
    def test_mentioned_ticker_fallback(self):
        """Test mentioned ticker is used when no explicit ticker"""
        result = self.vestor._resolve_ticker(
            explicit_ticker="",
            mentioned=['AAPL'],
            context_ticker="MSFT",
            question_lower="what about apple?"
        )
        self.assertEqual(result, 'AAPL')
    
    def test_context_ticker_for_followup(self):
        """Test context ticker is used for follow-up questions"""
        result = self.vestor._resolve_ticker(
            explicit_ticker="",
            mentioned=[],
            context_ticker="MSFT",
            question_lower="is it a good investment?"
        )
        self.assertEqual(result, 'MSFT')
    
    def test_no_ticker_found(self):
        """Test None is returned when no ticker found"""
        result = self.vestor._resolve_ticker(
            explicit_ticker="",
            mentioned=[],
            context_ticker="",
            question_lower="how do i invest?"
        )
        self.assertIsNone(result)


class TestVestorServiceResponseFormat(unittest.TestCase):
    """Test that responses are properly formatted"""
    
    def setUp(self):
        self.vestor = VestorService()
    
    def test_response_has_answer_string(self):
        """Test that response contains 'answer' key with string value"""
        result = self.vestor.process_chat(
            question="hello",
            ticker="",
            context_ticker="",
            conversation_history=[]
        )
        
        self.assertIn('answer', result)
        self.assertIsInstance(result['answer'], str)
        self.assertGreater(len(result['answer']), 0)
    
    def test_response_has_success_flag(self):
        """Test that response contains 'success' key"""
        result = self.vestor.process_chat(
            question="hello",
            ticker="",
            context_ticker="",
            conversation_history=[]
        )
        
        self.assertIn('success', result)
        self.assertIsInstance(result['success'], bool)
    
    def test_response_has_vestor_mode(self):
        """Test that response contains 'vestor_mode' key"""
        result = self.vestor.process_chat(
            question="hello",
            ticker="",
            context_ticker="",
            conversation_history=[]
        )
        
        self.assertIn('vestor_mode', result)
        self.assertIsInstance(result['vestor_mode'], str)


class TestVestorServiceFallbackResponse(unittest.TestCase):
    """Test fallback responses when AI fails"""
    
    def setUp(self):
        self.vestor = VestorService()
    
    def test_fallback_response_structure(self):
        """Test fallback response has correct structure"""
        result = self.vestor._fallback_response()
        
        self.assertIn('answer', result)
        self.assertIn('success', result)
        self.assertIn('vestor_mode', result)
        self.assertTrue(result['success'])
        self.assertIn('Vestor', result['answer'])


if __name__ == '__main__':
    unittest.main()
