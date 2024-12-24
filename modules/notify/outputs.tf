
output "sns_topic_arn" {
  description = "The ARN of the SNS topic from which messages will be sent to Slack"
  value       = local.sns_topic_arn
}

output "distributions" {
  description = "The list of slack/teams distributions that are managed"
  value       = local.distributions
}

output "notify_slack_lambda_function_arn" {
  description = "The ARN of the Lambda function"
  value       = try(module.lambda["slack"].lambda_function_arn, "")
}
output "notify_teams_lambda_function_arn" {
  description = "The ARN of the Lambda function"
  value       = try(module.lambda["teams"].lambda_function_arn, "")
}

output "notify_slack_slack_lambda_function_name" {
  description = "The name of the Lambda function"
  value       = try(module.lambda["slack"].lambda_function_name, "")
}
output "notify_teams_slack_lambda_function_name" {
  description = "The name of the Lambda function"
  value       = try(module.lambda["teams"].lambda_function_name, "")
}

output "notify_slack_lambda_function_version" {
  description = "Latest published version of your Lambda function"
  value       = try(module.lambda["slack"].lambda_function_version, "")
}
output "notify_teams_lambda_function_version" {
  description = "Latest published version of your Lambda function"
  value       = try(module.lambda["teams"].lambda_function_version, "")
}
