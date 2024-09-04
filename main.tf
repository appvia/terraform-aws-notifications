
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
module "notify" {
  source = "./modules/notify"

  cloudwatch_log_group_kms_key_id        = var.cloudwatch_log_group_kms_key_id
  cloudwatch_log_group_retention_in_days = var.cloudwatch_log_group_retention
  cloudwatch_log_group_tags              = var.tags
  create_sns_topic                       = false
  iam_role_tags                          = var.tags
  lambda_function_tags                   = var.tags
  recreate_missing_package               = false
  send_to_slack                          = var.send_to_slack
  send_to_teams                          = var.send_to_teams
  delivery_channels                      = local.channels_config
  sns_topic_name                         = var.sns_topic_name
  sns_topic_tags                         = var.tags
  tags                                   = var.tags

  accounts_id_to_name                    = var.accounts_id_to_name
  post_icons_url                         = var.post_icons_url

  depends_on = [module.sns]
}
