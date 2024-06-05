mock_provider "aws" {}

run "basic" {
  command = plan

  variables {
    sns_topic_name = "my-topic"
    tags = {
      Environment = "dev"
    }
  }
}
