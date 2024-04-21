
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
