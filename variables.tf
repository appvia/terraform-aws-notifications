
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
}

variable "sns_topic_name" {
  description = "The name of the source sns topic where events are published"
  type        = string
}

variable "allowed_aws_services" {
  description = "Optional, list of AWS services able to publish via the SNS topic (when creating topic) e.g cloudwatch.amazonaws.com"
  type        = list(string)
  default     = []
}

variable "allowed_aws_principals" {
  description = "Optional, list of AWS accounts able to publish via the SNS topic (when creating topic) e.g 123456789012"
  type        = list(string)
  default     = []
}

variable "sns_topic_policy" {
  description = "The policy to attach to the sns topic, else we default to account root"
  type        = string
  default     = null
}

variable "cloudwatch_log_group_retention" {
  description = "The retention period for the cloudwatch log group (for lambda function logs) in days"
  type        = string
  default     = "3"
}

variable "cloudwatch_log_group_kms_key_id" {
  description = "The KMS key id to use for encrypting the cloudwatch log group (default is none)"
  type        = string
  default     = null
}

variable "slack" {
  description = "The configuration for Slack notifications"
  type = object({
    channel = optional(string)
    # The channel to post to 
    lambda_name = optional(string, "slack-notify")
    # The name of the lambda function to create 
    secret_name = optional(string)
    # An optional secret name in secrets manager to use for the slack configuration 
    username = optional(string, ":aws: Notification")
    # The username to post as 
    webhook_url = optional(string)
    # The webhook url to post to
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

