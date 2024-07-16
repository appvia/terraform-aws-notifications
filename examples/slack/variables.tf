
variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default = {
    Environment = "dev"
  }
}

variable "sns_topic_name" {
  description = "The name of the SNS topic to create"
  type        = string
  default     = "my-topic"
}


variable "slack_webhook" {
  description = "The URL of the slack webhook"
  type = string
  default = null
}

variable "slack_channel" {
  description = "The name of the channel in slack associated with the webhook"
  type = string
  default = null
}
