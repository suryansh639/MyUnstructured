#!/bin/bash

echo "🚀 Starting Streamlit Document Processing App"
echo "=============================================="
echo ""

cd /home/ubuntu/MyUnstructured

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
if [ ! -f "venv/.installed" ]; then
    echo "📦 Installing dependencies..."
    pip install -q streamlit pandas plotly
    touch venv/.installed
fi

echo "✅ Starting Streamlit on http://localhost:8501"
echo "   (Configured to allow iframe embedding)"
echo ""

streamlit run app.py \
    --server.port 8501 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false
