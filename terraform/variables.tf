variable "aws_region" {
  description = "AWS region where resources will be created."
  type        = string
}

variable "project_name" {
  description = "Project prefix used to name AWS resources."
  type        = string
}

variable "dynamodb_table_name" {
  description = "Existing DynamoDB table name for URL records."
  type        = string
}

variable "stats_table_name" {
  description = "Existing DynamoDB table name for daily URL statistics."
  type        = string
}

variable "api_gateway_id" {
  description = "Existing API Gateway HTTP API id where GET /{codigo} will be attached."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{10}$", var.api_gateway_id))
    error_message = "api_gateway_id must be only the 10-character HTTP API id. Do not use the full URL, account id, ARN, or yes/no values."
  }
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}
