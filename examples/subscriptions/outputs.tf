
output "sns_topic_arn" {
  description = "The ARN of the SNS topic"
  value       = module.primary_notifications.sns_topic_arn
}
