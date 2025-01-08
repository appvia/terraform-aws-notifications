
locals {
  ## The current account id
  account_id = data.aws_caller_identity.current.account_id
  ## The current region
  region = data.aws_region.current.name
  ## Indicates if we are enabling emails notifications
  enable_email = var.email != null ? true : false

  ## Expected sns topic arn, assuming we are not creating the sns topic
  expected_sns_topic_arn = format("arn:aws:sns:%s:%s:%s", local.region, local.account_id, var.sns_topic_name)
  ## Is the arn of the sns topic to use
  sns_topic_arn = var.create_sns_topic ? module.sns[0].topic_arn : local.expected_sns_topic_arn
  ## Is the SNS topic policy to use
  sns_topic_policy = var.sns_topic_policy != null ? var.sns_topic_policy : data.aws_iam_policy_document.current.json

  ## Indicates if we are enabling slack notifications
  enable_slack_config = var.slack != null ? true : false
  ## Indicates if we are looking up the slack secret
  enable_slack_secret = local.enable_slack_config && try(var.slack.secret_name, null) != null ? true : false
  ## The webhook url for slack
  slack_webhook_url = local.enable_slack_secret ? try(jsondecode(data.aws_secretsmanager_secret_version.slack[0].secret_string)["webhook_url"], var.slack.webhook_url) : try(var.slack.webhook_url, null)

  ## Indicates if we are enabling teams notifications
  enable_teams_config = var.teams != null ? true : false
  ## Indicates if we are looking up the teams secret
  enable_teams_secret = local.enable_teams_config && try(var.teams.secret_name, null) != null ? true : false
  ## The webhook url for teams
  teams_webhook_url = local.enable_teams_secret ? try(jsondecode(data.aws_secretsmanager_secret_version.teams[0].secret_string)["webhook_url"], var.teams.webhook_url) : try(var.teams.webhook_url, null)

  channels_config = {
    "slack" = var.slack != null ? {
      webhook_url         = local.slack_webhook_url
      lambda_name         = try(var.slack.lambda_name, "slack-notify")
      lambda_description  = try(var.slack.lambda_description, "Sends posts to slack")
      filter_policy       = try(var.slack.filter_policy, null)
      filter_policy_scope = try(var.slack.filter_policy_scope, null)
    } : null,
    "teams" = var.teams != null ? {
      webhook_url         = local.teams_webhook_url
      lambda_name         = try(var.teams.lambda_name, "teams-notify")
      lambda_description  = try(var.teams.lambda_description, "Sends posts to teams")
      filter_policy       = try(var.teams.filter_policy, null)
      filter_policy_scope = try(var.teams.filter_policy_scope, null)
    } : null,
  }
}
