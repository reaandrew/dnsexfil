################################################################################
# Scheduled Threat Detection Lambda for DNS Firewall Automation
################################################################################

# IAM Role for Threat Detection Lambda
resource "aws_iam_role" "threat_detection_lambda_role" {
  name = "dns-threat-detection-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Threat Detection Lambda
resource "aws_iam_role_policy" "threat_detection_lambda_policy" {
  name = "dns-threat-detection-lambda-policy"
  role = aws_iam_role.threat_detection_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:ListNamedQueries",
          "athena:GetNamedQuery"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:ListBucketMultipartUploads",
          "s3:AbortMultipartUpload",
          "s3:ListMultipartUploadParts"
        ]
        Resource = [
          aws_s3_bucket.athena_results.arn,
          "${aws_s3_bucket.athena_results.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.dns_log_bucket.arn,
          "${aws_s3_bucket.dns_log_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "route53resolver:GetFirewallDomainList",
          "route53resolver:ListFirewallDomains",
          "route53resolver:UpdateFirewallDomains"
        ]
        Resource = aws_route53_resolver_firewall_domain_list.blocked_domains.arn
      },
      {
        Effect = "Allow"
        Action = [
          "glue:GetTable",
          "glue:GetPartitions"
        ]
        Resource = "*"
      }
    ]
  })
}

# Threat Detection Lambda Function
resource "aws_lambda_function" "threat_detection" {
  filename         = "threat_detection.zip"
  function_name    = "dns-threat-detection"
  role            = aws_iam_role.threat_detection_lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.12"
  timeout         = 300  # 5 minutes timeout for Athena queries

  source_code_hash = data.archive_file.threat_detection_zip.output_base64sha256

  environment {
    variables = {
      ATHENA_DATABASE = aws_glue_catalog_database.dns_logs_db.name
      ATHENA_WORKGROUP = aws_athena_workgroup.dns_analysis.name
      ATHENA_OUTPUT_LOCATION = "s3://${aws_s3_bucket.athena_results.bucket}/"
      FIREWALL_DOMAIN_LIST_ID = aws_route53_resolver_firewall_domain_list.blocked_domains.id
    }
  }

  tags = {
    Name = "dns-threat-detection"
  }
}

# Create Lambda deployment package
data "archive_file" "threat_detection_zip" {
  type        = "zip"
  output_path = "threat_detection.zip"
  source_dir  = "../lambdas/threat-detection"
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "threat_detection_logs" {
  name              = "/aws/lambda/dns-threat-detection"
  retention_in_days = 30

  tags = {
    Name = "dns-threat-detection-logs"
  }
}

# CloudWatch Events Rule - Run every minute
resource "aws_cloudwatch_event_rule" "threat_detection_schedule" {
  name                = "dns-threat-detection-schedule"
  description         = "Trigger DNS threat detection Lambda every minute"
  schedule_expression = "rate(1 minute)"

  tags = {
    Name = "dns-threat-detection-schedule"
  }
}

# CloudWatch Events Target
resource "aws_cloudwatch_event_target" "threat_detection_target" {
  rule      = aws_cloudwatch_event_rule.threat_detection_schedule.name
  target_id = "ThreatDetectionLambdaTarget"
  arn       = aws_lambda_function.threat_detection.arn
}

# Permission for CloudWatch Events to invoke Lambda
resource "aws_lambda_permission" "allow_cloudwatch_to_call_threat_detection" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.threat_detection.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.threat_detection_schedule.arn
}