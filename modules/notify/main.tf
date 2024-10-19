#trivy:ignore:avd-aws-0059
#trivy:ignore:avd-aws-0057
data "aws_iam_policy_document" "lambda" {
  for_each = local.distributions

  dynamic "statement" {
    for_each = var.kms_key_arn != "" ? [1] : []

    content {
      sid       = "AllowKMSDecrypt"
      effect    = "Allow"
      actions   = ["kms:Decrypt"]
      resources = [var.kms_key_arn]
    }
  }
}

## Configure a filter policy for the slack subscription 
resource "aws_sns_topic_subscription" "sns_notify_slack" {
  count = var.enable_slack && local.create_distribution["slack"] == true ? 1 : 0

  topic_arn           = local.sns_topic_arn
  protocol            = "lambda"
  endpoint            = module.lambda["slack"].lambda_function_arn
  filter_policy       = local.subscription_policies["slack"].filter
  filter_policy_scope = local.subscription_policies["slack"].scope
}

## Configure a filter policy for the teams subscription
resource "aws_sns_topic_subscription" "sns_notify_teams" {
  count = var.enable_teams && local.create_distribution["teams"] == true ? 1 : 0

  topic_arn           = local.sns_topic_arn
  protocol            = "lambda"
  endpoint            = module.lambda["teams"].lambda_function_arn
  filter_policy       = local.subscription_policies["teams"].filter
  filter_policy_scope = local.subscription_policies["teams"].scope
}

## Render a python dictionary of account id to account name 
resource "local_file" "notify_account_names_dict_python" {
  content  = local.accounts_id_to_name_python_dictonary
  filename = "${path.module}/functions/src/accounts.py"
}

## Provision the lambda functions to handle the triggers from cloudwatch metrics
#trivy:ignore:avd-aws-0067
module "lambda" {
  for_each = local.distributions
  source   = "terraform-aws-modules/lambda/aws"
  version  = "7.10.0"

  create      = true
  hash_extra  = each.value
  kms_key_arn = var.kms_key_arn
  tags        = var.tags

  # Function related 
  architectures                  = [var.architecture]
  description                    = try(var.delivery_channels[each.value].lambda_description, "")
  environment_variables          = local.lambda_env_vars[each.value]
  ephemeral_storage_size         = var.lambda_ephemeral_storage_size
  function_name                  = try(var.delivery_channels[each.value].lambda_name, "notify_${each.value}")
  function_tags                  = var.tags
  handler                        = "${local.lambda_handler[each.value]}.lambda_handler"
  policy_json                    = try(data.aws_iam_policy_document.lambda[each.value].json, "")
  publish                        = true
  recreate_missing_package       = var.recreate_missing_package
  reserved_concurrent_executions = var.reserved_concurrent_executions
  layers                         = [local.lambda_layer]
  runtime                        = var.python_runtime
  timeout                        = 10

  ## Lamba IAM Role 
  create_role                   = true
  attach_async_event_policy     = false
  attach_cloudwatch_logs_policy = true
  attach_dead_letter_policy     = false
  attach_network_policy         = false
  attach_policy_json            = true
  attach_policy_jsons           = length(var.iam_policy_jsons) > 0 ? true : false
  attach_tracing_policy         = false
  number_of_policy_jsons        = length(var.iam_policy_jsons)
  policies                      = var.iam_policy_arns
  policy_jsons                  = var.iam_policy_jsons
  role_description              = format("Lambda role for %s notifications", var.delivery_channels[each.value].lambda_name)
  role_force_detach_policies    = true
  role_name                     = format("%s", var.delivery_channels[each.value].lambda_name)
  role_path                     = "/"
  role_permissions_boundary     = var.iam_role_boundary_policy_arn
  role_tags                     = var.tags

  ## Cloud Watch Log Group 
  use_existing_cloudwatch_log_group = false
  cloudwatch_logs_kms_key_id        = var.cloudwatch_log_group_kms_key_id
  cloudwatch_logs_log_group_class   = "STANDARD"
  cloudwatch_logs_retention_in_days = var.cloudwatch_log_group_retention_in_days
  cloudwatch_logs_tags              = var.tags

  source_path = [
    {
      path             = "${path.module}/functions/src"
      pip_requirements = false
      prefix_in_zip    = ""
      patterns         = <<END
        msg_parser\.py
        accounts\.py
        emblems\.py
        !.*msg_render_.*\.py
        !.*notify_.*\.py
        .*${each.value}\.py
      END
    }
  ]

  allowed_triggers = {
    AllowExecutionFromSNS = {
      principal  = "sns.amazonaws.com"
      source_arn = local.sns_topic_arn
    }
  }

  depends_on = [
    local_file.notify_account_names_dict_python,
  ]
}
