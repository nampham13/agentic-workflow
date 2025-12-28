#!/bin/bash

# Run script cho Life AI Agentic Backend

echo "🚀 Starting Life AI Agentic Backend..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API documentation: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
