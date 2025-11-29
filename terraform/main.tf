terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Bucket for Documents
module "s3" {
  source      = "./modules/s3"
  project_name = var.project_name
  environment = var.environment
}

# Cognito for Authentication
module "cognito" {
  source      = "./modules/cognito"
  project_name = var.project_name
  environment = var.environment
}

# DynamoDB Tables
module "dynamodb" {
  source      = "./modules/dynamodb"
  project_name = var.project_name
  environment = var.environment
}

# Lambda Functions
module "lambda" {
  source              = "./modules/lambda"
  project_name        = var.project_name
  environment         = var.environment
  bucket_name         = module.s3.bucket_name
  users_table_name    = module.dynamodb.users_table_name
  usage_table_name    = module.dynamodb.usage_table_name
  documents_table_name = module.dynamodb.documents_table_name
  user_pool_id        = module.cognito.user_pool_id
  user_pool_client_id = module.cognito.user_pool_client_id
}

# API Gateway
module "api_gateway" {
  source                    = "./modules/api_gateway"
  project_name              = var.project_name
  environment               = var.environment
  user_pool_arn             = module.cognito.user_pool_arn
  user_pool_client_id       = module.cognito.user_pool_client_id
  process_document_invoke_arn = module.lambda.process_document_invoke_arn
  process_document_function_name = module.lambda.process_document_function_name
  register_user_invoke_arn  = module.lambda.register_user_invoke_arn
  register_user_function_name = module.lambda.register_user_function_name
  get_credits_invoke_arn    = module.lambda.get_credits_invoke_arn
  get_credits_function_name = module.lambda.get_credits_function_name
}
