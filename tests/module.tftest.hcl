mock_provider "aws" {}

run "input_validation_fail" {
  command = plan

  variables {
    sns_topic_name = "BAD topic_name"
    tags = {}
    email                = {
      addresses = [
        "email1@mail.com",
        "email11",
        "email2@mail.com"
      ]
    }
    allowed_aws_services = [
      "config.amazonaws.com",
      "cloudwatch.amazonaws.com",
      "cloudtrail.amazon.com"
    ]
    allowed_aws_principals = [
      "123AB245",
      "111143553",
      "1546745667",
    ]
  }

  expect_failures = [
    var.sns_topic_name,
    var.allowed_aws_principals,
    var.allowed_aws_services,
    var.email
  ]
}

run "unit_test_create_sns_topic" {
  command = plan

  # note to self - merge global tags with unit test tags
  variables {
    tags = {
      UT_tag_1 = "ut-tag-1"
    }
    sns_topic_name = "unit-test-topic"
    allowed_aws_services = ["cloudwatch.amazonaws.com", "cloudtrail.amazonaws.com"]
    create_sns_topic     = true
    slack = {
      webhook_url = "https://hooks.slack.com/services/..."
    }
  }

  assert {
    condition = aws_sns_topic_subscription.subscribers == {}
    error_message = "Expected an empty set of general subscribers"
  }

  assert {
    condition  = aws_sns_topic_subscription.email == {}
    error_message = "Expected an empty set of email subscribers"
  }
}

run "unit_test_sns_email_subscriptions" {
  command = plan

  # note to self - merge global tags with unit test tags
  variables {
    tags                = {
                            UT_tag_1 = "ut-tag-1"
                          }
    sns_topic_name       = "unit-test-topic"
    allowed_aws_services = ["cloudwatch.amazonaws.com", "cloudtrail.amazonaws.com"]
    create_sns_topic     = true

    # duplicate email addresses here is intentional test - to assert set dedup
    email                = {
      addresses      = [
        "email1@_example.com",
        "email1111@_example.com",
        "email1@_example.com",
      ]
    }
  }

  assert {
    condition = aws_sns_topic_subscription.subscribers == {}
    error_message = "Expected an empty set of general subscribers"
  }

  assert {
    condition  = length(aws_sns_topic_subscription.email) == 2
    error_message = "Expected an empty set of email subscribers"
  }

  assert {
    condition  = aws_sns_topic_subscription.email["email1111@_example.com"].endpoint == "email1111@_example.com"
    error_message = "Expected an empty set of email subscribers"
  }
  assert {
    condition  = aws_sns_topic_subscription.email["email1111@_example.com"].protocol == "email"
    error_message = "Expected an empty set of email subscribers"
  }
  assert {
    condition  = aws_sns_topic_subscription.email["email1@_example.com"].endpoint == "email1@_example.com"
    error_message = "Expected an empty set of email subscribers"
  }
  assert {
    condition  = aws_sns_topic_subscription.email["email1@_example.com"].protocol == "email"
    error_message = "Expected an empty set of email subscribers"
  }
}

run "unit_test_sns_general_subscriptions" {
  command = plan

  # note to self - merge global tags with unit test tags
  variables {
    tags                = {
                            UT_tag_1 = "ut-tag-1"
                          }
    sns_topic_name       = "unit-test-topic"
    allowed_aws_services = ["cloudwatch.amazonaws.com", "cloudtrail.amazonaws.com"]
    create_sns_topic     = true
    subscribers          = {
      "sub1" = {
        protocol               = "http"
        endpoint               = "http://url1.com/endpoint111"
        endpoint_auto_confirms = false
        raw_message_delivery   = true
      }
      "sub2" = {
        protocol               = "lambda"
        endpoint               = "arn:aws:sqs:eu-west-1:111122111:function:my-lamba-func"
        endpoint_auto_confirms = true
        raw_message_delivery   = false
      }
    }
  }

  assert {
    condition = aws_sns_topic_subscription.email == {}
    error_message = "Expected an empty set of general subscribers"
  }
  assert {
    condition  = length(aws_sns_topic_subscription.subscribers) == 2
    error_message = "Expected an empty set of email subscribers"
  }
  assert {
    condition  = aws_sns_topic_subscription.subscribers["sub1"].endpoint == "http://url1.com/endpoint111"
    error_message = "Expected an empty set of email subscribers"
  }
  assert {
    condition  = aws_sns_topic_subscription.subscribers["sub1"].protocol == "http"
    error_message = "Expected an empty set of email subscribers"
  }
  assert {
    condition  = aws_sns_topic_subscription.subscribers["sub2"].endpoint == "arn:aws:sqs:eu-west-1:111122111:function:my-lamba-func"
    error_message = "Expected an empty set of email subscribers"
  }
  assert {
    condition  = aws_sns_topic_subscription.subscribers["sub2"].protocol == "lambda"
    error_message = "Expected an empty set of email subscribers"
  }
}
