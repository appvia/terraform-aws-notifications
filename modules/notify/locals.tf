locals {
  # Filter only enabled policies
  enabled_policies = {
    for k, v in var.lambda_policy_config : k => v
    if v.enabled
  }

  # CPU architecture mapping
  architectures = {
    x86_64 = "amd64"
    arm64  = "arm64"
  }

  # AWS Managed Layer ARN patterns with architecture support
  aws_managed_layers = {
    powertools = {
      account_id = "017000801446"
      name_pattern = "AWSLambdaPowertoolsPythonV2-%ARCH%"
      arch_specific = true
    }
    parameters_secrets = {
      account_id = "133256977650"
      name_pattern = "AWS-Parameters-and-Secrets-Lambda-Extension-%ARCH%"
      arch_specific = true
    }
    # Add more AWS managed layers as needed
  }

  # Process layer ARNs based on configuration
  processed_layers = {
    for name, config in var.lambda_layers_config :
    name => {
      enabled = try(config.enabled, true)
      arn = try(
        # If ARN is directly provided, use it
        config.arn,
        # If it's a managed layer, construct the ARN using the managed layer pattern
        config.type == "managed" ? (
          "arn:aws:lambda:${config.region != null ? config.region : data.aws_region.current.name}:${local.aws_managed_layers[config.name].account_id}:layer:${
            local.aws_managed_layers[config.name].arch_specific ?
            replace(local.aws_managed_layers[config.name].name_pattern, "%ARCH%", local.architectures[var.architecture]) :
            local.aws_managed_layers[config.name].name_pattern
          }${config.version != null ? ":${config.version}" : ""}"
        ) : null
      )
    }
  }

  # Generate final list of enabled layer ARNs
  enabled_layers = [
    for name, layer in local.processed_layers :
    layer.arn
    if layer.enabled && layer.arn != null
  ]
}
