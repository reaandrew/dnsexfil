##################################
# EC2 Outputs
##################################

output "ec2_instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.dns_demo.id
}

output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.dns_demo.public_ip
}

output "ssh_connect_command" {
  description = "Example SSH command to connect to the EC2 instance"
  value       = "ssh ec2-user@${aws_instance.dns_demo.public_ip} -i ~/.ssh/id_rsa"
}

##################################
# VPC Outputs
##################################

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "subnet_id" {
  description = "ID of the public subnet"
  value       = aws_subnet.public_a.id
}

##################################
# DNS Logging / Firewall Outputs
##################################

output "dns_query_log_group" {
  description = "CloudWatch Log Group for DNS queries"
  value       = aws_cloudwatch_log_group.dns_query_logs.name
}

output "resolver_query_log_config_id" {
  description = "ID of the Route 53 Resolver Query-Log Config"
  value       = aws_route53_resolver_query_log_config.dns_logging.id
}

output "dns_firewall_rule_group_id" {
  description = "ID of the DNS Firewall Rule Group"
  value       = aws_route53_resolver_firewall_rule_group.default.id
}

output "dns_blocked_domains_list" {
  description = "Blocked domains in DNS firewall"
  value       = aws_route53_resolver_firewall_domain_list.blocked_domains.domains
}

##################################
# Athena / Logging S3 Outputs
# (comment these out if you haven't included athena_logs.tf)
##################################

output "dns_log_s3_bucket" {
  description = "S3 bucket where DNS logs land for Athena queries"
  value       = aws_s3_bucket.dns_log_bucket.bucket
}

output "athena_database" {
  description = "Glue database used by Athena"
  value       = aws_glue_catalog_database.dns_logs_db.name
}

output "athena_table" {
  description = "Glue table used by Athena"
  value       = aws_glue_catalog_table.resolver_dns_logs.name
}

##################################
# GuardDuty Outputs
##################################

output "guardduty_detector_id" {
  description = "GuardDuty detector ID"
  value       = aws_guardduty_detector.main.id
}

output "guardduty_findings_log_group" {
  description = "CloudWatch log group for GuardDuty DNS findings"
  value       = aws_cloudwatch_log_group.guardduty_findings.name
}

output "athena_workgroup" {
  description = "Athena workgroup for DNS analysis"
  value       = aws_athena_workgroup.dns_analysis.name
}

output "athena_results_bucket" {
  description = "S3 bucket for Athena query results"
  value       = aws_s3_bucket.athena_results.bucket
}
