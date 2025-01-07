locals {
  ## The region we are deploying to
  region = var.aws_region
  ## The account id of the caller
  account_id = var.aws_account_id
  ## The partition we are deploying to
  partition = var.aws_partition
  ## The ARN of the SNS topic
  sns_topic_arn = try(aws_sns_topic.this[0].arn, "arn:${local.partition}:sns:${local.region}:${local.account_id}:${var.sns_topic_name}", "")

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

  lambda_env_vars_layer_parameters_secrets = {
    SSM_PARAMETER_STORE_TIMEOUT_MILLIS           = "1000"
    SECRETS_MANAGER_TIMEOUT_MILLIS               = "1000"
    SSM_PARAMETER_STORE_TTL                      = "300"
    SECRETS_MANAGER_TTL                          = "300"
    PARAMETERS_SECRETS_EXTENSION_CACHE_ENABLED   = "true"
    PARAMETERS_SECRETS_EXTENSION_CACHE_SIZE      = "1000"
    PARAMETERS_SECRETS_EXTENSION_HTTP_PORT       = "2773"
    PARAMETERS_SECRETS_EXTENSION_MAX_CONNECTIONS = "3"
    PARAMETERS_SECRETS_EXTENSION_LOG_LEVEL       = "INFO"
    ACCOUNTS_ID_TO_NAME_PARAMETER_ARN            = try(var.accounts_id_to_name_parameter_arn, "")
  }

  lambda_env_vars_layers_powertools = {
    POWERTOOLS_SERVICE_NAME      = try(var.powertools_service_name, "service_undefined")
    POWERTOOLS_LOG_LEVEL         = "INFO"
    POWERTOOLS_METRICS_NAMESPACE = null
  }

  layer_env_vars_mapping = {
    powertools         = local.lambda_env_vars_layers_powertools
    parameters_secrets = local.lambda_env_vars_layer_parameters_secrets
  }

  enabled_layer_names = [
    for name, layer in local.processed_layers :
    name
    if layer.enabled && layer.arn != null
  ]

  layer_env_vars = merge([
    for layer_name in local.enabled_layer_names :
    lookup(local.layer_env_vars_mapping, layer_name, {})
  ]...)

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

  # the enable_[slack|teams] variable controls the subscription between SNS and lambda only; it is
  #  feasible that we want to keep the infrastructure (lambda, lambda role, log group et al) while suspending
  #  the posts.
  # but we only want to create the infrastructure if details of slack or team have been defined
  create_distribution = {
    "slack" = var.delivery_channels["slack"] != null ? true : false,
    "teams" = var.delivery_channels["teams"] != null ? true : false,
  }

  distributions = toset([for x in ["slack", "teams"] : x if local.create_distribution[x] == true])

  ## Lambda Layer
  # Filter only enabled policies
  enabled_policies = {
    for k, v in var.lambda_policy_config : k => v
    if v.enabled
  }

  # Python Runtime
  python_runtime = {
    "python3.13" = "python313"
    "python3.12" = "python312"
    "python3.11" = "python311"
    "python3.10" = "python310"
    "python3.9"  = "python39"
    "python3.8"  = "python38"
  }

  # AWS Managed Layer ARN patterns with architecture support
  aws_managed_layers = {
    powertools = {
      account_id    = "017000801446"
      name_pattern  = "AWSLambdaPowertoolsPythonV3-%PYTHONRUNTIME%-%ARCH%"
      arch_specific = true
      arch_format = {
        x86_64 = "x86_64"
        arm64  = "arm64" # lowercase for powertools
      }
    }
    parameters_secrets = {
      account_id    = "133256977650"
      name_pattern  = "AWS-Parameters-and-Secrets-Lambda-Extension-%ARCH%"
      arch_specific = true
      arch_format = {
        x86_64 = "X86_64" # Title case if needed
        arm64  = "Arm64"  # Title case if needed
      }
    }
  }

  # Process layer ARNs based on configuration
  processed_layers = {
    for name, config in var.lambda_layers_config :
    name => {
      enabled = coalesce(try(config.enabled, null), true)
      arn = coalesce(
        try(config.arn, null),
        try(config.type, "") == "managed" ?
        format("arn:%s:lambda:%s:%s:layer:%s:%s",
          local.partition,
          local.region,
          local.aws_managed_layers[name].account_id,
          (
            local.aws_managed_layers[name].arch_specific ?
            replace(
              replace(
                local.aws_managed_layers[name].name_pattern,
                "%PYTHONRUNTIME%",
                local.python_runtime[var.python_runtime]
              ),
              "%ARCH%",
              local.aws_managed_layers[name].arch_format[var.architecture]
            ) :
            local.aws_managed_layers[name].name_pattern
          ),
          config.version
        ) : null
      )
    }
  }

  enabled_layers = [
    for name, config in local.processed_layers :
    config.arn
    if config.enabled && config.arn != null
  ]
}
