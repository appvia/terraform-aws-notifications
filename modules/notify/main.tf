locals {
  sns_topic_arn = try(
    aws_sns_topic.this[0].arn,
    "arn:${data.aws_partition.current.id}:sns:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${var.sns_topic_name}",
    ""
  )

  sns_feedback_role = local.create_sns_feedback_role ? aws_iam_role.sns_feedback_role[0].arn : var.sns_topic_lambda_feedback_role_arn

  lambda_handler = {
    "slack" = try(split(".", basename(var.lambda_source_path))[0], "notify_slack"),
    "teams" = try(split(".", basename(var.lambda_source_path))[0], "notify_teams")
  }

  lambda_env_vars = {
    "slack" = {
      SLACK_WEBHOOK_URL    = try(var.delivery_channels["slack"].webhook_url, "https://null")
      IDENTITY_CENTER_URL  = try(var.identity_center_start_url, "")
      IDENTITY_CENTER_ROLE = try(var.identity_center_role, "")
    },
    "teams" = {
      TEAMS_WEBHOOK_URL    = try(var.delivery_channels["teams"].webhook_url, "https://null")
      IDENTITY_CENTER_URL  = try(var.identity_center_start_url, "")
      IDENTITY_CENTER_ROLE = try(var.identity_center_role, "")
    }
  }

  subscription_policies = {
    "slack" = {
      filter = try(var.delivery_channels["slack"].filter_policy, null)
      scope  = try(var.delivery_channels["slack"].filter_policy_scope, null)
    },
    "teams" = {
      filter = try(var.delivery_channels["teams"].filter_policy, null)
      scope  = try(var.delivery_channels["teams"].filter_policy_scope, null)
    }
  }

  ## We need to ensure the account names are ordered
  account_by_ids = [
    for name in sort(keys(var.accounts_id_to_name)) : {
      id   = name
      name = var.accounts_id_to_name[name]
    }
  ]

  accounts_id_to_name_python_dictonary = templatefile(
    "${path.module}/mapAccountIdToName-python-dict.tftpl",
    {
      accounts_id_to_name = local.account_by_ids
    }
  )
  notification_emblems_python = templatefile(
    "${path.module}/notification-emblems-python.tftpl",
    {
      error-icon-url   = var.post_icons_url.error_url
      warning-icon-url = var.post_icons_url.warning_url
    }
  )

  # the enable_[slack|teams] variable controls the subscription between SNS and lambda only; it is
  #  feasible that we want to keep the infrastructure (lambda, lambda role, log group et al) while suspending
  #  the posts.
  # but we only want to create the infrastructure if details of slack or team have been defined
  create_distribution = {
    "slack" = var.delivery_channels["slack"] != null ? true : false,
    "teams" = var.delivery_channels["teams"] != null ? true : false,
  }

  distributions = toset([for x in ["slack", "teams"] : x if local.create_distribution[x] == true])
}

#trivy:ignore:avd-aws-0095
resource "aws_sns_topic" "this" {
  count = var.create_sns_topic ? 1 : 0

  kms_master_key_id                   = var.sns_topic_kms_key_id
  lambda_failure_feedback_role_arn    = var.enable_sns_topic_delivery_status_logs ? local.sns_feedback_role : null
  lambda_success_feedback_role_arn    = var.enable_sns_topic_delivery_status_logs ? local.sns_feedback_role : null
  lambda_success_feedback_sample_rate = var.enable_sns_topic_delivery_status_logs ? var.sns_topic_lambda_feedback_sample_rate : null
  name                                = var.sns_topic_name
  tags                                = var.tags
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

resource "local_file" "notify_account_names_dict_python" {
  content  = local.accounts_id_to_name_python_dictonary
  filename = "${path.module}/functions/src/account_id_name_mappings.py"
}

resource "local_file" "notification_emblems_python" {
  content  = local.notification_emblems_python
  filename = "${path.module}/functions/src/notification_emblems.py"
}

#trivy:ignore:avd-aws-0067
module "lambda" {
  for_each = local.distributions

  source  = "terraform-aws-modules/lambda/aws"
  version = "7.16.0"

  architectures                      = [var.architecture]
  attach_cloudwatch_logs_policy      = true
  attach_create_log_group_permission = true
  attach_dead_letter_policy          = var.lambda_attach_dead_letter_policy
  attach_network_policy              = false
  attach_policy_json                 = false
  create                             = true
  create_role                        = var.lambda_role == ""
  dead_letter_target_arn             = var.lambda_dead_letter_target_arn
  description                        = try(var.delivery_channels[each.value].lambda_description, "")
  ephemeral_storage_size             = var.lambda_function_ephemeral_storage_size
  function_name                      = try(var.delivery_channels[each.value].lambda_name, "notify_${each.value}")
  handler                            = "${local.lambda_handler[each.value]}.lambda_handler"
  hash_extra                         = each.value
  kms_key_arn                        = var.kms_key_arn
  lambda_role                        = var.lambda_role
  publish                            = true
  recreate_missing_package           = var.recreate_missing_package
  reserved_concurrent_executions     = var.reserved_concurrent_executions
  role_name                          = "${var.iam_role_name_prefix}-${var.delivery_channels[each.value].lambda_name}"
  role_path                          = var.iam_role_path
  role_permissions_boundary          = var.iam_role_boundary_policy_arn
  role_tags                          = var.tags
  runtime                            = var.python_runtime
  s3_bucket                          = var.lambda_function_s3_bucket
  store_on_s3                        = var.lambda_function_store_on_s3
  tags                               = var.tags
  timeout                            = 10
  trigger_on_package_timestamp       = var.trigger_on_package_timestamp

  ## Logging related
  use_existing_cloudwatch_log_group = false
  cloudwatch_logs_kms_key_id        = var.cloudwatch_log_group_kms_key_id
  cloudwatch_logs_retention_in_days = var.cloudwatch_log_group_retention_in_days
  cloudwatch_logs_tags              = var.tags

  # Bug in this module when creating source bundles on updated code change:
  # `Error: Provider produced inconsistent final plan`
  # tried creating separate bundles; but still the error occurs
  # create_package                 = false
  # local_existing_package         = "${path.root}/builds/${each.value}_lambda_src.zip"

  # very bizarre behaviour on patterns filter - to only include the slack/teams specific code
  #  first have to exclude all variations on implementation and then include on the specific vendor implementations
  source_path = [
    {
      path             = "${path.module}/functions/src"
      pip_requirements = false
      prefix_in_zip    = ""
      patterns         = <<END
        msg_parser\.py
        account_id_name_mappings\.py
        notification_emblems\.py
        !.*msg_render_.*\.py
        !.*notify_.*\.py
        .*${each.value}\.py
      END
    }
  ]


  # utilise the AWS lambda PowerTools layer - must match the lamdba architecture
  #  using the Powertools for logging, supports managing the log level via standard Layer monitoring
  #  & logging log levels.
  layers = [
    "arn:aws:lambda:${data.aws_region.current.name}:017000801446:layer:${var.powertools_layer_arn_suffix}"
  ]

  environment_variables = (merge(
    local.lambda_env_vars[each.value],
    {
      POWERTOOLS_SERVICE_NAME = var.aws_powertools_service_name
    }
  ))

  allowed_triggers = {
    AllowExecutionFromSNS = {
      principal  = "sns.amazonaws.com"
      source_arn = local.sns_topic_arn
    }
  }

  depends_on = [
    local_file.notify_account_names_dict_python,
    local_file.notification_emblems_python
  ]
}
