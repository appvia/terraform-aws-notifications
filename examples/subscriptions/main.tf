#####################################################################################
# Terraform module examples are meant to show an _example_ on how to use a module
# per use-case. The code below should not be copied directly but referenced in order
# to build your own root module that invokes this module, where
#    source = "github.com/appvia/terraform-aws-notifications?ref=main"
#####################################################################################

module "primary_notifications" {
  source = "../.."

  create_sns_topic = false
  sns_topic_name   = var.sns_topic_name

  # consistent tags applied across all resources; merges these local tags with var.tags
  tags = (merge(
    {
      Environment = "subscriptions-dev"
      Mode        = "primary subscriptions"

    },
    var.tags,
  ))

  # enable sending to teams and provide the teams webhook
  #  alternatively, provide the name of the AWS Secret with JSON body and `webhook_url` attribute
  # Optionally:
  #  1. Override the name of the lambda - this will be essential if you are deploying multiple instances of this module
  #  2. Override the description of the lambda
  enable_teams = true
  teams = {
    webhook_url = var.primary_teams_webhook
    # secret_name        = "name of AWS secret with teams webhook_url"
    lambda_name        = "primary_teams_posts"
    lambda_description = "The default posting of notifications to teams"
  }

  # enable sending to slack and provide the slack webhook
  #  alternatively, provide the name of the AWS Secret with JSON body and `webhook_url` attribute
  # Optionally:
  #  1. Override the name of the lambda - this will be essential if you are deploying multiple instances of this module
  #  2. Override the description of the lambda
  enable_slack = true
  slack = {
    webhook_url = var.primary_slack_webhook
    # secret_name        = "name of AWS secret with slack webhook_url"
    lambda_name        = "primary_slack_posts"
    lambda_description = "The default posting of notifications to slack"
  }

  # many of the events will include the account id where the event originate from
  # List each account ID here along with a pseudonym that will appear also in the posts
  accounts_id_to_name_parameter_arn = var.accounts_id_to_name_parameter_arn
  # uncomment to override the warning and error icons that will be shown against each post
  #  The URLs must be public, and must resolve to transparent PNG ideally.
  #  appvia recommend images that are 50px by 50px.
  # post_icons_url = {
  #   error_url   = "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-attention-icon.png"
  #   warning_url = "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-warning-icon.png"
  # }

  # Override the number of the slack lambda logs are retained for.
  #
  # Possible values are: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653, and 0 (never expire).
  # See https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group.
  cloudwatch_log_group_retention = 3

  # other overrides, see "Customisations/Overrides" in README.md
}

module "security_hub_notifications" {
  source = "../.."

  create_sns_topic = false
  sns_topic_name   = var.sns_topic_name

  # consistent tags applied across all resources; merges these local tags with var.tags
  tags = (merge(
    {
      Environment = "subscriptions-dev"
      Mode        = "security hub only subscriptions"

    },
    var.tags,
  ))

  # enable sending to teams and provide the teams webhook
  #  alternatively, provide the name of the AWS Secret with JSON body and `webhook_url` attribute
  # Optionally:
  #  1. Override the name of the lambda - this will be essential if you are deploying multiple instances of this module
  #  2. Override the description of the lambda
  #  3. Optional: filter policy - must be a JSON string
  #  4. Optinoal: filter policy scope - either "MessageAttributes" (default) or "MessageBody"
  enable_teams = true
  teams = {
    webhook_url = var.security_hub_teams_webhook
    # secret_name        = "name of AWS secret with teams webhook_url"
    lambda_name         = "security_hub_teams_posts"
    lambda_description  = "The posting of Security Hub only notifications to teams"
    filter_policy       = file("${path.module}/security_hub_subscription_filter.json")
    filter_policy_scope = "MessageBody"
  }

  # enable sending to slack and provide the slack webhook
  #  alternatively, provide the name of the AWS Secret with JSON body and `webhook_url` attribute
  # Optionally:
  #  1. Override the name of the lambda - this will be essential if you are deploying multiple instances of this module
  #  2. Override the description of the lambda
  #  3. Optional: filter policy - must be a JSON string
  #  4. Optinoal: filter policy scope - either "MessageAttributes" (default) or "MessageBody"
  enable_slack = true
  slack = {
    webhook_url = var.security_hub_slack_webhook
    # secret_name        = "name of AWS secret with slack webhook_url"
    lambda_name         = "security_hub_slack_posts"
    lambda_description  = "The posting of Security Hub only notifications to slack"
    filter_policy       = file("${path.module}/security_hub_subscription_filter.json")
    filter_policy_scope = "MessageBody"
  }

  # many of the events will include the account id where the event originate from
  # List each account ID here along with a pseudonym that will appear also in the posts
  accounts_id_to_name_parameter_arn = var.accounts_id_to_name_parameter_arn

  # uncomment to override the warning and error icons that will be shown against each post
  #  The URLs must be public, and must resolve to transparent PNG ideally.
  #  appvia recommend images that are 50px by 50px.
  # post_icons_url = {
  #   error_url   = "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-attention-icon.png"
  #   warning_url = "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-warning-icon.png"
  # }

  # Override the number of the slack lambda logs are retained for.
  #
  # Possible values are: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653, and 0 (never expire).
  # See https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group.
  cloudwatch_log_group_retention = 3

  # other overrides, see "Customisations/Overrides" in README.md
  powertools_service_name = var.powertools_service_name
}
