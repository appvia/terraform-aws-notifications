Create a `local.tfvars` with:
```
teams_webhook="<your url>
teams_channel="<your teams channel name>"
slack_webhook="<your url>
slack_channel="<your slack channel name>"
sns_topic_name="<your SNS topic name>"
```
And run with:
```
terraform init
terraform plan --var-file=./local.tfvars
terraform apply--var-file=./local.tfvars
```

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.0.0 |
| <a name="requirement_awscc"></a> [awscc](#requirement\_awscc) | >= 0.11.0 |

## Providers

No providers.

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_notifications"></a> [notifications](#module\_notifications) | ../.. | n/a |

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_slack_webhook"></a> [slack\_webhook](#input\_slack\_webhook) | The URL of the slack webhook | `string` | `null` | no |
| <a name="input_sns_topic_name"></a> [sns\_topic\_name](#input\_sns\_topic\_name) | The name of the SNS topic to create | `string` | `"my-topic"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of tags to add to all resources | `map(string)` | <pre>{<br>  "Environment": "dev"<br>}</pre> | no |
| <a name="input_teams_webhook"></a> [teams\_webhook](#input\_teams\_webhook) | The URL of the teams webhook | `string` | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_sns_topic_arn"></a> [sns\_topic\_arn](#output\_sns\_topic\_arn) | The ARN of the SNS topic |
<!-- END_TF_DOCS -->