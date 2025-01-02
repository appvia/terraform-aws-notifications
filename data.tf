
## Find the current AWS account ID
data "aws_caller_identity" "current" {}

## Find the current AWS region
data "aws_region" "current" {}

## Find the aws partition
data "aws_partition" "current" {}

## Provision an SNS IAM policy allowing the account root
data "aws_iam_policy_document" "current" {
  statement {
    sid    = "AllowAccountRoot"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = [format("arn:aws:iam::%s:root", local.account_id)]
    }
    actions = [
      "sns:Publish"
    ]
    resources = ["*"]
  }

  dynamic "statement" {
    for_each = var.allowed_aws_services

    content {
      sid    = "AllowService${index(var.allowed_aws_services, statement.value)}"
      effect = "Allow"
      principals {
        type        = "Service"
        identifiers = [statement.value]
      }
      actions = [
        "sns:Publish"
      ]
      resources = ["*"]
    }
  }

  dynamic "statement" {
    for_each = var.allowed_aws_principals

    content {
      sid    = "AllowPrincipal${index(var.allowed_aws_principals, statement.value)}"
      effect = "Allow"
      principals {
        type        = "AWS"
        identifiers = [statement.value]
      }
      actions = [
        "sns:Publish"
      ]
      resources = ["*"]
    }
  }
}

## Find the slack secret if required
data "aws_secretsmanager_secret" "slack" {
  count = local.enable_slack_secret ? 1 : 0

  name = var.slack.secret_name
}

## Find the latest version of the slack secret if required
data "aws_secretsmanager_secret_version" "slack" {
  count = local.enable_slack_secret ? 1 : 0

  secret_id = data.aws_secretsmanager_secret.slack[0].id
}

## Find the teams secret if required
data "aws_secretsmanager_secret" "teams" {
  count = local.enable_teams_secret ? 1 : 0

  name = var.teams.secret_name
}

## Find the latest version of the teams secret if required
data "aws_secretsmanager_secret_version" "teams" {
  count = local.enable_teams_secret ? 1 : 0

  secret_id = data.aws_secretsmanager_secret.teams[0].id
}
