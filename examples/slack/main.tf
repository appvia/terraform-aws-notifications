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

  slack = {
    webhook_url = var.slack_webhook
  }

  send_to_slack = true
  send_to_teams = false

  accounts_id_to_name = {
    "12345678" = "mgmt",
    "123456789" = "audit"
  }

  # set URLs to non-existent URLs to disable icons
  post_icons_url = {
    error_url   = "https://doesn-t-exist-domain/attention.png"
    warning_url = "https://doesn-t-exist-domain/warning.png"
  }
}
