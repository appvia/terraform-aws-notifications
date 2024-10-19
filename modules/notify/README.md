# appvia notify module
Started as a fork from https://github.com/terraform-aws-modules/terraform-aws-notify-slack/releases/tag/v6.4.0.
The terraform-aws-notify-slack provided a great initial implementation, however, we needed integration with teams - which only requires complementary lambda functions, but we also required customising the POSTs sent to slack/teams. terraform-aws-notify-slack did not offer any message customisation. On 20240726, we brought the terraform-aws-notify-slack native. This included:
* separating the parsing of messages with the render to post
* additional parsers including Security Hub, Budget and Savings Plan
* mapping account ID to account names - driven by terraform var
* reformatted the slack messages to include a icon to more visually highlight priority - which aligns with the teams post -  - driven by terraform var
* reformatted the slack messages to make them easier to read - much of the posts were in block text
* better handling of region - does not assume the region of the SNS topic (may not necessarily be the same as that of the original event)
* for CloudWatch - better handing of the account id - terraform-aws-notify-slack assumed the SNS topic account - which is not true within appvia's LZA
* re-worked all the tests - by using a single input source being any array of records for all test cases
* introduced AWS Powertools for lambda layer - with logging and metrics

Note - rather than allowing for customised posts; this module prefers opinated posts given the variety of different events supported as per appvia's Landing Zone Architcture (LZA).

This module creates an SNS topic (or uses an existing one) and an AWS Lambda function that sends notifications to Slack using the [incoming webhooks API](https://api.slack.com/incoming-webhooks) or Teams (https://support.microsoft.com/en-gb/office/create-and-add-an-outgoing-webhook-in-microsoft-teams-8e1a1648-982f-4511-b342-6d8492437207).

Start by setting up an [incoming webhook integration](https://my.slack.com/services/new/incoming-webhook/) in your Slack workspace.

## Supported Features
- AWS Lambda runtime Python 3.11; defaults to using Graviton hosts (ARM64)
- Create new SNS topic or use existing one
- Support plaintext and encrypted version of Slack webhook URL
- Various event types are supported, even generic messages:
  - AWS CloudWatch Alarms
  - AWS CloudWatch LogMetrics Alarms
  - AWS GuardDuty Findings
  - AWS Security Hub
  - AWS Backup events
  - AWS Budget/Savings Plan alerts
  - Partial support for DMS events
- Map account ids to account names (who can remember account ids?)
- Supports service urls redirects through Identity Center - fixed role name.

## Limitations
- Slack posts using legacy format; need to migrate to Block Kit - SA-354
- Posts report in a variety of epoch, ISO and user date/times; need to consolidate and use Teams/Slack (Block Kit only) user timezone support - SA-353

## TODO
1. Python tests and update github workflow to run tests - SA-374
2. terraform tests - SA-375

## Usage
```hcl
module "appvia_notification" {
  source  = "github.com/appvia/terraform-aws-notifications?ref=main"
  version = "~> 5.0"

  create_sns_topic     = true
  sns_topic_name       = var.sns_topic_name
  tags                 = var.tags

  teams = {
    webhook_url = var.teams_webhook
  }
  slack = {
    webhook_url = var.slack_webhook
  }

  enable_slack = true
  enable_teams = true

  accounts_id_to_name = {
    "12345678"  = "mgmt",
    "123456789" = "audit"
  }

  post_icons_url = {
    error_url   = "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-attention-icon.png"
    warning_url = "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-warning-icon.png"
  }
}
```

## Use existing SNS topic or create new
If you want to subscribe the AWS Lambda Function created by this module to an existing SNS topic you should specify `create_sns_topic = false` as an argument and specify the name of existing SNS topic name in `sns_topic_name`.

## Examples
- [slack only](https://github.com/appvia/terraform-aws-notifications/tree/main/examples/slack) - send posts only to slack
- [teams only](https://github.com/appvia/terraform-aws-notifications/tree/main/examples/teams) - send posts only to teams
- [slack and teams](https://github.com/appvia/terraform-aws-notifications/tree/main/examples/teams-and-slack) - send posts to both teams and slack


## Acknowledgements
"terraform-aws-modules/terraform-aws-notify-slack" is maintained by [Anton Babenko](https://github.com/antonbabenko) with help from [these awesome contributors](https://github.com/terraform-aws-modules/terraform-aws-notify-slack/graphs/contributors).

## License
~~Apache 2 Licensed. See [LICENSE](https://github.com/terraform-aws-modules/terraform-aws-notify-slack/tree/master/LICENSE) for full details.~~
Subsumed by appvia's GNU V3 license; [see license](../../LICENSE).

<!-- BEGIN_TF_DOCS -->
## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 4.8 |
| <a name="provider_local"></a> [local](#provider\_local) | >= 2.1 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_id"></a> [account\_id](#input\_account\_id) | The AWS account ID | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | The AWS region to deploy to | `string` | n/a | yes |
| <a name="input_sns_topic_name"></a> [sns\_topic\_name](#input\_sns\_topic\_name) | The name of the SNS topic to create | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of tags to add to all resources | `map(string)` | n/a | yes |
| <a name="input_accounts_id_to_name"></a> [accounts\_id\_to\_name](#input\_accounts\_id\_to\_name) | A mapping of account id and account name - used by notification lamdba to map an account ID to a human readable name | `map(string)` | `{}` | no |
| <a name="input_architecture"></a> [architecture](#input\_architecture) | Instruction set architecture for your Lambda function. Valid values are "x86\_64" or "arm64". | `string` | `"arm64"` | no |
| <a name="input_aws_powertools_service_name"></a> [aws\_powertools\_service\_name](#input\_aws\_powertools\_service\_name) | The service name to use | `string` | `"appvia-notifications"` | no |
| <a name="input_cloudwatch_log_group_kms_key_id"></a> [cloudwatch\_log\_group\_kms\_key\_id](#input\_cloudwatch\_log\_group\_kms\_key\_id) | The ARN of the KMS Key to use when encrypting log data for Lambda | `string` | `null` | no |
| <a name="input_cloudwatch_log_group_retention_in_days"></a> [cloudwatch\_log\_group\_retention\_in\_days](#input\_cloudwatch\_log\_group\_retention\_in\_days) | Specifies the number of days you want to retain log events in log group for Lambda. | `number` | `0` | no |
| <a name="input_delivery_channels"></a> [delivery\_channels](#input\_delivery\_channels) | The configuration for Slack notifications | <pre>map(object({<br/>    lambda_name = optional(string, "delivery_channel")<br/>    # The name of the lambda function to create<br/>    lambda_description = optional(string, "Lambda function to send notifications")<br/>    # The description for the lambda<br/>    secret_name = optional(string)<br/>    # An optional secret name in secrets manager to use for the slack configuration <br/>    webhook_url = optional(string)<br/>    # The webhook url to post to<br/>    filter_policy = optional(string)<br/>    # An optional SNS subscription filter policy to apply<br/>    filter_policy_scope = optional(string)<br/>    # If filter policy provided this is the scope of that policy; either "MessageAttributes" (default) or "MessageBody"<br/>  }))</pre> | `null` | no |
| <a name="input_enable_slack"></a> [enable\_slack](#input\_enable\_slack) | To send to slack, set to true | `bool` | `false` | no |
| <a name="input_enable_teams"></a> [enable\_teams](#input\_enable\_teams) | To send to teams, set to true | `bool` | `false` | no |
| <a name="input_iam_policy_arns"></a> [iam\_policy\_arns](#input\_iam\_policy\_arns) | A list of IAM policy ARNs to attach to the Lambda function | `list(string)` | `[]` | no |
| <a name="input_iam_policy_jsons"></a> [iam\_policy\_jsons](#input\_iam\_policy\_jsons) | A list of IAM policies to attach to the Lambda function | `list(string)` | `[]` | no |
| <a name="input_iam_role_boundary_policy_arn"></a> [iam\_role\_boundary\_policy\_arn](#input\_iam\_role\_boundary\_policy\_arn) | The ARN of the policy that is used to set the permissions boundary for the role | `string` | `null` | no |
| <a name="input_identity_center_role"></a> [identity\_center\_role](#input\_identity\_center\_role) | The name of the role to use when redirecting through Identity Center | `string` | `null` | no |
| <a name="input_identity_center_start_url"></a> [identity\_center\_start\_url](#input\_identity\_center\_start\_url) | The start URL of your Identity Center instance | `string` | `null` | no |
| <a name="input_kms_key_arn"></a> [kms\_key\_arn](#input\_kms\_key\_arn) | ARN of the KMS key used for decrypting slack webhook url | `string` | `""` | no |
| <a name="input_lambda_ephemeral_storage_size"></a> [lambda\_ephemeral\_storage\_size](#input\_lambda\_ephemeral\_storage\_size) | Amount of ephemeral storage (/tmp) in MB your Lambda Function can use at runtime. Valid value between 512 MB to 10,240 MB (10 GB). | `number` | `512` | no |
| <a name="input_lambda_source_path"></a> [lambda\_source\_path](#input\_lambda\_source\_path) | The source path of the custom Lambda function | `string` | `null` | no |
| <a name="input_powertools_layer_arn_suffix"></a> [powertools\_layer\_arn\_suffix](#input\_powertools\_layer\_arn\_suffix) | The suffix of the ARN to use for AWS Powertools lambda layer (must match the architecture:https://docs.powertools.aws.dev/lambda/python/latest/. | `string` | `"AWSLambdaPowertoolsPythonV2-Arm64:79"` | no |
| <a name="input_python_runtime"></a> [python\_runtime](#input\_python\_runtime) | The lambda python runtime | `string` | `"python3.12"` | no |
| <a name="input_recreate_missing_package"></a> [recreate\_missing\_package](#input\_recreate\_missing\_package) | Whether to recreate missing Lambda package if it is missing locally or not | `bool` | `true` | no |
| <a name="input_reserved_concurrent_executions"></a> [reserved\_concurrent\_executions](#input\_reserved\_concurrent\_executions) | The amount of reserved concurrent executions for this lambda function. A value of 0 disables lambda from being triggered and -1 removes any concurrency limitations | `number` | `-1` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_distributions"></a> [distributions](#output\_distributions) | The list of slack/teams distributions that are managed |
| <a name="output_notify_slack_lambda_function_arn"></a> [notify\_slack\_lambda\_function\_arn](#output\_notify\_slack\_lambda\_function\_arn) | The ARN of the Lambda function |
| <a name="output_notify_slack_lambda_function_version"></a> [notify\_slack\_lambda\_function\_version](#output\_notify\_slack\_lambda\_function\_version) | Latest published version of your Lambda function |
| <a name="output_notify_slack_slack_lambda_function_name"></a> [notify\_slack\_slack\_lambda\_function\_name](#output\_notify\_slack\_slack\_lambda\_function\_name) | The name of the Lambda function |
| <a name="output_notify_teams_lambda_function_arn"></a> [notify\_teams\_lambda\_function\_arn](#output\_notify\_teams\_lambda\_function\_arn) | The ARN of the Lambda function |
| <a name="output_notify_teams_lambda_function_version"></a> [notify\_teams\_lambda\_function\_version](#output\_notify\_teams\_lambda\_function\_version) | Latest published version of your Lambda function |
| <a name="output_notify_teams_slack_lambda_function_name"></a> [notify\_teams\_slack\_lambda\_function\_name](#output\_notify\_teams\_slack\_lambda\_function\_name) | The name of the Lambda function |
| <a name="output_sns_topic_arn"></a> [sns\_topic\_arn](#output\_sns\_topic\_arn) | The ARN of the SNS topic from which messages will be sent to Slack |
<!-- END_TF_DOCS -->
