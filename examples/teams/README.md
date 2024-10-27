# Teams posts example using appvia notifications
This example assumes creating the SNS topic; _refer to [opsgenie example](../opsgenie/main.tf) if wanting to use an existing SNS topic_.

To run:
```
terraform init
TF_VAR_sns_topic_name="<your SNS topic name>" TF_VAR_teams_webhook="<your url>" TF_VAR_tags='{"your tag"="your tag value"}' terraform plan
TF_VAR_sns_topic_name="<your SNS topic name>" TF_VAR_teams_webhook="<your url>" TF_VAR_tags='{"your tag"="your tag value"}' terraform apply
```

Or create a `local.tfvars` with:
```
tags = {
  "tag1" = "value1"
}
teams_webhook="<your url>
sns_topic_name="<your SNS topic name>"
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
| <a name="input_sns_topic_name"></a> [sns\_topic\_name](#input\_sns\_topic\_name) | The name of the SNS topic to create | `string` | n/a | yes |
| <a name="input_teams_webhook"></a> [teams\_webhook](#input\_teams\_webhook) | The URL of the teams webhook | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of tags to add to all resources | `map(string)` | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_sns_topic_arn"></a> [sns\_topic\_arn](#output\_sns\_topic\_arn) | The ARN of the SNS topic |
<!-- END_TF_DOCS -->