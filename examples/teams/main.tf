#####################################################################################
# Terraform module examples are meant to show an _example_ on how to use a module
# per use-case. The code below should not be copied directly but referenced in order
# to build your own root module that invokes this module
#####################################################################################

module "notifications" {
  source = "../.."

  allowed_aws_services = ["cloudwatch.amazonaws.com", "cloudtrail.amazonaws.com"]
  create_sns_topic     = true
  sns_topic_name       = var.sns_topic_name
  tags                 = var.tags

  teams = {
    channel     = var.teams_channel
    webhook_url = var.teams_webhook
  }

  send_to_slack = false
  send_to_teams = true
}
