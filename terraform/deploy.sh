#!/bin/bash
set -e

echo "🚀 Deploying DocuAI Infrastructure to AWS"
echo "=========================================="

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo "Installing Terraform..."
    wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    sudo apt update && sudo apt install terraform -y
fi

# Package Lambda functions
echo "📦 Packaging Lambda functions..."
chmod +x package_lambdas.sh
./package_lambdas.sh

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Plan
echo "📋 Planning deployment..."
terraform plan -out=tfplan

# Apply
echo "🚀 Deploying infrastructure..."
terraform apply tfplan

# Get outputs
echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
terraform output

# Save outputs to file
terraform output -json > outputs.json

echo ""
echo "📝 Outputs saved to outputs.json"
echo ""
echo "Next steps:"
echo "1. Update frontend with API endpoint and Cognito details"
echo "2. Test API: curl \$(terraform output -raw api_endpoint)/v1/register"
echo "3. Deploy frontend to Vercel/Amplify"
