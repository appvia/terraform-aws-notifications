
variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = null
}

variable "sns_topic_name" {
  description = "The name of the SNS topic to create"
  type        = string
}


variable "primary_teams_webhook" {
  description = "The default URL of the teams webhook"
  type        = string
}

variable "primary_slack_webhook" {
  description = "The default URL of the slack webhook"
  type        = string
}

variable "security_hub_teams_webhook" {
  description = "The URL of the teams webhook to post Security Hub only events"
  type        = string
}

variable "security_hub_slack_webhook" {
  description = "The URL of the slack webhook to post Security Hub only events"
  type        = string
}
