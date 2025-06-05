# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a DNS exfiltration detection system built on AWS that monitors Route 53 Resolver DNS logs to identify malicious DNS patterns. The system captures DNS queries, processes them through Amazon Athena, and can automatically block suspicious domains via Route 53 DNS Firewall.

## Architecture

The system consists of three main layers:

**Data Collection Layer:**
- Route 53 Resolver logs DNS queries directly to S3 (bypassing CloudWatch for performance)
- VPC-level DNS logging captures all DNS activity from EC2 instances
- S3 buckets store both raw DNS logs and Athena query results

**Analysis Layer:**
- AWS Glue provides schema management and Public Suffix List (PSL) data for accurate apex domain extraction
- Amazon Athena executes threat detection queries with 5-minute windows for real-time detection
- Three detection patterns: high-frequency queries, data encoding detection, and subdomain enumeration
- Lambda function automatically repairs table partitions when new log files arrive

**Response Layer:**
- Route 53 DNS Firewall automatically blocks domains identified as malicious
- GuardDuty integration provides additional threat detection
- CloudWatch monitoring tracks system health and query metrics

## Key Commands

### Infrastructure Management
```bash
# Build Lambda packages and deploy infrastructure
make deploy

# Plan infrastructure changes
make plan

# Build Lambda deployment packages
make build-lambdas

# Clean build artifacts
make clean

# Destroy all infrastructure
make destroy
```

### AWS Operations
All AWS commands use `aws-vault exec ee-sandbox --` prefix for credential management.

### Lambda Development
The build system automatically discovers Lambda functions in `lambdas/` subdirectories and creates deployment packages with proper dependency handling.

## Critical Implementation Details

**Public Suffix List Integration:** The system uses PSL data to correctly extract apex domains from complex DNS names (e.g., `data1.evil.example.co.uk` → `example.co.uk`). This prevents false positives from treating `co.uk` as the apex domain.

**Partition Management:** The partition-repair Lambda automatically runs `MSCK REPAIR TABLE` when new DNS log files arrive in S3, ensuring Athena can immediately query new data without manual intervention.

**Query Design:** Detection queries use deterministic ordering (`ORDER BY suffix_len DESC, ts DESC`) to ensure consistent results when processing duplicate FQDNs across multiple time periods.

**Time Windows:** 
- Exfiltration detection: 5-minute windows for Lambda automation
- Data encoding detection: 5-minute windows for real-time blocking  
- Subdomain enumeration: 24-hour windows for investigation/alerting

## Testing

Use `TESTING.md` for comprehensive testing procedures. Tests require:
- SSH access to EC2 instance: `ssh ec2-user@35.176.181.211 -i ~/.ssh/id_rsa`
- AWS Athena console access with workgroup: `dns-exfiltration-analysis`
- 5-10 minute wait time for DNS logs to appear in S3

## Directory Structure

- `infrastructure/` - Terraform configuration files
- `lambdas/partition-repair/` - S3 event-triggered partition repair function
- `scripts/` - Utility scripts (PSL data updates)
- `diagrams/` - Infrastructure visualization tools
- `TESTING.md` - Complete testing procedures and expected results