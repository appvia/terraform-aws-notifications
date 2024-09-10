#####################################################################################
# Terraform module examples are meant to show an _example_ on how to use a module
# per use-case. The code below should not be copied directly but referenced in order
# to build your own root module that invokes this module, where
#    source = "github.com/appvia/terraform-aws-notifications?ref=main"
#####################################################################################

module "notifications" {
  source = "../.."

  allowed_aws_services = ["cloudwatch.amazonaws.com", "cloudtrail.amazonaws.com"]
  create_sns_topic     = true
  sns_topic_name       = var.sns_topic_name


  # consistent tags applied across all resources; merges these local tags with var.tags
  tags = (merge(
    {
      Environment = "teams-dev"
      Mode        = "teams posts"
    },
    var.tags,
  ))

  send_to_teams = true
  teams = {
    webhook_url = var.teams_webhook
    # secret_name        = "name of AWS secret with teams webhook_url"
    lambda_name        = "post-to-teams"
    lambda_description = "Post notifications from SNS to my teams"
  }

  # many of the events will include the account id where the event originate from
  # List each account ID here along with a pseudonym that will appear also in the posts 
  accounts_id_to_name = {
    "12345678"     = "mgmt",
    "735598076380" = "audit"
  }

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
  cloudwatch_log_group_retention = 1

  # other overrides, see "Customisations/Overrides" in README.md
}
