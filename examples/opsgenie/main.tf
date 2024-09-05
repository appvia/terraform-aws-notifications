#####################################################################################
# Terraform module examples are meant to show an _example_ on how to use a module
# per use-case. The code below should not be copied directly but referenced in order
# to build your own root module that invokes this module, where
#    source = "github.com/appvia/terraform-aws-notifications?ref=main"
#####################################################################################

module "notifications" {
  source = "../.."

  # assumes SNS topic already exists
  create_sns_topic = false
  sns_topic_name   = var.sns_topic_name


  # consistent tags applied across all resources
  tags = {
    Environment = "http-subscribers-dev"
    Mode        = "http(s) subscription"
  }

  # the set of subscribers; set "endpoint_auto_confirms" to false unless the endpoint handles the subscription request from AWS
  subscribers = {
    "opsgenie" = {
      protocol               = "https"
      endpoint               = var.opsgenie_endpoint
      endpoint_auto_confirms = false
      raw_message_delivery   = true
    }
  }
}
