// Portfolio Analysis App
const PORTFOLIO_STORAGE_KEY = 'saved_portfolio_tickers';  // Persistent portfolio
const SESSION_STORAGE_KEY = 'session_analysis_tickers';    // Current session
const CONFIG_STORAGE_KEY = 'app_configuration';             // App settings
const DEFAULT_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA'];

let sessionTickers = [];      // Tickers for current analysis (temporary)
let portfolioTickers = [];    // Saved portfolio tickers (persistent)
let appConfig = {              // App configuration
    currency: 'USD',           // USD, EUR, or 'native'
    defaultChartType: 'candlestick',
    displayMode: 'accordion'   // accordion or tabs (for future)
};

// ===== TOAST NOTIFICATION SYSTEM =====

function showToast(message, type = 'info', title = null) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    const defaultTitles = {
        success: 'Success',
        error: 'Error',
        warning: 'Warning',
        info: 'Information'
    };
    
    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || icons.info}</div>
        <div class="toast-content">
            <div class="toast-title">${title || defaultTitles[type]}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Load and save app configuration
function loadAppConfig() {
    const stored = localStorage.getItem(CONFIG_STORAGE_KEY);
    if (stored) {
        try {
            appConfig = { ...appConfig, ...JSON.parse(stored) };
        } catch (e) {
            console.error('Failed to load config:', e);
        }
    }
}

function saveAppConfig() {
    localStorage.setItem(CONFIG_STORAGE_KEY, JSON.stringify(appConfig));
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadAppConfig();
    loadPortfolioFromStorage();
    loadSessionTickers();
    updateTickerChips();
    updateChatTickers();  // Populate chat with portfolio tickers
    
    // Enter key support for analysis
    document.getElementById('tickerInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addTicker();
        }
    });
});

// Load saved portfolio from localStorage
function loadPortfolioFromStorage() {
    const stored = localStorage.getItem(PORTFOLIO_STORAGE_KEY);
    if (stored) {
        try {
            portfolioTickers = JSON.parse(stored);
        } catch (e) {
            portfolioTickers = [];
        }
    }
}

// Save portfolio to localStorage
function savePortfolioToStorage() {
    localStorage.setItem(PORTFOLIO_STORAGE_KEY, JSON.stringify(portfolioTickers));
}

// Load session tickers (or use portfolio if session is empty)
function loadSessionTickers() {
    const stored = localStorage.getItem(SESSION_STORAGE_KEY);
    if (stored) {
        try {
            sessionTickers = JSON.parse(stored);
        } catch (e) {
            sessionTickers = [];
        }
    }
    
    // If no session tickers, use portfolio tickers
    if (sessionTickers.length === 0 && portfolioTickers.length > 0) {
        sessionTickers = [...portfolioTickers];
        saveSessionTickers();
    }
}

// Save session tickers
function saveSessionTickers() {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(sessionTickers));
}

// Add ticker to analysis session
function addTicker() {
    const input = document.getElementById('tickerInput');
    const ticker = input.value.trim().toUpperCase();
    
    if (!ticker) {
        showToast('Please enter a ticker symbol', 'warning');
        return;
    }
    
    if (sessionTickers.includes(ticker)) {
        showToast(`${ticker} is already in your analysis session`, 'info');
        return;
    }
    
    sessionTickers.push(ticker);
    input.value = '';
    saveSessionTickers();
    updateTickerChips();
    showToast(`${ticker} added to analysis session`, 'success');
}

// Remove ticker from analysis session (not from portfolio)
function removeTicker(ticker) {
    sessionTickers = sessionTickers.filter(t => t !== ticker);
    saveSessionTickers();
    updateTickerChips();
}

// Clear all session tickers
function clearTickers() {
    if (sessionTickers.length === 0) return;
    
    if (confirm('Clear all tickers from current analysis?\n\n(This will not affect your saved portfolio)')) {
        sessionTickers = [];
        saveSessionTickers();
        updateTickerChips();
        document.getElementById('results').style.display = 'none';
    }
}

// Load portfolio into analysis session
function loadPortfolioToSession() {
    if (portfolioTickers.length === 0) {
        showToast('No saved portfolio found. Please configure your portfolio first.', 'warning');
        togglePortfolioConfig();
        return;
    }
    
    sessionTickers = [...portfolioTickers];
    saveSessionTickers();
    updateTickerChips();
    showToast(`Loaded ${portfolioTickers.length} ticker(s) from portfolio: ${portfolioTickers.join(', ')}`, 'success');
}

// Load default portfolio
function loadDefaultPortfolio() {
    sessionTickers = [...DEFAULT_TICKERS];
    saveSessionTickers();
    updateTickerChips();
}

// Toggle portfolio configuration modal
function togglePortfolioConfig() {
    const modal = document.getElementById('portfolioModal');
    if (modal.classList.contains('show')) {
        modal.classList.remove('show');
    } else {
        modal.classList.add('show');
        updateSavedTickersList();
        loadConfigToUI();
    }
}

// Load config settings to UI
function loadConfigToUI() {
    document.getElementById('configChartType').value = appConfig.defaultChartType;
    document.getElementById('configCurrency').value = appConfig.currency;
}

// Save config settings from UI
function saveConfigSettings() {
    appConfig.defaultChartType = document.getElementById('configChartType').value;
    appConfig.currency = document.getElementById('configCurrency').value;
    saveAppConfig();
    showToast('Settings saved successfully', 'success');
}

// Update saved tickers list in modal
function updateSavedTickersList() {
    const container = document.getElementById('savedTickersList');
    
    if (portfolioTickers.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    container.innerHTML = portfolioTickers.map(ticker => `
        <span class="ticker-chip">
            ${ticker}
            <button class="ticker-chip-remove" onclick="removeFromPortfolio('${ticker}');">×</button>
        </span>
    `).join('');
}

// Add ticker to portfolio (from modal)
function addTickerToPortfolio() {
    const input = document.getElementById('portfolioTickerInput');
    const ticker = input.value.trim().toUpperCase();
    
    if (!ticker) {
        alert('Please enter a ticker symbol');
        return;
    }
    
    if (portfolioTickers.includes(ticker)) {
        alert('Ticker already in portfolio');
        return;
    }
    
    // Basic validation: 1-5 alphanumeric characters (covers most global tickers)
    if (!/^[A-Z0-9]{1,5}$/.test(ticker)) {
        if (confirm(`"${ticker}" doesn't match typical ticker format.\n\nAdd anyway?`)) {
            portfolioTickers.push(ticker);
        } else {
            return;
        }
    } else {
        portfolioTickers.push(ticker);
    }
    
    input.value = '';
    savePortfolioToStorage();
    updateSavedTickersList();
}

// Remove ticker from portfolio
function removeFromPortfolio(ticker) {
    portfolioTickers = portfolioTickers.filter(t => t !== ticker);
    savePortfolioToStorage();
    updateSavedTickersList();
}

// Add ticker to portfolio from analysis view
function addToPortfolioFromAnalysis(ticker) {
    if (portfolioTickers.includes(ticker)) {
        alert(`${ticker} is already in your portfolio`);
        return;
    }
    
    portfolioTickers.push(ticker);
    savePortfolioToStorage();
    updateTickerChips(); // Update star badges
    alert(`✅ ${ticker} added to portfolio!`);
    
    // Re-render the stock details to show "In Portfolio" instead of button
    const resultIndex = window.analysisResults.findIndex(r => r.ticker === ticker);
    if (resultIndex !== -1) {
        renderStockDetails(ticker, resultIndex);
    }
}

// Save portfolio preferences
function savePortfolioPreferences() {
    if (portfolioTickers.length === 0) {
        alert('Portfolio is empty. Add some tickers first!');
        return;
    }
    
    savePortfolioToStorage();
    alert(`✅ Portfolio saved with ${portfolioTickers.length} ticker(s): ${portfolioTickers.join(', ')}`);
    togglePortfolioConfig();
}

// Clear all portfolio tickers with confirmation
function clearAllTickers() {
    if (portfolioTickers.length === 0) {
        alert('Portfolio is already empty.');
        return;
    }
    
    if (confirm(`⚠️ Are you sure you want to remove all ${portfolioTickers.length} ticker(s) from your portfolio?\n\nThis will NOT affect your current analysis session.`)) {
        portfolioTickers = [];
        savePortfolioToStorage();
        updateSavedTickersList();
        alert('✅ Portfolio cleared successfully.');
    }
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('portfolioModal');
    if (event.target === modal) {
        togglePortfolioConfig();
    }
});

// Update ticker chips display (shows session tickers)
function updateTickerChips() {
    const container = document.getElementById('tickerChips');
    
    if (sessionTickers.length === 0) {
        container.innerHTML = '<p style="color: #7f8c8d; padding: 10px;">No tickers in analysis. Add tickers above or load your portfolio.</p>';
        return;
    }
    
    container.innerHTML = sessionTickers.map(ticker => {
        const isInPortfolio = portfolioTickers.includes(ticker);
        const badge = isInPortfolio ? '<span style="color: #22c55e; margin-left: 5px;" title="In Portfolio">⭐</span>' : '';
        return `
            <div class="ticker-chip">
                ${ticker}${badge}
                <span class="remove" onclick="removeTicker('${ticker}')">×</span>
            </div>
        `;
    }).join('');
}

// Analyze portfolio
async function analyzePortfolio() {
    if (sessionTickers.length === 0) {
        showToast('Please add at least one ticker to analyze', 'warning');
        return;
    }
    
    // Use configured default chart type
    const chartType = appConfig.defaultChartType;
    
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
                tickers: sessionTickers,
                chart_type: chartType  // Initial chart type for all
            })
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const data = await response.json();
        
        // Check if any results failed
        if (data.results && data.results.length > 0) {
            const failedTickers = sessionTickers.filter(t => 
                !data.results.find(r => r.ticker === t)
            );
            
            if (failedTickers.length > 0) {
                showToast(
                    `Failed to analyze: ${failedTickers.join(', ')}. Check ticker symbols and try adding exchange suffix (e.g., UPL.IR for Irish stocks).`,
                    'error',
                    'Analysis Warning'
                );
            }
            
            if (data.results.length > 0) {
                displayResults(data);
            } else {
                showToast('No stocks were successfully analyzed. Please check your ticker symbols.', 'error');
            }
        } else {
            showToast('Analysis returned no results. Please verify your ticker symbols.', 'error');
        }
        
    } catch (error) {
        showToast('Error analyzing portfolio: ' + error.message, 'error');
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
        showToast('No results to display', 'warning');
        return;
    }
    
    // Show results section
    document.getElementById('results').style.display = 'block';
    
    // Update timestamp
    const now = new Date();
    document.getElementById('timestamp').textContent = 
        `Analysis generated on ${now.toLocaleString()}`;
    
    // Display portfolio performance stats
    displayPortfolioStats(results);
    
    // Display summary table
    displaySummaryTable(results);
    
    // Display detailed analysis
    displayDetailedAnalysis(results);
    
    // Update chat ticker dropdown
    updateChatTickers();
    
    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

// Display portfolio performance stats
function displayPortfolioStats(results) {
    const container = document.getElementById('portfolioStats');
    
    if (!results || results.length === 0) {
        container.innerHTML = '<p>No data available</p>';
        return;
    }
    
    // Calculate stats
    const totalStocks = results.length;
    const avgScore = (results.reduce((sum, r) => sum + (r.combined_score || 0), 0) / totalStocks).toFixed(1);
    const avgChange = results.reduce((sum, r) => sum + (r.price_change || 0), 0) / totalStocks;
    
    // Count recommendations - normalize STRONG BUY/SELL to BUY/SELL
    const recommendations = results.reduce((acc, r) => {
        let rec = r.recommendation || 'HOLD';
        // Normalize: STRONG BUY -> BUY, STRONG SELL -> SELL
        if (rec.includes('BUY')) rec = 'BUY';
        else if (rec.includes('SELL')) rec = 'SELL';
        else if (!rec.includes('HOLD')) rec = 'HOLD';
        
        acc[rec] = (acc[rec] || 0) + 1;
        return acc;
    }, {});
    
    // Find best and worst performers
    const sortedByChange = [...results].sort((a, b) => 
        (b.price_change || 0) - (a.price_change || 0)
    );
    const bestPerformer = sortedByChange[0];
    const worstPerformer = sortedByChange[sortedByChange.length - 1];
    
    // Determine overall sentiment
    let overallClass = 'neutral';
    let overallEmoji = '😐';
    if (avgScore >= 0.6) {
        overallClass = 'positive';
        overallEmoji = '😊';
    } else if (avgScore <= 0.4) {
        overallClass = 'negative';
        overallEmoji = '😞';
    }
    
    // Render stats grid based on number of stocks
    let statsHTML = `
        <div class="stat-card">
            <div class="stat-label">Total Stocks</div>
            <div class="stat-value neutral">${totalStocks}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">${totalStocks > 1 ? 'Avg Sentiment' : 'Sentiment'}</div>
            <div class="stat-value ${overallClass}">${overallEmoji} ${(avgScore * 100).toFixed(1)}%</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">${totalStocks > 1 ? 'Avg 3M Change' : '3M Change'}</div>
            <div class="stat-value ${avgChange >= 0 ? 'positive' : 'negative'}">
                ${avgChange >= 0 ? '▲' : '▼'} ${Math.abs(avgChange).toFixed(2)}%
            </div>
        </div>
    `;
    
    // Only show recommendation breakdown if multiple stocks
    if (totalStocks > 1) {
        statsHTML += `
        <div class="stat-card">
            <div class="stat-label">Recommendations</div>
            <div class="stat-value neutral">
                <div class="stat-subtext">
                    ${recommendations.BUY || 0} Buy | 
                    ${recommendations.HOLD || 0} Hold | 
                    ${recommendations.SELL || 0} Sell
                </div>
            </div>
        </div>
        `;
    } else {
        // Single stock - show the recommendation directly
        const singleRec = results[0].recommendation || 'HOLD';
        // Determine class and emoji based on recommendation
        let recClass, recEmoji;
        if (singleRec.includes('BUY')) {
            recClass = 'positive';
            recEmoji = '📈';
        } else if (singleRec.includes('SELL')) {
            recClass = 'negative';
            recEmoji = '📉';
        } else {
            recClass = 'neutral';
            recEmoji = '➡️';
        }
        
        statsHTML += `
        <div class="stat-card">
            <div class="stat-label">Recommendation</div>
            <div class="stat-value ${recClass}">${recEmoji} ${singleRec}</div>
        </div>
        `;
    }
    
    // Only show best/worst performers if multiple stocks
    if (totalStocks > 1) {
        statsHTML += `
        <div class="stat-card">
            <div class="stat-label">🏆 Best Performer</div>
            <div class="stat-value positive">
                ${bestPerformer.ticker}
                <div class="stat-subtext">+${(bestPerformer.price_change || 0).toFixed(2)}%</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-label">📉 Worst Performer</div>
            <div class="stat-value negative">
                ${worstPerformer.ticker}
                <div class="stat-subtext">${(worstPerformer.price_change || 0).toFixed(2)}%</div>
            </div>
        </div>
        `;
    }
    
    container.innerHTML = statsHTML;
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
        <div class="stock-accordion" id="card_${r.ticker}">
            <div class="stock-accordion-header" onclick="toggleStockDetails('${r.ticker}', ${index})" 
                 style="border-left: 4px solid ${r.color}">
                <div class="accordion-header-content">
                    <div class="accordion-header-main">
                        <h4 class="stock-title">
                            ${r.ticker} - ${r.name || r.ticker}
                            <span class="recommendation-badge" style="background: ${r.color}">
                                ${r.recommendation}
                            </span>
                        </h4>
                        <div class="accordion-header-metrics">
                            <span class="metric-badge">Price: $${r.current_price.toFixed(2)}</span>
                            <span class="metric-badge ${r.price_change >= 0 ? 'positive' : 'negative'}">
                                ${r.price_change >= 0 ? '↑' : '↓'} ${Math.abs(r.price_change).toFixed(2)}%
                            </span>
                            <span class="metric-badge">Score: ${r.combined_score.toFixed(3)}</span>
                        </div>
                    </div>
                    <div class="accordion-toggle">
                        <span class="toggle-icon" id="toggle_${r.ticker}">▼</span>
                    </div>
                </div>
            </div>
            
            <div class="stock-accordion-body" id="body_${r.ticker}" style="display: none;">
                <div class="loading-placeholder" id="loading_${r.ticker}">
                    ⏳ Loading detailed analysis...
                </div>
            </div>
        </div>
    `).join('');
    
    document.getElementById('detailsContainer').innerHTML = html;
    
    // Store results globally
    window.analysisResults = results;
}

// ===== ACCORDION FUNCTIONS =====

function toggleStockDetails(ticker, resultIndex) {
    const body = document.getElementById(`body_${ticker}`);
    const toggle = document.getElementById(`toggle_${ticker}`);
    const loading = document.getElementById(`loading_${ticker}`);
    
    if (body.style.display === 'none') {
        // Opening - load content if not already loaded
        body.style.display = 'block';
        toggle.textContent = '▲';
        
        // Check if content is already loaded
        if (loading && loading.style.display !== 'none') {
            // Load the detailed content
            renderStockDetails(ticker, resultIndex);
        }
    } else {
        // Closing
        body.style.display = 'none';
        toggle.textContent = '▼';
    }
}

function renderStockDetails(ticker, resultIndex) {
    const r = window.analysisResults[resultIndex];
    const body = document.getElementById(`body_${ticker}`);
    const isInPortfolio = portfolioTickers.includes(ticker);
    
    const html = `
        <div class="stock-details-content">
            <div style="display: flex; justify-content: flex-end; margin-bottom: 15px;">
                ${!isInPortfolio ? `
                    <button onclick="addToPortfolioFromAnalysis('${ticker}')" class="btn-small btn-primary" style="display: flex; align-items: center; gap: 5px;">
                        ⭐ Add to Portfolio
                    </button>
                ` : `
                    <span style="color: #22c55e; font-weight: 600;">⭐ In Portfolio</span>
                `}
            </div>
            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="metric-label">Combined Score</div>
                    <div class="metric-value">${r.combined_score.toFixed(3)}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Overall Sentiment</div>
                    <div class="metric-value">${r.sentiment_score.toFixed(3)}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">News Sentiment</div>
                    <div class="metric-value">${r.news_sentiment_score ? r.news_sentiment_score.toFixed(3) : 'N/A'}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Social Sentiment</div>
                    <div class="metric-value">${r.social_sentiment_score ? r.social_sentiment_score.toFixed(3) : 'N/A'}</div>
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
                ${r.news_count > 0 ? `
                    <div class="section-title">📰 News Sentiment (${r.news_count} articles)</div>
                    ${r.sentiment_results.filter(s => s.source_type === 'news').map(sent => {
                        const emoji = sent.label === 'positive' ? '😊' : sent.label === 'negative' ? '😞' : '😐';
                        const posPercent = (sent.positive * 100).toFixed(1);
                        const neuPercent = (sent.neutral * 100).toFixed(1);
                        const negPercent = (sent.negative * 100).toFixed(1);
                        return `
                        <div class="news-item sentiment-${sent.label}">
                            <div class="news-title">
                                ${sent.link ? `<a href="${sent.link}" target="_blank" rel="noopener">${sent.title}</a>` : sent.title}
                                ${sent.publisher ? `<span class="news-publisher">- ${sent.publisher}</span>` : ''}
                            </div>
                            <div class="news-sentiment">
                                ${emoji} <strong>${sent.label.toUpperCase()}</strong> | 
                                😊 ${posPercent}% · 😐 ${neuPercent}% · 😞 ${negPercent}%
                            </div>
                        </div>
                    `}).join('')}
                ` : ''}
                
                ${r.social_count > 0 ? `
                    <div class="section-title">💬 Social Media Sentiment (${r.social_count} posts)</div>
                    ${r.sentiment_results.filter(s => s.source_type === 'social_media').map(sent => {
                        const emoji = sent.label === 'positive' ? '😊' : sent.label === 'negative' ? '😞' : '😐';
                        const posPercent = (sent.positive * 100).toFixed(1);
                        const neuPercent = (sent.neutral * 100).toFixed(1);
                        const negPercent = (sent.negative * 100).toFixed(1);
                        return `
                        <div class="news-item sentiment-${sent.label}">
                            <div class="news-title">
                                <strong>${sent.source || 'Social Media'}</strong>: ${sent.text}
                            </div>
                            <div class="news-sentiment">
                                ${emoji} <strong>${sent.label.toUpperCase()}</strong> | 
                                😊 ${posPercent}% · 😐 ${neuPercent}% · 😞 ${negPercent}%
                            </div>
                        </div>
                    `}).join('')}
                ` : ''}
            ` : '<p>No sentiment data available</p>'}
            
            ${r.chart_data ? `
                <div class="section-title">📊 Interactive Chart</div>
                <div class="chart-controls">
                    <label for="chartType_${r.ticker}">Chart Type:</label>
                    <select id="chartType_${r.ticker}" class="chart-type-select-inline" 
                            onchange="updateChart('${r.ticker}', ${resultIndex})">
                        <option value="candlestick" selected>🕯️ Candlestick</option>
                        <option value="line">📈 Line</option>
                        <option value="ohlc">📊 OHLC</option>
                        <option value="area">📉 Area</option>
                        <option value="mountain">⛰️ Mountain</option>
                        <option value="volume">📊 Volume</option>
                    </select>
                    
                    <label for="timeframe_${r.ticker}" style="margin-left: 15px;">Timeframe:</label>
                    <select id="timeframe_${r.ticker}" class="chart-type-select-inline" 
                            onchange="updateChart('${r.ticker}', ${resultIndex})">
                        <option value="1d">1 Day</option>
                        <option value="5d">1 Week</option>
                        <option value="1mo">1 Month</option>
                        <option value="3mo" selected>3 Months</option>
                        <option value="6mo">6 Months</option>
                        <option value="1y">1 Year</option>
                        <option value="2y">2 Years</option>
                        <option value="5y">5 Years</option>
                        <option value="max">All Time</option>
                    </select>
                    
                    <button class="btn-small btn-refresh" onclick="refreshChart('${r.ticker}', ${resultIndex})">
                        🔄 Refresh
                    </button>
                </div>
                <div class="chart-container" id="chart_${r.ticker}"></div>
            ` : ''}
        </div>
    `;
    
    body.innerHTML = html;
    
    // Render chart if available
    if (r.chart_data) {
        const initialChartType = document.getElementById('chartType').value;
        const dropdown = document.getElementById(`chartType_${r.ticker}`);
        if (dropdown) {
            dropdown.value = r.chart_type_used || initialChartType;
        }
        console.log(`Rendering ${r.ticker} with chart type: ${r.chart_type_used || initialChartType}`);
        renderChart(r.ticker, r.chart_data);
    }
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
        
        // Clear any existing chart first
        chartDiv.innerHTML = '';
        
        // Create a new plot with unique data
        Plotly.newPlot(chartDiv, chartData.data, chartData.layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        }).then(() => {
            console.log(`✓ Chart rendered successfully for ${ticker}`);
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
    const timeframe = document.getElementById(`timeframe_${ticker}`).value;
    console.log(`Updating ${ticker} to ${chartType} chart with ${timeframe} timeframe`);
    
    // Show loading on this specific chart
    const chartDiv = document.getElementById(`chart_${ticker}`);
    chartDiv.innerHTML = '<div class="chart-loading">⏳ Regenerating chart...</div>';
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                tickers: [ticker],
                chart_type: chartType,
                timeframe: timeframe,
                use_cache: false
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update chart');
        }
        
        const data = await response.json();
        
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

// ===== AI CHAT FUNCTIONS =====

function toggleChat() {
    const chatPanel = document.getElementById('chatPanel');
    chatPanel.classList.toggle('chat-open');
}

function updateChatTickers() {
    const chatTicker = document.getElementById('chatTicker');
    const currentValue = chatTicker.value;
    
    // Clear and rebuild options
    chatTicker.innerHTML = '<option value="">💬 General Question...</option>';
    
    // Combine all available stocks: analyzed + portfolio + session
    const availableTickers = new Map(); // Use Map to avoid duplicates
    
    // 1. Add currently analyzed stocks (highest priority - has full data)
    if (window.analysisResults && window.analysisResults.length > 0) {
        window.analysisResults.forEach(result => {
            availableTickers.set(result.ticker, {
                ticker: result.ticker,
                name: result.name || result.ticker,
                source: 'analyzed'
            });
        });
    }
    
    // 2. Add portfolio tickers
    portfolioTickers.forEach(ticker => {
        if (!availableTickers.has(ticker)) {
            availableTickers.set(ticker, {
                ticker: ticker,
                name: ticker,
                source: 'portfolio'
            });
        }
    });
    
    // 3. Add session tickers
    sessionTickers.forEach(ticker => {
        if (!availableTickers.has(ticker)) {
            availableTickers.set(ticker, {
                ticker: ticker,
                name: ticker,
                source: 'session'
            });
        }
    });
    
    // Populate dropdown with sections
    if (availableTickers.size > 0) {
        const analyzed = Array.from(availableTickers.values()).filter(s => s.source === 'analyzed');
        const portfolio = Array.from(availableTickers.values()).filter(s => s.source === 'portfolio');
        const session = Array.from(availableTickers.values()).filter(s => s.source === 'session');
        
        if (analyzed.length > 0) {
            const optgroup = document.createElement('optgroup');
            optgroup.label = '📊 Analyzed Stocks';
            analyzed.forEach(stock => {
                const option = document.createElement('option');
                option.value = stock.ticker;
                option.textContent = `${stock.ticker}${stock.name !== stock.ticker ? ' - ' + stock.name : ''}`;
                optgroup.appendChild(option);
            });
            chatTicker.appendChild(optgroup);
        }
        
        if (portfolio.length > 0) {
            const optgroup = document.createElement('optgroup');
            optgroup.label = '⭐ Portfolio';
            portfolio.forEach(stock => {
                const option = document.createElement('option');
                option.value = stock.ticker;
                option.textContent = stock.ticker;
                optgroup.appendChild(option);
            });
            chatTicker.appendChild(optgroup);
        }
        
        if (session.length > 0) {
            const optgroup = document.createElement('optgroup');
            optgroup.label = '🔍 Session';
            session.forEach(stock => {
                const option = document.createElement('option');
                option.value = stock.ticker;
                option.textContent = stock.ticker;
                optgroup.appendChild(option);
            });
            chatTicker.appendChild(optgroup);
        }
    }
    
    // Restore selection if it still exists
    if (currentValue && availableTickers.has(currentValue)) {
        chatTicker.value = currentValue;
    }
}

function addChatMessage(message, isUser = false) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = message;
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const tickerSelect = document.getElementById('chatTicker');
    const question = input.value.trim();
    const ticker = tickerSelect.value;
    
    if (!question) {
        return;
    }
    
    // If no ticker selected, provide general response or ask user to be specific
    if (!ticker) {
        addChatMessage(question, true);
        input.value = '';
        
        // Try to extract ticker from question (e.g., "What about MSFT?")
        const tickerMatch = question.match(/\b([A-Z]{1,5}(?:\.[A-Z]{1,2})?)\b/);
        if (tickerMatch && window.analysisResults) {
            const extractedTicker = tickerMatch[1];
            const foundResult = window.analysisResults.find(r => r.ticker === extractedTicker);
            if (foundResult) {
                // Auto-select and answer
                tickerSelect.value = extractedTicker;
                sendChatWithTicker(question, extractedTicker);
                return;
            }
        }
        
        addChatMessage('💡 Please select a stock from the dropdown, or mention a ticker in your question (e.g., "What about MSFT?").', false);
        return;
    }
    
    // Add user message
    addChatMessage(question, true);
    input.value = '';
    
    await sendChatWithTicker(question, ticker);
}

async function sendChatWithTicker(question, ticker) {
    // Show loading
    const loadingId = 'loading-' + Date.now();
    addChatMessage('🤔 Thinking...', false);
    const messagesContainer = document.getElementById('chatMessages');
    const loadingMsg = messagesContainer.lastChild;
    loadingMsg.id = loadingId;
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                ticker: ticker
            })
        });
        
        // Remove loading message
        if (loadingMsg) {
            loadingMsg.remove();
        }
        
        if (!response.ok) {
            throw new Error('Chat request failed');
        }
        
        const data = await response.json();
        
        if (data.success) {
            const confidence = (data.confidence * 100).toFixed(0);
            addChatMessage(`${data.answer}\n\n(Confidence: ${confidence}%)`, false);
        } else {
            addChatMessage(data.answer || 'Sorry, I could not answer that question.', false);
        }
        
    } catch (error) {
        // Remove loading message
        if (loadingMsg) {
            loadingMsg.remove();
        }
        console.error('Chat error:', error);
        addChatMessage('❌ Sorry, there was an error processing your question.', false);
    }
}
