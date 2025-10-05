#!/bin/bash
# Build desktop executable using PyInstaller

echo "🏗️  Building Desktop Executable for Stock Analysis Helper"
echo "=========================================================="
echo ""

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Build executable
echo "🔨 Building executable (this will take several minutes)..."
pyinstaller StockAnalysisHelper.spec --clean

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "📦 Executable location: dist/StockAnalysisHelper/"
    echo ""
    echo "To run the app:"
    echo "  cd dist/StockAnalysisHelper"
    echo "  ./StockAnalysisHelper"
    echo ""
    echo "To create a distributable archive:"
    echo "  cd dist"
    echo "  tar -czf StockAnalysisHelper-Linux.tar.gz StockAnalysisHelper/"
    echo ""
    
    # Calculate size
    SIZE=$(du -sh dist/StockAnalysisHelper | cut -f1)
    echo "📊 Package size: $SIZE"
    echo ""
    echo "⚠️  Note: First run will download AI models (~1.2GB)"
else
    echo ""
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi
