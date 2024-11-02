variable "architecture" {
  description = "Instruction set architecture for your Lambda function. Valid values are \"x86_64\" or \"arm64\"."
  type        = string
  default     = "arm64"
}

variable "python_runtime" {
  description = "The lambda python runtime"
  type        = string
  default     = "python3.12"
}

variable "powertools_layer_arn_suffix" {
  description = "The suffix of the ARN to use for AWS Powertools lambda layer (must match the architecture:https://docs.powertools.aws.dev/lambda/python/latest/."
  type        = string
  default     = "AWSLambdaPowertoolsPythonV2-Arm64:79"
}

variable "create" {
  description = "Whether to create all resources"
  type        = bool
  default     = true
}

variable "create_sns_topic" {
  description = "Whether to create new SNS topic"
  type        = bool
  default     = true
}

variable "lambda_role" {
  description = "IAM role attached to the Lambda Function.  If this is set then a role will not be created for you."
  type        = string
  default     = ""
}

variable "lambda_source_path" {
  description = "The source path of the custom Lambda function"
  type        = string
  default     = null
}

variable "lambda_dead_letter_target_arn" {
  description = "The ARN of an SNS topic or SQS queue to notify when an invocation fails."
  type        = string
  default     = null
}

variable "lambda_attach_dead_letter_policy" {
  description = "Controls whether SNS/SQS dead letter notification policy should be added to IAM role for Lambda Function"
  type        = bool
  default     = false
}

variable "sns_topic_name" {
  description = "The name of the SNS topic to create"
  type        = string
}

variable "sns_topic_kms_key_id" {
  description = "ARN of the KMS key used for enabling SSE on the topic"
  type        = string
  default     = ""
}

variable "enable_sns_topic_delivery_status_logs" {
  description = "Whether to enable SNS topic delivery status logs"
  type        = bool
  default     = false
}

variable "sns_topic_lambda_feedback_role_arn" {
  description = "IAM role for SNS topic delivery status logs.  If this is set then a role will not be created for you."
  type        = string
  default     = ""
}

variable "sns_topic_feedback_role_name" {
  description = "Name of the IAM role to use for SNS topic delivery status logging"
  type        = string
  default     = null
}

variable "sns_topic_feedback_role_description" {
  description = "Description of IAM role to use for SNS topic delivery status logging"
  type        = string
  default     = null
}

variable "sns_topic_feedback_role_path" {
  description = "Path of IAM role to use for SNS topic delivery status logging"
  type        = string
  default     = null
}

variable "sns_topic_feedback_role_force_detach_policies" {
  description = "Specifies to force detaching any policies the IAM role has before destroying it."
  type        = bool
  default     = true
}

variable "sns_topic_feedback_role_permissions_boundary" {
  description = "The ARN of the policy that is used to set the permissions boundary for the IAM role used by SNS topic delivery status logging"
  type        = string
  default     = null
}

variable "sns_topic_lambda_feedback_sample_rate" {
  description = "The percentage of successful deliveries to log"
  type        = number
  default     = 100
}

variable "kms_key_arn" {
  description = "ARN of the KMS key used for decrypting slack webhook url"
  type        = string
  default     = ""
}

variable "recreate_missing_package" {
  description = "Whether to recreate missing Lambda package if it is missing locally or not"
  type        = bool
  default     = true
}

variable "reserved_concurrent_executions" {
  description = "The amount of reserved concurrent executions for this lambda function. A value of 0 disables lambda from being triggered and -1 removes any concurrency limitations"
  type        = number
  default     = -1
}

variable "cloudwatch_log_group_retention_in_days" {
  description = "Specifies the number of days you want to retain log events in log group for Lambda."
  type        = number
  default     = 0
}

variable "cloudwatch_log_group_kms_key_id" {
  description = "The ARN of the KMS Key to use when encrypting log data for Lambda"
  type        = string
  default     = null
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
}

variable "iam_role_boundary_policy_arn" {
  description = "The ARN of the policy that is used to set the permissions boundary for the role"
  type        = string
  default     = null
}

variable "iam_role_name_prefix" {
  description = "A unique role name beginning with the specified prefix"
  type        = string
  default     = "lambda"
}

variable "iam_role_path" {
  description = "Path of IAM role to use for Lambda Function"
  type        = string
  default     = null
}

variable "iam_policy_path" {
  description = "Path of policies to that should be added to IAM role for Lambda Function"
  type        = string
  default     = null
}

variable "lambda_function_vpc_subnet_ids" {
  description = "List of subnet ids when Lambda Function should run in the VPC. Usually private or intra subnets."
  type        = list(string)
  default     = null
}

variable "lambda_function_vpc_security_group_ids" {
  description = "List of security group ids when Lambda Function should run in the VPC."
  type        = list(string)
  default     = null
}

variable "lambda_function_store_on_s3" {
  description = "Whether to store produced artifacts on S3 or locally."
  type        = bool
  default     = false
}

variable "lambda_function_s3_bucket" {
  description = "S3 bucket to store artifacts"
  type        = string
  default     = null
}

variable "lambda_function_ephemeral_storage_size" {
  description = "Amount of ephemeral storage (/tmp) in MB your Lambda Function can use at runtime. Valid value between 512 MB to 10,240 MB (10 GB)."
  type        = number
  default     = 512
}

variable "enable_slack" {
  description = "To send to slack, set to true"
  type        = bool
  default     = false
}

variable "enable_teams" {
  description = "To send to teams, set to true"
  type        = bool
  default     = false
}

variable "delivery_channels" {
  description = "The configuration for Slack notifications"
  type = map(object({
    lambda_name = optional(string, "delivery_channel")
    # The name of the lambda function to create
    lambda_description = optional(string, "Lambda function to send notifications")
    # The description for the lambda
    secret_name = optional(string)
    # An optional secret name in secrets manager to use for the slack configuration 
    webhook_url = optional(string)
    # The webhook url to post to
    filter_policy = optional(string)
    # An optional SNS subscription filter policy to apply
    filter_policy_scope = optional(string)
    # If filter policy provided this is the scope of that policy; either "MessageAttributes" (default) or "MessageBody"
  }))
  default = null
}

variable "aws_powertools_service_name" {
  description = "The service name to use"
  type        = string
  default     = "appvia-notifications"
}

variable "accounts_id_to_name" {
  description = "A mapping of account id and account name - used by notification lamdba to map an account ID to a human readable name"
  type        = map(string)
  default     = {}
}

variable "post_icons_url" {
  description = "URLs (not base64 encoded!) to publically available icons for highlighting posts of error and/or warning status. Ideally 50px square."
  type = object({
    error_url   = string
    warning_url = string
  })
  default = {
    error_url   = "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-attention-icon.png"
    warning_url = "https://raw.githubusercontent.com/appvia/terraform-aws-notifications/main/resources/posts-warning-icon.png"
  }
}

variable "identity_center_start_url" {
  description = "The start URL of your Identity Center instance"
  type        = string
  default     = null
}

variable "identity_center_role" {
  description = "The name of the role to use when redirecting through Identity Center"
  type        = string
  default     = null
}
