
variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = null
}

variable "sns_topic_name" {
  description = "The name of the SNS topic to create"
  type        = string
}


variable "teams_webhook" {
  description = "The URL of the teams webhook"
  type        = string
}

variable "slack_webhook" {
  description = "The URL of the slack webhook"
  type        = string
}

variable "powertools_service_name" {
  description = "Sets service name used for tracing namespace, metrics dimension and structured logging for the AWS Powertool Lambda Layer"
  type        = string
  default     = "appvia-notifications-dev"
}

variable "accounts_id_to_name_parameter_arn" {
  description = "The ARN of your parameter containing the your account ID to name mapping. This ARN will be attached to lambda execution role as a resource, therefore a valid resource must exist. e.g 'arn:aws:ssm:eu-west-2:0123456778:parameter/myorg/configmaps/accounts_id_to_name_mapping' to enable the lambda retrieve values from ssm."
  type        = string
  default     = null

  validation {
    condition     = var.accounts_id_to_name_parameter_arn == null ? true : can(regex("^arn:[^:]+:ssm:[a-z0-9-]+:[0-9]{12}:parameter/.+$", var.accounts_id_to_name_parameter_arn))
    error_message = "The accounts_id_to_name_parameter_arn must be a valid SSM parameter ARN."
  }
}
