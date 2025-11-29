output "process_document_invoke_arn" {
  value = aws_lambda_function.process_document.invoke_arn
}

output "process_document_function_name" {
  value = aws_lambda_function.process_document.function_name
}

output "register_user_invoke_arn" {
  value = aws_lambda_function.register_user.invoke_arn
}

output "register_user_function_name" {
  value = aws_lambda_function.register_user.function_name
}

output "get_credits_invoke_arn" {
  value = aws_lambda_function.get_credits.invoke_arn
}

output "get_credits_function_name" {
  value = aws_lambda_function.get_credits.function_name
}
