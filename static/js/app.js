// Portfolio Analysis App
const STORAGE_KEY = 'portfolio_tickers';
const DEFAULT_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA'];

let tickers = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadTickersFromStorage();
    updateTickerChips();
    
    // Enter key support
    document.getElementById('tickerInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addTicker();
        }
    });
});

// Load tickers from localStorage
function loadTickersFromStorage() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
        try {
            tickers = JSON.parse(stored);
        } catch (e) {
            tickers = [];
        }
    }
}

// Save tickers to localStorage
function saveTickersToStorage() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tickers));
}

// Add ticker
function addTicker() {
    const input = document.getElementById('tickerInput');
    const ticker = input.value.trim().toUpperCase();
    
    if (!ticker) {
        alert('Please enter a ticker symbol');
        return;
    }
    
    if (tickers.includes(ticker)) {
        alert('Ticker already added');
        return;
    }
    
    tickers.push(ticker);
    input.value = '';
    saveTickersToStorage();
    updateTickerChips();
}

// Remove ticker
function removeTicker(ticker) {
    tickers = tickers.filter(t => t !== ticker);
    saveTickersToStorage();
    updateTickerChips();
}

// Clear all tickers
function clearTickers() {
    if (tickers.length === 0) return;
    
    if (confirm('Are you sure you want to clear all tickers?')) {
        tickers = [];
        saveTickersToStorage();
        updateTickerChips();
        document.getElementById('results').style.display = 'none';
    }
}

// Load default portfolio
function loadDefaultPortfolio() {
    tickers = [...DEFAULT_TICKERS];
    saveTickersToStorage();
    updateTickerChips();
}

// Update ticker chips display
function updateTickerChips() {
    const container = document.getElementById('tickerChips');
    
    if (tickers.length === 0) {
        container.innerHTML = '<p style="color: #7f8c8d; padding: 10px;">No tickers added yet. Add some to get started!</p>';
        return;
    }
    
    container.innerHTML = tickers.map(ticker => `
        <div class="ticker-chip">
            ${ticker}
            <span class="remove" onclick="removeTicker('${ticker}')">×</span>
        </div>
    `).join('');
}

// Analyze portfolio
async function analyzePortfolio() {
    if (tickers.length === 0) {
        alert('Please add at least one ticker to analyze');
        return;
    }
    
    // Get selected default chart type (used for initial render)
    const chartType = document.getElementById('chartType').value;
    
    // Show loading
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    document.getElementById('analyzeBtn').disabled = true;
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                tickers: tickers,
                chart_type: chartType  // Initial chart type for all
            })
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        alert('Error analyzing portfolio: ' + error.message);
        console.error('Error:', error);
    } finally {
        document.getElementById('loadingIndicator').style.display = 'none';
        document.getElementById('analyzeBtn').disabled = false;
    }
}

// Display results
function displayResults(data) {
    const results = data.results;
    
    if (!results || results.length === 0) {
        alert('No results to display');
        return;
    }
    
    // Show results section
    document.getElementById('results').style.display = 'block';
    
    // Update timestamp
    const now = new Date();
    document.getElementById('timestamp').textContent = 
        `Analysis generated on ${now.toLocaleString()}`;
    
    // Display summary table
    displaySummaryTable(results);
    
    // Display detailed analysis
    displayDetailedAnalysis(results);
    
    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

// Display summary table
function displaySummaryTable(results) {
    const html = `
        <table>
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Name</th>
                    <th>Recommendation</th>
                    <th>Combined Score</th>
                    <th>Current Price</th>
                    <th>Change (3mo)</th>
                    <th>Sentiment</th>
                    <th>Technical</th>
                </tr>
            </thead>
            <tbody>
                ${results.map(r => `
                    <tr>
                        <td><strong>${r.ticker}</strong></td>
                        <td>${r.name || r.ticker}</td>
                        <td>
                            <span class="recommendation-badge" style="background: ${r.color}">
                                ${r.recommendation}
                            </span>
                        </td>
                        <td>${r.combined_score.toFixed(3)}</td>
                        <td>$${r.current_price.toFixed(2)}</td>
                        <td class="${r.price_change >= 0 ? 'price-change-positive' : 'price-change-negative'}">
                            ${r.price_change >= 0 ? '+' : ''}${r.price_change.toFixed(2)}%
                        </td>
                        <td>${r.sentiment_score.toFixed(3)}</td>
                        <td>${r.technical_score.toFixed(3)} (${r.technical_signal})</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    document.getElementById('summaryTable').innerHTML = html;
}

// Display detailed analysis
function displayDetailedAnalysis(results) {
    const html = results.map((r, index) => `
        <div class="stock-card" style="border-left-color: ${r.color}" id="card_${r.ticker}">
            <h4>
                ${r.ticker} - ${r.name || r.ticker}
                <span class="recommendation-badge" style="background: ${r.color}">
                    ${r.recommendation}
                </span>
            </h4>
            
            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="metric-label">Combined Score</div>
                    <div class="metric-value">${r.combined_score.toFixed(3)}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Sentiment Score</div>
                    <div class="metric-value">${r.sentiment_score.toFixed(3)}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Technical Score</div>
                    <div class="metric-value">${r.technical_score.toFixed(3)}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Current Price</div>
                    <div class="metric-value">$${r.current_price.toFixed(2)}</div>
                </div>
            </div>
            
            <div class="section-title">🔍 Technical Indicators</div>
            <p><strong>Signal:</strong> ${r.technical_signal}</p>
            <ul class="reasons-list">
                ${r.technical_reasons.map(reason => `<li>${reason}</li>`).join('')}
            </ul>
            
            ${r.sentiment_results && r.sentiment_results.length > 0 ? `
                <div class="section-title">📰 News Sentiment</div>
                ${r.sentiment_results.map(sent => `
                    <div class="news-item sentiment-${sent.label}">
                        <div class="news-title">${sent.title}</div>
                        <div class="news-sentiment">
                            <strong>${sent.label.toUpperCase()}</strong> (Score: ${sent.score.toFixed(3)}) | 
                            Pos: ${sent.positive.toFixed(2)}, Neu: ${sent.neutral.toFixed(2)}, Neg: ${sent.negative.toFixed(2)}
                        </div>
                    </div>
                `).join('')}
            ` : '<p>No news available</p>'}
            
            ${r.chart_data ? `
                <div class="section-title">📊 Interactive Chart</div>
                <div class="chart-controls">
                    <label for="chartType_${r.ticker}">Chart Type:</label>
                    <select id="chartType_${r.ticker}" class="chart-type-select-inline" 
                            onchange="updateChart('${r.ticker}', ${index})">
                        <option value="candlestick" selected>🕯️ Candlestick</option>
                        <option value="line">📈 Line</option>
                        <option value="ohlc">📊 OHLC</option>
                        <option value="area">📉 Area</option>
                        <option value="mountain">⛰️ Mountain</option>
                        <option value="volume">📊 Volume</option>
                    </select>
                    <button class="btn-small btn-refresh" onclick="refreshChart('${r.ticker}', ${index})">
                        🔄 Refresh
                    </button>
                </div>
                <div class="chart-container" id="chart_${r.ticker}"></div>
            ` : ''}
        </div>
    `).join('');
    
    document.getElementById('detailsContainer').innerHTML = html;
    
    // Store results globally for chart updates
    window.analysisResults = results;
    
    // Get the initial chart type used
    const initialChartType = document.getElementById('chartType').value;
    
    // Render Plotly charts after DOM is updated
    results.forEach((r, index) => {
        if (r.chart_data) {
            // Set the dropdown to the initial chart type
            const dropdown = document.getElementById(`chartType_${r.ticker}`);
            if (dropdown) {
                dropdown.value = r.chart_type_used || initialChartType;
            }
            console.log(`Rendering ${r.ticker} with chart type: ${r.chart_type_used || initialChartType}`);
            renderChart(r.ticker, r.chart_data);
        } else {
            console.warn(`No chart data for ${r.ticker}`);
        }
    });
}

// Render a single chart
function renderChart(ticker, chartDataJson) {
    try {
        const chartData = JSON.parse(chartDataJson);
        const chartDiv = document.getElementById(`chart_${ticker}`);
        
        if (!chartDiv) {
            console.error(`Chart container not found for ${ticker}`);
            return;
        }
        
        // DEBUG: Log first price point and chart title to verify uniqueness
        console.log(`\n=== RENDERING ${ticker} ===`);
        console.log('Chart title:', chartData.layout?.title?.text || chartData.layout?.annotations?.[0]?.text);
        if (chartData.data && chartData.data[0]) {
            const firstTrace = chartData.data[0];
            console.log('First trace type:', firstTrace.type);
            console.log('First trace name:', firstTrace.name);
            // Log first few data points to verify uniqueness
            if (firstTrace.x && firstTrace.x.length > 0) {
                console.log('First date:', firstTrace.x[0]);
                console.log('Last date:', firstTrace.x[firstTrace.x.length - 1]);
            }
            if (firstTrace.close && firstTrace.close.length > 0) {
                console.log('First close price:', firstTrace.close[0]);
                console.log('Last close price:', firstTrace.close[firstTrace.close.length - 1]);
            } else if (firstTrace.y && firstTrace.y.length > 0) {
                console.log('First y value:', firstTrace.y[0]);
                console.log('Last y value:', firstTrace.y[firstTrace.y.length - 1]);
            }
        }
        console.log('Total traces:', chartData.data.length);
        console.log('========================\n');
        
        // Clear any existing chart first
        chartDiv.innerHTML = '';
        
        // Create a new plot with unique data
        Plotly.newPlot(chartDiv, chartData.data, chartData.layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        }).then(() => {
            console.log(`✓ Chart rendered successfully for ${ticker} (${chartData.data.length} traces)`);
        }).catch(err => {
            console.error(`✗ Failed to render chart for ${ticker}:`, err);
            chartDiv.innerHTML = '<div class="chart-error">Failed to render chart</div>';
        });
        
    } catch (e) {
        console.error(`Error parsing chart data for ${ticker}:`, e);
        const chartDiv = document.getElementById(`chart_${ticker}`);
        if (chartDiv) {
            chartDiv.innerHTML = '<div class="chart-error">Error parsing chart data</div>';
        }
    }
}

// Update chart type for a specific ticker
async function updateChart(ticker, resultIndex) {
    const chartType = document.getElementById(`chartType_${ticker}`).value;
    console.log(`Updating ${ticker} to ${chartType} chart`);
    
    // Show loading on this specific chart
    const chartDiv = document.getElementById(`chart_${ticker}`);
    chartDiv.innerHTML = '<div class="chart-loading">⏳ Regenerating chart...</div>';
    
    try {
        // Request chart update using cache (faster)
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                tickers: [ticker],
                chart_type: chartType,
                use_cache: true  // Use cached data for faster regeneration
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update chart');
        }
        
        const data = await response.json();
        console.log(`Chart update for ${ticker}:`, data.from_cache ? 'from cache' : 'fresh analysis');
        
        if (data.results && data.results.length > 0) {
            const result = data.results[0];
            window.analysisResults[resultIndex] = result;
            renderChart(ticker, result.chart_data);
        }
    } catch (error) {
        console.error(`Error updating chart for ${ticker}:`, error);
        chartDiv.innerHTML = '<div class="chart-error">❌ Error loading chart. Try refreshing the page.</div>';
    }
}

// Refresh current chart
function refreshChart(ticker, resultIndex) {
    updateChart(ticker, resultIndex);
}
