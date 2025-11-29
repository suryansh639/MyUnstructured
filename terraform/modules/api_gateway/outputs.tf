output "api_endpoint" {
  value = "${aws_apigatewayv2_api.main.api_endpoint}/${var.environment}"
}

output "api_id" {
  value = aws_apigatewayv2_api.main.id
}
