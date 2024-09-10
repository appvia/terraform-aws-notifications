variable "sns_topic_name" {
  description = "The name of the SNS topic to create"
  type        = string
}

variable "opsgenie_endpoint" {
  description = "The opsgenie api endpoint url"
  type        = string
  default     = null
}
