# Identity Center posts example using appvia notifications
This example assumes creating the SNS topic.

Some of the posts, such as, CloudWatch, GuardDuty and SecurityHub, include URLs that can take you to direct to the event in AWS web console.
But if using Identity Center, then you can redirect through your Identity Center start URL to a given role and account. Assume the given role is the same
across all accounts and has access to all event services; typically this is a Read Only support role.

The Identity Center URL should end with start, namely:
```
https://a-12345678.awsapps.com/start
```

To run:
```
terraform init
TF_VAR_sns_topic_name="<your SNS topic name>" TF_VAR_slack_webhook="<your url>" TF_VAR_identity_center_start_url="<your url>" TF_VAR_identity_center_role="<your role>" terraform plan
TF_VAR_sns_topic_name="<your SNS topic name>" TF_VAR_slack_webhook="<your url>" TF_VAR_identity_center_start_url="<your url>" TF_VAR_identity_center_role="<your role>" terraform apply
```

Or create a `local.tfvars` with:
```
slack_webhook="<your url>
sns_topic_name="<your SNS topic name>"
identity_center_start_url = "<your url>"
identity_center_role = "<your role>"
```

And run with:
```
terraform init
terraform plan --var-file=./local.tfvars
terraform apply--var-file=./local.tfvars
```

## Customisations/Overrides
This example shows how to control the lambda CloudWatch logs retention period.

The module allows for further customisation of:
* `cloudwatch_log_group_kms_key_id` - if using custom KMS key to protect logs
* `allowed_aws_principals` - used to apply policy to SNS topic (if creating the SNS topic);  refer to [data.tf](../../data.tf) and [locals.tf](../../locals.tf)
* `allowed_aws_services` - used to apply policy to SNS topic (if creating the SNS topic);  refer to [data.tf](../../data.tf) and [locals.tf](../../locals.tf)
* `sns_topic_policy` - used to override the generated SNS topic policy (if creating the SNS topic): refer to [locals.tf](../../locals.tf)

<!-- BEGIN_TF_DOCS -->
## Providers

No providers.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_identity_center_role"></a> [identity\_center\_role](#input\_identity\_center\_role) | The name of the role to use when redirecting through Identity Center | `string` | n/a | yes |
| <a name="input_identity_center_start_url"></a> [identity\_center\_start\_url](#input\_identity\_center\_start\_url) | The start URL of your Identity Center instance | `string` | n/a | yes |
| <a name="input_slack_webhook"></a> [slack\_webhook](#input\_slack\_webhook) | The URL of the slack webhook | `string` | n/a | yes |
| <a name="input_sns_topic_name"></a> [sns\_topic\_name](#input\_sns\_topic\_name) | The name of the SNS topic to create | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_sns_topic_arn"></a> [sns\_topic\_arn](#output\_sns\_topic\_arn) | The ARN of the SNS topic |
<!-- END_TF_DOCS -->