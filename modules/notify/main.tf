data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}
data "aws_region" "current" {}

locals {
  create = var.create

  sns_topic_arn = try(
    aws_sns_topic.this[0].arn,
    "arn:${data.aws_partition.current.id}:sns:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${var.sns_topic_name}",
    ""
  )

  sns_feedback_role = local.create_sns_feedback_role ? aws_iam_role.sns_feedback_role[0].arn : var.sns_topic_lambda_feedback_role_arn
  lambda_policy_document = {
    "slack" = {
      sid       = "AllowWriteToCloudwatchLogsSlack"
      effect    = "Allow"
      actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
      resources = [replace("${try(aws_cloudwatch_log_group.lambda["slack"].arn, "")}:*", ":*:*", ":*")]
    },
    "teams" = {
      sid       = "AllowWriteToCloudwatchLogsTeams"
      effect    = "Allow"
      actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
      resources = [replace("${try(aws_cloudwatch_log_group.lambda["teams"].arn, "")}:*", ":*:*", ":*")]
    }
  }

  lambda_policy_document_kms = {
    sid       = "AllowKMSDecrypt"
    effect    = "Allow"
    actions   = ["kms:Decrypt"]
    resources = [var.kms_key_arn]
  }

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

  accounts_id_to_name_python_dictonary = templatefile(
    "${path.module}/mapAccountIdToName-python-dict.tftpl",
    {
      accounts_id_to_name = var.accounts_id_to_name
    }
  )
  notification_emblems_python = templatefile(
    "${path.module}/notification-emblems-python.tftpl",
    {
      error-icon-url   = var.post_icons_url.error_url
      warning-icon-url = var.post_icons_url.warning_url
    }
  )

  # the enable_[slack|teams] variable controls the subsubcription between SNS and lambda only; it is
  #  feasible that we want to keep the infrastructure (lambda, lambda role, log group et al) while suspending
  #  the posts.
  # but we only want to create the infrastructure if details of slack or team have been defined
  create_distribution = {
    "slack" = var.delivery_channels["slack"] != null ? true : false,
    "teams" = var.delivery_channels["teams"] != null ? true : false,
  }

  distributions = toset([for x in ["slack", "teams"] : x if local.create_distribution[x] == true])
}

data "aws_iam_policy_document" "lambda" {
  for_each = local.distributions

  dynamic "statement" {
    for_each = concat([local.lambda_policy_document[each.value]], var.kms_key_arn != "" ? [local.lambda_policy_document_kms] : [])
    content {
      sid       = statement.value.sid
      effect    = statement.value.effect
      actions   = statement.value.actions
      resources = statement.value.resources
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda" {
  for_each = local.distributions

  name              = "/aws/lambda/${var.delivery_channels[each.value].lambda_name}"
  retention_in_days = var.cloudwatch_log_group_retention_in_days
  kms_key_id        = var.cloudwatch_log_group_kms_key_id

  tags = merge(var.tags, var.cloudwatch_log_group_tags)
}

resource "aws_sns_topic" "this" {
  count = var.create_sns_topic && var.create ? 1 : 0

  name = var.sns_topic_name

  kms_master_key_id = var.sns_topic_kms_key_id

  lambda_failure_feedback_role_arn    = var.enable_sns_topic_delivery_status_logs ? local.sns_feedback_role : null
  lambda_success_feedback_role_arn    = var.enable_sns_topic_delivery_status_logs ? local.sns_feedback_role : null
  lambda_success_feedback_sample_rate = var.enable_sns_topic_delivery_status_logs ? var.sns_topic_lambda_feedback_sample_rate : null

  tags = merge(var.tags, var.sns_topic_tags)
}


resource "aws_sns_topic_subscription" "sns_notify_slack" {
  count = var.create && var.enable_slack && local.create_distribution["slack"] == true ? 1 : 0

  topic_arn           = local.sns_topic_arn
  protocol            = "lambda"
  endpoint            = module.lambda["slack"].lambda_function_arn
  filter_policy       = local.subscription_policies["slack"].filter
  filter_policy_scope = local.subscription_policies["slack"].scope
}

resource "aws_sns_topic_subscription" "sns_notify_teams" {
  count = var.create && var.enable_teams && local.create_distribution["teams"] == true ? 1 : 0

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

# a bug in "terraform-aws-modules/lambda/aws::source_path" when
#  running with for_each, even with the "hash_extra" creates a ZIP
#  build with a timestamp of "0" epoch timestamp, and causes a race-condition
#  whereby the hash of the new bundle fails as it is compared with the old bundle hash
#  making the build fail.
# Thus having to build separate bundles here.
# data "archive_file" "slack_lambda_archive" {
#   type        = "zip"
#   output_path = "${path.root}/builds/slack_lambda_src.zip"
#   source_dir  = "${path.module}/functions/src"
#   excludes    = [
#     "*_teams.py",
#     ".gitignore"
#   ]

#   depends_on = [
#     local_file.notify_account_names_dict_python,
#     local_file.notification_emblems_python
#   ]
# }
# data "archive_file" "teams_lambda_archive" {
#   type        = "zip"
#   output_path = "${path.root}/builds/teams_lambda_src.zip"
#   source_dir  = "${path.module}/functions/src"
#   excludes    = [
#     "*_slack.py",
#     ".gitignore"
#   ]

#   depends_on = [
#     local_file.notify_account_names_dict_python,
#     local_file.notification_emblems_python
#   ]
# }

module "lambda" {
  for_each = local.distributions

  source  = "terraform-aws-modules/lambda/aws"
  version = "3.2.0"

  create = var.create

  function_name = try(var.delivery_channels[each.value].lambda_name, "notify_${each.value}")
  description   = try(var.delivery_channels[each.value].lambda_description, "")

  hash_extra = each.value
  handler    = "${local.lambda_handler[each.value]}.lambda_handler"

  # source_path                    = var.lambda_source_path != null ? "${path.root}/${var.lambda_source_path}" : "${path.module}/functions/src/notify_${each.value}.py"
  # source_path                    = var.lambda_source_path != null ? "${path.root}/${var.lambda_source_path}" : "${path.module}/functions/src"


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

  recreate_missing_package       = var.recreate_missing_package
  runtime                        = var.python_runtime
  architectures                  = [var.architecture]
  timeout                        = 10
  kms_key_arn                    = var.kms_key_arn
  reserved_concurrent_executions = var.reserved_concurrent_executions
  ephemeral_storage_size         = var.lambda_function_ephemeral_storage_size

  # If publish is disabled, there will be "Error adding new Lambda Permission for notify_xxxxx:
  # InvalidParameterValueException: We currently do not support adding policies for $LATEST."
  publish = true

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

  create_role               = var.lambda_role == ""
  lambda_role               = var.lambda_role
  role_name                 = "${var.iam_role_name_prefix}-${var.delivery_channels[each.value].lambda_name}"
  role_permissions_boundary = var.iam_role_boundary_policy_arn
  role_tags                 = var.iam_role_tags
  role_path                 = var.iam_role_path
  policy_path               = var.iam_policy_path

  # Do not use Lambda's policy for cloudwatch logs, because we have to add a policy
  # for KMS conditionally. This way attach_policy_json is always true independenty of
  # the value of presense of KMS. Famous "computed values in count" bug...
  attach_cloudwatch_logs_policy = false
  attach_policy_json            = true
  policy_json                   = try(data.aws_iam_policy_document.lambda[each.value].json, "")

  use_existing_cloudwatch_log_group = true
  attach_network_policy             = var.lambda_function_vpc_subnet_ids != null

  dead_letter_target_arn    = var.lambda_dead_letter_target_arn
  attach_dead_letter_policy = var.lambda_attach_dead_letter_policy

  allowed_triggers = {
    AllowExecutionFromSNS = {
      principal  = "sns.amazonaws.com"
      source_arn = local.sns_topic_arn
    }
  }

  store_on_s3 = var.lambda_function_store_on_s3
  s3_bucket   = var.lambda_function_s3_bucket

  vpc_subnet_ids         = var.lambda_function_vpc_subnet_ids
  vpc_security_group_ids = var.lambda_function_vpc_security_group_ids

  tags = merge(var.tags, var.lambda_function_tags)

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    local_file.notify_account_names_dict_python,
    local_file.notification_emblems_python
  ]
}
