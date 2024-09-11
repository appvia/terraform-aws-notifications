output "sns_topic_arn" {
  description = "The ARN of the SNS topic"
  value       = local.sns_topic_arn
}

output "distributions" {
  description = "The list of slack/teams distributions that are managed"
  value       = try(module.notify.distributions, "")
}

output "channels_config" {
  description = "The configuration data for each distribution channel"
  value       = local.channels_config
}