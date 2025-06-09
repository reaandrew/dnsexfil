################################################################################
#  guardduty.tf  –  Enable GuardDuty for DNS exfiltration detection
################################################################################

# Enable GuardDuty detector
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = {
    Name = "dns-exfil-guardduty"
  }
}

# Enable runtime monitoring feature for GuardDuty
resource "aws_guardduty_detector_feature" "runtime_monitoring" {
  detector_id = aws_guardduty_detector.main.id
  name        = "RUNTIME_MONITORING"
  status      = "ENABLED"
}

# Optional: Create a CloudWatch Event Rule to capture GuardDuty findings
resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  name        = "guardduty-dns-findings"
  description = "Capture GuardDuty DNS-related findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
    detail = {
      type = [
        "Trojan:DNS/DNSDataExfiltration",
        "Recon:DNS/SubdomainQuery"
      ]
    }
  })
}

# CloudWatch Log Group for GuardDuty findings
resource "aws_cloudwatch_log_group" "guardduty_findings" {
  name              = "/aws/events/guardduty-dns-findings"
  retention_in_days = 30

  tags = {
    Name = "guardduty-dns-findings"
  }
}

# CloudWatch Event Target to send findings to logs
resource "aws_cloudwatch_event_target" "guardduty_logs" {
  rule      = aws_cloudwatch_event_rule.guardduty_findings.name
  target_id = "GuardDutyDNSFindings"
  arn       = aws_cloudwatch_log_group.guardduty_findings.arn
}

# IAM role for CloudWatch Events to write to logs
resource "aws_iam_role" "guardduty_events_role" {
  name = "guardduty-events-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "guardduty_events_policy" {
  name = "guardduty-events-policy"
  role = aws_iam_role.guardduty_events_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.guardduty_findings.arn}:*"
      }
    ]
  })
}