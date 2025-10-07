"""
Chart Generator Module
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ChartGenerator:
    @staticmethod
    def create_candlestick_chart(ticker, df, indicators, chart_type='candlestick', timeframe='3mo'):
        """Create interactive chart with indicators
        
        Args:
            ticker: Stock ticker symbol
            df: DataFrame with OHLC data
            indicators: Technical indicators
            chart_type: Type of chart ('candlestick', 'line', 'ohlc', 'area', 'volume', 'mountain')
            timeframe: Timeframe for the chart (e.g., '1wk', '1mo', '3mo', '1y')
        """
        print(f"  📊 Generating {chart_type} chart for {ticker} with {len(df)} data points")
        print(f"     Price range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
        
        # Calculate time range for title
        start_date = df.index[0].strftime('%Y-%m-%d')
        end_date = df.index[-1].strftime('%Y-%m-%d')
        time_delta = df.index[-1] - df.index[0]
        
        # Format timeframe display
        if time_delta.days < 7:
            time_display = f"{time_delta.days} days"
        elif time_delta.days < 30:
            time_display = f"{time_delta.days // 7} weeks"
        elif time_delta.days < 365:
            time_display = f"{time_delta.days // 30} months"
        else:
            time_display = f"{time_delta.days // 365} years"
        
        chart_title = f"{ticker} - {time_display} ({start_date} to {end_date})"
        
        if df is None or df.empty:
            return None
        
        # Check if we have meaningful indicators (not all zeros or insufficient data)
        has_indicators = False
        has_macd = False
        has_rsi = False
        
        if indicators:
            # Check if MACD has meaningful data (not all zeros)
            has_macd = indicators['MACD'] is not None and indicators['MACD'].abs().max() > 0.001
            # Check if RSI has meaningful data (not all zeros)
            has_rsi = indicators['RSI'] is not None and indicators['RSI'].abs().max() > 0.001
            has_indicators = has_macd or has_rsi
        
        # Determine number of rows and create subplot titles
        if not has_indicators:
            # Price only (or Price + Volume)
            if chart_type == 'volume':
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    subplot_titles=(chart_title, 'Volume'),
                    row_heights=[0.7, 0.3]
                )
            else:
                fig = make_subplots(
                    rows=1, cols=1,
                    subplot_titles=(chart_title,)
                )
        elif chart_type == 'volume':
            # Price + Volume + available indicators
            rows = 2
            titles = [chart_title, 'Volume']
            heights = [0.4, 0.2]
            
            if has_macd:
                rows += 1
                titles.append('MACD')
                heights.append(0.2)
            if has_rsi:
                rows += 1
                titles.append('RSI')
                heights.append(0.2)
            
            fig = make_subplots(
                rows=rows, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=tuple(titles),
                row_heights=heights
            )
        else:
            # Price + available indicators
            rows = 1
            titles = [chart_title]
            heights = [0.6]
            
            if has_macd:
                rows += 1
                titles.append('MACD')
                heights.append(0.2)
            if has_rsi:
                rows += 1
                titles.append('RSI')
                heights.append(0.2)
            
            fig = make_subplots(
                rows=rows, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=tuple(titles),
                row_heights=heights
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
        
        if indicators and has_indicators:
            # Moving Averages (always on price chart - row 1)
            fig.add_trace(go.Scatter(
                x=df.index.tolist(), y=indicators['SMA_20'].tolist(),
                name='SMA(20)', line=dict(color='orange', width=1.5)
            ), row=1, col=1)
            
            if indicators['SMA_50'] is not None and len(df) >= 50:
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
            
            # Dynamically determine row numbers
            current_row = 2 if chart_type == 'volume' else 1
            
            # MACD
            if has_macd:
                current_row += 1
                fig.add_trace(go.Scatter(
                    x=df.index.tolist(), y=indicators['MACD'].tolist(),
                    name='MACD', line=dict(color='#2196F3', width=2)
                ), row=current_row, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df.index.tolist(), y=indicators['MACD_signal'].tolist(),
                    name='Signal', line=dict(color='#FF9800', width=2)
                ), row=current_row, col=1)
                
                colors = ['#26a69a' if val >= 0 else '#ef5350' for val in indicators['MACD_diff']]
                fig.add_trace(go.Bar(
                    x=df.index.tolist(), y=indicators['MACD_diff'].tolist(),
                    name='MACD Histogram',
                    marker_color=colors,
                    showlegend=False
                ), row=current_row, col=1)
            
            # RSI
            if has_rsi:
                current_row += 1
                fig.add_trace(go.Scatter(
                    x=df.index.tolist(), y=indicators['RSI'].tolist(),
                    name='RSI', line=dict(color='#9C27B0', width=2)
                ), row=current_row, col=1)
                
                fig.add_hline(y=70, line_dash="dash", line_color="red", 
                             annotation_text="Overbought", row=current_row, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green",
                             annotation_text="Oversold", row=current_row, col=1)
        
        # Adjust height based on number of rows
        if not has_indicators:
            chart_height = 500 if chart_type != 'volume' else 600
            # Add annotation for missing indicators
            if len(df) < 14:
                fig.add_annotation(
                    text=f"ℹ️ Insufficient data ({len(df)} points) for technical indicators.<br>Minimum 14 points required for RSI/MACD.",
                    xref="paper", yref="paper",
                    x=0.5, y=-0.1,
                    showarrow=False,
                    font=dict(size=12, color="#6c757d"),
                    align="center"
                )
        else:
            # Calculate based on number of rows
            base_height = 400
            indicator_height = 150
            num_indicator_rows = (1 if has_macd else 0) + (1 if has_rsi else 0)
            chart_height = base_height + (num_indicator_rows * indicator_height)
            if chart_type == 'volume':
                chart_height += 150  # Extra for volume
        
        # Determine x-axis formatting based on timeframe
        time_delta = df.index[-1] - df.index[0]
        if time_delta.days <= 1:
            # Intraday - show hours and minutes
            xaxis_format = {
                'tickformat': '%H:%M',
                'dtick': 3600000,  # 1 hour in milliseconds
                'tickangle': -45
            }
        elif time_delta.days <= 7:
            # 1 week - show day of week and date
            xaxis_format = {
                'tickformat': '%a<br>%b %d',
                'dtick': 86400000,  # 1 day in milliseconds
                'tickangle': 0
            }
        elif time_delta.days <= 31:
            # 1 month - show date
            xaxis_format = {
                'tickformat': '%b %d',
                'tickangle': -45
            }
        else:
            # Longer periods - show month and year
            xaxis_format = {
                'tickformat': '%b %Y',
                'tickangle': -45
            }
        
        fig.update_layout(
            height=chart_height,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            template='plotly_white',
            hovermode='x unified',
            font=dict(size=10)
        )
        
        # Apply custom x-axis formatting to all subplots
        fig.update_xaxes(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(128,128,128,0.2)',
            **xaxis_format
        )
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        return fig
