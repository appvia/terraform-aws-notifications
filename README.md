<!-- markdownlint-disable -->

<a href="https://www.appvia.io/"><img src="./images/banner.jpg" alt="Appvia Banner"/></a><br/><p align="right"> <a href="https://registry.terraform.io/modules/appvia/notifications/aws/latest"><img src="https://img.shields.io/static/v1?label=APPVIA&message=Terraform%20Registry&color=191970&style=for-the-badge" alt="Terraform Registry"/></a></a> <a href="https://github.com/appvia/terraform-aws-notifications/releases/latest"><img src="https://img.shields.io/github/release/appvia/terraform-aws-notifications.svg?style=for-the-badge&color=006400" alt="Latest Release"/></a> <a href="https://appvia-community.slack.com/join/shared_invite/zt-1s7i7xy85-T155drryqU56emm09ojMVA#/shared-invite/email"><img src="https://img.shields.io/badge/Slack-Join%20Community-purple?style=for-the-badge&logo=slack" alt="Slack Community"/></a> <a href="https://github.com/appvia/terraform-aws-notifications/graphs/contributors"><img src="https://img.shields.io/github/contributors/appvia/terraform-aws-notifications.svg?style=for-the-badge&color=FF8C00" alt="Contributors"/></a><a href="https://img.shields.io/github/actions/workflow/status/appvia/terraform-aws-notifications/terraform.yml" alt="Release"></a>

<!-- markdownlint-restore -->

# Terraform AWS Notifications

## Description

The purpose of this module is to provide a building block for processing and delivering notifications, sourced from SNS and forwarded to one or more endpoints (email, slack, teams and or custom subscribers).

## Usage

```hcl
module "notifications" {
  source = "github.com/appvia/terraform-aws-notifications?ref=main"

  allowed_aws_services = ["cloudwatch.amazonaws.com"]
  create_sns_topic     = true
  sns_topic_name       = var.sns_topic_name
  tags                 = var.tags

  subscribers = {
    "opsgenie" = {
      protocol               = "https"
      endpoint               = "https://api.opsgenie.com/v2/alerts"
      endpoint_auto_confirms = true
      raw_message_delivery   = true
    }
  }

  email = {
    addresses = var.email_addresses
  }

  enable_slack = true
  teams = {
    webhook_url = var.teams_webhook
  }
  enable_teams = true
  slack = {
    webhook_url = var.slack_webhook
  }

  accounts_id_to_name = {
    "12345678"  = "mgmt",
    "123456789" = "audit"
  }

  post_icons_url = {
    error_url   = "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-attention-icon.png"
    warning_url = "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-warning-icon.png"
  }

  # To redirect event URL in post through Identity Center, e.g.:
  identity_center_start_url = "<your start url>"
  identity_center_role      = "<your role - consistent across all accounts - namely read only>
}
```

## Update Documentation

The `terraform-docs` utility is used to generate this README. Follow the below steps to update:

1. Make changes to the `.terraform-docs.yml` file
2. Fetch the `terraform-docs` binary (https://terraform-docs.io/user-guide/installation/)
3. Run `terraform-docs markdown table --output-file ${PWD}/README.md --output-mode inject .`

## Using Secrets Manager

The `slack` configuration can be sourced from AWS Secrets Manager, using the `var.slack.secret_name`. The secret should be a JSON object reassembling the `slack` configuration.

```json
{
  "webhook_url": "https://hooks.slack.com/services/..."
}
```

## Maintenance

Frequently (quartley at least) check and upgrade:

1. Python runtime - [python_runtime](./modules/notify/variables.tf)
2. AWS PowerTools Lambda Layer for python ARN: [powertools_layer_arn_suffix](./modules/notify/variables.tf)

## Acknowledgements

- [notify-teams](https://github.com/teamclairvoyant/terraform-aws-notify-teams/releases/tag/v4.12.0.6) - distributed under Apache 2.0 license; obligations met under this GNU V3 license
- [terraform-aws-notify-slack](https://github.com/terraform-aws-modules/terraform-aws-notify-slack/releases/tag/v6.4.0) - distributed under Apache 2.0 license; obligations met under this GNU V3 license

<!-- BEGIN_TF_DOCS -->
## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 5.0.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_sns_topic_name"></a> [sns\_topic\_name](#input\_sns\_topic\_name) | The name of the source sns topic where events are published | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to apply to all resources | `map(string)` | n/a | yes |
| <a name="input_accounts_id_to_name"></a> [accounts\_id\_to\_name](#input\_accounts\_id\_to\_name) | A mapping of account id and account name - used by notification lamdba to map an account ID to a human readable name | `map(string)` | `{}` | no |
| <a name="input_allowed_aws_principals"></a> [allowed\_aws\_principals](#input\_allowed\_aws\_principals) | Optional, list of AWS accounts able to publish via the SNS topic (when creating topic) e.g 123456789012 | `list(string)` | `[]` | no |
| <a name="input_allowed_aws_services"></a> [allowed\_aws\_services](#input\_allowed\_aws\_services) | Optional, list of AWS services able to publish via the SNS topic (when creating topic) e.g cloudwatch.amazonaws.com | `list(string)` | `[]` | no |
| <a name="input_cloudwatch_log_group_kms_key_id"></a> [cloudwatch\_log\_group\_kms\_key\_id](#input\_cloudwatch\_log\_group\_kms\_key\_id) | The KMS key id to use for encrypting the cloudwatch log group (default is none) | `string` | `null` | no |
| <a name="input_cloudwatch_log_group_retention"></a> [cloudwatch\_log\_group\_retention](#input\_cloudwatch\_log\_group\_retention) | The retention period for the cloudwatch log group (for lambda function logs) in days | `string` | `"0"` | no |
| <a name="input_create_sns_topic"></a> [create\_sns\_topic](#input\_create\_sns\_topic) | Whether to create an SNS topic for notifications | `bool` | `false` | no |
| <a name="input_email"></a> [email](#input\_email) | The configuration for Email notifications | <pre>object({<br/>    addresses = optional(list(string))<br/>    # The email addresses to send notifications to<br/>  })</pre> | `null` | no |
| <a name="input_enable_slack"></a> [enable\_slack](#input\_enable\_slack) | To send to slack, set to true | `bool` | `false` | no |
| <a name="input_enable_teams"></a> [enable\_teams](#input\_enable\_teams) | To send to teams, set to true | `bool` | `false` | no |
| <a name="input_identity_center_role"></a> [identity\_center\_role](#input\_identity\_center\_role) | The name of the role to use when redirecting through Identity Center | `string` | `null` | no |
| <a name="input_identity_center_start_url"></a> [identity\_center\_start\_url](#input\_identity\_center\_start\_url) | The start URL of your Identity Center instance | `string` | `null` | no |
| <a name="input_post_icons_url"></a> [post\_icons\_url](#input\_post\_icons\_url) | URLs (not base64 encoded!) to publically available icons for highlighting posts of error and/or warning status. Ideally 50px square. Set to non-existent URLs to disable icons | <pre>object({<br/>    error_url   = string<br/>    warning_url = string<br/>  })</pre> | <pre>{<br/>  "error_url": "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-attention-icon.png",<br/>  "warning_url": "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-warning-icon.png"<br/>}</pre> | no |
| <a name="input_slack"></a> [slack](#input\_slack) | The configuration for Slack notifications | <pre>object({<br/>    lambda_name = optional(string, "slack-notify")<br/>    # The name of the lambda function to create <br/>    lambda_description = optional(string, "Lambda function to send slack notifications")<br/>    # The description for the slack lambda<br/>    secret_name = optional(string)<br/>    # An optional secret name in secrets manager to use for the slack configuration <br/>    webhook_url = optional(string)<br/>    # The webhook url to post to<br/>    filter_policy = optional(string)<br/>    # An optional SNS subscription filter policy to apply<br/>    filter_policy_scope = optional(string)<br/>    # If filter policy provided this is the scope of that policy; either "MessageAttributes" (default) or "MessageBody"<br/>  })</pre> | `null` | no |
| <a name="input_sns_topic_policy"></a> [sns\_topic\_policy](#input\_sns\_topic\_policy) | The policy to attach to the sns topic, else we default to account root | `string` | `null` | no |
| <a name="input_subscribers"></a> [subscribers](#input\_subscribers) | Optional list of custom subscribers to the SNS topic | <pre>map(object({<br/>    protocol = string<br/>    # The protocol to use. The possible values for this are: sqs, sms, lambda, application. (http or https are partially supported, see below).<br/>    endpoint = string<br/>    # The endpoint to send data to, the contents will vary with the protocol. (see below for more information)<br/>    endpoint_auto_confirms = bool<br/>    # Boolean indicating whether the end point is capable of auto confirming subscription e.g., PagerDuty (default is false)<br/>    raw_message_delivery = bool<br/>    # Boolean indicating whether or not to enable raw message delivery (the original message is directly passed, not wrapped in JSON with the original message in the message property) (default is false)<br/>  }))</pre> | `{}` | no |
| <a name="input_teams"></a> [teams](#input\_teams) | The configuration for teams notifications | <pre>object({<br/>    lambda_name = optional(string, "teams-notify")<br/>    # The name of the lambda function to create <br/>    lambda_description = optional(string, "Lambda function to send teams notifications")<br/>    # The description for the teams lambda<br/>    secret_name = optional(string)<br/>    # An optional secret name in secrets manager to use for the slack configuration <br/>    webhook_url = optional(string)<br/>    # The webhook url to post to<br/>    filter_policy = optional(string)<br/>    # An optional SNS subscription filter policy to apply<br/>    filter_policy_scope = optional(string)<br/>    # If filter policy provided this is the scope of that policy; either "MessageAttributes" (default) or "MessageBody"<br/>  })</pre> | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_channels_config"></a> [channels\_config](#output\_channels\_config) | The configuration data for each distribution channel |
| <a name="output_distributions"></a> [distributions](#output\_distributions) | The list of slack/teams distributions that are managed |
| <a name="output_sns_topic_arn"></a> [sns\_topic\_arn](#output\_sns\_topic\_arn) | The ARN of the SNS topic |
<!-- END_TF_DOCS -->
