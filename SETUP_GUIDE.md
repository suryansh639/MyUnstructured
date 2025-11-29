# 🚀 Complete Setup Guide - DocuAI SaaS Platform

## Step 1: Install Node.js (for Landing Page)

```bash
# Fix apt dependencies first
sudo apt --fix-broken install

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

## Step 2: Setup Landing Page

```bash
cd /home/ubuntu/MyUnstructured/landing-page

# Install dependencies
npm install

# Run development server
npm run dev
```

**Landing page will be available at: http://localhost:3000**

## Step 3: Setup Python API Backend

```bash
cd /home/ubuntu/MyUnstructured

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install API dependencies
pip install -r requirements_api.txt

# Run FastAPI server
uvicorn api_service:app --reload --host 0.0.0.0 --port 8000
```

**API will be available at: http://localhost:8000**
**API docs at: http://localhost:8000/docs**

## Step 4: Setup Streamlit App (Document Processing UI)

```bash
# In same virtual environment
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py --server.port 8501
```

**Streamlit app at: http://localhost:8501**

## Step 5: Setup AWS Infrastructure

### 5.1 Create DynamoDB Table for Usage Tracking

```bash
aws dynamodb create-table \
  --table-name api-usage \
  --attribute-definitions \
    AttributeName=api_key,AttributeType=S \
    AttributeName=user_id,AttributeType=S \
  --key-schema \
    AttributeName=api_key,KeyType=HASH \
  --global-secondary-indexes \
    IndexName=UserIdIndex,KeySchema=[{AttributeName=user_id,KeyType=HASH}],Projection={ProjectionType=ALL} \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 5.2 Create S3 Bucket for Document Storage

```bash
aws s3 mb s3://docuai-documents-$(date +%s) --region us-east-1
```

### 5.3 Deploy Full Infrastructure (Optional)

```bash
aws cloudformation create-stack \
  --stack-name docuai-infrastructure \
  --template-body file://infrastructure.yaml \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

## Step 6: Setup Stripe for Payments

### 6.1 Create Stripe Account
1. Go to https://dashboard.stripe.com/register
2. Complete registration
3. Get your API keys from https://dashboard.stripe.com/apikeys

### 6.2 Create Products in Stripe

```bash
# Set your Stripe secret key
export STRIPE_SECRET_KEY="sk_test_..."

# Create products using Stripe CLI or dashboard
stripe products create --name="Starter Plan" --description="5K docs/month"
stripe prices create --product=prod_xxx --unit-amount=2900 --currency=usd --recurring[interval]=month
```

### 6.3 Set Environment Variables

```bash
# Create .env file
cat > .env << EOF
STRIPE_SECRET_KEY=sk_test_your_key_here
BUCKET_NAME=docuai-documents-xxxxx
USAGE_TABLE=api-usage
AWS_REGION=us-east-1
EOF
```

## Step 7: Test the Complete Flow

### 7.1 Create Test API Key

```bash
# Add test user to DynamoDB
aws dynamodb put-item \
  --table-name api-usage \
  --item '{
    "api_key": {"S": "test_key_123"},
    "user_id": {"S": "user_001"},
    "plan": {"S": "free"},
    "limit": {"N": "100"},
    "usage": {"N": "0"}
  }'
```

### 7.2 Test API with curl

```bash
# Test document processing
curl -X POST "http://localhost:8000/v1/process" \
  -H "X-API-Key: test_key_123" \
  -F "file=@sample.pdf" \
  -F 'request={"output_format":"json"}'

# Check usage
curl "http://localhost:8000/v1/usage" \
  -H "X-API-Key: test_key_123"
```

## Step 8: Deploy to Production

### Option A: Deploy to AWS Lambda (Recommended)

```bash
# Install deployment tools
pip install mangum

# Package Lambda function
cd /home/ubuntu/MyUnstructured
zip -r lambda.zip api_service.py billing.py requirements_api.txt

# Create Lambda function
aws lambda create-function \
  --function-name docuai-api \
  --runtime python3.11 \
  --handler api_service.handler \
  --zip-file fileb://lambda.zip \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --timeout 300 \
  --memory-size 3008
```

### Option B: Deploy to EC2/ECS

```bash
# Use the existing deploy.sh script
chmod +x deploy.sh
./deploy.sh
```

### Deploy Landing Page to Vercel

```bash
cd landing-page

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## Step 9: Monitor and Scale

### Setup CloudWatch Alarms

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name docuai-high-usage \
  --alarm-description "Alert when API usage is high" \
  --metric-name Invocations \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold
```

## Quick Start Commands (All in One)

```bash
# Terminal 1: Landing Page
cd /home/ubuntu/MyUnstructured/landing-page && npm install && npm run dev

# Terminal 2: API Backend
cd /home/ubuntu/MyUnstructured && source venv/bin/activate && uvicorn api_service:app --reload

# Terminal 3: Streamlit App
cd /home/ubuntu/MyUnstructured && source venv/bin/activate && streamlit run app.py
```

## Troubleshooting

### Node.js Installation Issues
```bash
sudo apt --fix-broken install
sudo apt-get update
```

### Python Dependencies Issues
```bash
pip install --upgrade pip
pip install -r requirements_api.txt --no-cache-dir
```

### AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Key, and region
```

## Next Steps

1. ✅ Test locally (all 3 services running)
2. ✅ Create Stripe products
3. ✅ Deploy to AWS
4. ✅ Point domain to services
5. ✅ Launch marketing campaign
6. ✅ Get first 10 customers

## Support

- API Docs: http://localhost:8000/docs
- Landing Page: http://localhost:3000
- Streamlit UI: http://localhost:8501

Good luck with your SaaS! 🚀
