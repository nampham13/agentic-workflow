#!/bin/bash

# Setup script cho Life AI Agentic Backend

echo "🚀 Setting up Life AI Agentic - Molecule Generation & Screening Backend"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "🔨 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup completed!"
echo ""
echo "📝 Next steps:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Run server: uvicorn app.main:app --reload"
echo "   3. Open API docs: http://localhost:8000/docs"
echo ""
