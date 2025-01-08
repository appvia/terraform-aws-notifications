# Slack posts example using appvia notifications
This example assumes creating the SNS topic; _refer to [opsgenie example](../opsgenie/main.tf) if wanting to use an existing SNS topic_.

To run:
```
terraform init
TF_VAR_sns_topic_name="<your SNS topic name>" TF_VAR_slack_webhook="<your url>" TF_VAR_tags='{"your tag"="your tag value"}' terraform plan
TF_VAR_sns_topic_name="<your SNS topic name>" TF_VAR_slack_webhook="<your url>" TF_VAR_tags='{"your tag"="your tag value"}' terraform apply
```

Or create a `local.tfvars` with:
```
tags = {
  "tag1" = "value1"
}
slack_webhook="<your url>
sns_topic_name="<your SNS topic name>"
powertools_service_name="my-service-namespace"
accounts_id_to_name_parameter_arn="arn:aws:ssm:eu-west-2:1234567890:parameter/myparam"
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
| <a name="input_slack_webhook"></a> [slack\_webhook](#input\_slack\_webhook) | The URL of the slack webhook | `string` | n/a | yes |
| <a name="input_sns_topic_name"></a> [sns\_topic\_name](#input\_sns\_topic\_name) | The name of the SNS topic to create | `string` | n/a | yes |
| <a name="input_accounts_id_to_name_parameter_arn"></a> [accounts\_id\_to\_name\_parameter\_arn](#input\_accounts\_id\_to\_name\_parameter\_arn) | The ARN of your parameter containing the your account ID to name mapping. This ARN will be attached to lambda execution role as a resource, therefore a valid resource must exist. e.g 'arn:aws:ssm:eu-west-2:0123456778:parameter/myorg/configmaps/accounts\_id\_to\_name\_mapping' to enable the lambda retrieve values from ssm. | `string` | `null` | no |
| <a name="input_powertools_service_name"></a> [powertools\_service\_name](#input\_powertools\_service\_name) | Sets service name used for tracing namespace, metrics dimension and structured logging for the AWS Powertool Lambda Layer | `string` | `"appvia-notifications-dev"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of tags to add to all resources | `map(string)` | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_sns_topic_arn"></a> [sns\_topic\_arn](#output\_sns\_topic\_arn) | The ARN of the SNS topic |
<!-- END_TF_DOCS -->