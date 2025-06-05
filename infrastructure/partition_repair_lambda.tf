################################################################################
# S3 Event + Lambda for Automatic Partition Repair
################################################################################

# IAM Role for Lambda
resource "aws_iam_role" "partition_repair_lambda_role" {
  name = "dns-partition-repair-lambda-role"

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

# IAM Policy for Lambda
resource "aws_iam_role_policy" "partition_repair_lambda_policy" {
  name = "dns-partition-repair-lambda-policy"
  role = aws_iam_role.partition_repair_lambda_role.id

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
          "athena:GetQueryResults"
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
          "glue:GetTable",
          "glue:GetPartitions"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda function code
resource "aws_lambda_function" "partition_repair" {
  filename         = "partition_repair.zip"
  function_name    = "dns-partition-repair"
  role            = aws_iam_role.partition_repair_lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.12"
  timeout         = 60

  source_code_hash = data.archive_file.partition_repair_zip.output_base64sha256

  environment {
    variables = {
      ATHENA_DATABASE = aws_glue_catalog_database.dns_logs_db.name
      ATHENA_WORKGROUP = aws_athena_workgroup.dns_analysis.name
      ATHENA_OUTPUT_LOCATION = "s3://${aws_s3_bucket.athena_results.bucket}/"
    }
  }

  tags = {
    Name = "dns-partition-repair"
  }
}

# Create Lambda deployment package
data "archive_file" "partition_repair_zip" {
  type        = "zip"
  output_path = "partition_repair.zip"
  source_dir  = "../lambdas/partition-repair"
}

# S3 bucket notification
resource "aws_s3_bucket_notification" "dns_log_notification" {
  bucket = aws_s3_bucket.dns_log_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.partition_repair.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "AWSLogs/"
    filter_suffix       = ".log.gz"
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}

# Permission for S3 to invoke Lambda
resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.partition_repair.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.dns_log_bucket.arn
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "partition_repair_logs" {
  name              = "/aws/lambda/dns-partition-repair"
  retention_in_days = 7

  tags = {
    Name = "dns-partition-repair-logs"
  }
}