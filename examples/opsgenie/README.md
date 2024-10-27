# http endpoint only example using appvia notifications
This examples assumes the SNS topic already exists; create topic in target account/region.

This examples assumes an HTTPS endpoint; for test/example, you can create a lambda in target account/region and log the "event" to console, create a function URL with public access. Then after the plan as applied, check in cloudwatch for lambda logs the `SubscribeURL` attribute of the JSON payload. Copy that URL, and then in SNS topic, under select the pending subscription and "Confirm Subscription"; paste the "SubscribeURL".

Create a `tfvars` local file with variables for:
```
opsgenie_endpoint = "https://your url"
sns_topic_name    = "your existing sns topic name!"
```

Then:
```
terraform init
AWS_PROFILE=<profile name> terraform apply --var-file=./<your vars>.tfvars
```

And to delete:
```
AWS_PROFILE=<profile name> terraform destroy --var-file=./<your vars>.tfvars
```

<!-- BEGIN_TF_DOCS -->
## Providers

No providers.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_sns_topic_name"></a> [sns\_topic\_name](#input\_sns\_topic\_name) | The name of the SNS topic to create | `string` | n/a | yes |
| <a name="input_opsgenie_endpoint"></a> [opsgenie\_endpoint](#input\_opsgenie\_endpoint) | The opsgenie api endpoint url | `string` | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_sns_topic_arn"></a> [sns\_topic\_arn](#output\_sns\_topic\_arn) | The ARN of the SNS topic |
<!-- END_TF_DOCS -->