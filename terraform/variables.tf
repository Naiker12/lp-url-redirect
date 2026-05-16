variable "aws_region" {
  description = "AWS region where resources will be created."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project prefix used to name AWS resources."
  type        = string
  default     = "lp-url-redirect"
}

variable "dynamodb_table_name" {
  description = "Existing DynamoDB table name for URL records."
  type        = string
  default     = "urls"
}

variable "api_gateway_id" {
  description = "Existing API Gateway HTTP API id where GET /{codigo} will be attached."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{10}$", var.api_gateway_id))
    error_message = "api_gateway_id must be only the HTTP API id, for example fqltkzf336. Do not use the full URL, account id, ARN, or yes/no values."
  }
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}
