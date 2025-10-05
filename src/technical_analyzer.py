"""
Technical Analysis Module
"""
import pandas as pd
import ta

class TechnicalAnalyzer:
    @staticmethod
    def calculate_indicators(df):
        """Calculate technical indicators"""
        if df.empty or len(df) < 20:
            return None
        
        indicators = {}
        
        # Moving Averages
        indicators['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        indicators['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50) if len(df) >= 50 else None
        indicators['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
        
        # RSI
        indicators['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        # MACD
        macd = ta.trend.MACD(df['Close'])
        indicators['MACD'] = macd.macd()
        indicators['MACD_signal'] = macd.macd_signal()
        indicators['MACD_diff'] = macd.macd_diff()
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['Close'])
        indicators['BB_high'] = bollinger.bollinger_hband()
        indicators['BB_low'] = bollinger.bollinger_lband()
        indicators['BB_mid'] = bollinger.bollinger_mavg()
        
        return indicators
    
    @staticmethod
    def generate_signals(df, indicators):
        """Generate buy/sell/hold signals"""
        if indicators is None or df.empty:
            return {'signal': 'HOLD', 'score': 0.5, 'reasons': ['Insufficient data']}
        
        signals = []
        score = 0.5
        reasons = []
        
        # Get latest values
        current_price = df['Close'].iloc[-1]
        rsi = indicators['RSI'].iloc[-1]
        macd_diff = indicators['MACD_diff'].iloc[-1]
        sma_20 = indicators['SMA_20'].iloc[-1]
        
        # RSI Analysis
        if rsi < 30:
            signals.append('BUY')
            score += 0.15
            reasons.append(f'RSI oversold ({rsi:.1f})')
        elif rsi > 70:
            signals.append('SELL')
            score -= 0.15
            reasons.append(f'RSI overbought ({rsi:.1f})')
        
        # MACD Analysis
        if macd_diff > 0:
            signals.append('BUY')
            score += 0.1
            reasons.append('MACD bullish crossover')
        elif macd_diff < 0:
            signals.append('SELL')
            score -= 0.1
            reasons.append('MACD bearish crossover')
        
        # Price vs SMA
        if current_price > sma_20:
            signals.append('BUY')
            score += 0.1
            reasons.append('Price above SMA(20)')
        else:
            signals.append('SELL')
            score -= 0.1
            reasons.append('Price below SMA(20)')
        
        # Bollinger Bands
        bb_low = indicators['BB_low'].iloc[-1]
        bb_high = indicators['BB_high'].iloc[-1]
        if current_price < bb_low:
            signals.append('BUY')
            score += 0.1
            reasons.append('Price below lower Bollinger Band')
        elif current_price > bb_high:
            signals.append('SELL')
            score -= 0.1
            reasons.append('Price above upper Bollinger Band')
        
        # Determine overall signal
        score = max(0, min(1, score))
        if score > 0.6:
            overall_signal = 'BUY'
        elif score < 0.4:
            overall_signal = 'SELL'
        else:
            overall_signal = 'HOLD'
        
        return {'signal': overall_signal, 'score': score, 'reasons': reasons}
