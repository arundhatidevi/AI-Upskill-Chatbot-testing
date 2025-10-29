#!/bin/bash
# Setup script for Chatbot UI Automation

set -e

echo "🚀 Setting up Chatbot UI Automation..."

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python -m playwright install --with-deps chromium

# Copy .env.example to .env if not exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
fi

# Create artifacts directories
echo "📁 Creating artifacts directories..."
mkdir -p artifacts/{logs,screenshots,videos,junit,allure}

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Activate the virtual environment: source .venv/bin/activate"
echo "3. Run tests: pytest -v"
echo ""
echo "For CI/CD, see .github/workflows/ci.yml"










