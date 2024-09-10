variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = null
}

variable "sns_topic_name" {
  description = "The name of the SNS topic to create"
  type        = string
}

variable "slack_webhook" {
  description = "The URL of the slack webhook"
  type        = string
}
