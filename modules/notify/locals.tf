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

  # ## We need to ensure the account names are ordered
  # account_by_ids = [
  #   for name in sort(keys(var.accounts_id_to_name)) : {
  #     id   = name
  #     name = var.accounts_id_to_name[name]
  #   }
  # ]

  # accounts_id_to_name_python_dictonary = templatefile(
  #   "${path.module}/mapAccountIdToName-python-dict.tftpl",
  #   {
  #     accounts_id_to_name = local.account_by_ids
  #   }
  # )

  # the enable_[slack|teams] variable controls the subscription between SNS and lambda only; it is
  #  feasible that we want to keep the infrastructure (lambda, lambda role, log group et al) while suspending
  #  the posts.
  # but we only want to create the infrastructure if details of slack or team have been defined
  create_distribution = {
    "slack" = var.delivery_channels["slack"] != null ? true : false,
    "teams" = var.delivery_channels["teams"] != null ? true : false,
  }

  distributions = toset([for x in ["slack", "teams"] : x if local.create_distribution[x] == true])

  # Filter only enabled policies
  enabled_policies = {
    for k, v in var.lambda_policy_config : k => v
    if v.enabled
  }

  # CPU architecture mapping
  architectures = {
    x86_64 = "amd64"
    arm64  = "arm64"
  }

  # AWS Managed Layer ARN patterns with architecture support
  aws_managed_layers = {
    powertools = {
      account_id    = "017000801446"
      name_pattern  = "AWSLambdaPowertoolsPythonV2-%ARCH%"
      arch_specific = true
    }
    parameters_secrets = {
      account_id    = "133256977650"
      name_pattern  = "AWS-Parameters-and-Secrets-Lambda-Extension-%ARCH%"
      arch_specific = true
    }
    # Add more AWS managed layers as needed
  }

  # Process layer ARNs based on configuration
  processed_layers = {
    for name, config in var.lambda_layers_config :
    name => {
      enabled = try(config.enabled, true)
      arn = try(
        # If ARN is directly provided, use it
        config.arn,
        # If it's a managed layer, construct the ARN using the managed layer pattern
        config.type == "managed" ? (
          "arn:aws:lambda:${config.region != null ? config.region : local.region}:${local.aws_managed_layers[config.name].account_id}:layer:${
            local.aws_managed_layers[config.name].arch_specific ?
            replace(local.aws_managed_layers[config.name].name_pattern, "%ARCH%", local.architectures[var.architecture]) :
            local.aws_managed_layers[config.name].name_pattern
          }${config.version != null ? ":${config.version}" : ""}"
        ) : null
      )
    }
  }

  # Generate final list of enabled layer ARNs
  enabled_layers = [
    for name, layer in local.processed_layers :
    layer.arn
    if layer.enabled && layer.arn != null
  ]
}
