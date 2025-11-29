# 🚀 DocuAI - Unstructured to Structured Data SaaS

Transform unstructured documents (PDFs, Word, HTML) into AI-ready structured data using AWS serverless architecture.

## 🏗️ Architecture

**AWS Services:**
- **Cognito** - User authentication & JWT tokens
- **DynamoDB** - User credits, API usage tracking
- **Lambda** - Serverless document processing
- **API Gateway** - RESTful API with JWT authorization
- **S3** - Document storage
- **Terraform** - Infrastructure as Code

## ⚡ Quick Start

### Option 1: One-Command Deployment

```bash
cd terraform
./deploy.sh
```

This will:
1. Install Terraform (if needed)
2. Package Lambda functions
3. Deploy all AWS infrastructure
4. Output API endpoint and Cognito details

### Option 2: Manual Steps

```bash
# 1. Configure AWS
aws configure

# 2. Deploy infrastructure
cd terraform
terraform init
./package_lambdas.sh
terraform apply

# 3. Get outputs
terraform output

# 4. Configure frontend
cd ../landing-page
cp .env.local.template .env.local
# Edit .env.local with Terraform outputs

# 5. Run frontend
npm install
npm run dev
```

## 📊 What Gets Deployed

| Resource | Purpose | Cost |
|----------|---------|------|
| Cognito User Pool | Authentication | Free (50K MAU) |
| DynamoDB (3 tables) | Users, Usage, Documents | Free (25GB) |
| Lambda (3 functions) | API logic | Free (1M requests) |
| API Gateway | REST API | Free (1M requests) |
| S3 Bucket | Document storage | $0.023/GB |

**Total Cost:** ~$0-5/month for first 1000 users

## 🔑 API Endpoints

### POST /v1/register
Register new user with 100 free credits
```bash
curl -X POST $API_ENDPOINT/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'
```

### POST /v1/process
Process document (requires JWT token)
```bash
curl -X POST $API_ENDPOINT/v1/process \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file": "base64_encoded_file",
    "filename": "document.pdf"
  }'
```

### GET /v1/credits
Get user credits and info
```bash
curl $API_ENDPOINT/v1/credits \
  -H "Authorization: Bearer $JWT_TOKEN"
```

## 🗂️ Project Structure

```
MyUnstructured/
├── terraform/                    # Infrastructure as Code
│   ├── main.tf                  # Main Terraform config
│   ├── variables.tf             # Variables
│   ├── outputs.tf               # Outputs
│   ├── deploy.sh                # Deployment script
│   ├── package_lambdas.sh       # Lambda packaging
│   ├── modules/
│   │   ├── cognito/            # Cognito user pool
│   │   ├── dynamodb/           # DynamoDB tables
│   │   ├── lambda/             # Lambda functions
│   │   ├── api_gateway/        # API Gateway
│   │   └── s3/                 # S3 bucket
│   └── lambda_functions/
│       ├── register_user.py    # User registration
│       ├── process_document.py # Document processing
│       └── get_credits.py      # Get user credits
├── landing-page/                # Next.js frontend
│   ├── app/
│   │   └── page.tsx            # Landing page
│   ├── lib/
│   │   ├── aws-config.ts       # AWS configuration
│   │   ├── api-client.ts       # API client
│   │   └── use-auth.ts         # Auth hook
│   └── .env.local.template     # Environment template
└── DEPLOYMENT_GUIDE.md         # Detailed deployment guide
```

## 🧪 Testing

### 1. Test Infrastructure
```bash
cd terraform
terraform output
```

### 2. Test API
```bash
# Get API endpoint
API_ENDPOINT=$(cd terraform && terraform output -raw api_endpoint)

# Register user
curl -X POST $API_ENDPOINT/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!","name":"Test"}'
```

### 3. Test Frontend
```bash
cd landing-page
npm run dev
# Open http://localhost:3000
```

## 🚀 Deployment to Production

### Deploy Infrastructure
```bash
cd terraform
./deploy.sh
```

### Deploy Frontend to Vercel
```bash
cd landing-page
npm i -g vercel
vercel --prod
```

Add environment variables in Vercel dashboard:
- `NEXT_PUBLIC_AWS_REGION`
- `NEXT_PUBLIC_USER_POOL_ID`
- `NEXT_PUBLIC_USER_POOL_CLIENT_ID`
- `NEXT_PUBLIC_API_ENDPOINT`

## 📈 Monitoring

```bash
# View Lambda logs
aws logs tail /aws/lambda/docuai-prod-process-document --follow

# Check DynamoDB
aws dynamodb scan --table-name docuai-prod-users --max-items 5

# Monitor API Gateway
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=docuai-prod-api \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## 🔧 Customization

### Add More Credits
```bash
aws dynamodb update-item \
  --table-name docuai-prod-users \
  --key '{"user_id": {"S": "USER_ID"}}' \
  --update-expression "SET credits = :val" \
  --expression-attribute-values '{":val": {"N": "1000"}}'
```

### Update Lambda Code
```bash
cd terraform
# Edit lambda_functions/*.py
./package_lambdas.sh
terraform apply
```

### Change Region
```bash
cd terraform
terraform apply -var="aws_region=eu-west-1"
```

## 🗑️ Cleanup

```bash
cd terraform
terraform destroy
```

## 📚 Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [AWS Cognito](https://docs.aws.amazon.com/cognito/)

## 💡 Next Steps

1. ✅ Deploy infrastructure with Terraform
2. ✅ Test API endpoints
3. ✅ Deploy frontend
4. ⬜ Add Stripe for payments
5. ⬜ Implement Unstructured.io processing
6. ⬜ Add monitoring & alerts
7. ⬜ Set up CI/CD
8. ⬜ Launch!

## 🆘 Troubleshooting

**Terraform errors:**
```bash
terraform init -upgrade
terraform plan
```

**Lambda errors:**
```bash
aws logs tail /aws/lambda/FUNCTION_NAME --follow
```

**Cognito issues:**
```bash
aws cognito-idp list-users --user-pool-id YOUR_POOL_ID
```

## 📞 Support

- AWS Documentation: https://docs.aws.amazon.com
- Terraform Registry: https://registry.terraform.io
- Issues: Check CloudWatch Logs

---

**Built with ❤️ using AWS Serverless**
