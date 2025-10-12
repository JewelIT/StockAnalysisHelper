// Portfolio Analysis App

// ===== DEBUG CONFIGURATION =====
// Set DEBUG_MODE in localStorage to enable console logging
// Usage: localStorage.setItem('DEBUG_MODE', 'true')  // Enable
// To disable: localStorage.removeItem('DEBUG_MODE')  // Remove completely
// Note: Setting to 'false' won't work - must remove it!
const DEBUG_MODE = localStorage.getItem('DEBUG_MODE') === 'true';

// Smart console wrapper - only logs if DEBUG_MODE is enabled
const debug = {
    log: (...args) => DEBUG_MODE && console.log(...args),
    info: (...args) => DEBUG_MODE && console.info(...args),
    warn: (...args) => console.warn(...args),  // Always show warnings
    error: (...args) => console.error(...args)  // Always show errors
};

// Show debug mode status on load
if (DEBUG_MODE) {
    console.log('%c🐛 DEBUG MODE ENABLED', 'background: #ff9800; color: white; padding: 2px 8px; border-radius: 3px;');
    console.log('To disable: localStorage.removeItem("DEBUG_MODE"); location.reload();');
}

const PORTFOLIO_STORAGE_KEY = 'saved_portfolio_tickers';  // Persistent portfolio
const SESSION_STORAGE_KEY = 'session_analysis_tickers';    // Current session
const CONFIG_STORAGE_KEY = 'app_configuration';             // App settings
const DEFAULT_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA'];

let sessionTickers = [];      // Tickers for current analysis (temporary)
let portfolioTickers = [];    // Saved portfolio tickers (persistent)
let appConfig = {              // App configuration
    currency: 'USD',           // USD, EUR, or 'native'
    defaultChartType: 'candlestick',
    defaultTimeframe: '3mo',   // Default analysis timeframe
    displayMode: 'accordion',   // accordion or tabs (for future)
    maxNews: 5,                // Maximum news articles to display
    maxSocial: 5,              // Maximum social media posts to display
    newsSort: 'relevance',     // How to sort news: relevance, date_desc, date_asc
    socialSort: 'relevance',   // How to sort social media: relevance, date_desc, date_asc
    newsDays: 3,               // How many days back for news
    socialDays: 7,             // How many days back for social media
    // Default indicator visibility
    defaultIndicators: {
        sma20: true,
        sma50: true,
        bb: true,
        macd: true,
        rsi: true,
        vwap: true,
        ichimoku: true
    }
};

// Conversation context for chat
let conversationContext = {
    lastTicker: null,
    lastTopic: null,
    analyzedTickers: []
};

// Exchange rates (updated periodically, fallback values)
let exchangeRates = {
    EUR: 0.92,  // 1 USD = 0.92 EUR
    GBP: 0.79,  // 1 USD = 0.79 GBP
    USD: 1.0
};

// ===== EXCHANGE RATE FETCHING =====

/**
 * Fetch live exchange rates from external API
 * Caches rates in localStorage for 24 hours
 */
async function fetchExchangeRates() {
    try {
        // Check cache first
        const cached = localStorage.getItem('exchange_rates_cache');
        if (cached) {
            const { rates, timestamp } = JSON.parse(cached);
            const age = Date.now() - timestamp;
            const MAX_AGE = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
            
            if (age < MAX_AGE) {
                debug.log('Using cached exchange rates (age: ' + Math.round(age / 3600000) + ' hours)');
                exchangeRates = rates;
                return rates;
            }
        }
        
        // Fetch fresh rates
        debug.log('Fetching live exchange rates...');
        const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
        
        if (!response.ok) {
            throw new Error('Exchange rate API returned ' + response.status);
        }
        
        const data = await response.json();
        
        // Update global rates
        exchangeRates = {
            USD: 1.0,
            EUR: data.rates.EUR || 0.92,
            GBP: data.rates.GBP || 0.79
        };
        
        // Cache for 24 hours
        localStorage.setItem('exchange_rates_cache', JSON.stringify({
            rates: exchangeRates,
            timestamp: Date.now()
        }));
        
        debug.log('Exchange rates updated:', exchangeRates);
        return exchangeRates;
        
    } catch (error) {
        console.warn('Failed to fetch exchange rates, using fallbacks:', error.message);
        // Keep fallback values already set
        return exchangeRates;
    }
}

// ===== TIMESTAMP FORMATTING =====

function formatTimestamp(timestamp) {
    if (!timestamp) return '';
    
    try {
        let date;
        
        // Check if it's a Unix timestamp (number) or ISO string
        if (typeof timestamp === 'number') {
            // Unix timestamp (in seconds) - convert to milliseconds
            date = new Date(timestamp * 1000);
        } else if (typeof timestamp === 'string') {
            // ISO date string or other format
            date = new Date(timestamp);
        } else {
            return '';
        }
        
        // Check if valid date
        if (isNaN(date.getTime())) return '';
        
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHour / 24);
        
        // Relative time for recent items
        if (diffSec < 60) return 'Just now';
        if (diffMin < 60) return `${diffMin} minute${diffMin === 1 ? '' : 's'} ago`;
        if (diffHour < 24) return `${diffHour} hour${diffHour === 1 ? '' : 's'} ago`;
        if (diffDay < 7) return `${diffDay} day${diffDay === 1 ? '' : 's'} ago`;
        
        // Absolute date for older items
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    } catch (e) {
        return '';
    }
}

// ===== CURRENCY FORMATTING =====

function formatPrice(priceUSD, ticker = null) {
    const currency = appConfig.currency;
    
    // If native currency requested, show in ticker's currency (for now, we only have USD)
    // TODO: Fetch actual ticker currency from API
    if (currency === 'native') {
        return `$${priceUSD.toFixed(2)} USD`;
    }
    
    // Convert to selected currency
    const rate = exchangeRates[currency] || 1.0;
    const convertedPrice = priceUSD * rate;
    
    const symbols = {
        USD: '$',
        EUR: '€',
        GBP: '£'
    };
    
    const symbol = symbols[currency] || '$';
    return `${symbol}${convertedPrice.toFixed(2)} ${currency}`;
}

// ===== TOAST NOTIFICATION SYSTEM =====

function showToast(message, type = 'info', title = null) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `custom-toast toast-${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    // Build toast HTML - only show title if explicitly provided
    let toastHTML = `
        <div class="toast-icon">${icons[type] || icons.info}</div>
        <div class="toast-content">`;
    
    if (title) {
        toastHTML += `<div class="toast-title">${title}</div>`;
    }
    
    toastHTML += `
            <div class="toast-message ${title ? '' : 'toast-message-only'}">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    toast.innerHTML = toastHTML;
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
    loadIndicatorSettings();  // Load saved indicator settings
    
    // Apply default timeframe to dropdown if set
    if (appConfig.defaultTimeframe) {
        const timeframeSelect = document.getElementById('timeframeSelect');
        if (timeframeSelect) {
            timeframeSelect.value = appConfig.defaultTimeframe;
        }
    }
    
    updateTickerChips();
    updateChatTickers();  // Populate chat with portfolio tickers
    initTickerAutocomplete();  // Initialize autocomplete
    
    // Enter key support for analysis (handled in autocomplete now, but keep as fallback)
    document.getElementById('tickerInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const dropdown = document.getElementById('tickerAutocomplete');
            if (dropdown.style.display === 'none') {
                addTicker();
            }
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

// Load saved indicator settings from localStorage
function loadIndicatorSettings() {
    const stored = localStorage.getItem('indicator_settings');
    if (stored) {
        try {
            window.indicatorSettings = JSON.parse(stored);
            debug.log('Loaded indicator settings from localStorage:', window.indicatorSettings);
        } catch (e) {
            console.error('Failed to load indicator settings:', e);
            window.indicatorSettings = {};
        }
    } else {
        window.indicatorSettings = {};
    }
}

// Save portfolio to localStorage
function savePortfolioToStorage() {
    localStorage.setItem(PORTFOLIO_STORAGE_KEY, JSON.stringify(portfolioTickers));
}

// Load session tickers (don't auto-load portfolio)
function loadSessionTickers() {
    const stored = localStorage.getItem(SESSION_STORAGE_KEY);
    if (stored) {
        try {
            sessionTickers = JSON.parse(stored);
        } catch (e) {
            sessionTickers = [];
        }
    }
    // Session starts empty - user must explicitly load portfolio or add tickers
}

// Save session tickers
function saveSessionTickers() {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(sessionTickers));
}

// Ticker autocomplete functionality
let autocompleteTimeout = null;
let selectedAutocompleteIndex = -1;

function initTickerAutocomplete() {
    const input = document.getElementById('tickerInput');
    const dropdown = document.getElementById('tickerAutocomplete');
    
    if (!input || !dropdown) return;
    
    // Handle input changes
    input.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Clear existing timeout
        if (autocompleteTimeout) {
            clearTimeout(autocompleteTimeout);
        }
        
        // Hide dropdown if query too short
        if (query.length < 1) {
            dropdown.style.display = 'none';
            return;
        }
        
        // Debounce search
        autocompleteTimeout = setTimeout(() => {
            searchTickers(query);
        }, 300);
    });
    
    // Handle keyboard navigation
    input.addEventListener('keydown', function(e) {
        const items = dropdown.querySelectorAll('.autocomplete-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedAutocompleteIndex = Math.min(selectedAutocompleteIndex + 1, items.length - 1);
            updateAutocompleteSelection(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedAutocompleteIndex = Math.max(selectedAutocompleteIndex - 1, -1);
            updateAutocompleteSelection(items);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (selectedAutocompleteIndex >= 0 && items[selectedAutocompleteIndex]) {
                const ticker = items[selectedAutocompleteIndex].dataset.ticker;
                selectTicker(ticker);
            } else {
                addTicker();
            }
        } else if (e.key === 'Escape') {
            dropdown.style.display = 'none';
            selectedAutocompleteIndex = -1;
        }
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
            selectedAutocompleteIndex = -1;
        }
    });
}

async function searchTickers(query) {
    const dropdown = document.getElementById('tickerAutocomplete');
    
    try {
        dropdown.innerHTML = '<div class="autocomplete-loading"><i class="bi bi-search"></i> Searching...</div>';
        dropdown.style.display = 'block';
        
        const response = await fetch(`/search_ticker?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            dropdown.innerHTML = data.results.map(item => `
                <div class="autocomplete-item" data-ticker="${item.ticker}" onclick="selectTicker('${item.ticker}')">
                    <span class="autocomplete-ticker">${item.ticker}</span>
                    <span class="autocomplete-name">${item.name || ''}</span>
                    ${item.exchange ? `<span class="autocomplete-exchange">${item.exchange}</span>` : ''}
                </div>
            `).join('');
        } else {
            dropdown.innerHTML = `
                <div class="autocomplete-no-results">
                    No results found. Try entering the exact ticker symbol.
                </div>
            `;
        }
        
        selectedAutocompleteIndex = -1;
    } catch (error) {
        console.error('Ticker search error:', error);
        dropdown.innerHTML = '<div class="autocomplete-no-results">Search unavailable. Enter ticker directly.</div>';
    }
}

function updateAutocompleteSelection(items) {
    items.forEach((item, index) => {
        if (index === selectedAutocompleteIndex) {
            item.classList.add('active');
            item.scrollIntoView({ block: 'nearest' });
        } else {
            item.classList.remove('active');
        }
    });
}

function selectTicker(ticker) {
    const input = document.getElementById('tickerInput');
    const dropdown = document.getElementById('tickerAutocomplete');
    
    input.value = ticker;
    dropdown.style.display = 'none';
    selectedAutocompleteIndex = -1;
    
    // Automatically add the ticker
    addTicker();
}

// Add ticker to analysis session
function addTicker() {
    const input = document.getElementById('tickerInput');
    const dropdown = document.getElementById('tickerAutocomplete');
    const ticker = input.value.trim().toUpperCase();
    
    if (!ticker) {
        showToast('Please enter a ticker symbol', 'warning');
        return;
    }
    
    if (sessionTickers.includes(ticker)) {
        showToast(`${ticker} is already in your analysis session`, 'info');
        input.value = '';
        dropdown.style.display = 'none';
        return;
    }
    
    sessionTickers.push(ticker);
    input.value = '';
    dropdown.style.display = 'none';
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

// Analyze saved portfolio directly (without loading to session)
async function analyzeSavedPortfolio() {
    if (portfolioTickers.length === 0) {
        showToast('No saved portfolio found. Please configure your portfolio first.', 'warning');
        togglePortfolioConfig();
        return;
    }
    
    // Temporarily use portfolio for analysis
    const originalSession = [...sessionTickers];
    sessionTickers = [...portfolioTickers];
    
    showToast(`Analyzing your portfolio: ${portfolioTickers.join(', ')}`, 'info');
    
    // Run analysis
    await analyzePortfolio();
    
    // Restore original session
    sessionTickers = originalSession;
    saveSessionTickers();
}

// Clear all session tickers
function clearSessionTickers() {
    if (sessionTickers.length === 0) {
        showToast('No tickers to clear', 'info');
        return;
    }
    
    sessionTickers = [];
    saveSessionTickers();
    updateTickerChips();
    document.getElementById('results').style.display = 'none';
    showToast('All tickers cleared from analysis list', 'success');
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
        // Default to display tab
        switchTab('display');
    }
}

// Switch between tabs in configuration modal
function switchTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all tab buttons
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    const selectedTab = document.getElementById(`${tabName}Tab`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Highlight selected tab button
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        const tabText = btn.textContent.trim().toLowerCase();
        const targetText = tabName.toLowerCase();
        if (tabText.includes('display') && targetText === 'display') btn.classList.add('active');
        else if (tabText.includes('newsfeeds') && targetText === 'newsfeeds') btn.classList.add('active');
        else if (tabText.includes('portfolio') && targetText === 'portfolio') btn.classList.add('active');
        else if (tabText.includes('about') && targetText === 'about') btn.classList.add('active');
    });
}

// Load config settings to UI
function loadConfigToUI() {
    document.getElementById('configChartType').value = appConfig.defaultChartType;
    document.getElementById('configCurrency').value = appConfig.currency;
    
    // Load default timeframe
    const defaultTimeframeEl = document.getElementById('configDefaultTimeframe');
    if (defaultTimeframeEl) {
        defaultTimeframeEl.value = appConfig.defaultTimeframe || '3mo';
    }
    
    // Load default indicators
    const indicators = appConfig.defaultIndicators || {};
    const indicatorElements = {
        sma20: 'defaultSMA20',
        sma50: 'defaultSMA50',
        bb: 'defaultBB',
        macd: 'defaultMACD',
        rsi: 'defaultRSI',
        vwap: 'defaultVWAP',
        ichimoku: 'defaultIchimoku'
    };
    
    for (const [key, elementId] of Object.entries(indicatorElements)) {
        const el = document.getElementById(elementId);
        if (el) {
            el.checked = indicators[key] !== false; // Default to true if not set
        }
    }
    
    // Load chat panel default state
    const chatPanelDefaultEl = document.getElementById('chatPanelDefault');
    if (chatPanelDefaultEl) {
        const savedState = localStorage.getItem('chatPanelState') || 'collapsed';
        chatPanelDefaultEl.value = savedState;
    }
    
    // Load newsfeed settings if elements exist
    const maxNewsEl = document.getElementById('configMaxNews');
    const maxSocialEl = document.getElementById('configMaxSocial');
    const newsSortEl = document.getElementById('configNewsSort');
    const socialSortEl = document.getElementById('configSocialSort');
    const newsDaysEl = document.getElementById('configNewsDays');
    const socialDaysEl = document.getElementById('configSocialDays');
    
    if (maxNewsEl) {
        maxNewsEl.value = appConfig.maxNews || 5;
        updateNewsLimitDisplay(maxNewsEl.value);
    }
    if (maxSocialEl) {
        maxSocialEl.value = appConfig.maxSocial || 5;
        updateSocialLimitDisplay(maxSocialEl.value);
    }
    if (newsSortEl) newsSortEl.value = appConfig.newsSort || 'relevance';
    if (socialSortEl) socialSortEl.value = appConfig.socialSort || 'relevance';
    if (newsDaysEl) newsDaysEl.value = appConfig.newsDays || 3;
    if (socialDaysEl) socialDaysEl.value = appConfig.socialDays || 7;
}

// Save all config settings from UI and close modal (called by Save & Close button)
function saveAllConfigAndClose() {
    const oldCurrency = appConfig.currency;
    
    // Save display settings
    appConfig.defaultChartType = document.getElementById('configChartType').value;
    appConfig.currency = document.getElementById('configCurrency').value;
    
    // Save default timeframe
    const defaultTimeframeEl = document.getElementById('configDefaultTimeframe');
    if (defaultTimeframeEl) {
        appConfig.defaultTimeframe = defaultTimeframeEl.value;
        // Update the main timeframe selector
        document.getElementById('timeframeSelect').value = appConfig.defaultTimeframe;
    }
    
    // Save default indicators
    appConfig.defaultIndicators = {
        sma20: document.getElementById('defaultSMA20')?.checked !== false,
        sma50: document.getElementById('defaultSMA50')?.checked !== false,
        bb: document.getElementById('defaultBB')?.checked !== false,
        macd: document.getElementById('defaultMACD')?.checked !== false,
        rsi: document.getElementById('defaultRSI')?.checked !== false,
        vwap: document.getElementById('defaultVWAP')?.checked !== false,
        ichimoku: document.getElementById('defaultIchimoku')?.checked !== false
    };
    
    // Save chat panel default state
    const chatPanelDefaultEl = document.getElementById('chatPanelDefault');
    if (chatPanelDefaultEl) {
        appConfig.chatPanelDefault = chatPanelDefaultEl.value;
        // Update localStorage directly for chat panel state
        localStorage.setItem('chatPanelState', chatPanelDefaultEl.value);
    }
    
    // Save newsfeed settings if they exist
    const maxNewsEl = document.getElementById('configMaxNews');
    const maxSocialEl = document.getElementById('configMaxSocial');
    const newsSortEl = document.getElementById('configNewsSort');
    const socialSortEl = document.getElementById('configSocialSort');
    const newsDaysEl = document.getElementById('configNewsDays');
    const socialDaysEl = document.getElementById('configSocialDays');
    
    if (maxNewsEl) appConfig.maxNews = parseInt(maxNewsEl.value);
    if (maxSocialEl) appConfig.maxSocial = parseInt(maxSocialEl.value);
    if (newsSortEl) appConfig.newsSort = newsSortEl.value;
    if (socialSortEl) appConfig.socialSort = socialSortEl.value;
    if (newsDaysEl) appConfig.newsDays = parseInt(newsDaysEl.value);
    if (socialDaysEl) appConfig.socialDays = parseInt(socialDaysEl.value);
    
    // Persist to localStorage
    saveAppConfig();
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
    if (modal) modal.hide();
    
    // Show success message
    showToast('✅ Settings saved successfully', 'success');
    
    // If currency changed, refresh data to update all prices
    if (oldCurrency !== appConfig.currency) {
        // Re-render existing analysis results
        if (window.analysisResults && window.analysisResults.length > 0) {
            displayResults(window.analysisResults);
        }
        
        // 💱 Refresh market sentiment with new currency
        loadMarketSentiment(true);
    }
}

// Update news limit display label
function updateNewsLimitDisplay(value) {
    const display = document.getElementById('newsLimitDisplay');
    if (display) {
        display.textContent = value === '0' ? 'Disabled' : `${value} article${value === '1' ? '' : 's'}`;
    }
}

// Update social media limit display label
function updateSocialLimitDisplay(value) {
    const display = document.getElementById('socialLimitDisplay');
    if (display) {
        display.textContent = value === '0' ? 'Disabled' : `${value} post${value === '1' ? '' : 's'}`;
    }
}

// Update saved tickers list in modal
function updateSavedTickersList() {
    const container = document.getElementById('savedTickersList');
    
    if (portfolioTickers.length === 0) {
        container.innerHTML = '<p class="text-muted mb-0">No tickers saved yet. Add some above!</p>';
        return;
    }
    
    container.innerHTML = portfolioTickers.map(ticker => `
        <div class="ticker-chip">
            ${ticker}
            <span class="remove" onclick="removeFromPortfolio('${ticker}')">×</span>
        </div>
    `).join('');
}

// Add ticker to portfolio (from modal)
function addTickerToPortfolio() {
    const input = document.getElementById('portfolioTickerInput');
    const ticker = input.value.trim().toUpperCase();
    
    if (!ticker) {
        showToast('Please enter a ticker symbol', 'warning');
        return;
    }
    
    if (portfolioTickers.includes(ticker)) {
        showToast('Ticker already in portfolio', 'warning');
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
        showToast(`${ticker} is already in your portfolio`, 'info');
        return;
    }
    
    portfolioTickers.push(ticker);
    savePortfolioToStorage();
    updateTickerChips(); // Update star badges
    showToast(`${ticker} added to portfolio!`, 'success');
    
    // Re-render the stock details to show "In Portfolio" instead of button
    const resultIndex = window.analysisResults.findIndex(r => r.ticker === ticker);
    if (resultIndex !== -1) {
        renderStockDetails(ticker, resultIndex);
    }
}

// Save portfolio preferences
function savePortfolioPreferences() {
    if (portfolioTickers.length === 0) {
        showToast('Portfolio is empty. Add some tickers first!', 'warning');
        return;
    }
    
    savePortfolioToStorage();
    showToast(`Portfolio saved with ${portfolioTickers.length} ticker(s): ${portfolioTickers.join(', ')}`, 'success');
    togglePortfolioConfig();
}

// Clear all portfolio tickers with confirmation
function clearAllTickers() {
    if (portfolioTickers.length === 0) {
        showToast('Portfolio is already empty.', 'info');
        return;
    }
    
    if (confirm(`⚠️ Are you sure you want to remove all ${portfolioTickers.length} ticker(s) from your portfolio?\n\nThis will NOT affect your current analysis session.`)) {
        portfolioTickers = [];
        savePortfolioToStorage();
        updateSavedTickersList();
        showToast('Portfolio cleared successfully.', 'success');
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
async function analyzeSingleTicker(ticker) {
    /**
     * Analyze a single ticker without showing UI - for chat background analysis
     */
    const chartType = appConfig.defaultChartType;
    const theme = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                tickers: [ticker],  // Only analyze this one ticker
                chart_type: chartType,
                theme: theme,
                max_news: appConfig.maxNews,
                max_social: appConfig.maxSocial,
                news_sort: appConfig.newsSort,
                social_sort: appConfig.socialSort,
                news_days: appConfig.newsDays,
                social_days: appConfig.socialDays
            })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to analyze ${ticker}`);
        }
        
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            // Update results array
            window.analysisResults = window.analysisResults || [];
            
            // Remove old result for this ticker if exists
            window.analysisResults = window.analysisResults.filter(r => r.ticker !== ticker);
            
            // Add new result
            window.analysisResults.push(...data.results);
            
            return data.results[0];
        } else {
            throw new Error(`No analysis data received for ${ticker}`);
        }
    } catch (error) {
        console.error('Single ticker analysis error:', error);
        throw error;
    }
}

// Calculate news/social days based on timeframe
// Match the actual time window being displayed (not the fetch period)
function getDaysFromTimeframe(timeframe) {
    const timeframeMap = {
        // Intraday timeframes - match the actual window shown (very recent data)
        '5m': { news: 1, social: 1 },      // Last 5 minutes - use today's news
        '15m': { news: 1, social: 1 },     // Last 15 minutes - use today's news
        '30m': { news: 1, social: 1 },     // Last 30 minutes - use today's news
        '1h': { news: 1, social: 1 },      // Last 1 hour - use today's news
        '3h': { news: 1, social: 1 },      // Last 3 hours - use today's news
        '6h': { news: 1, social: 1 },      // Last 6 hours - use today's news
        '12h': { news: 1, social: 1 },     // Last 12 hours - use today's news
        // Daily and longer
        '1d': { news: 1, social: 1 },
        '5d': { news: 5, social: 5 },
        '1wk': { news: 7, social: 7 },
        '1mo': { news: 30, social: 30 },
        '3mo': { news: 7, social: 14 },
        '6mo': { news: 14, social: 30 },
        '1y': { news: 30, social: 60 },
        '2y': { news: 60, social: 90 },
        '5y': { news: 90, social: 180 },
        'max': { news: 180, social: 365 }
    };
    
    return timeframeMap[timeframe] || { news: 7, social: 14 };
}

async function analyzePortfolio() {
    if (sessionTickers.length === 0) {
        showToast('Please add at least one ticker to analyze', 'warning');
        return;
    }
    
    // Use configured default chart type
    const chartType = appConfig.defaultChartType;
    
    // Get selected timeframe
    const timeframe = document.getElementById('timeframeSelect').value || '3mo';
    
    // Calculate appropriate news/social days based on timeframe
    const days = getDaysFromTimeframe(timeframe);
    
    // Detect current theme
    const theme = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
    
    // Show full-screen loading overlay
    document.getElementById('fullScreenLoader').style.display = 'block';
    
    // Switch to Market Analysis tab
    const analysisTabButton = document.getElementById('analysis-tab');
    if (analysisTabButton) {
        const tab = new bootstrap.Tab(analysisTabButton);
        tab.show();
    }
    
    // Hide results and disable button
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
                chart_type: chartType,  // Initial chart type for all
                timeframe: timeframe,    // Analysis timeframe
                theme: theme,            // Chart theme (dark/light)
                max_news: appConfig.maxNews,
                max_social: appConfig.maxSocial,
                news_sort: appConfig.newsSort,
                social_sort: appConfig.socialSort,
                news_days: days.news,      // Dynamic based on timeframe
                social_days: days.social   // Dynamic based on timeframe
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
        document.getElementById('fullScreenLoader').style.display = 'none';
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
                    <th>
                        Recommendation
                        ${results.length > 0 && results[0].recommendation_explanation ? `
                            <i class="bi bi-info-circle ms-1" 
                               style="cursor: pointer; color: #6c757d; font-size: 0.85rem; opacity: 0.7;" 
                               onclick="showRecommendationExplanation('${results[0].ticker}')" 
                               data-bs-toggle="tooltip"
                               data-bs-placement="top"
                               title="How are recommendations calculated?"></i>
                        ` : ''}
                    </th>
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
                        <td>${formatPrice(r.current_price, r.ticker)}</td>
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
    
    // Initialize Bootstrap tooltips
    initializeTooltips();
}

// Display detailed analysis
function displayDetailedAnalysis(results) {
    const html = results.map((r, index) => `
        <div class="stock-accordion" id="card_${r.ticker}">
            <div class="stock-accordion-header" onclick="toggleStockDetails('${r.ticker}', ${index})" 
                 style="border-left-color: ${r.color}">
                <div class="accordion-header-content">
                    <div class="accordion-header-main">
                        <div class="stock-title">
                            <div class="stock-title-text">
                                <span class="stock-ticker">${r.ticker}</span>
                                <span class="stock-name">${r.name || r.ticker}</span>
                            </div>
                            <span class="recommendation-badge" style="background: ${r.color}">
                                ${r.recommendation}
                            </span>
                        </div>
                        <div class="accordion-header-metrics">
                            <span class="metric-badge">
                                <i class="bi bi-currency-dollar"></i> ${formatPrice(r.current_price, r.ticker)}
                            </span>
                            <span class="metric-badge ${r.price_change >= 0 ? 'positive' : 'negative'}">
                                <i class="bi bi-graph-${r.price_change >= 0 ? 'up' : 'down'}-arrow"></i>
                                ${r.price_change >= 0 ? '+' : ''}${r.price_change.toFixed(2)}%
                            </span>
                            <span class="metric-badge">
                                <i class="bi bi-star-fill"></i> ${r.combined_score.toFixed(2)}
                            </span>
                        </div>
                    </div>
                    <div class="accordion-toggle">
                        <i class="bi bi-chevron-down toggle-icon" id="toggle_${r.ticker}"></i>
                    </div>
                </div>
            </div>
            
            <div class="stock-accordion-body" id="body_${r.ticker}" style="display: none;">
                <div class="loading-placeholder" id="loading_${r.ticker}">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading detailed analysis...</p>
                </div>
            </div>
        </div>
    `).join('');
    
    document.getElementById('detailsContainer').innerHTML = html;
    
    // Store results globally
    window.analysisResults = results;
    
    // Initialize Bootstrap tooltips
    initializeTooltips();
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// ===== ACCORDION FUNCTIONS =====

function toggleStockDetails(ticker, resultIndex) {
    const body = document.getElementById(`body_${ticker}`);
    const toggle = document.getElementById(`toggle_${ticker}`);
    const loading = document.getElementById(`loading_${ticker}`);
    
    if (body.style.display === 'none') {
        // Opening - load content if not already loaded
        body.style.display = 'block';
        toggle.className = 'bi bi-chevron-up toggle-icon';
        
        // Check if content is already loaded
        if (loading && loading.style.display !== 'none') {
            // Load the detailed content
            renderStockDetails(ticker, resultIndex);
        }
    } else {
        // Closing
        body.style.display = 'none';
        toggle.className = 'bi bi-chevron-down toggle-icon';
    }
}

// Generate gauge chart for analyst recommendation
function generateAnalystGauge(recommendationMean, containerId) {
    // Convert 1-5 scale to 0-100 for display (inverted: 1=best, 5=worst)
    const value = ((5 - recommendationMean) / 4) * 100;
    
    const data = [{
        type: "indicator",
        mode: "gauge+number+delta",
        value: value,
        number: { 
            suffix: "%", 
            font: { size: 24 }
        },
        gauge: {
            axis: { 
                range: [0, 100],
                tickwidth: 1,
                tickcolor: "darkgray"
            },
            bar: { color: "rgba(0,0,0,0)" },
            bgcolor: "white",
            borderwidth: 2,
            bordercolor: "gray",
            steps: [
                { range: [0, 20], color: "#ef4444" },    // Strong Sell - Red
                { range: [20, 40], color: "#fb923c" },   // Sell - Orange  
                { range: [40, 60], color: "#fbbf24" },   // Hold - Yellow
                { range: [60, 80], color: "#86efac" },   // Buy - Light Green
                { range: [80, 100], color: "#22c55e" }   // Strong Buy - Green
            ],
            threshold: {
                line: { color: "#1e40af", width: 4 },
                thickness: 0.75,
                value: value
            }
        }
    }];
    
    const layout = {
        width: 280,
        height: 180,
        margin: { t: 10, r: 10, b: 10, l: 10 },
        paper_bgcolor: "rgba(0,0,0,0)",
        font: { color: "darkgray", family: "Arial" }
    };
    
    const config = {
        displayModeBar: false,
        responsive: true
    };
    
    Plotly.newPlot(containerId, data, layout, config);
}

function renderStockDetails(ticker, resultIndex) {
    const r = window.analysisResults[resultIndex];
    const body = document.getElementById(`body_${ticker}`);
    const isInPortfolio = portfolioTickers.includes(ticker);
    
    const html = `
        <div class="stock-details-content">
            <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                ${!isInPortfolio ? `
                    <button onclick="addToPortfolioFromAnalysis('${ticker}')" class="btn-small btn-primary" style="display: flex; align-items: center; gap: 5px;">
                        ⭐ Add to Portfolio
                    </button>
                ` : `
                    <span style="color: #22c55e; font-weight: 600;">⭐ In Portfolio</span>
                `}
            </div>
            
            <!-- Compact Dashboard Layout -->
            <div class="row g-3">
                <!-- Left Column: Key Metrics & Recommendation -->
                <div class="col-lg-6">
                    <!-- Recommendation Comparison (Compact) -->
                    ${r.analyst_consensus ? `
                    <div class="card border-0 shadow-sm mb-3" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                        <div class="card-body p-3">
                            <div class="row align-items-center text-white">
                                <div class="col-6 border-end border-white border-opacity-25">
                                    <small class="d-block opacity-75 mb-1">📊 Wall Street</small>
                                    <strong style="font-size: 1.1rem;">${r.analyst_consensus.signal}</strong>
                                    <small class="d-block opacity-75 mt-1">${r.analyst_consensus.num_analysts} analysts</small>
                                </div>
                                <div class="col-6">
                                    <small class="d-block opacity-75 mb-1">🤖 AI Powered</small>
                                    <strong style="font-size: 1.1rem;">${r.recommendation}</strong>
                                    <small class="d-block opacity-75 mt-1">Score: ${r.combined_score.toFixed(2)}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    ` : `
                    <div class="card border-0 shadow-sm mb-3" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                        <div class="card-body p-3 text-center text-white">
                            <small class="d-block opacity-75 mb-1">🤖 AI Recommendation</small>
                            <strong style="font-size: 1.3rem;">${r.recommendation}</strong>
                            <small class="d-block opacity-75 mt-1">Score: ${r.combined_score.toFixed(2)}</small>
                        </div>
                    </div>
                    `}
                    
                    <!-- Compact Score Metrics -->
                    <div class="card border-0 shadow-sm mb-3">
                        <div class="card-body p-3">
                            <h6 class="card-title mb-3" style="font-size: 0.9rem; color: #6c757d;">
                                <i class="bi bi-speedometer2"></i> Analysis Scores
                            </h6>
                            <div class="row g-2">
                                <div class="col-6">
                                    <div class="p-2 bg-light rounded text-center">
                                        <small class="d-block text-muted" style="font-size: 0.75rem;">Sentiment</small>
                                        <strong style="font-size: 1rem;">${r.sentiment_score.toFixed(2)}</strong>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="p-2 bg-light rounded text-center">
                                        <small class="d-block text-muted" style="font-size: 0.75rem;">Technical</small>
                                        <strong style="font-size: 1rem;">${r.technical_score.toFixed(2)}</strong>
                                    </div>
                                </div>
                                ${r.analyst_score !== null && r.analyst_score !== undefined ? `
                                <div class="col-6">
                                    <div class="p-2 bg-light rounded text-center">
                                        <small class="d-block text-muted" style="font-size: 0.75rem;">Analyst</small>
                                        <strong style="font-size: 1rem;">${r.analyst_score.toFixed(2)}</strong>
                                    </div>
                                </div>
                                ` : ''}
                                <div class="col-6">
                                    <div class="p-2 bg-primary bg-opacity-10 rounded text-center">
                                        <small class="d-block text-primary" style="font-size: 0.75rem;">Combined</small>
                                        <strong class="text-primary" style="font-size: 1rem;">${r.combined_score.toFixed(2)}</strong>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Price Information (Current + Pre-Market Side by Side) -->
                    <div class="card border-0 shadow-sm">
                        <div class="card-body p-3">
                            <div class="row g-3">
                                <div class="col-6">
                                    <h6 class="mb-2" style="font-size: 0.85rem; color: #6c757d;">
                                        <i class="bi bi-currency-dollar"></i> Current Price
                                    </h6>
                                    <div class="h4 mb-0">${formatPrice(r.current_price, r.ticker)}</div>
                                    <small class="text-muted">Last traded</small>
                                </div>
                                ${r.pre_market_data && r.pre_market_data.has_data ? `
                                <div class="col-6 border-start">
                                    <h6 class="mb-2" style="font-size: 0.85rem; color: #ffc107;">
                                        <i class="bi bi-clock-history"></i> Pre-Market
                                    </h6>
                                    <div class="h4 mb-0">${formatPrice(r.pre_market_data.price, r.ticker)}</div>
                                    <small class="${r.pre_market_data.change >= 0 ? 'text-success' : 'text-danger'}">
                                        ${r.pre_market_data.change >= 0 ? '↗ +' : '↘ '}${r.pre_market_data.change_percent.toFixed(2)}%
                                    </small>
                                </div>
                                ` : `
                                <div class="col-6 border-start text-center">
                                    <div class="text-muted" style="padding-top: 20px;">
                                        <i class="bi bi-moon" style="font-size: 1.5rem;"></i>
                                        <small class="d-block mt-2">Market Closed</small>
                                    </div>
                                </div>
                                `}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Right Column: Analyst Gauge & Price Targets -->
                <div class="col-lg-6">
                    ${r.analyst_consensus ? `
                    <!-- Analyst Gauge Chart -->
                    <div class="card border-0 shadow-sm mb-3">
                        <div class="card-body p-3">
                            <h6 class="card-title mb-2" style="font-size: 0.9rem;">
                                📊 Wall Street Consensus
                                ${r.analyst_coverage_level === 'limited' ? `
                                <span class="badge bg-warning text-dark ms-2" title="Limited analyst coverage" style="font-size: 0.7rem;">
                                    <i class="bi bi-exclamation-triangle"></i> Limited
                                </span>
                                ` : ''}
                            </h6>
                            <div id="analystGauge_${ticker}" style="display: flex; justify-content: center;"></div>
                            <div class="text-center mt-2">
                                <small class="text-muted">${r.analyst_consensus.num_analysts} analysts · Rating: ${r.analyst_consensus.recommendation_mean.toFixed(2)}/5.0</small>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Price Targets (Compact) -->
                    ${r.analyst_data && r.analyst_data.target_mean_price ? `
                    <div class="card border-0 shadow-sm">
                        <div class="card-body p-3">
                            <h6 class="card-title mb-3" style="font-size: 0.9rem;">
                                <i class="bi bi-bullseye"></i> Price Targets
                            </h6>
                            <div class="row g-2 mb-2">
                                <div class="col-4">
                                    <div class="text-center p-2 bg-danger bg-opacity-10 rounded">
                                        <small class="d-block text-danger" style="font-size: 0.7rem;">LOW</small>
                                        <strong class="text-danger" style="font-size: 0.95rem;">${r.analyst_data.target_low_price ? formatPrice(r.analyst_data.target_low_price, r.ticker) : 'N/A'}</strong>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="text-center p-2 bg-primary bg-opacity-10 rounded">
                                        <small class="d-block text-primary" style="font-size: 0.7rem;">TARGET</small>
                                        <strong class="text-primary" style="font-size: 0.95rem;">${formatPrice(r.analyst_data.target_mean_price, r.ticker)}</strong>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="text-center p-2 bg-success bg-opacity-10 rounded">
                                        <small class="d-block text-success" style="font-size: 0.7rem;">HIGH</small>
                                        <strong class="text-success" style="font-size: 0.95rem;">${r.analyst_data.target_high_price ? formatPrice(r.analyst_data.target_high_price, r.ticker) : 'N/A'}</strong>
                                    </div>
                                </div>
                            </div>
                            ${r.analyst_data.current_price ? `
                            <div class="mt-2 p-2 rounded bg-gradient text-white text-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                                <small class="d-block opacity-75" style="font-size: 0.75rem;">Projected Return</small>
                                <strong style="font-size: 1.2rem;">
                                    ${(((r.analyst_data.target_mean_price - r.analyst_data.current_price) / r.analyst_data.current_price) * 100) >= 0 ? '↗' : '↘'}
                                    ${Math.abs(((r.analyst_data.target_mean_price - r.analyst_data.current_price) / r.analyst_data.current_price) * 100).toFixed(1)}%
                                </strong>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                    ` : ''}
                    ` : `
                    <div class="card border-0 shadow-sm">
                        <div class="card-body p-4 text-center text-muted">
                            <i class="bi bi-info-circle" style="font-size: 2rem;"></i>
                            <p class="mt-2 mb-0" style="font-size: 0.9rem;">No analyst coverage available</p>
                        </div>
                    </div>
                    `}
                </div>
            </div>
            
            <!-- Our AI-Powered Analysis Section -->
            <div class="section-title" style="border-top: 2px solid #dee2e6; padding-top: 1.5rem; margin-top: 1.5rem;">
                🤖 Our AI-Powered Analysis
            </div>
            <div class="alert alert-secondary" style="border-left: 4px solid #6c757d;">
                <small class="text-muted">
                    <i class="bi bi-cpu me-1"></i>
                    Based on FinBERT sentiment analysis, social media trends, and technical indicators
                </small>
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
                                ${sent.title}
                                ${sent.publisher ? `<span class="news-publisher">- ${sent.publisher}</span>` : ''}
                                ${sent.link ? `<a href="${sent.link}" target="_blank" rel="noopener" class="news-link-icon" title="Read full article">🔗</a>` : ''}
                            </div>
                            ${sent.published ? `<div class="news-timestamp">📅 ${formatTimestamp(sent.published)}</div>` : ''}
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
                        const textPreview = sent.text.length > 200 ? sent.text.substring(0, 200) + '...' : sent.text;
                        return `
                        <div class="news-item sentiment-${sent.label}">
                            <div class="news-title">
                                <strong>${sent.source || 'Social Media'}</strong>: ${textPreview}
                                ${sent.link && !sent.link.includes('message/undefined') && !sent.link.includes('message/') ? 
                                    `<a href="${sent.link}" target="_blank" rel="noopener" class="news-link-icon" title="View post">🔗</a>` : 
                                    `<span class="news-link-icon" title="No link available" style="cursor: default;">⛓️‍💥</span>`}
                            </div>
                            ${sent.created_at ? `<div class="news-timestamp">📅 ${formatTimestamp(sent.created_at)}</div>` : ''}
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
                        <optgroup label="Intraday">
                            <option value="5m" ${r.timeframe_used === '5m' ? 'selected' : ''}>5 Minutes</option>
                            <option value="15m" ${r.timeframe_used === '15m' ? 'selected' : ''}>15 Minutes</option>
                            <option value="30m" ${r.timeframe_used === '30m' ? 'selected' : ''}>30 Minutes</option>
                            <option value="1h" ${r.timeframe_used === '1h' ? 'selected' : ''}>1 Hour</option>
                            <option value="3h" ${r.timeframe_used === '3h' ? 'selected' : ''}>3 Hours</option>
                            <option value="6h" ${r.timeframe_used === '6h' ? 'selected' : ''}>6 Hours</option>
                            <option value="12h" ${r.timeframe_used === '12h' ? 'selected' : ''}>12 Hours</option>
                        </optgroup>
                        <optgroup label="Daily & Longer">
                            <option value="1d" ${r.timeframe_used === '1d' ? 'selected' : ''}>1 Day</option>
                            <option value="5d" ${r.timeframe_used === '5d' ? 'selected' : ''}>5 Days</option>
                            <option value="1wk" ${r.timeframe_used === '1wk' ? 'selected' : ''}>1 Week</option>
                            <option value="1mo" ${r.timeframe_used === '1mo' ? 'selected' : ''}>1 Month</option>
                            <option value="3mo" ${!r.timeframe_used || r.timeframe_used === '3mo' ? 'selected' : ''}>3 Months</option>
                            <option value="6mo" ${r.timeframe_used === '6mo' ? 'selected' : ''}>6 Months</option>
                            <option value="1y" ${r.timeframe_used === '1y' ? 'selected' : ''}>1 Year</option>
                            <option value="2y" ${r.timeframe_used === '2y' ? 'selected' : ''}>2 Years</option>
                            <option value="5y" ${r.timeframe_used === '5y' ? 'selected' : ''}>5 Years</option>
                            <option value="max" ${r.timeframe_used === 'max' ? 'selected' : ''}>Max</option>
                        </optgroup>
                    </select>
                    
                    <button class="btn-small btn-secondary" onclick="toggleIndicators('${r.ticker}')" 
                            style="margin-left: 15px;" title="Show/Hide Indicators">
                        <i class="bi bi-sliders"></i> Indicators
                    </button>
                    
                    <button class="btn-small btn-refresh" id="refreshBtn_${r.ticker}" onclick="refreshChart('${r.ticker}', ${resultIndex})">
                        🔄 Refresh
                    </button>
                </div>
                
                <!-- Indicator Controls (Hidden by default) -->
                <div id="indicatorControls_${r.ticker}" class="indicator-controls" style="display: none; margin-top: 10px; padding: 15px; border-radius: 8px;">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <h6 style="font-size: 0.9rem; margin-bottom: 10px;">
                                <i class="bi bi-graph-up"></i> Moving Averages
                            </h6>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="showSMA20_${r.ticker}" ${appConfig.defaultIndicators?.sma20 !== false ? 'checked' : ''}>
                                <label class="form-check-label" for="showSMA20_${r.ticker}">
                                    SMA(20) - Orange
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="showSMA50_${r.ticker}" ${appConfig.defaultIndicators?.sma50 !== false ? 'checked' : ''}>
                                <label class="form-check-label" for="showSMA50_${r.ticker}">
                                    SMA(50) - Blue
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="showBB_${r.ticker}" ${appConfig.defaultIndicators?.bb !== false ? 'checked' : ''}>
                                <label class="form-check-label" for="showBB_${r.ticker}">
                                    Bollinger Bands
                                </label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h6 style="font-size: 0.9rem; margin-bottom: 10px;">
                                <i class="bi bi-activity"></i> Oscillators
                            </h6>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="showMACD_${r.ticker}" ${appConfig.defaultIndicators?.macd !== false ? 'checked' : ''}>
                                <label class="form-check-label" for="showMACD_${r.ticker}">
                                    MACD
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="showRSI_${r.ticker}" ${appConfig.defaultIndicators?.rsi !== false ? 'checked' : ''}>
                                <label class="form-check-label" for="showRSI_${r.ticker}">
                                    RSI
                                </label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h6 style="font-size: 0.9rem; margin-bottom: 10px;">
                                <i class="bi bi-bar-chart"></i> Advanced
                            </h6>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="showVWAP_${r.ticker}" ${appConfig.defaultIndicators?.vwap !== false ? 'checked' : ''}>
                                <label class="form-check-label" for="showVWAP_${r.ticker}">
                                    VWAP - Red dotted
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="showIchimoku_${r.ticker}" ${appConfig.defaultIndicators?.ichimoku !== false ? 'checked' : ''}>
                                <label class="form-check-label" for="showIchimoku_${r.ticker}">
                                    Ichimoku Cloud
                                </label>
                            </div>
                        </div>
                    </div>
                    <div class="mt-3 text-center">
                        <button class="btn-small btn-primary" onclick="applyIndicatorSettings('${r.ticker}', ${resultIndex})">
                            <i class="bi bi-check-lg"></i> Apply Settings
                        </button>
                        <button class="btn-small btn-secondary" onclick="toggleIndicators('${r.ticker}')">
                            Cancel
                        </button>
                    </div>
                </div>
                <div class="chart-container" id="chart_${r.ticker}"></div>
            ` : ''}
        </div>
    `;
    
    body.innerHTML = html;
    
    // Render analyst gauge if available
    if (r.analyst_consensus) {
        setTimeout(() => {
            generateAnalystGauge(r.analyst_consensus.recommendation_mean, `analystGauge_${ticker}`);
        }, 100);
    }
    
    // Render chart if available and mark button as "Refresh" after first render
    if (r.chart_data) {
        const initialChartType = document.getElementById('chartType')?.value || 'candlestick';
        const dropdown = document.getElementById(`chartType_${r.ticker}`);
        if (dropdown) {
            dropdown.value = r.chart_type_used || initialChartType;
        }
        
        // Check if chart has been rendered before
        const refreshBtn = document.getElementById(`refreshBtn_${r.ticker}`);
        const chartDiv = document.getElementById(`chart_${r.ticker}`);
        
        if (chartDiv && chartDiv.innerHTML.trim() === '') {
            // First time - button should say "Generate"
            if (refreshBtn) {
                refreshBtn.innerHTML = '📊 Generate Chart';
            }
        }
        
        debug.log(`Rendering ${r.ticker} with chart type: ${r.chart_type_used || initialChartType}`);
        renderChart(r.ticker, r.chart_data);
        
        // Apply saved indicator settings after initial render
        if (window.indicatorSettings && window.indicatorSettings[ticker]) {
            debug.log(`Applying saved indicator settings for ${ticker} after initial render`);
            setTimeout(() => {
                applyIndicatorSettings(ticker, resultIndex, true); // Silent mode
            }, 200);
        }
        
        // After rendering, change button to "Refresh"
        setTimeout(() => {
            if (refreshBtn) {
                refreshBtn.innerHTML = '🔄 Refresh';
            }
        }, 500);
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
            debug.log(`✓ Chart rendered successfully for ${ticker}`);
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
async function updateChart(ticker, resultIndex, chartType = null, timeframe = null) {
    // Get values from controls if not provided
    if (!chartType) {
        const chartTypeSelect = document.getElementById(`chartType_${ticker}`);
        chartType = chartTypeSelect ? chartTypeSelect.value : 'candlestick';
    }
    if (!timeframe) {
        const timeframeSelect = document.getElementById(`timeframe_${ticker}`);
        timeframe = timeframeSelect ? timeframeSelect.value : '3mo';
    }
    
    debug.log(`Updating ${ticker} to ${chartType} chart with ${timeframe} timeframe`);
    
    // Show loading placeholder with spinner (preserve layout)
    const chartDiv = document.getElementById(`chart_${ticker}`);
    const currentHeight = chartDiv.offsetHeight || 800;
    chartDiv.innerHTML = `
        <div class="chart-loading-placeholder" style="height: ${currentHeight}px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.02); border-radius: 8px; position: relative;">
            <div style="filter: blur(8px); opacity: 0.3; position: absolute; width: 100%; height: 100%; background: linear-gradient(180deg, rgba(33,150,243,0.1) 0%, rgba(156,39,176,0.1) 100%);"></div>
            <div style="position: relative; z-index: 1; text-align: center;">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 text-muted" style="font-size: 1.1rem;">
                    <i class="bi bi-graph-up-arrow"></i> Regenerating ${chartType} chart...
                </p>
                <small class="text-muted">Timeframe: ${timeframe}</small>
            </div>
        </div>
    `;
    
    try {
        // Detect current theme
        const theme = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
        
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                tickers: [ticker],
                chart_type: chartType,
                timeframe: timeframe,
                theme: theme,
                use_cache: false,
                max_news: appConfig.maxNews,
                max_social: appConfig.maxSocial,
                news_sort: appConfig.newsSort,
                social_sort: appConfig.socialSort,
                news_days: appConfig.newsDays,
                social_days: appConfig.socialDays
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
            
            // Re-apply saved indicator settings after chart refresh (silent mode)
            if (window.indicatorSettings && window.indicatorSettings[ticker]) {
                debug.log(`Re-applying saved indicator settings for ${ticker} after chart update`);
                setTimeout(() => {
                    applyIndicatorSettings(ticker, resultIndex, true); // Silent mode: no toast, no panel close
                }, 100);
            }
        }
    } catch (error) {
        console.error(`Error updating chart for ${ticker}:`, error);
        chartDiv.innerHTML = '<div class="chart-error">❌ Error loading chart. Try refreshing the page.</div>';
    }
}

// Refresh current chart
function refreshChart(ticker, resultIndex) {
    const refreshBtn = document.getElementById(`refreshBtn_${ticker}`);
    if (refreshBtn) {
        refreshBtn.innerHTML = '⏳ Loading...';
        refreshBtn.disabled = true;
    }
    
    updateChart(ticker, resultIndex);
    
    // Re-enable button after update
    setTimeout(() => {
        if (refreshBtn) {
            refreshBtn.innerHTML = '🔄 Refresh';
            refreshBtn.disabled = false;
        }
    }, 1000);
}

// Toggle indicator controls visibility
function toggleIndicators(ticker) {
    const controlsDiv = document.getElementById(`indicatorControls_${ticker}`);
    if (controlsDiv) {
        controlsDiv.style.display = controlsDiv.style.display === 'none' ? 'block' : 'none';
    }
}

// Apply indicator settings by showing/hiding traces
function applyIndicatorSettings(ticker, resultIndex, silent = false) {
    // Get default settings from config
    const defaults = appConfig.defaultIndicators || {};
    
    const settings = {
        showSMA20: document.getElementById(`showSMA20_${ticker}`)?.checked ?? (defaults.sma20 !== false),
        showSMA50: document.getElementById(`showSMA50_${ticker}`)?.checked ?? (defaults.sma50 !== false),
        showBB: document.getElementById(`showBB_${ticker}`)?.checked ?? (defaults.bb !== false),
        showMACD: document.getElementById(`showMACD_${ticker}`)?.checked ?? (defaults.macd !== false),
        showRSI: document.getElementById(`showRSI_${ticker}`)?.checked ?? (defaults.rsi !== false),
        showVWAP: document.getElementById(`showVWAP_${ticker}`)?.checked ?? (defaults.vwap !== false),
        showIchimoku: document.getElementById(`showIchimoku_${ticker}`)?.checked ?? (defaults.ichimoku !== false)
    };
    
    if (!silent) {
        debug.log(`Applying indicator settings for ${ticker}:`, settings);
    }
    
    // Store settings for future use (in memory and localStorage)
    if (!window.indicatorSettings) {
        window.indicatorSettings = {};
    }
    window.indicatorSettings[ticker] = settings;
    
    // Save to localStorage for persistence across page refreshes
    try {
        localStorage.setItem('indicator_settings', JSON.stringify(window.indicatorSettings));
    } catch (e) {
        console.error('Failed to save indicator settings to localStorage:', e);
    }
    
    // Get the chart div
    const chartDiv = document.getElementById(`chart_${ticker}`);
    if (!chartDiv || !chartDiv.data) {
        console.error('Chart not found or not initialized');
        return;
    }
    
    // Map indicator names to trace names in the chart
    const updates = [];
    const traceIndices = [];
    
    chartDiv.data.forEach((trace, index) => {
        const traceName = trace.name || '';
        let visible = true; // Default to visible (keep price and volume)
        let shouldUpdate = false;
        
        // Determine visibility based on trace name
        if (traceName.includes('SMA(20)')) {
            visible = settings.showSMA20;
            shouldUpdate = true;
        } else if (traceName.includes('SMA(50)')) {
            visible = settings.showSMA50;
            shouldUpdate = true;
        } else if (traceName.includes('BB Upper') || traceName.includes('BB Lower')) {
            visible = settings.showBB;
            shouldUpdate = true;
        } else if (traceName.includes('MACD') || traceName.includes('Signal') || traceName.includes('MACD Histogram')) {
            visible = settings.showMACD;
            shouldUpdate = true;
        } else if (traceName.includes('RSI')) {
            visible = settings.showRSI;
            shouldUpdate = true;
        } else if (traceName.includes('VWAP')) {
            visible = settings.showVWAP;
            shouldUpdate = true;
        } else if (traceName.includes('Tenkan-sen') || traceName.includes('Kijun-sen') || 
                   traceName.includes('Senkou A') || traceName.includes('Senkou B') || 
                   traceName.includes('Chikou Span')) {
            visible = settings.showIchimoku;
            shouldUpdate = true;
        }
        
        if (shouldUpdate) {
            updates.push(visible);
            traceIndices.push(index);
        }
    });
    
    // Update trace visibility using batch update
    if (traceIndices.length > 0) {
        if (!silent) {
            debug.log(`Updating visibility for ${traceIndices.length} traces`);
        }
        traceIndices.forEach((traceIndex, i) => {
            Plotly.restyle(chartDiv, { visible: updates[i] }, [traceIndex]);
        });
    }
    
    // Hide controls and show toast only if not silent
    if (!silent) {
        toggleIndicators(ticker);
        showToast(`Indicator settings applied for ${ticker}`, 'success');
    }
}

// ===== AI CHAT FUNCTIONS =====

function toggleChat() {
    const chatPanel = document.getElementById('chatPanel');
    chatPanel.classList.toggle('chat-open');
}

function updateChatTickers() {
    const chatTicker = document.getElementById('chatTicker');
    if (!chatTicker) return;
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
    
    // Format the message (convert markdown-style to HTML)
    // First, split by paragraphs (double newlines)
    let paragraphs = message.split(/\n\n+/);
    
    let formattedMessage = paragraphs.map(para => {
        para = para.trim();
        if (!para) return '';
        
        // Bold text: **text** -> <strong>text</strong>
        para = para.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Check if paragraph contains list items
        if (para.match(/^[•\-\*]\s/m) || para.match(/^\d+\.\s/m)) {
            // Convert bullet points and numbered lists
            para = para
                .replace(/^[•\-\*]\s+(.+)$/gm, '<li>$1</li>')
                .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');
            
            // Wrap in ul tags
            para = '<ul>' + para + '</ul>';
        } else {
            // Regular paragraph - single line breaks become spaces
            para = para.replace(/\n/g, ' ');
            para = '<p>' + para + '</p>';
        }
        
        return para;
    }).join('');
    
    // Clean up any empty paragraphs
    formattedMessage = formattedMessage.replace(/<p>\s*<\/p>/g, '');
    
    contentDiv.innerHTML = formattedMessage;
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const tickerSelect = document.getElementById('chatTicker');
    const question = input.value.trim();
    const ticker = tickerSelect ? tickerSelect.value : '';
    
    if (!question) {
        return;
    }
    
    // If no ticker selected, try to extract from question
    if (!ticker) {
        addChatMessage(question, true);
        input.value = '';
        
        // Try to extract ticker from question (supports stocks and crypto)
        // Matches: MSFT, BTC-USD, ETH-EUR, UPR.IR, etc.
        const tickerMatch = question.match(/\b([A-Z]{2,5}(?:[-\.][A-Z]{2,4})?)\b/);
        if (tickerMatch) {
            const extractedTicker = tickerMatch[1];
            
            // Check if it's in analyzed results
            if (window.analysisResults) {
                const foundResult = window.analysisResults.find(r => 
                    r.ticker.toUpperCase() === extractedTicker.toUpperCase()
                );
                if (foundResult) {
                    // Auto-select and answer
                    if (tickerSelect) {
                        tickerSelect.value = foundResult.ticker;
                    }
                    sendChatWithTicker(question, foundResult.ticker);
                    return;
                }
            }
            
            // Not analyzed yet - trigger auto-analysis
            addChatMessage(`� I found **${extractedTicker}** in your question!\n\nLet me analyze it for you right away... ⏳`, false);
            
            // Trigger SINGLE ticker analysis (not whole portfolio!)
            try {
                await analyzeSingleTicker(extractedTicker);
                
                // After analysis completes, send question to backend WITHOUT re-analyzing
                addChatMessage(`✅ Analysis complete! Now let me answer your question...`, false);
                
                // Send the question with ticker context (backend won't re-analyze)
                await sendChatWithTicker(question, extractedTicker);
                
            } catch (error) {
                addChatMessage(`❌ Sorry, there was an error analyzing ${extractedTicker}. Please try again manually.`, false);
            }
            return;
        }
        
        // No ticker found - send to backend anyway (it handles educational questions!)
        await sendChatWithTicker(question, '');
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
    
    // Get context ticker (last discussed ticker)
    const contextTicker = conversationContext?.lastTicker || '';
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                ticker: ticker,
                context_ticker: contextTicker
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
        
        // Update conversation context
        if (data.ticker && conversationContext) {
            conversationContext.lastTicker = data.ticker;
            if (!conversationContext.analyzedTickers.includes(data.ticker)) {
                conversationContext.analyzedTickers.push(data.ticker);
            }
        }
        
        // Check if background analysis is needed
        if (data.needs_background_analysis && data.pending_ticker) {
            addChatMessage(data.answer, false);
            
            // SECURITY: Check if already analyzed to prevent infinite loop
            const alreadyAnalyzed = window.analysisResults && 
                window.analysisResults.some(r => r.ticker.toUpperCase() === data.pending_ticker.toUpperCase());
            
            if (!alreadyAnalyzed) {
                // Auto-trigger background analysis after 2 seconds
                setTimeout(async () => {
                    addChatMessage(`⏳ Running background analysis for ${data.pending_ticker}...`, false);
                    
                    // Add to session without updating UI
                    if (!sessionTickers.includes(data.pending_ticker)) {
                        sessionTickers.push(data.pending_ticker);
                        saveSessionTickers();
                    }
                    
                    try {
                        // Silent analysis - SINGLE TICKER ONLY
                        await analyzeSingleTicker(data.pending_ticker);
                        addChatMessage(`✅ Analysis complete for ${data.pending_ticker}! Feel free to ask more questions about it.`, false);
                        
                        // DON'T re-ask the question - this prevents infinite loop
                        // User can ask follow-up questions manually
                    } catch (error) {
                        addChatMessage(`❌ Sorry, I encountered an error analyzing ${data.pending_ticker}.`, false);
                    }
                }, 2000);
            } else {
                addChatMessage(`ℹ️  ${data.pending_ticker} is already analyzed. You can ask me questions about it!`, false);
            }
            return;
        }
        
        // Check if it's an educational response
        if (data.educational) {
            addChatMessage(data.answer, false);
            return;
        }
        
        // Check if ticker was inferred
        if (data.inferred_ticker) {
            addChatMessage(data.answer, false);
            if (data.ticker && conversationContext) {
                conversationContext.lastTicker = data.ticker;
            }
            return;
        }
        
        // Check for general response
        if (data.general_response) {
            addChatMessage(data.answer, false);
            return;
        }
        
        // Check for security warning
        if (data.security_warning) {
            addChatMessage(data.answer, false);
            return;
        }
        
        // Normal response
        if (data.success) {
            addChatMessage(data.answer, false);
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

// ===== THEME MANAGEMENT =====

function changeTheme(theme) {
    const html = document.documentElement;
    
    if (theme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        html.setAttribute('data-bs-theme', prefersDark ? 'dark' : 'light');
        localStorage.setItem('theme', 'auto');
    } else {
        html.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
    }
    
    debug.log(`Theme changed to: ${theme}`);
}

function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const themeSelect = document.getElementById('themeSelect');
    
    if (themeSelect) {
        themeSelect.value = savedTheme;
    }
    
    if (savedTheme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-bs-theme', prefersDark ? 'dark' : 'light');
        
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (localStorage.getItem('theme') === 'auto') {
                document.documentElement.setAttribute('data-bs-theme', e.matches ? 'dark' : 'light');
            }
        });
    } else {
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
    }
}

// ===== CHAT PANEL TOGGLE =====

function toggleChatPanel() {
    const chatPanel = document.getElementById('chatPanel');
    const toggleBtn = document.getElementById('chatToggleBtn');
    const body = document.body;
    
    if (chatPanel.classList.contains('hidden')) {
        // Show chat panel
        chatPanel.classList.remove('hidden');
        chatPanel.classList.add('show');
        body.classList.remove('chat-collapsed');
        if (toggleBtn) {
            toggleBtn.style.display = 'none';
        }
        // Save state
        localStorage.setItem('chatPanelState', 'open');
    } else {
        // Hide chat panel
        chatPanel.classList.add('hidden');
        chatPanel.classList.remove('show');
        body.classList.add('chat-collapsed');
        if (toggleBtn) {
            toggleBtn.style.display = 'flex';
        }
        // Save state
        localStorage.setItem('chatPanelState', 'collapsed');
    }
}

// ===== START NEW CHAT =====

function clearChatHistory() {
    if (!confirm('Start a new conversation? This will clear your current chat history.')) {
        return;
    }
    
    fetch('/clear-chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const messagesContainer = document.getElementById('chatMessages');
            messagesContainer.innerHTML = `
                <div class="chat-message assistant-message mb-3">
                    <div class="message-avatar bg-primary text-white">
                        <i class="bi bi-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-text">
                            <strong>👋 Welcome back!</strong> Conversation cleared. How can I help you?
                        </div>
                    </div>
                </div>
            `;
            
            if (conversationContext) {
                conversationContext.lastTicker = null;
                conversationContext.lastQuestion = null;
            }
            
            showToast('Conversation cleared', 'success');
        }
    })
    .catch(error => {
        console.error('Error clearing chat:', error);
        showToast('Failed to clear conversation', 'danger');
    });
}

// ===== TOAST NOTIFICATIONS =====

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toastId = 'toast_' + Date.now();
    const iconMap = {
        success: 'check-circle-fill',
        danger: 'exclamation-triangle-fill',
        warning: 'exclamation-circle-fill',
        info: 'info-circle-fill'
    };
    
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="toast-header bg-${type} text-white">
            <i class="bi bi-${iconMap[type]} me-2"></i>
            <strong class="me-auto">Notification</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// ===== INITIALIZE ON PAGE LOAD =====

// Load chat history from session on page load
async function loadChatHistory() {
    try {
        const response = await fetch('/get-chat-history');
        if (!response.ok) return;
        
        const data = await response.json();
        if (!data.success || !data.history || data.history.length === 0) return;
        
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;
        
        // Clear existing messages
        messagesContainer.innerHTML = '';
        
        // Load history
        data.history.forEach(msg => {
            const isUser = msg.role === 'user';
            addChatMessage(msg.content, isUser);
        });
        
        // Update conversation context
        if (data.last_ticker && conversationContext) {
            conversationContext.lastTicker = data.last_ticker;
            if (!conversationContext.analyzedTickers.includes(data.last_ticker)) {
                conversationContext.analyzedTickers.push(data.last_ticker);
            }
        }
        
        debug.log('✅ Chat history loaded:', data.history.length, 'messages');
    } catch (error) {
        console.error('Failed to load chat history:', error);
    }
}

// Show recommendation explanation modal
function showRecommendationExplanation(ticker) {
    const result = window.analysisResults.find(r => r.ticker === ticker);
    if (!result || !result.recommendation_explanation) {
        showToast('Recommendation explanation not available', 'info');
        return;
    }
    
    const exp = result.recommendation_explanation;
    const sentComponents = exp.sentiment_components;
    const analystComponents = exp.analyst_components;
    
    // Build explanation HTML
    let explanationHTML = `
        <div style="text-align: left;">
            <h5 class="mb-3">📊 How ${ticker}'s ${result.recommendation} Recommendation was Calculated</h5>
            
            <div class="alert alert-info mb-3">
                <strong>Formula:</strong> ${exp.formula}
            </div>
            
            <h6 class="mt-3 mb-2">🔢 Final Score: ${exp.final_score}</h6>
            
            <h6 class="mt-3 mb-2">📰 Sentiment Analysis (${exp.sentiment_weight} weight)</h6>
            <ul>
                <li><strong>News Sentiment:</strong> ${sentComponents.news_sentiment} (${sentComponents.news_weight})</li>
                <li><strong>Social Media Sentiment:</strong> ${sentComponents.social_sentiment} (${sentComponents.social_weight})</li>
                <li><strong>Combined Sentiment Score:</strong> ${result.sentiment_score.toFixed(2)}</li>
            </ul>
            
            <h6 class="mt-3 mb-2">📈 Technical Analysis (${exp.technical_weight} weight)</h6>
            <ul>
                ${exp.technical_components.map(reason => `<li>${reason}</li>`).join('')}
                <li><strong>Technical Score:</strong> ${result.technical_score.toFixed(2)}</li>
            </ul>
            
            ${analystComponents ? `
            <h6 class="mt-3 mb-2">👔 Analyst Consensus (${exp.analyst_weight} weight)</h6>
            <ul>
                <li><strong>Consensus:</strong> ${analystComponents.consensus} (${analystComponents.num_analysts} analyst${analystComponents.num_analysts !== 1 ? 's' : ''})</li>
                <li><strong>Recommendation Mean:</strong> ${analystComponents.recommendation_mean} (1=Strong Buy, 5=Strong Sell)</li>
                <li><strong>Price Target:</strong> ${analystComponents.target_price} (Current: ${analystComponents.current_price})</li>
                <li><strong>Upside Potential:</strong> ${analystComponents.upside}</li>
                <li><strong>Analyst Score:</strong> ${analystComponents.analyst_score}</li>
                <li style="font-size: 0.9em; color: #6c757d;">
                    Note: Analyst score is ${analystComponents.recommendation_weight} from consensus ratings, ${analystComponents.target_weight} from price targets
                </li>
            </ul>
            ` : `
            <div class="alert alert-warning mt-3">
                <i class="bi bi-info-circle me-2"></i>
                <strong>Note:</strong> No analyst coverage available for this stock (requires at least 3 analysts). Recommendation based on sentiment and technical analysis only.
            </div>
            `}
            
            <h6 class="mt-3 mb-2">🎯 Recommendation Thresholds</h6>
            <table class="table table-sm table-bordered">
                <thead>
                    <tr>
                        <th>Recommendation</th>
                        <th>Score Range</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(exp.thresholds).map(([rec, range]) => `
                        <tr ${rec === result.recommendation ? 'class="table-success"' : ''}>
                            <td><strong>${rec}</strong></td>
                            <td>${range}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            
            <div class="alert alert-warning mt-3">
                <i class="bi bi-exclamation-triangle me-2"></i>
                <strong>Disclaimer:</strong> This recommendation is for educational purposes only. Always conduct your own research and consult with financial professionals before making investment decisions.
            </div>
        </div>
    `;
    
    // Create and show modal (using Bootstrap if available, otherwise alert)
    const modalId = 'recommendationExplanationModal';
    let modal = document.getElementById(modalId);
    
    if (!modal) {
        // Create modal
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Recommendation Calculation</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="${modalId}Body">
                        ${explanationHTML}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    } else {
        // Update existing modal
        document.getElementById(`${modalId}Body`).innerHTML = explanationHTML;
    }
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

document.addEventListener('DOMContentLoaded', function() {
    debug.log('🚀 FinBERT Portfolio Analyzer - Modern UI Loaded');
    
    initializeTheme();
    initializeChatPanel();  // Initialize chat panel state
    fetchExchangeRates();   // 💱 Fetch live exchange rates
    loadSessionTickers();
    loadChatHistory();  // Load previous conversation
    loadMarketSentiment();  // Load daily market sentiment
    
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) {
        // Load config immediately when modal is about to show (before animation)
        settingsModal.addEventListener('show.bs.modal', function() {
            loadConfigToUI();  // 🔧 FIX: Load saved settings before modal animation
            updateSavedTickersList();
        });
    }
    
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
    
    debug.log('✅ Theme, portfolio, chat, and market sentiment initialized');
    
    // Listen for theme changes and refresh charts
    setupThemeChangeListener();
});

// Setup theme change listener to refresh charts automatically
function setupThemeChangeListener() {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-bs-theme') {
                const newTheme = document.documentElement.getAttribute('data-bs-theme');
                debug.log(`🎨 Theme changed to: ${newTheme}`);
                refreshAllChartsForTheme();
            }
        });
    });

    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-bs-theme']
    });
    
    debug.log('👀 Theme change observer activated');
}

// Refresh all visible charts when theme changes
function refreshAllChartsForTheme() {
    if (!window.analysisResults || window.analysisResults.length === 0) {
        debug.log('No charts to refresh');
        return;
    }
    
    const theme = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
    debug.log(`🔄 Refreshing ${window.analysisResults.length} chart(s) for ${theme} theme`);
    
    window.analysisResults.forEach((result, index) => {
        const chartDiv = document.getElementById(`chart_${result.ticker}`);
        
        // Only refresh if chart exists and has been rendered
        if (chartDiv && chartDiv.innerHTML.trim() !== '') {
            debug.log(`  ↻ Refreshing chart for ${result.ticker}`);
            
            // Get current chart type and timeframe from controls
            const chartTypeSelect = document.getElementById(`chartType_${result.ticker}`);
            const timeframeSelect = document.getElementById(`timeframe_${result.ticker}`);
            
            const chartType = chartTypeSelect ? chartTypeSelect.value : result.chart_type_used;
            const timeframe = timeframeSelect ? timeframeSelect.value : result.timeframe_used;
            
            // Update chart with new theme
            updateChart(result.ticker, index, chartType, timeframe);
        }
    });
}

// Initialize chat panel - start collapsed
function initializeChatPanel() {
    const chatPanel = document.getElementById('chatPanel');
    const toggleBtn = document.getElementById('chatToggleBtn');
    const body = document.body;
    
    // Check saved state or default to collapsed
    const savedState = localStorage.getItem('chatPanelState') || 'collapsed';
    
    if (savedState === 'collapsed') {
        chatPanel.classList.add('hidden');
        chatPanel.classList.remove('show');
        body.classList.add('chat-collapsed');
        if (toggleBtn) {
            toggleBtn.style.display = 'flex';
        }
    } else {
        chatPanel.classList.remove('hidden');
        chatPanel.classList.add('show');
        body.classList.remove('chat-collapsed');
        if (toggleBtn) {
            toggleBtn.style.display = 'none';
        }
    }
    
    debug.log(`💬 Chat panel initialized: ${savedState}`);
}

// ===== MARKET SENTIMENT =====

/**
 * Load and display daily market sentiment
 */
async function loadMarketSentiment(forceRefresh = false) {
    const contentDiv = document.getElementById('marketSentimentContent');
    
    if (!contentDiv) return;
    
    // Show loading state
    contentDiv.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Analyzing market sentiment...</p>
        </div>
    `;
    
    try {
        const params = new URLSearchParams();
        if (forceRefresh) params.append('refresh', 'true');
        
        // 💱 Pass user's currency preference to backend
        params.append('currency', appConfig.currency || 'USD');
        
        const url = `/market-sentiment?${params.toString()}`;
        const response = await fetch(url);
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Failed to load market sentiment');
        }
        
        renderMarketSentiment(result.data);
        
    } catch (error) {
        console.error('Error loading market sentiment:', error);
        contentDiv.innerHTML = `
            <div class="alert alert-warning mb-0">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Unable to load market sentiment. Please try again later.
            </div>
        `;
    }
}

/**
 * Render market sentiment data
 */
function renderMarketSentiment(data) {
    const contentDiv = document.getElementById('marketSentimentContent');
    
    if (!contentDiv || !data) return;
    
    const sentimentColor = {
        'BULLISH': 'success',
        'BEARISH': 'danger',
        'NEUTRAL': 'warning'
    }[data.sentiment] || 'secondary';
    
    const sentimentIcon = {
        'BULLISH': 'arrow-up-circle-fill',
        'BEARISH': 'arrow-down-circle-fill',
        'NEUTRAL': 'dash-circle-fill'
    }[data.sentiment] || 'circle-fill';
    
    const timestamp = data.timestamp ? new Date(data.timestamp).toLocaleString() : '';
    
    let html = `
        <!-- Overall Sentiment -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="d-flex align-items-center justify-content-between mb-3">
                    <div class="d-flex align-items-center gap-3">
                        <div class="display-4">
                            <i class="bi bi-${sentimentIcon} text-${sentimentColor}"></i>
                        </div>
                        <div>
                            <h3 class="mb-1 text-${sentimentColor}">${data.sentiment}</h3>
                            <div class="progress" style="width: 200px; height: 8px;">
                                <div class="progress-bar bg-${sentimentColor}" role="progressbar" 
                                     style="width: ${data.confidence}%" 
                                     aria-valuenow="${data.confidence}" aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                            <small class="text-muted">Confidence: ${data.confidence}%</small>
                        </div>
                    </div>
                    <small class="text-muted">
                        <i class="bi bi-clock me-1"></i>${timestamp}
                    </small>
                </div>
                
                ${data.summary ? `
                <div class="alert alert-${sentimentColor} alert-dismissible fade show mb-3" role="alert">
                    <strong><i class="bi bi-megaphone me-2"></i>Market Summary:</strong> ${data.summary}
                </div>
                ` : ''}
                
                ${data.reasoning ? `
                <div class="card border-0 bg-light mb-3">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="bi bi-lightbulb text-warning me-2"></i>Analysis
                        </h6>
                        <p class="mb-0">${data.reasoning}</p>
                    </div>
                </div>
                ` : ''}
            </div>
        </div>
        
        <!-- Market Indices -->
        ${data.market_indices && Object.keys(data.market_indices).length > 0 ? `
        <div class="row mb-4">
            <div class="col-12">
                <h6 class="mb-3">
                    <i class="bi bi-graph-up text-primary me-2"></i>Market Indices
                </h6>
                <div class="row g-3">
                    ${Object.entries(data.market_indices).map(([name, idx]) => `
                        <div class="col-md-6 col-lg-3">
                            <div class="card h-100 border-0 shadow-sm">
                                <div class="card-body">
                                    <h6 class="card-title text-truncate" title="${name}">${name}</h6>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <span class="h5 mb-0">${idx.current}</span>
                                        <span class="badge bg-${idx.trend === 'up' ? 'success' : 'danger'}">
                                            <i class="bi bi-arrow-${idx.trend === 'up' ? 'up' : 'down'} me-1"></i>${idx.change_pct}%
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
        ` : ''}
        
        <!-- Top Sectors -->
        ${data.top_sectors && Object.keys(data.top_sectors).length > 0 ? `
        <div class="row mb-4">
            <div class="col-12">
                <h6 class="mb-3">
                    <i class="bi bi-pie-chart text-info me-2"></i>Top Performing Sectors
                </h6>
                <div class="list-group">
                    ${Object.entries(data.top_sectors).map(([name, sector]) => `
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${name}</strong>
                                <small class="text-muted ms-2">${sector.symbol}</small>
                            </div>
                            <span class="badge bg-${sector.trend === 'up' ? 'success' : 'danger'} fs-6">
                                <i class="bi bi-arrow-${sector.trend === 'up' ? 'up' : 'down'} me-1"></i>${sector.change_pct}%
                            </span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
        ` : ''}
        
        <!-- Key Factors -->
        ${data.key_factors && data.key_factors.length > 0 ? `
        <div class="row mb-4">
            <div class="col-12">
                <h6 class="mb-3">
                    <i class="bi bi-key text-warning me-2"></i>Key Factors
                </h6>
                <ul class="list-group list-group-flush">
                    ${data.key_factors.map(factor => `
                        <li class="list-group-item">
                            <i class="bi bi-chevron-right text-primary me-2"></i>${factor}
                        </li>
                    `).join('')}
                </ul>
            </div>
        </div>
        ` : ''}
        
        <!-- Stock Recommendations -->
        <div class="row">
            <!-- Buy Recommendations -->
            <div class="col-md-6 mb-3">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="mb-0 text-success">
                        <i class="bi bi-cart-plus me-2"></i>Top Picks to Buy
                    </h6>
                    <button class="btn btn-sm btn-outline-success" id="refreshBuyRecsBtn" 
                            onclick="refreshRecommendations()" 
                            title="Get different recommendations">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                </div>
                ${data.buy_recommendations && data.buy_recommendations.length > 0 ? 
                    data.buy_recommendations.map((rec, idx) => `
                        <div class="card border-success mb-2">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <div>
                                        <h6 class="mb-1">
                                            <span class="badge bg-success me-2">${idx + 1}</span>
                                            <strong>${rec.ticker}</strong>
                                            ${rec.price ? `<span class="badge bg-secondary ms-2">${formatPrice(rec.price, rec.ticker)}</span>` : ''}
                                        </h6>
                                    </div>
                                    <button class="btn btn-sm btn-outline-success" 
                                            onclick="addTickerFromRecommendation('${rec.ticker}')"
                                            title="Add to analysis">
                                        <i class="bi bi-plus-circle"></i>
                                    </button>
                                </div>
                                <small class="text-muted d-block mb-2">
                                    <i class="bi bi-tag me-1"></i>${rec.sector || 'N/A'}
                                </small>
                                <p class="mb-0 small">${rec.reason}</p>
                            </div>
                        </div>
                    `).join('') 
                : `
                    <div class="alert alert-info mb-0">
                        <i class="bi bi-info-circle me-2"></i>
                        No buy recommendations available at this time.
                    </div>
                `}
            </div>
            
            <!-- Sell Recommendations -->
            <div class="col-md-6 mb-3">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="mb-0 text-danger">
                        <i class="bi bi-x-circle me-2"></i>Stocks to Avoid/Sell
                    </h6>
                    <button class="btn btn-sm btn-outline-danger" id="refreshSellRecsBtn" 
                            onclick="refreshRecommendations()" 
                            title="Get different recommendations">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                </div>
                ${data.sell_recommendations && data.sell_recommendations.length > 0 ? 
                    data.sell_recommendations.map((rec, idx) => `
                        <div class="card border-danger mb-2">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <h6 class="mb-1">
                                        <span class="badge bg-danger me-2">${idx + 1}</span>
                                        <strong>${rec.ticker}</strong>
                                        ${rec.price ? `<span class="badge bg-secondary ms-2">${formatPrice(rec.price, rec.ticker)}</span>` : ''}
                                    </h6>
                                </div>
                                <small class="text-muted d-block mb-2">
                                    <i class="bi bi-tag me-1"></i>${rec.sector || 'N/A'}
                                </small>
                                <p class="mb-0 small">${rec.reason}</p>
                            </div>
                        </div>
                    `).join('')
                : `
                    <div class="alert alert-info mb-0">
                        <i class="bi bi-info-circle me-2"></i>
                        No sell recommendations available at this time.
                    </div>
                `}
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}

/**
 * Refresh market sentiment (full dashboard)
 */
async function refreshMarketSentiment() {
    const btn = document.getElementById('refreshSentimentBtn');
    if (btn) {
        btn.disabled = true;
        // Use only spinner, not the arrow icon to avoid double spinning
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
    }
    
    await loadMarketSentiment(true);
    
    if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
    }
}

/**
 * Refresh only stock recommendations (not the entire sentiment analysis)
 */
async function refreshRecommendations() {
    const buyBtn = document.getElementById('refreshBuyRecsBtn');
    const sellBtn = document.getElementById('refreshSellRecsBtn');
    
    // Disable buttons and show loading
    if (buyBtn) {
        buyBtn.disabled = true;
        buyBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
    }
    if (sellBtn) {
        sellBtn.disabled = true;
        sellBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
    }
    
    try {
        // Force refresh to get new recommendations
        const params = new URLSearchParams();
        params.append('refresh', 'true');
        
        const url = `/market-sentiment?${params.toString()}`;
        const response = await fetch(url);
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Failed to load recommendations');
        }
        
        // Get the data
        const data = result.data;
        
        // Find the recommendations row specifically (it's the last row with col-md-6 children)
        const allRows = document.querySelectorAll('#marketSentimentContent .row');
        let recommendationsRow = null;
        
        // Find the row that contains the buy/sell recommendations
        for (let i = allRows.length - 1; i >= 0; i--) {
            const cols = allRows[i].querySelectorAll('.col-md-6');
            if (cols.length === 2) {
                // Check if this row has the recommendations by looking for the specific buttons
                const hasBuyBtn = allRows[i].querySelector('#refreshBuyRecsBtn');
                const hasSellBtn = allRows[i].querySelector('#refreshSellRecsBtn');
                if (hasBuyBtn || hasSellBtn) {
                    recommendationsRow = allRows[i];
                    break;
                }
            }
        }
        
        if (!recommendationsRow) {
            console.error('Could not find recommendations row');
            return;
        }
        
        const cols = recommendationsRow.querySelectorAll('.col-md-6');
        const buyContainer = cols[0];
        const sellContainer = cols[1];
        
        if (buyContainer && data.buy_recommendations) {
            // Rebuild buy recommendations section
            const buyHtml = `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="mb-0 text-success">
                        <i class="bi bi-cart-plus me-2"></i>Top Picks to Buy
                    </h6>
                    <button class="btn btn-sm btn-outline-success" id="refreshBuyRecsBtn" 
                            onclick="refreshRecommendations()" 
                            title="Get different recommendations">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                </div>
                ${data.buy_recommendations.map((rec, idx) => `
                    <div class="card border-success mb-2">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <div>
                                    <h6 class="mb-1">
                                        <span class="badge bg-success me-2">${idx + 1}</span>
                                        <strong>${rec.ticker}</strong>
                                        ${rec.price ? `<span class="badge bg-secondary ms-2">${formatPrice(rec.price)}</span>` : ''}
                                    </h6>
                                </div>
                                <button class="btn btn-sm btn-outline-success" 
                                        onclick="addTickerFromRecommendation('${rec.ticker}')"
                                        title="Add to analysis">
                                    <i class="bi bi-plus-circle"></i>
                                </button>
                            </div>
                            <small class="text-muted d-block mb-2">
                                <i class="bi bi-tag me-1"></i>${rec.sector || 'N/A'}
                            </small>
                            <p class="mb-0 small">${rec.reason}</p>
                        </div>
                    </div>
                `).join('')}
            `;
            buyContainer.innerHTML = buyHtml;
        }
        
        if (sellContainer && data.sell_recommendations) {
            // Rebuild sell recommendations section
            const sellHtml = `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="mb-0 text-danger">
                        <i class="bi bi-x-circle me-2"></i>Stocks to Avoid/Sell
                    </h6>
                    <button class="btn btn-sm btn-outline-danger" id="refreshSellRecsBtn" 
                            onclick="refreshRecommendations()" 
                            title="Get different recommendations">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                </div>
                ${data.sell_recommendations.map((rec, idx) => `
                    <div class="card border-danger mb-2">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="mb-1">
                                    <span class="badge bg-danger me-2">${idx + 1}</span>
                                    <strong>${rec.ticker}</strong>
                                    ${rec.price ? `<span class="badge bg-secondary ms-2">${formatPrice(rec.price)}</span>` : ''}
                                </h6>
                            </div>
                            <small class="text-muted d-block mb-2">
                                <i class="bi bi-tag me-1"></i>${rec.sector || 'N/A'}
                            </small>
                            <p class="mb-0 small">${rec.reason}</p>
                        </div>
                    </div>
                `).join('')}
            `;
            sellContainer.innerHTML = sellHtml;
        }
        
    } catch (error) {
        console.error('Error refreshing recommendations:', error);
        showToast('Failed to refresh recommendations', 'danger');
    } finally {
        // Re-enable buttons
        if (buyBtn) {
            buyBtn.disabled = false;
            buyBtn.innerHTML = '<i class="bi bi-arrow-repeat"></i>';
        }
        if (sellBtn) {
            sellBtn.disabled = false;
            sellBtn.innerHTML = '<i class="bi bi-arrow-repeat"></i>';
        }
    }
}



/**
 * Add ticker from recommendation to analysis
 */
function addTickerFromRecommendation(ticker) {
    if (!ticker) return;
    
    const tickerInput = document.getElementById('tickerInput');
    if (tickerInput) {
        tickerInput.value = ticker.toUpperCase();
        addTicker();  // addTicker() already shows a toast
    }
}


// ===== DEVELOPER MODE FUNCTIONS =====

/**
 * Initialize developer mode UI elements
 * Shows/hides developer tab based on DEBUG_MODE
 */
function initializeDeveloperMode() {
    const devTabNav = document.getElementById('developer-tab-nav');
    const devDebugToggle = document.getElementById('devDebugModeToggle');
    const devDebugStatus = document.getElementById('devDebugStatus');
    
    if (DEBUG_MODE) {
        // Show developer tab
        if (devTabNav) {
            devTabNav.style.display = 'block';
        }
        
        // Update toggle state
        if (devDebugToggle) {
            devDebugToggle.checked = true;
        }
        
        // Update status badge
        if (devDebugStatus) {
            devDebugStatus.textContent = 'Enabled';
            devDebugStatus.className = 'badge bg-success';
        }
    } else {
        // Hide developer tab
        if (devTabNav) {
            devTabNav.style.display = 'none';
        }
        
        // Update toggle state
        if (devDebugToggle) {
            devDebugToggle.checked = false;
        }
        
        // Update status badge
        if (devDebugStatus) {
            devDebugStatus.textContent = 'Disabled';
            devDebugStatus.className = 'badge bg-secondary';
        }
    }
}

/**
 * Toggle frontend debug mode
 */
function toggleDebugMode(enabled) {
    if (enabled) {
        localStorage.setItem('DEBUG_MODE', 'true');
        showToast('Debug mode enabled. Reload page to see console logs.', 'info');
    } else {
        localStorage.removeItem('DEBUG_MODE');
        showToast('Debug mode disabled. Reload page to apply.', 'info');
    }
    
    // Update status
    const devDebugStatus = document.getElementById('devDebugStatus');
    if (devDebugStatus) {
        devDebugStatus.textContent = enabled ? 'Enabled (reload needed)' : 'Disabled (reload needed)';
        devDebugStatus.className = enabled ? 'badge bg-warning' : 'badge bg-secondary';
    }
}

/**
 * Update backend log level command display
 */
function updateLogLevelCommand() {
    const logLevel = document.getElementById('devLogLevel')?.value || 'INFO';
    const commandInput = document.getElementById('devLogLevelCommand');
    
    if (commandInput) {
        commandInput.value = `LOG_LEVEL=${logLevel} python3 app.py`;
    }
}

/**
 * Copy log level command to clipboard
 */
function copyLogLevelCommand() {
    const commandInput = document.getElementById('devLogLevelCommand');
    
    if (commandInput) {
        commandInput.select();
        document.execCommand('copy');
        showToast('Command copied to clipboard!', 'success');
    }
}

// Listen for log level changes
document.addEventListener('DOMContentLoaded', function() {
    const devLogLevelSelect = document.getElementById('devLogLevel');
    if (devLogLevelSelect) {
        devLogLevelSelect.addEventListener('change', updateLogLevelCommand);
        updateLogLevelCommand(); // Initialize
    }
    
    // Initialize developer mode UI
    initializeDeveloperMode();
});
