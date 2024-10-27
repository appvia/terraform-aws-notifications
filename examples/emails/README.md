# Email example using appvia notifications

Create a `tfvars` local file with variables for:
```
email_addresses = ["<your mail1@address1.domain>"]
sns_topic_name  = "your new sns topic name!"
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
| <a name="input_email_addresses"></a> [email\_addresses](#input\_email\_addresses) | A list of target email addresses | `list(string)` | n/a | yes |
| <a name="input_sns_topic_name"></a> [sns\_topic\_name](#input\_sns\_topic\_name) | The name of the SNS topic to create | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_sns_topic_arn"></a> [sns\_topic\_arn](#output\_sns\_topic\_arn) | The ARN of the SNS topic |
<!-- END_TF_DOCS -->