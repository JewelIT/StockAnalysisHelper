"""Tests for portfolio management module"""

import unittest
import tempfile
import os
from pathlib import Path

from stock_analysis_helper.portfolio import PortfolioManager


class TestPortfolioManager(unittest.TestCase):
    """Test cases for PortfolioManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.portfolio = PortfolioManager()
    
    def test_add_stock(self):
        """Test adding a stock to portfolio"""
        self.portfolio.add_stock("AAPL", 10, 150.00)
        
        summary = self.portfolio.get_portfolio_summary()
        self.assertEqual(summary['total_stocks'], 1)
        self.assertEqual(summary['stocks'][0]['symbol'], 'AAPL')
        self.assertEqual(summary['stocks'][0]['shares'], 10)
        self.assertEqual(summary['stocks'][0]['purchase_price'], 150.00)
    
    def test_add_crypto(self):
        """Test adding cryptocurrency to portfolio"""
        self.portfolio.add_crypto("BTC", 0.5, 40000.00)
        
        summary = self.portfolio.get_portfolio_summary()
        self.assertEqual(summary['total_crypto'], 1)
        self.assertEqual(summary['crypto'][0]['symbol'], 'BTC')
        self.assertEqual(summary['crypto'][0]['amount'], 0.5)
    
    def test_add_to_watchlist(self):
        """Test adding to watchlist"""
        self.portfolio.add_to_watchlist("TSLA", "stock")
        
        summary = self.portfolio.get_portfolio_summary()
        self.assertEqual(summary['watchlist_items'], 1)
        self.assertEqual(summary['watchlist'][0]['symbol'], 'TSLA')
    
    def test_get_all_symbols(self):
        """Test getting all symbols"""
        self.portfolio.add_stock("AAPL", 10, 150.00)
        self.portfolio.add_crypto("BTC", 0.5, 40000.00)
        self.portfolio.add_to_watchlist("TSLA", "stock")
        
        symbols = self.portfolio.get_all_symbols()
        self.assertIn("AAPL", symbols)
        self.assertIn("BTC-USD", symbols)
        self.assertIn("TSLA", symbols)
    
    def test_save_and_load_yaml(self):
        """Test saving and loading portfolio as YAML"""
        self.portfolio.add_stock("AAPL", 10, 150.00)
        self.portfolio.add_crypto("BTC", 0.5, 40000.00)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            self.portfolio.save_portfolio(temp_path)
            
            # Load the portfolio
            loaded_portfolio = PortfolioManager(temp_path)
            summary = loaded_portfolio.get_portfolio_summary()
            
            self.assertEqual(summary['total_stocks'], 1)
            self.assertEqual(summary['total_crypto'], 1)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_portfolio_summary(self):
        """Test portfolio summary"""
        self.portfolio.add_stock("AAPL", 10, 150.00)
        self.portfolio.add_stock("MSFT", 5, 300.00)
        self.portfolio.add_crypto("BTC", 0.5, 40000.00)
        self.portfolio.add_to_watchlist("TSLA", "stock")
        
        summary = self.portfolio.get_portfolio_summary()
        
        self.assertEqual(summary['total_stocks'], 2)
        self.assertEqual(summary['total_crypto'], 1)
        self.assertEqual(summary['watchlist_items'], 1)


if __name__ == '__main__':
    unittest.main()
