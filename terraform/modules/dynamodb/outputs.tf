output "users_table_name" {
  value = aws_dynamodb_table.users.name
}

output "users_table_arn" {
  value = aws_dynamodb_table.users.arn
}

output "usage_table_name" {
  value = aws_dynamodb_table.api_usage.name
}

output "usage_table_arn" {
  value = aws_dynamodb_table.api_usage.arn
}

output "documents_table_name" {
  value = aws_dynamodb_table.documents.name
}

output "documents_table_arn" {
  value = aws_dynamodb_table.documents.arn
}
