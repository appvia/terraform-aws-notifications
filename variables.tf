
variable "create_sns_topic" {
  description = "Whether to create an SNS topic for notifications"
  type        = bool
  default     = false
}

variable "email" {
  description = "The configuration for Email notifications"
  type = object({
    addresses = optional(list(string))
    # The email addresses to send notifications to
  })
  default = null

  validation {
    condition = alltrue([
      for e in coalesce(var.email, { addresses = [] }).addresses : can(regex("^.+@.+$", e))
    ])
    error_message = "Invalid email address"
  }
}

variable "sns_topic_name" {
  description = "The name of the source sns topic where events are published"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9_-]{1,256}$", var.sns_topic_name))
    error_message = "Invalid SNS topic name"
  }
}

variable "allowed_aws_services" {
  description = "Optional, list of AWS services able to publish via the SNS topic (when creating topic) e.g cloudwatch.amazonaws.com"
  type        = list(string)
  default     = []

  validation {
    condition = alltrue([
      for s in var.allowed_aws_services : can(regex(".+.amazonaws.com$", s))
    ])
    error_message = "List must be a valid set of AWS services"
  }
}

variable "allowed_aws_principals" {
  description = "Optional, list of AWS accounts able to publish via the SNS topic (when creating topic) e.g 123456789012"
  type        = list(string)
  default     = []

  validation {
    condition = alltrue([
      for p in var.allowed_aws_principals : can(regex("^[0-9]{6,}$", p))
    ])
    error_message = "List must be a valid set of AWS account ids - only the ID not the iam"
  }
}

variable "sns_topic_policy" {
  description = "The policy to attach to the sns topic, else we default to account root"
  type        = string
  default     = null
}

variable "cloudwatch_log_group_retention" {
  description = "The retention period for the cloudwatch log group (for lambda function logs) in days"
  type        = string
  default     = "0"
}

variable "cloudwatch_log_group_kms_key_id" {
  description = "The KMS key id to use for encrypting the cloudwatch log group (default is none)"
  type        = string
  default     = null
}

variable "slack" {
  description = "The configuration for Slack notifications"
  type = object({
    lambda_name = optional(string, "slack-notify")
    # The name of the lambda function to create
    lambda_description = optional(string, "Lambda function to send slack notifications")
    # The description for the slack lambda
    secret_name = optional(string)
    # An optional secret name in secrets manager to use for the slack configuration
    webhook_url = optional(string)
    # The webhook url to post to
    filter_policy = optional(string)
    # An optional SNS subscription filter policy to apply
    filter_policy_scope = optional(string)
    # If filter policy provided this is the scope of that policy; either "MessageAttributes" (default) or "MessageBody"
  })
  default = null
}

variable "teams" {
  description = "The configuration for teams notifications"
  type = object({
    lambda_name = optional(string, "teams-notify")
    # The name of the lambda function to create
    lambda_description = optional(string, "Lambda function to send teams notifications")
    # The description for the teams lambda
    secret_name = optional(string)
    # An optional secret name in secrets manager to use for the slack configuration
    webhook_url = optional(string)
    # The webhook url to post to
    filter_policy = optional(string)
    # An optional SNS subscription filter policy to apply
    filter_policy_scope = optional(string)
    # If filter policy provided this is the scope of that policy; either "MessageAttributes" (default) or "MessageBody"
  })
  default = null
}

variable "subscribers" {
  description = "Optional list of custom subscribers to the SNS topic"
  type = map(object({
    protocol = string
    # The protocol to use. The possible values for this are: sqs, sms, lambda, application. (http or https are partially supported, see below).
    endpoint = string
    # The endpoint to send data to, the contents will vary with the protocol. (see below for more information)
    endpoint_auto_confirms = bool
    # Boolean indicating whether the end point is capable of auto confirming subscription e.g., PagerDuty (default is false)
    raw_message_delivery = bool
    # Boolean indicating whether or not to enable raw message delivery (the original message is directly passed, not wrapped in JSON with the original message in the message property) (default is false)
  }))
  default = {}
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
}

variable "enable_slack" {
  description = "To send to slack, set to true"
  type        = bool
  default     = false
}

variable "enable_teams" {
  description = "To send to teams, set to true"
  type        = bool
  default     = false
}


variable "identity_center_start_url" {
  description = "The start URL of your Identity Center instance"
  type        = string
  default     = null
}

variable "identity_center_role" {
  description = "The name of the role to use when redirecting through Identity Center"
  type        = string
  default     = null
}

variable "powertools_service_name" {
  description = "Sets service name used for tracing namespace, metrics dimension and structured logging for the AWS Powertools Lambda Layer"
  type        = string
  default     = "appvia-notifications"
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
