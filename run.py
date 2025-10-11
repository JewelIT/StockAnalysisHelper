"""
Vestor - AI Financial Advisor Application
Main application entry point
"""
import os
from src.web import create_app
from src.logging_config import setup_logging

# Setup logging
logger = setup_logging()

# Create Flask application
app = create_app()

if __name__ == '__main__':
    print("="*80)
    print("🤖 VESTOR - AI Financial Advisor")
    print("="*80)
    print("🚀 Starting application...")
    print("📊 Access at: http://localhost:5000")
    print("💡 FinBERT model will load on first analysis request")
    print("="*80)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
