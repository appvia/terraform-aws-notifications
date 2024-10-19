
locals {
  ## Checks if we are creating the sns topic 
  create_distribution = {
    "slack" = var.delivery_channels["slack"] != null ? true : false,
    "teams" = var.delivery_channels["teams"] != null ? true : false,
  }

  ## We create a map entry for each distribution we are creating
  distributions = toset([for x in ["slack", "teams"] : x if local.create_distribution[x] == true])

  ## The ARN of the SNS topic based on the user passing the name 
  sns_topic_arn = format("arn:aws:sns:%s:%s:%s", var.region, var.account_id, var.sns_topic_name)

  ## The lambda functions to create
  lambda_handler = {
    "slack" = try(split(".", basename(var.lambda_source_path))[0], "notify_slack"),
    "teams" = try(split(".", basename(var.lambda_source_path))[0], "notify_teams")
  }

  ## The lambda environment variables
  lambda_env_vars = {
    "slack" = {
      SLACK_WEBHOOK_URL       = try(var.delivery_channels["slack"].webhook_url, "https://null")
      IDENTITY_CENTER_URL     = try(var.identity_center_start_url, "")
      IDENTITY_CENTER_ROLE    = try(var.identity_center_role, "")
      POWERTOOLS_SERVICE_NAME = var.aws_powertools_service_name
    },
    "teams" = {
      TEAMS_WEBHOOK_URL       = try(var.delivery_channels["teams"].webhook_url, "https://null")
      IDENTITY_CENTER_URL     = try(var.identity_center_start_url, "")
      IDENTITY_CENTER_ROLE    = try(var.identity_center_role, "")
      POWERTOOLS_SERVICE_NAME = var.aws_powertools_service_name
    }
  }

  ## The lambda layer to use 
  lambda_layer = "arn:aws:lambda:${var.region}:017000801446:layer:${var.powertools_layer_arn_suffix}"

  ## The subscription policies for the slack and teams subscriptions
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

  ## Generate a python dictionary of account id to account name 
  accounts_id_to_name_python_dictonary = templatefile(
    "${path.module}/assets/accounts.tftpl",
    {
      accounts_id_to_name = var.accounts_id_to_name
    }
  )
}

