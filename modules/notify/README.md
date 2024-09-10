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

## Limitations
- Slack posts using legacy format; need to migrate to Block Kit - SA-354
- Posts report in a varity of epoch, ISO and user date/times; need to consolidate and use Teams/Slack (Block Kit only) user timezone support - SA-353

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

  send_to_slack = true
  send_to_teams = true

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
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.8 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 4.8 |
| <a name="provider_local"></a> [local](#provider\_local) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_lambda"></a> [lambda](#module\_lambda) | terraform-aws-modules/lambda/aws | 3.2.0 |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_log_group.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_iam_role.sns_feedback_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_sns_topic.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic) | resource |
| [aws_sns_topic_subscription.sns_notify_slack](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription) | resource |
| [aws_sns_topic_subscription.sns_notify_teams](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription) | resource |
| [local_file.notification_emblems_python](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [local_file.notify_account_names_dict_python](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy_document.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.sns_feedback](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_partition.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/partition) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_accounts_id_to_name"></a> [accounts\_id\_to\_name](#input\_accounts\_id\_to\_name) | A mapping of account id and account name - used by notification lamdba to map an account ID to a human readable name | `map(string)` | `{}` | no |
| <a name="input_architecture"></a> [architecture](#input\_architecture) | Instruction set architecture for your Lambda function. Valid values are "x86\_64" or "arm64". | `string` | `"arm64"` | no |
| <a name="input_aws_powertools_log_level"></a> [aws\_powertools\_log\_level](#input\_aws\_powertools\_log\_level) | The log level for aws powertools | `string` | `"DEBUG"` | no |
| <a name="input_aws_powertools_service_name"></a> [aws\_powertools\_service\_name](#input\_aws\_powertools\_service\_name) | The service name to use | `string` | `"appvia-notifications"` | no |
| <a name="input_cloudwatch_log_group_kms_key_id"></a> [cloudwatch\_log\_group\_kms\_key\_id](#input\_cloudwatch\_log\_group\_kms\_key\_id) | The ARN of the KMS Key to use when encrypting log data for Lambda | `string` | `null` | no |
| <a name="input_cloudwatch_log_group_retention_in_days"></a> [cloudwatch\_log\_group\_retention\_in\_days](#input\_cloudwatch\_log\_group\_retention\_in\_days) | Specifies the number of days you want to retain log events in log group for Lambda. | `number` | `0` | no |
| <a name="input_cloudwatch_log_group_tags"></a> [cloudwatch\_log\_group\_tags](#input\_cloudwatch\_log\_group\_tags) | Additional tags for the Cloudwatch log group | `map(string)` | `{}` | no |
| <a name="input_create"></a> [create](#input\_create) | Whether to create all resources | `bool` | `true` | no |
| <a name="input_create_sns_topic"></a> [create\_sns\_topic](#input\_create\_sns\_topic) | Whether to create new SNS topic | `bool` | `true` | no |
| <a name="input_delivery_channels"></a> [delivery\_channels](#input\_delivery\_channels) | The configuration for Slack notifications | <pre>map(object({<br>    lambda_name = optional(string, "delivery_channel")<br>    # The name of the lambda function to create<br>    lambda_description = optional(string, "Lambda function to send notifications")<br>    # The description for the lambda<br>    secret_name = optional(string)<br>    # An optional secret name in secrets manager to use for the slack configuration <br>    webhook_url = optional(string)<br>    # The webhook url to post to<br>    filter_policy = optional(string)<br>    # An optional SNS subscription filter policy to apply<br>    filter_policy_scope = optional(string)<br>    # If filter policy provided this is the scope of that policy; either "MessageAttributes" (default) or "MessageBody"<br>  }))</pre> | `null` | no |
| <a name="input_enable_sns_topic_delivery_status_logs"></a> [enable\_sns\_topic\_delivery\_status\_logs](#input\_enable\_sns\_topic\_delivery\_status\_logs) | Whether to enable SNS topic delivery status logs | `bool` | `false` | no |
| <a name="input_hash_extra"></a> [hash\_extra](#input\_hash\_extra) | The string to add into hashing function. Useful when building same source path for different functions. | `string` | `""` | no |
| <a name="input_iam_policy_path"></a> [iam\_policy\_path](#input\_iam\_policy\_path) | Path of policies to that should be added to IAM role for Lambda Function | `string` | `null` | no |
| <a name="input_iam_role_boundary_policy_arn"></a> [iam\_role\_boundary\_policy\_arn](#input\_iam\_role\_boundary\_policy\_arn) | The ARN of the policy that is used to set the permissions boundary for the role | `string` | `null` | no |
| <a name="input_iam_role_name_prefix"></a> [iam\_role\_name\_prefix](#input\_iam\_role\_name\_prefix) | A unique role name beginning with the specified prefix | `string` | `"lambda"` | no |
| <a name="input_iam_role_path"></a> [iam\_role\_path](#input\_iam\_role\_path) | Path of IAM role to use for Lambda Function | `string` | `null` | no |
| <a name="input_iam_role_tags"></a> [iam\_role\_tags](#input\_iam\_role\_tags) | Additional tags for the IAM role | `map(string)` | `{}` | no |
| <a name="input_kms_key_arn"></a> [kms\_key\_arn](#input\_kms\_key\_arn) | ARN of the KMS key used for decrypting slack webhook url | `string` | `""` | no |
| <a name="input_lambda_attach_dead_letter_policy"></a> [lambda\_attach\_dead\_letter\_policy](#input\_lambda\_attach\_dead\_letter\_policy) | Controls whether SNS/SQS dead letter notification policy should be added to IAM role for Lambda Function | `bool` | `false` | no |
| <a name="input_lambda_dead_letter_target_arn"></a> [lambda\_dead\_letter\_target\_arn](#input\_lambda\_dead\_letter\_target\_arn) | The ARN of an SNS topic or SQS queue to notify when an invocation fails. | `string` | `null` | no |
| <a name="input_lambda_function_ephemeral_storage_size"></a> [lambda\_function\_ephemeral\_storage\_size](#input\_lambda\_function\_ephemeral\_storage\_size) | Amount of ephemeral storage (/tmp) in MB your Lambda Function can use at runtime. Valid value between 512 MB to 10,240 MB (10 GB). | `number` | `512` | no |
| <a name="input_lambda_function_s3_bucket"></a> [lambda\_function\_s3\_bucket](#input\_lambda\_function\_s3\_bucket) | S3 bucket to store artifacts | `string` | `null` | no |
| <a name="input_lambda_function_store_on_s3"></a> [lambda\_function\_store\_on\_s3](#input\_lambda\_function\_store\_on\_s3) | Whether to store produced artifacts on S3 or locally. | `bool` | `false` | no |
| <a name="input_lambda_function_tags"></a> [lambda\_function\_tags](#input\_lambda\_function\_tags) | Additional tags for the Lambda function | `map(string)` | `{}` | no |
| <a name="input_lambda_function_vpc_security_group_ids"></a> [lambda\_function\_vpc\_security\_group\_ids](#input\_lambda\_function\_vpc\_security\_group\_ids) | List of security group ids when Lambda Function should run in the VPC. | `list(string)` | `null` | no |
| <a name="input_lambda_function_vpc_subnet_ids"></a> [lambda\_function\_vpc\_subnet\_ids](#input\_lambda\_function\_vpc\_subnet\_ids) | List of subnet ids when Lambda Function should run in the VPC. Usually private or intra subnets. | `list(string)` | `null` | no |
| <a name="input_lambda_role"></a> [lambda\_role](#input\_lambda\_role) | IAM role attached to the Lambda Function.  If this is set then a role will not be created for you. | `string` | `""` | no |
| <a name="input_lambda_source_path"></a> [lambda\_source\_path](#input\_lambda\_source\_path) | The source path of the custom Lambda function | `string` | `null` | no |
| <a name="input_post_icons_url"></a> [post\_icons\_url](#input\_post\_icons\_url) | URLs (not base64 encoded!) to publically available icons for highlighting posts of error and/or warning status. Ideally 50px square. | <pre>object({<br>    error_url   = string<br>    warning_url = string<br>  })</pre> | <pre>{<br>  "error_url": "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-attention-icon.png",<br>  "warning_url": "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-warning-icon.png"<br>}</pre> | no |
| <a name="input_powertools_layer_arn_suffix"></a> [powertools\_layer\_arn\_suffix](#input\_powertools\_layer\_arn\_suffix) | The suffix of the ARN to use for AWS Powertools lambda layer (must match the architecture:https://docs.powertools.aws.dev/lambda/python/latest/. | `string` | `"AWSLambdaPowertoolsPythonV2-Arm64:79"` | no |
| <a name="input_putin_khuylo"></a> [putin\_khuylo](#input\_putin\_khuylo) | Do you agree that Putin doesn't respect Ukrainian sovereignty and territorial integrity? More info: https://en.wikipedia.org/wiki/Putin_khuylo! | `bool` | `true` | no |
| <a name="input_python_runtime"></a> [python\_runtime](#input\_python\_runtime) | The lambda python runtime | `string` | `"python3.12"` | no |
| <a name="input_recreate_missing_package"></a> [recreate\_missing\_package](#input\_recreate\_missing\_package) | Whether to recreate missing Lambda package if it is missing locally or not | `bool` | `true` | no |
| <a name="input_reserved_concurrent_executions"></a> [reserved\_concurrent\_executions](#input\_reserved\_concurrent\_executions) | The amount of reserved concurrent executions for this lambda function. A value of 0 disables lambda from being triggered and -1 removes any concurrency limitations | `number` | `-1` | no |
| <a name="input_send_to_slack"></a> [send\_to\_slack](#input\_send\_to\_slack) | To send to slack, set to true | `bool` | `false` | no |
| <a name="input_send_to_teams"></a> [send\_to\_teams](#input\_send\_to\_teams) | To send to teams, set to true | `bool` | `false` | no |
| <a name="input_slack_emoji"></a> [slack\_emoji](#input\_slack\_emoji) | A custom emoji that will appear on Slack messages | `string` | `":aws:"` | no |
| <a name="input_sns_topic_feedback_role_description"></a> [sns\_topic\_feedback\_role\_description](#input\_sns\_topic\_feedback\_role\_description) | Description of IAM role to use for SNS topic delivery status logging | `string` | `null` | no |
| <a name="input_sns_topic_feedback_role_force_detach_policies"></a> [sns\_topic\_feedback\_role\_force\_detach\_policies](#input\_sns\_topic\_feedback\_role\_force\_detach\_policies) | Specifies to force detaching any policies the IAM role has before destroying it. | `bool` | `true` | no |
| <a name="input_sns_topic_feedback_role_name"></a> [sns\_topic\_feedback\_role\_name](#input\_sns\_topic\_feedback\_role\_name) | Name of the IAM role to use for SNS topic delivery status logging | `string` | `null` | no |
| <a name="input_sns_topic_feedback_role_path"></a> [sns\_topic\_feedback\_role\_path](#input\_sns\_topic\_feedback\_role\_path) | Path of IAM role to use for SNS topic delivery status logging | `string` | `null` | no |
| <a name="input_sns_topic_feedback_role_permissions_boundary"></a> [sns\_topic\_feedback\_role\_permissions\_boundary](#input\_sns\_topic\_feedback\_role\_permissions\_boundary) | The ARN of the policy that is used to set the permissions boundary for the IAM role used by SNS topic delivery status logging | `string` | `null` | no |
| <a name="input_sns_topic_feedback_role_tags"></a> [sns\_topic\_feedback\_role\_tags](#input\_sns\_topic\_feedback\_role\_tags) | A map of tags to assign to IAM the SNS topic feedback role | `map(string)` | `{}` | no |
| <a name="input_sns_topic_kms_key_id"></a> [sns\_topic\_kms\_key\_id](#input\_sns\_topic\_kms\_key\_id) | ARN of the KMS key used for enabling SSE on the topic | `string` | `""` | no |
| <a name="input_sns_topic_lambda_feedback_role_arn"></a> [sns\_topic\_lambda\_feedback\_role\_arn](#input\_sns\_topic\_lambda\_feedback\_role\_arn) | IAM role for SNS topic delivery status logs.  If this is set then a role will not be created for you. | `string` | `""` | no |
| <a name="input_sns_topic_lambda_feedback_sample_rate"></a> [sns\_topic\_lambda\_feedback\_sample\_rate](#input\_sns\_topic\_lambda\_feedback\_sample\_rate) | The percentage of successful deliveries to log | `number` | `100` | no |
| <a name="input_sns_topic_name"></a> [sns\_topic\_name](#input\_sns\_topic\_name) | The name of the SNS topic to create | `string` | n/a | yes |
| <a name="input_sns_topic_tags"></a> [sns\_topic\_tags](#input\_sns\_topic\_tags) | Additional tags for the SNS topic | `map(string)` | `{}` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of tags to add to all resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_notify_slack_lambda_function_arn"></a> [notify\_slack\_lambda\_function\_arn](#output\_notify\_slack\_lambda\_function\_arn) | The ARN of the Lambda function |
| <a name="output_notify_slack_lambda_function_version"></a> [notify\_slack\_lambda\_function\_version](#output\_notify\_slack\_lambda\_function\_version) | Latest published version of your Lambda function |
| <a name="output_notify_slack_slack_lambda_function_name"></a> [notify\_slack\_slack\_lambda\_function\_name](#output\_notify\_slack\_slack\_lambda\_function\_name) | The name of the Lambda function |
| <a name="output_notify_teams_lambda_function_arn"></a> [notify\_teams\_lambda\_function\_arn](#output\_notify\_teams\_lambda\_function\_arn) | The ARN of the Lambda function |
| <a name="output_notify_teams_lambda_function_version"></a> [notify\_teams\_lambda\_function\_version](#output\_notify\_teams\_lambda\_function\_version) | Latest published version of your Lambda function |
| <a name="output_notify_teams_slack_lambda_function_name"></a> [notify\_teams\_slack\_lambda\_function\_name](#output\_notify\_teams\_slack\_lambda\_function\_name) | The name of the Lambda function |
| <a name="output_slack_lambda_cloudwatch_log_group_arn"></a> [slack\_lambda\_cloudwatch\_log\_group\_arn](#output\_slack\_lambda\_cloudwatch\_log\_group\_arn) | The Amazon Resource Name (ARN) specifying the log group |
| <a name="output_sns_topic_arn"></a> [sns\_topic\_arn](#output\_sns\_topic\_arn) | The ARN of the SNS topic from which messages will be sent to Slack |
| <a name="output_teams_lambda_cloudwatch_log_group_arn"></a> [teams\_lambda\_cloudwatch\_log\_group\_arn](#output\_teams\_lambda\_cloudwatch\_log\_group\_arn) | The Amazon Resource Name (ARN) specifying the log group |
<!-- END_TF_DOCS -->