# ⚡ Quick Start Guide - DocuAI SaaS

## 🎯 What You Have

A complete AWS-powered SaaS platform that converts unstructured documents to structured AI-ready data.

**Tech Stack:**
- ✅ AWS Cognito (Authentication)
- ✅ DynamoDB (User data & credits)
- ✅ Lambda (Document processing)
- ✅ API Gateway (REST API)
- ✅ S3 (Document storage)
- ✅ Next.js (Frontend)
- ✅ Terraform (Infrastructure as Code)

## 🚀 Deploy in 3 Steps

### Step 1: Configure AWS (One-time)

```bash
# Install AWS CLI (if not installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Region: us-east-1
# Output format: json
```

### Step 2: Deploy Everything

```bash
cd /home/ubuntu/MyUnstructured

# Make script executable
chmod +x deploy_all.sh

# Deploy (takes 5-10 minutes)
./deploy_all.sh
```

This single command will:
1. ✅ Install Terraform
2. ✅ Package Lambda functions
3. ✅ Deploy all AWS resources
4. ✅ Configure frontend
5. ✅ Test API
6. ✅ Show you all endpoints

### Step 3: Run Frontend

```bash
cd landing-page
npm install
npm run dev
```

Open http://localhost:3000 🎉

## 📋 What Gets Created

### AWS Resources:
- **Cognito User Pool** - For user authentication
- **3 DynamoDB Tables** - Users, API usage, Documents
- **3 Lambda Functions** - Register, Process, Get Credits
- **API Gateway** - REST API with JWT auth
- **S3 Bucket** - Document storage

### API Endpoints:
- `POST /v1/register` - Register new user (100 free credits)
- `POST /v1/process` - Process document (requires auth)
- `GET /v1/credits` - Get user credits (requires auth)

## 🧪 Test Your API

After deployment, you'll get an API endpoint. Test it:

```bash
# Save your API endpoint
API_ENDPOINT="https://xxxxx.execute-api.us-east-1.amazonaws.com/prod"

# Register a user
curl -X POST $API_ENDPOINT/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'

# Response:
# {
#   "message": "User registered successfully",
#   "user_id": "...",
#   "email": "user@example.com",
#   "credits": 100
# }
```

## 🌐 Deploy Frontend to Production

```bash
cd landing-page

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Add environment variables in Vercel dashboard
# (They're already in .env.local)
```

## 💰 Pricing Model

**Free Tier:**
- 100 documents/month
- All features included

**Paid Plans (Future):**
- Starter: $29/mo - 5K docs
- Pro: $99/mo - 50K docs
- Enterprise: $499/mo - 1M docs

## 📊 Monitor Your Application

```bash
# View Lambda logs
aws logs tail /aws/lambda/docuai-prod-process-document --follow

# Check users in DynamoDB
aws dynamodb scan --table-name docuai-prod-users --max-items 5

# Get API metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=docuai-prod-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum
```

## 🔧 Common Tasks

### Update Lambda Code
```bash
cd terraform
# Edit lambda_functions/*.py
./package_lambdas.sh
terraform apply
```

### Add Credits to User
```bash
aws dynamodb update-item \
  --table-name docuai-prod-users \
  --key '{"user_id": {"S": "USER_ID_HERE"}}' \
  --update-expression "SET credits = :val" \
  --expression-attribute-values '{":val": {"N": "1000"}}'
```

### View All Resources
```bash
cd terraform
terraform show
```

## 🗑️ Delete Everything

```bash
cd terraform
terraform destroy
# Type 'yes' to confirm
```

## 📚 Full Documentation

- **DEPLOYMENT_GUIDE.md** - Detailed deployment steps
- **README.md** - Complete project overview
- **README_BUSINESS.md** - Business strategy & monetization

## 🆘 Troubleshooting

### "AWS credentials not configured"
```bash
aws configure
# Enter your credentials
```

### "Terraform not found"
```bash
# The deploy script will install it automatically
# Or install manually:
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

### "Lambda function failed"
```bash
# Check logs
aws logs tail /aws/lambda/docuai-prod-process-document --since 1h
```

## 🎉 You're Ready!

Your complete SaaS platform is deployed and ready to use. Start building your business!

**Estimated Setup Time:** 15 minutes
**Monthly Cost (Free Tier):** $0
**Monthly Cost (1000 users):** ~$5-10

Good luck! 🚀
