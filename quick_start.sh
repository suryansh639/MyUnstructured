#!/bin/bash

echo "🚀 DocuAI SaaS Platform - Quick Start"
echo "======================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    sudo apt --fix-broken install -y
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

echo "✅ Node.js version: $(node --version)"
echo ""

# Setup Landing Page
echo "🎨 Setting up Landing Page..."
cd landing-page
if [ ! -d "node_modules" ]; then
    npm install
fi
echo "✅ Landing page ready!"
echo ""

# Setup Python Environment
echo "🐍 Setting up Python environment..."
cd ..
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements_api.txt
echo "✅ Python environment ready!"
echo ""

echo "======================================"
echo "🎉 Setup Complete! Now run:"
echo ""
echo "Terminal 1 (Landing Page):"
echo "  cd landing-page && npm run dev"
echo ""
echo "Terminal 2 (API Backend):"
echo "  source venv/bin/activate && uvicorn api_service:app --reload"
echo ""
echo "Terminal 3 (Streamlit UI):"
echo "  source venv/bin/activate && streamlit run app.py"
echo ""
echo "📚 Full guide: cat SETUP_GUIDE.md"
echo "======================================"
