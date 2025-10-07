"""
Analyst Consensus Fetcher
Retrieves analyst recommendations, price targets, and consensus ratings from Yahoo Finance
"""
import yfinance as yf
import pandas as pd
from datetime import datetime


class AnalystConsensusFetcher:
    """Fetches and processes analyst consensus data from Yahoo Finance"""
    
    def __init__(self):
        """Initialize the analyst consensus fetcher"""
        pass
    
    def fetch_analyst_data(self, ticker):
        """
        Fetch analyst recommendations and price targets from Yahoo Finance
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dict with analyst consensus data
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get recommendation data
            recommendations = None
            try:
                recs = stock.recommendations
                if recs is not None and not recs.empty:
                    recommendations = recs.tail(1).to_dict('records')[0] if len(recs) > 0 else None
            except Exception as e:
                print(f"Could not fetch recommendations history for {ticker}: {e}")
            
            # Extract analyst consensus data
            analyst_data = {
                'has_data': False,
                'recommendation_key': info.get('recommendationKey', None),
                'recommendation_mean': info.get('recommendationMean', None),
                'number_of_analysts': info.get('numberOfAnalystOpinions', 0),
                'target_mean_price': info.get('targetMeanPrice', None),
                'target_high_price': info.get('targetHighPrice', None),
                'target_low_price': info.get('targetLowPrice', None),
                'current_price': info.get('currentPrice', None),
                'recommendations_breakdown': recommendations
            }
            
            # Check if we have meaningful analyst data
            if analyst_data['recommendation_mean'] is not None and analyst_data['number_of_analysts'] > 0:
                analyst_data['has_data'] = True
            
            return analyst_data
            
        except Exception as e:
            print(f"Error fetching analyst data for {ticker}: {e}")
            return {
                'has_data': False,
                'error': str(e)
            }
    
    def calculate_analyst_score(self, analyst_data):
        """
        Convert analyst consensus to a normalized score (0-1)
        
        Yahoo Finance recommendation scale:
        1.0 = Strong Buy
        2.0 = Buy
        3.0 = Hold
        4.0 = Sell
        5.0 = Strong Sell
        
        We convert to 0-1 scale:
        1.0 (Strong Buy) -> 1.0
        2.0 (Buy) -> 0.75
        3.0 (Hold) -> 0.5
        4.0 (Sell) -> 0.25
        5.0 (Strong Sell) -> 0.0
        
        Args:
            analyst_data: Dict with analyst consensus data
            
        Returns:
            Float between 0 and 1, or None if no data
        """
        if not analyst_data.get('has_data', False):
            return None
        
        recommendation_mean = analyst_data.get('recommendation_mean')
        if recommendation_mean is None:
            return None
        
        # Convert Yahoo's 1-5 scale (lower is better) to 0-1 scale (higher is better)
        # Formula: score = (5 - recommendation_mean) / 4
        # This maps: 1->1.0, 2->0.75, 3->0.5, 4->0.25, 5->0.0
        analyst_score = (5.0 - recommendation_mean) / 4.0
        
        # Clamp to 0-1 range
        analyst_score = max(0.0, min(1.0, analyst_score))
        
        return analyst_score
    
    def calculate_price_target_score(self, analyst_data):
        """
        Calculate score based on price target vs current price
        
        If target price is significantly higher than current price -> bullish
        If target price is significantly lower than current price -> bearish
        
        Args:
            analyst_data: Dict with analyst consensus data
            
        Returns:
            Float between 0 and 1, or None if no data
        """
        target_mean = analyst_data.get('target_mean_price')
        current_price = analyst_data.get('current_price')
        
        if target_mean is None or current_price is None or current_price == 0:
            return None
        
        # Calculate upside/downside percentage
        price_change_pct = ((target_mean - current_price) / current_price) * 100
        
        # Convert to 0-1 score
        # -20% or worse -> 0.0
        # 0% -> 0.5
        # +20% or better -> 1.0
        if price_change_pct >= 20:
            score = 1.0
        elif price_change_pct <= -20:
            score = 0.0
        else:
            # Linear interpolation between 0 and 1
            score = 0.5 + (price_change_pct / 40.0)
        
        return max(0.0, min(1.0, score))
    
    def get_analyst_consensus_signal(self, analyst_data):
        """
        Get human-readable analyst consensus signal
        
        Args:
            analyst_data: Dict with analyst consensus data
            
        Returns:
            Dict with signal info
        """
        if not analyst_data.get('has_data', False):
            return {
                'signal': 'NO DATA',
                'description': 'No analyst coverage available',
                'strength': 0
            }
        
        recommendation_mean = analyst_data.get('recommendation_mean', 3.0)
        num_analysts = analyst_data.get('number_of_analysts', 0)
        
        # Determine signal based on recommendation mean
        if recommendation_mean <= 1.5:
            signal = 'STRONG BUY'
            strength = 5
        elif recommendation_mean <= 2.5:
            signal = 'BUY'
            strength = 4
        elif recommendation_mean <= 3.5:
            signal = 'HOLD'
            strength = 3
        elif recommendation_mean <= 4.5:
            signal = 'SELL'
            strength = 2
        else:
            signal = 'STRONG SELL'
            strength = 1
        
        # Add price target info if available
        target_mean = analyst_data.get('target_mean_price')
        current_price = analyst_data.get('current_price')
        upside_text = ''
        
        if target_mean and current_price and current_price > 0:
            upside_pct = ((target_mean - current_price) / current_price) * 100
            upside_text = f' ({upside_pct:+.1f}% to target)'
        
        description = f'{num_analysts} analyst{"s" if num_analysts != 1 else ""} recommend {signal}{upside_text}'
        
        return {
            'signal': signal,
            'description': description,
            'strength': strength,
            'num_analysts': num_analysts,
            'recommendation_mean': recommendation_mean
        }
    
    def format_analyst_summary(self, analyst_data):
        """
        Format analyst data into human-readable summary
        
        Args:
            analyst_data: Dict with analyst consensus data
            
        Returns:
            Dict with formatted summary
        """
        if not analyst_data.get('has_data', False):
            return {
                'available': False,
                'summary': 'No analyst coverage'
            }
        
        consensus_signal = self.get_analyst_consensus_signal(analyst_data)
        
        # Build breakdown if available
        breakdown = analyst_data.get('recommendations_breakdown')
        breakdown_text = ''
        if breakdown:
            strong_buy = breakdown.get('strongBuy', 0)
            buy = breakdown.get('buy', 0)
            hold = breakdown.get('hold', 0)
            sell = breakdown.get('sell', 0)
            strong_sell = breakdown.get('strongSell', 0)
            
            breakdown_text = f'{strong_buy} Strong Buy, {buy} Buy, {hold} Hold, {sell} Sell, {strong_sell} Strong Sell'
        
        # Price target info
        target_info = {}
        if analyst_data.get('target_mean_price'):
            target_info = {
                'mean': analyst_data['target_mean_price'],
                'high': analyst_data.get('target_high_price'),
                'low': analyst_data.get('target_low_price'),
                'current': analyst_data.get('current_price')
            }
        
        return {
            'available': True,
            'consensus': consensus_signal,
            'breakdown': breakdown_text,
            'price_targets': target_info,
            'num_analysts': analyst_data.get('number_of_analysts', 0)
        }
