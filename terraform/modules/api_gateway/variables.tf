variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "user_pool_arn" {
  type = string
}

variable "user_pool_client_id" {
  type = string
}

variable "process_document_invoke_arn" {
  type = string
}

variable "process_document_function_name" {
  type = string
}

variable "register_user_invoke_arn" {
  type = string
}

variable "register_user_function_name" {
  type = string
}

variable "get_credits_invoke_arn" {
  type = string
}

variable "get_credits_function_name" {
  type = string
}
