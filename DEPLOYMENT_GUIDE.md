# 🚀 Complete Deployment Guide - DocuAI SaaS

## Architecture Overview

**AWS Services Used:**
- ✅ **Cognito** - User authentication & management
- ✅ **DynamoDB** - User data, credits, API usage tracking
- ✅ **Lambda** - Serverless document processing
- ✅ **API Gateway** - RESTful API endpoints
- ✅ **S3** - Document storage
- ✅ **IAM** - Security & permissions

## Prerequisites

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# Install Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform -y

# Verify installations
aws --version
terraform --version
```

## Step 1: Deploy AWS Infrastructure

```bash
cd /home/ubuntu/MyUnstructured/terraform

# Make scripts executable
chmod +x *.sh

# Deploy everything
./deploy.sh
```

This will:
1. Package Lambda functions
2. Initialize Terraform
3. Create all AWS resources
4. Output API endpoint and Cognito details

**Expected output:**
```
api_endpoint = "https://xxxxx.execute-api.us-east-1.amazonaws.com/prod"
user_pool_id = "us-east-1_xxxxx"
user_pool_client_id = "xxxxxxxxxxxxx"
bucket_name = "docuai-documents-xxxxx"
```

## Step 2: Configure Frontend

```bash
cd /home/ubuntu/MyUnstructured/landing-page

# Copy environment template
cp .env.local.template .env.local

# Edit with your values from Terraform output
nano .env.local
```

Update `.env.local`:
```bash
NEXT_PUBLIC_AWS_REGION=us-east-1
NEXT_PUBLIC_USER_POOL_ID=<from terraform output>
NEXT_PUBLIC_USER_POOL_CLIENT_ID=<from terraform output>
NEXT_PUBLIC_API_ENDPOINT=<from terraform output>
```

## Step 3: Test Locally

### Terminal 1: Start Frontend
```bash
cd /home/ubuntu/MyUnstructured/landing-page
npm install
npm run dev
# Opens at http://localhost:3000
```

### Test the API directly:
```bash
# Get API endpoint from Terraform
API_ENDPOINT=$(cd terraform && terraform output -raw api_endpoint)

# Test registration
curl -X POST $API_ENDPOINT/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "name": "Test User"
  }'

# Expected response:
# {"message": "User registered successfully", "user_id": "...", "credits": 100}
```

## Step 4: Deploy Frontend to Vercel

```bash
cd /home/ubuntu/MyUnstructured/landing-page

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Add environment variables in Vercel dashboard:
# Settings > Environment Variables
# Add all NEXT_PUBLIC_* variables
```

## Step 5: Test End-to-End

### 1. Register a User
```bash
curl -X POST https://your-api.execute-api.us-east-1.amazonaws.com/prod/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'
```

### 2. Login (Get JWT Token)
```bash
# Use AWS Cognito to authenticate
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id YOUR_CLIENT_ID \
  --auth-parameters USERNAME=user@example.com,PASSWORD=SecurePass123!
```

### 3. Process Document
```bash
# Convert file to base64
FILE_BASE64=$(base64 -w 0 sample.pdf)

curl -X POST https://your-api.execute-api.us-east-1.amazonaws.com/prod/v1/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d "{
    \"file\": \"$FILE_BASE64\",
    \"filename\": \"sample.pdf\"
  }"
```

### 4. Check Credits
```bash
curl https://your-api.execute-api.us-east-1.amazonaws.com/prod/v1/credits \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Architecture Diagram

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Next.js App    │ (Vercel)
│  Landing Page   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Gateway    │ (AWS)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│Cognito │ │Lambda  │
│  Auth  │ │Process │
└────────┘ └───┬────┘
               │
        ┌──────┴──────┐
        ▼             ▼
   ┌────────┐    ┌────────┐
   │DynamoDB│    │   S3   │
   │Credits │    │  Docs  │
   └────────┘    └────────┘
```

## Cost Estimation

**Free Tier (First Year):**
- Lambda: 1M requests/month free
- DynamoDB: 25GB storage free
- S3: 5GB storage free
- API Gateway: 1M requests/month free
- Cognito: 50,000 MAU free

**Expected Monthly Cost (after free tier):**
- 1,000 users, 10K documents/month: ~$5-10/month
- 10,000 users, 100K documents/month: ~$50-100/month

## Monitoring & Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/docuai-prod-process-document --follow

# Check DynamoDB tables
aws dynamodb scan --table-name docuai-prod-users --max-items 5

# Monitor API Gateway
aws apigateway get-rest-apis
```

## Troubleshooting

### Lambda Function Errors
```bash
# Check Lambda logs
aws logs tail /aws/lambda/docuai-prod-process-document --since 1h

# Update Lambda code
cd terraform
./package_lambdas.sh
terraform apply
```

### Cognito Issues
```bash
# List users
aws cognito-idp list-users --user-pool-id YOUR_POOL_ID

# Confirm user email
aws cognito-idp admin-confirm-sign-up \
  --user-pool-id YOUR_POOL_ID \
  --username user@example.com
```

### DynamoDB Issues
```bash
# Check table
aws dynamodb describe-table --table-name docuai-prod-users

# Query user
aws dynamodb get-item \
  --table-name docuai-prod-users \
  --key '{"user_id": {"S": "USER_ID"}}'
```

## Cleanup (Delete Everything)

```bash
cd /home/ubuntu/MyUnstructured/terraform

# Destroy all resources
terraform destroy

# Confirm with 'yes'
```

## Next Steps

1. ✅ Deploy infrastructure
2. ✅ Test API endpoints
3. ✅ Deploy frontend
4. ⬜ Add Stripe integration for payments
5. ⬜ Implement actual document processing with Unstructured.io
6. ⬜ Add monitoring & alerts
7. ⬜ Set up CI/CD pipeline
8. ⬜ Launch marketing campaign

## Support

- AWS Documentation: https://docs.aws.amazon.com
- Terraform AWS Provider: https://registry.terraform.io/providers/hashicorp/aws
- Issues: Check CloudWatch Logs

Good luck! 🚀
