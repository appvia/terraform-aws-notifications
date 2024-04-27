
## Provision a SQS queue if required 
## Provision the SNS topic for the budgets 
module "sns" {
  count   = var.create_sns_topic ? 1 : 0
  source  = "terraform-aws-modules/sns/aws"
  version = "v6.0.1"

  name                          = var.sns_topic_name
  source_topic_policy_documents = [local.sns_topic_policy]
  tags                          = var.tags
}

## Provision any email notifications if required 
resource "aws_sns_topic_subscription" "email" {
  for_each = local.enable_email ? toset(var.email.addresses) : toset([])

  topic_arn = local.sns_topic_arn
  protocol  = "email"
  endpoint  = each.value

  depends_on = [module.sns]
}

## Provision the sns topic subscriptions if required 
resource "aws_sns_topic_subscription" "subscribers" {
  for_each = var.subscribers

  endpoint               = each.value.endpoint
  endpoint_auto_confirms = each.value.endpoint_auto_confirms
  protocol               = each.value.protocol
  raw_message_delivery   = each.value.raw_message_delivery
  topic_arn              = local.sns_topic_arn

  depends_on = [module.sns]
}

#
## Provision the slack notification if enabled
#
# tfsec:ignore:aws-lambda-enable-tracing
# tfsec:ignore:aws-lambda-restrict-source-arn
module "slack" {
  count   = local.enable_slack ? 1 : 0
  source  = "terraform-aws-modules/notify-slack/aws"
  version = "6.3.0"

  create_sns_topic         = false
  lambda_description       = "Lambda function to send slack notifications, for sns topic ${var.sns_topic_name}"
  lambda_function_name     = var.slack.lambda_name
  lambda_function_tags     = var.tags
  recreate_missing_package = false
  slack_channel            = local.slack_channel
  slack_username           = local.slack_username
  slack_webhook_url        = local.slack_webhook_url
  sns_topic_name           = var.sns_topic_name
  tags                     = var.tags

  depends_on = [module.sns]
}
