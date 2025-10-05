#!/bin/bash
# Quick start script for Docker deployment

echo "🚀 Stock Analysis Helper - Docker Setup"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose not found, using 'docker compose' instead"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Build and start
echo "📦 Building Docker image (this may take a few minutes)..."
$COMPOSE_CMD build

echo ""
echo "🚀 Starting Stock Analysis Helper..."
$COMPOSE_CMD up -d

echo ""
echo "✅ Stock Analysis Helper is starting!"
echo ""
echo "📊 Access the app at: http://localhost:5000"
echo ""
echo "⏳ First analysis will download AI models (~1.2GB)"
echo "   This only happens once - models are cached for future use."
echo ""
echo "📝 To stop the app: $COMPOSE_CMD down"
echo "📝 To view logs: $COMPOSE_CMD logs -f"
echo "📝 To rebuild: $COMPOSE_CMD build --no-cache"
echo ""
echo "🌟 Opening browser in 5 seconds..."
sleep 5

# Try to open browser
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:5000 2>/dev/null || echo "Open http://localhost:5000 in your browser"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:5000
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    start http://localhost:5000
else
    echo "Please open http://localhost:5000 in your browser"
fi
