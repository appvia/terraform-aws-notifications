# subscriptions example using appvia notifications
Assumes SNS topic already exists creating multiple instances of the notification module using subscription policies when
attaching the lambdas to allow for separating the events and posting separating to teams/slack and/or channels within
teams/slack.

Specifically, this example duplicates SecurityHub findings to an additional teams/slack channel webhook.

When deploying multiple instances of the module, you MUST override the name of the lambda to prevent conflict.

SNS subscriptions can filter messages received into the SNS topic: https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering.html.
These are called subscription policies, which can filter either SNS message (**_But, not SNS Message "Subject" surprisingly._**):
* MessageAttributes
* Body

To create the subscription policy, you need to understand more about the SNS event. Examples are provided in:
* "module/notify/functions/test/events" - for SNS message body
* "module/notify/functions/test/messages" - for SNS event - including "messageAttributes"

For this specific example, we are wanting to filter on Seucirty Hub events; the lambda filters these by checking the SNS subject line being ""
But given we cannot filter on subject, we have to inspect the message body:
```
{
  "FindingId": "arn:aws:securityhub:eu-west-2:123456789:subscription/nist-800-53/v/5.0.0/EC2.8/finding/89deac02-0ea8-49a2-a1e7-31b64bc037f2",
  "Description": "This control checks whether your Amazon Elastic Compute Cloud (Amazon EC2) instance metadata version is configured with Instance Metadata Service Version 2 (IMDSv2). The control passes if HttpTokens is set to required for IMDSv2. The control fails if HttpTokens is set to optional.",
  "GeneratorId": "nist-800-53/v/5.0.0/EC2.8",
  "Severity": "HIGH",
  "AccountName": "SupportProd",
  "Resources": [
      {
          "Partition": "aws",
          "Type": "AwsEc2Instance",
          "Details": {
              "AwsEc2Instance": {
                  "VpcId": "vpc-738575683784",
                  "MetadataOptions": {
                      "HttpPutResponseHopLimit": 2,
                      "HttpProtocolIpv6": "disabled",
                      "HttpTokens": "optional",
                      "InstanceMetadataTags": "disabled",
                      "HttpEndpoint": "enabled"
                  },
                  "VirtualizationType": "hvm",
                  "NetworkInterfaces": [
                      {
                          "NetworkInterfaceId": "eni-070adc8dad15224ce"
                      },
                      {
                          "NetworkInterfaceId": "eni-0beb2cc73e332cca7"
                      }
                  ],
                  "ImageId": "ami-7e78237da982",
                  "SubnetId": "subnet-7e782f2da982",
                  "LaunchedAt": "2024-02-15T11:41:53.000Z",
                  "Monitoring": {
                      "State": "disabled"
                  },
                  "IamInstanceProfileArn": "arn:aws:iam::123456789:instance-profile/eks-aaaabbbb-1111-1111-1111-fb829a08212d"
              }
          },
          "Region": "eu-west-2",
          "Id": "arn:aws:ec2:eu-west-2:123456789:instance/i-1111aa22222ddd333333",
          "Tags": {
              "aws:autoscaling:groupName": "eks-compute-aaaabbbb-1111-1111-1111-fb829a08212d",
              "aws:ec2:fleet-id": "fleet-aaaabbbb-1111-1111-1111-fb829a08212d",
              "k8s.io/cluster-autoscaler/ws-supp-portal-eks": "owned",
              "aws:eks:cluster-name": "cluster1-eks",
              "eks:cluster-name": "cluster1-eks",
              "aws:ec2launchtemplate:version": "1",
              "eks:nodegroup-name": "compute",
              "k8s.io/cluster-autoscaler/enabled": "true",
              "kubernetes.io/cluster/ws-supp-portal-eks": "owned",
              "aws:ec2launchtemplate:id": "lt-aaaa1111eeee8765e"
          }
      }
  ]
}
```
 
We simply need to ensure "FindingId" property exists; the policy is very simple
```
{
   "FindingId": [{ "exists": true }]
}
```

This example continues to send all events to the primary slack/teams channels. If you want to not send Security Hub events to
the primary channel, then simply create another subscription filter where `"FindingId": [{ "exists": false }]` and attach the primary notifications.

Create a `local.tfvars` with:
```
tags = {
  "tag1" = "value1"
}
sns_topic_name="<your SNS topic name>"
primary_teams_webhook="<your webhook url>
primary_slack_webhook="<your webhook url>
security_hub_teams_webhook="<your webhook url>
security_hub_slack_webhook="<your webhook url>
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
| <a name="input_primary_slack_webhook"></a> [primary\_slack\_webhook](#input\_primary\_slack\_webhook) | The default URL of the slack webhook | `string` | n/a | yes |
| <a name="input_primary_teams_webhook"></a> [primary\_teams\_webhook](#input\_primary\_teams\_webhook) | The default URL of the teams webhook | `string` | n/a | yes |
| <a name="input_security_hub_slack_webhook"></a> [security\_hub\_slack\_webhook](#input\_security\_hub\_slack\_webhook) | The URL of the slack webhook to post Security Hub only events | `string` | n/a | yes |
| <a name="input_security_hub_teams_webhook"></a> [security\_hub\_teams\_webhook](#input\_security\_hub\_teams\_webhook) | The URL of the teams webhook to post Security Hub only events | `string` | n/a | yes |
| <a name="input_sns_topic_name"></a> [sns\_topic\_name](#input\_sns\_topic\_name) | The name of the SNS topic to create | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of tags to add to all resources | `map(string)` | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_sns_topic_arn"></a> [sns\_topic\_arn](#output\_sns\_topic\_arn) | The ARN of the SNS topic |
<!-- END_TF_DOCS -->