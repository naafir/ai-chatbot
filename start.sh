#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# AI Chat — Startup Script
# Run with: bash start.sh
# ═══════════════════════════════════════════════════════════════

set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║          AI Chat — Starting Up           ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install it from https://python.org"
    exit 1
fi

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Install from https://ollama.ai"
    echo "   Then run: ollama pull llama3"
    echo "   Then run: ollama serve"
else
    echo "✅ Ollama found"
    # Start Ollama in background if not already running
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "🚀 Starting Ollama..."
        ollama serve &
        sleep 3
    else
        echo "✅ Ollama already running"
    fi
fi

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt -q

# Create database directory
mkdir -p database

# Copy .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚙️  Created .env from .env.example"
fi

echo ""
echo "🚀 Starting FastAPI server..."
echo "   → API:      http://localhost:8000"
echo "   → App:      http://localhost:8000"
echo "   → API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
