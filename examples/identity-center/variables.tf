variable "sns_topic_name" {
  description = "The name of the SNS topic to create"
  type        = string
}

variable "slack_webhook" {
  description = "The URL of the slack webhook"
  type        = string
}

variable "identity_center_start_url" {
  description = "The start URL of your Identity Center instance"
  type        = string
}

variable "identity_center_role" {
  description = "The name of the role to use when redirecting through Identity Center"
  type        = string
}
