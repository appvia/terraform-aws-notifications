
## Provision a SQS queue if required 
## Provision the SNS topic for the budgets 
module "sns" {
  count   = var.create_sns_topic ? 1 : 0
  source  = "terraform-aws-modules/sns/aws"
  version = "6.1.1"

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

  confirmation_timeout_in_minutes = 1
  endpoint                        = each.value.endpoint
  endpoint_auto_confirms          = each.value.endpoint_auto_confirms
  protocol                        = each.value.protocol
  raw_message_delivery            = each.value.raw_message_delivery
  topic_arn                       = local.sns_topic_arn

  depends_on = [module.sns]
}

#
## Provision the slack/teams notification if enabled
#
# tfsec:ignore:aws-lambda-enable-tracing
# tfsec:ignore:aws-lambda-restrict-source-arn
module "notify" {
  source = "./modules/notify"

  accounts_id_to_name                    = var.accounts_id_to_name
  cloudwatch_log_group_kms_key_id        = var.cloudwatch_log_group_kms_key_id
  cloudwatch_log_group_retention_in_days = var.cloudwatch_log_group_retention
  cloudwatch_log_group_tags              = var.tags
  create_sns_topic                       = false
  delivery_channels                      = local.channels_config
  enable_slack                           = var.enable_slack
  enable_teams                           = var.enable_teams
  iam_role_tags                          = var.tags
  identity_center_role                   = var.identity_center_role
  identity_center_start_url              = var.identity_center_start_url
  lambda_function_tags                   = var.tags
  post_icons_url                         = var.post_icons_url
  recreate_missing_package               = false
  sns_topic_name                         = var.sns_topic_name
  sns_topic_tags                         = var.tags
  tags                                   = var.tags

  depends_on = [module.sns]
}
