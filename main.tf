
## Provision a SQS queue if required
## Provision the SNS topic for the budgets
module "sns" {
  count   = var.create_sns_topic ? 1 : 0
  source  = "terraform-aws-modules/sns/aws"
  version = "6.2.1"

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

  accounts_id_to_name_parameter_arn      = var.accounts_id_to_name_parameter_arn
  aws_account_id                         = data.aws_caller_identity.current.account_id
  aws_partition                          = data.aws_partition.current.partition
  aws_region                             = data.aws_region.current.name
  cloudwatch_log_group_kms_key_id        = var.cloudwatch_log_group_kms_key_id
  cloudwatch_log_group_retention_in_days = var.cloudwatch_log_group_retention
  create_sns_topic                       = false
  delivery_channels                      = local.channels_config
  enable_slack                           = var.enable_slack
  enable_teams                           = var.enable_teams
  identity_center_role                   = var.identity_center_role
  identity_center_start_url              = var.identity_center_start_url
  powertools_service_name                = var.powertools_service_name
  recreate_missing_package               = false
  sns_topic_name                         = var.sns_topic_name
  tags                                   = var.tags
  trigger_on_package_timestamp           = true

  # Additional IAM Policies to be attached to notify lambda
  lambda_policy_config = {
    ssm = {
      enabled   = true
      effect    = "Allow"
      actions   = ["ssm:GetParameter", "ssm:GetParameters"]
      resources = [coalesce(var.accounts_id_to_name_parameter_arn, "*")]
    }
    layers = {
      enabled   = true
      effect    = "Allow"
      actions   = ["lambda:GetLayerVersion", "lambda:ListLayerVersions"]
      resources = ["*"]
    }
  }

  # Layers included by default are AWS Powertools v3 and AWS Parameter & Secrets Extension.

  # AWS Powertools ARNs

  # x86: https://docs.powertools.aws.dev/lambda/python/latest/#x86_65
  # ARM: https://docs.powertools.aws.dev/lambda/python/latest/#arm64_1

  # AWS Parameter & Secrets Extension ARNs

  # - https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html#ps-integration-lambda-extensions-add

  # Note: version number is denoted by the integer following final semi colon.
  # i.e arn:aws:lambda:eu-west-2:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-arm64:3

  # Alternatively you can provide an ARN directly by using create a new layer and pass in the ARN e.g.
  # lambda_layers = {
  #   custom_layer = {
  #     enabled     = true
  #     type        = "custom"
  #     arn         = "arn:aws:lambda:us-east-1:123456789012:layer:my-custom-layer:1"
  #     version     = "1.0.0"
  #     region      = "us-east-1"
  #   }

  lambda_layers_config = {
    powertools = {
      enabled = true
      type    = "managed"
      version = "3"
    }
    parameters_secrets = {
      enabled = true
      type    = "managed"
      version = "12"
    }
  }

  depends_on = [module.sns]
}
