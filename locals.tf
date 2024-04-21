
locals {
  ## The current account id 
  account_id = data.aws_caller_identity.current.account_id
  ## The current region 
  region = data.aws_region.current.name
  ## Indicates if we are enabling emails notifications 
  enable_email = var.email != null ? true : false

  ## Expected sns topic arn, assuming we are not creating the sns topic
  expected_sns_topic_arn = format("arn:aws:sns:%s::%s", local.region, local.account_id)
  ## Is the arn of the sns topic to use 
  sns_topic_arn = var.create_sns_topic ? module.notifications[0].topic_arn : format("arn:aws:sns:%s::%s", local.expected_sns_topic_arn)
  ## Is the SNS topic policy to use 
  sns_topic_policy = var.sns_topic_policy != null ? var.sns_topic_policy : data.aws_iam_policy_document.current.json

  ## Indicates if we are enabling slack notifications 
  enable_slack = var.slack != null ? true : false
  ## Indicates if we are looking up the slack secret 
  enable_slack_secret = local.enable_slack && try(var.slack.secret_name, null) != null ? true : false
  ## The webhook url for slack 
  slack_webhook_url = local.enable_slack_secret ? jsondecode(data.aws_secretsmanager_secret_version.slack[0].secret_string)["webhook_url"] : try(var.slack.webhook_url, null)
  ## The slack channel to post to 
  slack_channel = local.enable_slack_secret ? jsondecode(data.aws_secretsmanager_secret_version.slack[0].secret_string)["channel"] : try(var.slack.channel, null)
}
