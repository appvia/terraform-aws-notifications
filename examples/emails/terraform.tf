variable "sns_topic_name" {
  description = "The name of the SNS topic to create"
  type        = string
}

variable "email_addresses" {
  description = "A list of target email addresses"
  type        = list(string)
}