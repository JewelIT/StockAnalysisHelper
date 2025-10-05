# Dockerfile for Stock Analysis Helper
# Production-ready Flask app with AI models

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create exports directory
RUN mkdir -p exports

# Pre-download models (optional - speeds up first run)
# Uncomment to pre-cache models in Docker image (increases image size by ~1.2GB)
# RUN python3 -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
#     AutoTokenizer.from_pretrained('yiyanghkust/finbert-tone'); \
#     AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone'); \
#     AutoTokenizer.from_pretrained('cardiffnlp/twitter-roberta-base-sentiment-latest'); \
#     AutoModelForSequenceClassification.from_pretrained('cardiffnlp/twitter-roberta-base-sentiment-latest'); \
#     AutoTokenizer.from_pretrained('distilbert-base-cased-distilled-squad'); \
#     AutoModelForSequenceClassification.from_pretrained('distilbert-base-cased-distilled-squad')"

# Expose Flask port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["python3", "app.py"]
