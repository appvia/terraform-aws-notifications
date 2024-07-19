
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
  ## The slack channel to post to 
  slack_channel = local.enable_slack_secret ? try(jsondecode(data.aws_secretsmanager_secret_version.slack[0].secret_string)["channel"], var.slack.channel) : try(var.slack.channel, null)
  ## slack_username to use  
  slack_username = local.enable_slack_secret ? try(jsondecode(data.aws_secretsmanager_secret_version.slack[0].secret_string)["username"], var.slack.username) : try(var.slack.username, null)
  ## Indicates slack has all the configuration needed 
  enable_slack = local.enable_slack_config && local.slack_channel != null && local.slack_webhook_url != null

  ## Indicates if we are enabling teams notifications 
  enable_teams_config = var.teams != null ? true : false
  ## Indicates if we are looking up the teams secret 
  enable_teams_secret = local.enable_teams_config && try(var.teams.secret_name, null) != null ? true : false
  ## The webhook url for teams 
  teams_webhook_url = local.enable_teams_secret ? try(jsondecode(data.aws_secretsmanager_secret_version.teams[0].secret_string)["webhook_url"], var.teams.webhook_url) : try(var.teams.webhook_url, null)
  ## The teams channel to post to 
  teams_channel = local.enable_teams_secret ? try(jsondecode(data.aws_secretsmanager_secret_version.teams[0].secret_string)["channel"], var.teams.channel) : try(var.teams.channel, null)
  ## teams_username to use  
  teams_username = local.enable_teams_secret ? try(jsondecode(data.aws_secretsmanager_secret_version.teams[0].secret_string)["username"], var.teams.username) : try(var.teams.username, null)
  ## Indicates teams has all the configuration needed 
  enable_teams = local.enable_teams_config && local.teams_channel != null && local.teams_webhook_url != null


  channels_config = {
    "slack" = {
      channel            = local.slack_channel
      webhook_url        = local.slack_webhook_url
      username           = try(local.slack_username, null)
      lambda_name        = try(var.slack.lambda_name, null)
      lambda_description = try(var.slack.lambda_description, null)
    },
    "teams" = {
      channel            = local.teams_channel
      webhook_url        = local.teams_webhook_url
      username           = try(local.teams_username, null)
      lambda_name        = try(var.teams.lambda_name, null)
      lambda_description = try(var.teams.lambda_description, null)
    }
  }
}
