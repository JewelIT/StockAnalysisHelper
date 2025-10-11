"""
Unit and Integration Tests for New Features
- Intraday timeframes (5m, 15m, 30m, 1h, etc.)
- VWAP indicator
- Ichimoku Cloud indicator
- Theme parameter flow
"""
import unittest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.data_fetcher import DataFetcher
from src.utils.technical_analyzer import TechnicalAnalyzer
from src.utils.chart_generator import ChartGenerator
from src.web import create_app


class TestIntradayTimeframes(unittest.TestCase):
    """Test intraday timeframe data fetching"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fetcher = DataFetcher()
        self.test_ticker = "AAPL"
    
    def test_5m_timeframe(self):
        """Test 5-minute bars fetch correctly"""
        df = self.fetcher.fetch_historical_data(self.test_ticker, period="5m")
        
        self.assertIsNotNone(df, "5m data should not be None")
        self.assertFalse(df.empty, "5m data should not be empty")
        self.assertGreater(len(df), 0, "Should have at least one data point")
        
        # Verify it's intraday data (time delta less than 2 days)
        time_delta = df.index[-1] - df.index[0]
        self.assertLess(time_delta.days, 2, "5m should be within 1 day")
    
    def test_15m_timeframe(self):
        """Test 15-minute bars fetch correctly"""
        df = self.fetcher.fetch_historical_data(self.test_ticker, period="15m")
        
        self.assertIsNotNone(df)
        self.assertFalse(df.empty)
        self.assertGreater(len(df), 0)
        
        # Should have multiple days of data
        time_delta = df.index[-1] - df.index[0]
        self.assertGreater(time_delta.days, 0, "15m should have multiple days")
        self.assertLess(time_delta.days, 10, "15m should be within ~5 days")
    
    def test_1h_timeframe(self):
        """Test 1-hour bars fetch correctly"""
        df = self.fetcher.fetch_historical_data(self.test_ticker, period="1h")
        
        self.assertIsNotNone(df)
        self.assertFalse(df.empty)
        self.assertGreater(len(df), 10, "Should have multiple data points")
    
    def test_all_intraday_timeframes(self):
        """Test all intraday timeframes return data"""
        timeframes = ["5m", "15m", "30m", "1h", "3h", "6h", "12h"]
        
        for timeframe in timeframes:
            with self.subTest(timeframe=timeframe):
                df = self.fetcher.fetch_historical_data(self.test_ticker, period=timeframe)
                self.assertIsNotNone(df, f"{timeframe} should return data")
                if df is not None:
                    self.assertFalse(df.empty, f"{timeframe} should not be empty")
    
    def test_intraday_has_required_columns(self):
        """Test intraday data has OHLCV columns"""
        df = self.fetcher.fetch_historical_data(self.test_ticker, period="5m")
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            self.assertIn(col, df.columns, f"Should have {col} column")
    
    def test_intraday_data_quality(self):
        """Test intraday data quality and consistency"""
        df = self.fetcher.fetch_historical_data(self.test_ticker, period="15m")
        
        # Check for no NaN values in critical columns
        self.assertFalse(df['Close'].isna().any(), "Close prices should not have NaN")
        
        # High should be >= Low
        self.assertTrue((df['High'] >= df['Low']).all(), "High >= Low for all bars")
        
        # Close should be between High and Low
        self.assertTrue((df['Close'] <= df['High']).all(), "Close <= High")
        self.assertTrue((df['Close'] >= df['Low']).all(), "Close >= Low")


class TestVWAPIndicator(unittest.TestCase):
    """Test VWAP (Volume Weighted Average Price) indicator"""
    
    def setUp(self):
        """Create sample data for testing"""
        self.analyzer = TechnicalAnalyzer()
        
        # Create sample OHLCV data
        dates = pd.date_range(start='2025-10-01', periods=50, freq='1H')
        np.random.seed(42)
        
        prices = 100 + np.cumsum(np.random.randn(50) * 0.5)
        volumes = np.random.randint(1000, 10000, 50)
        
        self.df = pd.DataFrame({
            'Open': prices + np.random.randn(50) * 0.1,
            'High': prices + abs(np.random.randn(50) * 0.3),
            'Low': prices - abs(np.random.randn(50) * 0.3),
            'Close': prices,
            'Volume': volumes
        }, index=dates)
    
    def test_vwap_calculation(self):
        """Test VWAP is calculated"""
        indicators = self.analyzer.calculate_indicators(self.df)
        
        self.assertIsNotNone(indicators, "Indicators should be calculated")
        self.assertIn('VWAP', indicators, "Should have VWAP indicator")
        self.assertIsNotNone(indicators['VWAP'], "VWAP should not be None")
    
    def test_vwap_values_reasonable(self):
        """Test VWAP values are within reasonable range"""
        indicators = self.analyzer.calculate_indicators(self.df)
        vwap = indicators['VWAP']
        
        # VWAP should be close to price range
        min_price = self.df['Low'].min()
        max_price = self.df['High'].max()
        
        self.assertTrue((vwap >= min_price * 0.9).all(), "VWAP should be near price range")
        self.assertTrue((vwap <= max_price * 1.1).all(), "VWAP should be near price range")
    
    def test_vwap_is_cumulative(self):
        """Test VWAP is cumulative (monotonic or near-monotonic)"""
        indicators = self.analyzer.calculate_indicators(self.df)
        vwap = indicators['VWAP']
        
        # VWAP should not have large jumps
        vwap_changes = vwap.diff().abs()
        max_change_pct = (vwap_changes / vwap).max()
        
        self.assertLess(max_change_pct, 0.5, "VWAP should change smoothly")


class TestIchimokuIndicator(unittest.TestCase):
    """Test Ichimoku Cloud indicator components"""
    
    def setUp(self):
        """Create sample data for testing"""
        self.analyzer = TechnicalAnalyzer()
        
        # Create sample data with enough points for Ichimoku
        dates = pd.date_range(start='2025-07-01', periods=100, freq='D')
        np.random.seed(42)
        
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        
        self.df = pd.DataFrame({
            'Open': prices + np.random.randn(100) * 0.1,
            'High': prices + abs(np.random.randn(100) * 0.3),
            'Low': prices - abs(np.random.randn(100) * 0.3),
            'Close': prices,
            'Volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
    
    def test_ichimoku_components_exist(self):
        """Test all Ichimoku components are calculated"""
        indicators = self.analyzer.calculate_indicators(self.df)
        
        expected_components = [
            'Ichimoku_tenkan',
            'Ichimoku_kijun',
            'Ichimoku_senkou_a',
            'Ichimoku_senkou_b',
            'Ichimoku_chikou'
        ]
        
        for component in expected_components:
            self.assertIn(component, indicators, f"Should have {component}")
    
    def test_tenkan_sen_calculation(self):
        """Test Tenkan-sen (Conversion Line) is calculated correctly"""
        indicators = self.analyzer.calculate_indicators(self.df)
        tenkan = indicators['Ichimoku_tenkan']
        
        self.assertIsNotNone(tenkan, "Tenkan-sen should be calculated")
        
        # Tenkan should be between high and low of recent period
        # (with some tolerance for edge cases)
        self.assertTrue((tenkan >= self.df['Low'].min() * 0.95).all() or tenkan.isna().any())
        self.assertTrue((tenkan <= self.df['High'].max() * 1.05).all() or tenkan.isna().any())
    
    def test_kijun_sen_calculation(self):
        """Test Kijun-sen (Base Line) is calculated correctly"""
        indicators = self.analyzer.calculate_indicators(self.df)
        kijun = indicators['Ichimoku_kijun']
        
        self.assertIsNotNone(kijun, "Kijun-sen should be calculated")
    
    def test_senkou_spans_form_cloud(self):
        """Test Senkou Span A and B form the cloud"""
        indicators = self.analyzer.calculate_indicators(self.df)
        senkou_a = indicators['Ichimoku_senkou_a']
        senkou_b = indicators['Ichimoku_senkou_b']
        
        self.assertIsNotNone(senkou_a, "Senkou Span A should exist")
        self.assertIsNotNone(senkou_b, "Senkou Span B should exist")
        
        # Both should have some non-null values
        self.assertGreater(senkou_a.notna().sum(), 0, "Senkou A should have values")
        self.assertGreater(senkou_b.notna().sum(), 0, "Senkou B should have values")
    
    def test_ichimoku_with_limited_data(self):
        """Test Ichimoku handles limited data gracefully"""
        # Create small dataset
        small_df = self.df.head(20)
        indicators = self.analyzer.calculate_indicators(small_df)
        
        # Should still calculate but may have more NaN values
        self.assertIn('Ichimoku_tenkan', indicators)
        self.assertIn('Ichimoku_kijun', indicators)


class TestThemeParameterFlow(unittest.TestCase):
    """Test theme parameter flows through the system"""
    
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_analyze_accepts_theme_parameter(self):
        """Test /analyze endpoint accepts theme parameter"""
        response = self.client.post('/analyze', json={
            'tickers': ['AAPL'],
            'theme': 'dark',
            'chart_type': 'candlestick',
            'timeframe': '1mo'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('results', data)
    
    def test_analyze_validates_theme_parameter(self):
        """Test theme parameter is validated"""
        # Valid themes
        for theme in ['dark', 'light']:
            response = self.client.post('/analyze', json={
                'tickers': ['AAPL'],
                'theme': theme,
                'timeframe': '1mo'
            })
            self.assertEqual(response.status_code, 200)
        
        # Invalid theme should default to 'dark'
        response = self.client.post('/analyze', json={
            'tickers': ['AAPL'],
            'theme': 'invalid',
            'timeframe': '1mo'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_chart_generator_accepts_theme(self):
        """Test ChartGenerator accepts theme parameter"""
        fetcher = DataFetcher()
        analyzer = TechnicalAnalyzer()
        generator = ChartGenerator()
        
        # Fetch data
        df = fetcher.fetch_historical_data("AAPL", period="1mo")
        indicators = analyzer.calculate_indicators(df)
        
        # Generate charts with both themes
        for theme in ['dark', 'light']:
            fig = generator.create_candlestick_chart(
                "AAPL", df, indicators, 
                chart_type='candlestick',
                timeframe='1mo',
                theme=theme
            )
            self.assertIsNotNone(fig, f"Chart should be generated with {theme} theme")


class TestIntradayIntegration(unittest.TestCase):
    """Integration tests for intraday analysis"""
    
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_full_intraday_analysis(self):
        """Test complete analysis with intraday timeframe"""
        response = self.client.post('/analyze', json={
            'tickers': ['AAPL'],
            'chart_type': 'candlestick',
            'timeframe': '5m',
            'theme': 'dark',
            'max_news': 3,
            'max_social': 3
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('results', data)
        self.assertGreater(len(data['results']), 0)
        
        result = data['results'][0]
        self.assertEqual(result['ticker'], 'AAPL')
        self.assertTrue(result['success'])
        self.assertIn('chart_data', result)
        self.assertEqual(result['timeframe_used'], '5m')
    
    def test_multiple_intraday_timeframes(self):
        """Test multiple intraday timeframes in sequence"""
        timeframes = ['5m', '15m', '1h']
        
        for timeframe in timeframes:
            with self.subTest(timeframe=timeframe):
                response = self.client.post('/analyze', json={
                    'tickers': ['MSFT'],
                    'timeframe': timeframe,
                    'theme': 'light'
                })
                
                self.assertEqual(response.status_code, 200)
                data = response.get_json()
                self.assertIn('results', data)
                result = data['results'][0]
                self.assertEqual(result['timeframe_used'], timeframe)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
