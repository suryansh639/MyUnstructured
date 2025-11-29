#!/bin/bash

set -e

echo "🚀 DocuAI - Complete Deployment Script"
echo "======================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    echo "Run: curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip' && unzip awscliv2.zip && sudo ./aws/install"
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured."
    echo "Run: aws configure"
    exit 1
fi

echo "✅ AWS CLI configured"

# Deploy infrastructure
echo ""
echo "🏗️  Deploying AWS Infrastructure..."
echo "===================================="
cd terraform
chmod +x *.sh
./deploy.sh

# Get outputs
echo ""
echo "📊 Getting deployment outputs..."
API_ENDPOINT=$(terraform output -raw api_endpoint)
USER_POOL_ID=$(terraform output -raw user_pool_id)
USER_POOL_CLIENT_ID=$(terraform output -raw user_pool_client_id)
BUCKET_NAME=$(terraform output -raw bucket_name)

# Configure frontend
echo ""
echo "⚙️  Configuring frontend..."
cd ../landing-page

cat > .env.local << EOF
NEXT_PUBLIC_AWS_REGION=us-east-1
NEXT_PUBLIC_USER_POOL_ID=$USER_POOL_ID
NEXT_PUBLIC_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID
NEXT_PUBLIC_API_ENDPOINT=$API_ENDPOINT
EOF

echo "✅ Frontend configured"

# Test API
echo ""
echo "🧪 Testing API..."
echo "Registering test user..."

RESPONSE=$(curl -s -X POST $API_ENDPOINT/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@docuai.com",
    "password": "TestPass123!",
    "name": "Test User"
  }')

echo "Response: $RESPONSE"

# Summary
echo ""
echo "======================================="
echo "✅ Deployment Complete!"
echo "======================================="
echo ""
echo "📊 Your Infrastructure:"
echo "  API Endpoint: $API_ENDPOINT"
echo "  User Pool ID: $USER_POOL_ID"
echo "  Client ID: $USER_POOL_CLIENT_ID"
echo "  S3 Bucket: $BUCKET_NAME"
echo ""
echo "🌐 Next Steps:"
echo "  1. Start frontend: cd landing-page && npm install && npm run dev"
echo "  2. Open: http://localhost:3000"
echo "  3. Deploy to Vercel: cd landing-page && vercel --prod"
echo ""
echo "📚 Documentation:"
echo "  - Deployment Guide: cat DEPLOYMENT_GUIDE.md"
echo "  - API Testing: cat DEPLOYMENT_GUIDE.md | grep 'Test End-to-End'"
echo ""
echo "🎉 Happy building!"
