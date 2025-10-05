"""
Chart Generator Module
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ChartGenerator:
    @staticmethod
    def create_candlestick_chart(ticker, df, indicators, chart_type='candlestick'):
        """Create interactive chart with indicators
        
        Args:
            ticker: Stock ticker symbol
            df: DataFrame with OHLC data
            indicators: Technical indicators
            chart_type: Type of chart ('candlestick', 'line', 'ohlc', 'area', 'volume', 'mountain')
        """
        print(f"  📊 Generating {chart_type} chart for {ticker} with {len(df)} data points")
        print(f"     Price range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
        
        if df is None or df.empty:
            return None
        
        # Adjust layout based on chart type
        if chart_type == 'volume':
            # Price + Volume + MACD + RSI
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(f'{ticker} Price', 'Volume', 'MACD', 'RSI'),
                row_heights=[0.4, 0.2, 0.2, 0.2]
            )
        else:
            # Standard: Price + MACD + RSI
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(f'{ticker} Price & Indicators', 'MACD', 'RSI'),
                row_heights=[0.6, 0.2, 0.2]
            )
        
        # Add main price chart based on type
        if chart_type == 'candlestick':
            fig.add_trace(
                go.Candlestick(
                    x=df.index.tolist(),
                    open=df['Open'].tolist(),
                    high=df['High'].tolist(),
                    low=df['Low'].tolist(),
                    close=df['Close'].tolist(),
                    name='Price',
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                ),
                row=1, col=1
            )
        elif chart_type == 'ohlc':
            fig.add_trace(
                go.Ohlc(
                    x=df.index.tolist(),
                    open=df['Open'].tolist(),
                    high=df['High'].tolist(),
                    low=df['Low'].tolist(),
                    close=df['Close'].tolist(),
                    name='Price',
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                ),
                row=1, col=1
            )
        elif chart_type == 'line':
            fig.add_trace(
                go.Scatter(
                    x=df.index.tolist(),
                    y=df['Close'].tolist(),
                    name='Close Price',
                    line=dict(color='#2196F3', width=2),
                    mode='lines'
                ),
                row=1, col=1
            )
        elif chart_type == 'area':
            fig.add_trace(
                go.Scatter(
                    x=df.index.tolist(),
                    y=df['Close'].tolist(),
                    name='Close Price',
                    line=dict(color='#2196F3', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(33, 150, 243, 0.3)',
                    mode='lines'
                ),
                row=1, col=1
            )
        elif chart_type == 'mountain':
            # Mountain chart with gradient fill
            fig.add_trace(
                go.Scatter(
                    x=df.index.tolist(),
                    y=df['Close'].tolist(),
                    name='Close Price',
                    line=dict(color='#667eea', width=2.5),
                    fill='tozeroy',
                    fillcolor='rgba(102, 126, 234, 0.4)',
                    mode='lines'
                ),
                row=1, col=1
            )
        elif chart_type == 'volume':
            # Candlestick for volume view
            fig.add_trace(
                go.Candlestick(
                    x=df.index.tolist(),
                    open=df['Open'].tolist(),
                    high=df['High'].tolist(),
                    low=df['Low'].tolist(),
                    close=df['Close'].tolist(),
                    name='Price',
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                ),
                row=1, col=1
            )
            
            # Add Volume bars
            colors = ['#26a69a' if df['Close'].iloc[i] >= df['Open'].iloc[i] 
                     else '#ef5350' for i in range(len(df))]
            fig.add_trace(
                go.Bar(
                    x=df.index.tolist(),
                    y=df['Volume'].tolist(),
                    name='Volume',
                    marker_color=colors,
                    showlegend=True
                ),
                row=2, col=1
            )
        
        if indicators:
            # Moving Averages
            fig.add_trace(go.Scatter(
                x=df.index.tolist(), y=indicators['SMA_20'].tolist(),
                name='SMA(20)', line=dict(color='orange', width=1.5)
            ), row=1, col=1)
            
            if indicators['SMA_50'] is not None:
                fig.add_trace(go.Scatter(
                    x=df.index.tolist(), y=indicators['SMA_50'].tolist(),
                    name='SMA(50)', line=dict(color='blue', width=1.5)
                ), row=1, col=1)
            
            # Bollinger Bands
            fig.add_trace(go.Scatter(
                x=df.index.tolist(), y=indicators['BB_high'].tolist(),
                name='BB Upper', line=dict(color='gray', width=1, dash='dash'),
                showlegend=False
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index.tolist(), y=indicators['BB_low'].tolist(),
                name='BB Lower', line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty', fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ), row=1, col=1)
            
            # MACD (adjust row based on chart type)
            macd_row = 3 if chart_type == 'volume' else 2
            fig.add_trace(go.Scatter(
                x=df.index.tolist(), y=indicators['MACD'].tolist(),
                name='MACD', line=dict(color='#2196F3', width=2)
            ), row=macd_row, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index.tolist(), y=indicators['MACD_signal'].tolist(),
                name='Signal', line=dict(color='#FF9800', width=2)
            ), row=macd_row, col=1)
            
            colors = ['#26a69a' if val >= 0 else '#ef5350' for val in indicators['MACD_diff']]
            fig.add_trace(go.Bar(
                x=df.index.tolist(), y=indicators['MACD_diff'].tolist(),
                name='MACD Histogram',
                marker_color=colors,
                showlegend=False
            ), row=macd_row, col=1)
            
            # RSI (adjust row based on chart type)
            rsi_row = 4 if chart_type == 'volume' else 3
            fig.add_trace(go.Scatter(
                x=df.index.tolist(), y=indicators['RSI'].tolist(),
                name='RSI', line=dict(color='#9C27B0', width=2)
            ), row=rsi_row, col=1)
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         annotation_text="Overbought", row=rsi_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green",
                         annotation_text="Oversold", row=rsi_row, col=1)
        
        # Adjust height based on chart type
        chart_height = 900 if chart_type == 'volume' else 800
        
        fig.update_layout(
            height=chart_height,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            template='plotly_white',
            hovermode='x unified',
            font=dict(size=10)
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        return fig
