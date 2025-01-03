
#trivy:ignore:avd-aws-0095
resource "aws_sns_topic" "this" {
  count = var.create_sns_topic ? 1 : 0

  kms_master_key_id = var.sns_topic_kms_key_id
  name              = var.sns_topic_name
  tags              = var.tags
}

resource "aws_sns_topic_subscription" "sns_notify_slack" {
  count = var.enable_slack && local.create_distribution["slack"] == true ? 1 : 0

  topic_arn           = local.sns_topic_arn
  protocol            = "lambda"
  endpoint            = module.lambda["slack"].lambda_function_arn
  filter_policy       = local.subscription_policies["slack"].filter
  filter_policy_scope = local.subscription_policies["slack"].scope
}

resource "aws_sns_topic_subscription" "sns_notify_teams" {
  count = var.enable_teams && local.create_distribution["teams"] == true ? 1 : 0

  topic_arn           = local.sns_topic_arn
  protocol            = "lambda"
  endpoint            = module.lambda["teams"].lambda_function_arn
  filter_policy       = local.subscription_policies["teams"].filter
  filter_policy_scope = local.subscription_policies["teams"].scope
}

# resource "local_file" "notify_account_names_dict_python" {
#   content  = local.accounts_id_to_name_python_dictonary
#   filename = "${path.module}/functions/src/account_id_name_mappings.py"
# }

#trivy:ignore:avd-aws-0067
module "lambda" {
  for_each = local.distributions
  source   = "terraform-aws-modules/lambda/aws"
  version  = "7.17.0"

  architectures                      = [var.architecture]
  attach_cloudwatch_logs_policy      = true
  attach_create_log_group_permission = true
  attach_network_policy              = false
  attach_policy_json                 = false
  create                             = true
  description                        = try(var.delivery_channels[each.value].lambda_description, "")
  ephemeral_storage_size             = var.lambda_function_ephemeral_storage_size
  function_name                      = try(var.delivery_channels[each.value].lambda_name, "notify_${each.value}")
  handler                            = "${local.lambda_handler[each.value]}.lambda_handler"
  hash_extra                         = each.value
  kms_key_arn                        = var.kms_key_arn
  publish                            = true
  recreate_missing_package           = var.recreate_missing_package
  reserved_concurrent_executions     = var.reserved_concurrent_executions
  runtime                            = var.python_runtime
  s3_bucket                          = var.lambda_function_s3_bucket
  store_on_s3                        = var.lambda_function_store_on_s3
  tags                               = var.tags
  timeout                            = 10
  trigger_on_package_timestamp       = var.trigger_on_package_timestamp

  ## Related to the IAM
  create_role               = true
  lambda_role               = var.lambda_role
  role_name                 = format("%s-%s", var.iam_role_name_prefix, var.delivery_channels[each.value].lambda_name)
  role_path                 = var.iam_role_path
  role_permissions_boundary = var.iam_role_boundary_policy_arn
  role_tags                 = var.tags

  ## Additional Policy Requirements
  attach_policy_statements = length(local.enabled_policies) > 0
  policy_statements = {
    for policy_name, policy in local.enabled_policies : policy_name => {
      effect    = policy.effect
      actions   = policy.actions
      resources = policy.resources
    }
  }

  ## Logging related
  use_existing_cloudwatch_log_group = false
  cloudwatch_logs_kms_key_id        = var.cloudwatch_log_group_kms_key_id
  cloudwatch_logs_retention_in_days = var.cloudwatch_log_group_retention_in_days
  cloudwatch_logs_tags              = var.tags

  ## Lambda function source code
  source_path = [
    {
      path             = "${path.module}/functions/src"
      pip_requirements = false
      prefix_in_zip    = ""
      patterns         = <<END
        msg_parser\.py
        notification_emblems\.py
        !.*msg_render_.*\.py
        !.*notify_.*\.py
        .*${each.value}\.py
      END
    }
  ]

  ## Lambda layers
  layers = local.enabled_layers

  ## Lambda environment variables
  environment_variables = merge(
    local.layer_env_vars,
    local.lambda_env_vars[each.value]
  )

  allowed_triggers = {
    AllowExecutionFromSNS = {
      principal  = "sns.amazonaws.com"
      source_arn = local.sns_topic_arn
    }
  }

  depends_on = [
    # local_file.notify_account_names_dict_python,
  ]
}
