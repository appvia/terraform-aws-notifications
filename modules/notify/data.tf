
## Find the current AWS account ID
data "aws_caller_identity" "current" {}

## Find the current AWS partition
data "aws_partition" "current" {}

## Find the current AWS region 
data "aws_region" "current" {}

