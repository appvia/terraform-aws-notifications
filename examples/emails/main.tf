#####################################################################################
# Terraform module examples are meant to show an _example_ on how to use a module
# per use-case. The code below should not be copied directly but referenced in order
# to build your own root module that invokes this module, where
#    source = "github.com/appvia/terraform-aws-notifications?ref=main"
#####################################################################################

module "notifications" {
  source = "../.."

  # creates the SNS topic of the given name, and allows CloudWatch service to post to topic
  allowed_aws_services = ["cloudwatch.amazonaws.com"]
  create_sns_topic     = true
  sns_topic_name       = var.sns_topic_name


  # consistent tags applied across all resources
  tags = {
    Environment = "email-dev"
    Mode        = "email subscription"
  }

  # list of email address that will be subscribed
  email = {
    addresses = var.email_addresses
  }
}
