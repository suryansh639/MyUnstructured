#!/bin/bash

echo "🚀 Starting DocuAI Frontend"
echo "==========================="
echo ""

cd /home/ubuntu/MyUnstructured/landing-page

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo ""
echo "✅ Starting Next.js app..."
echo "📍 Open: http://localhost:3000"
echo ""

npm run dev
