################################################################################
#  dns_logs_athena.tf  –  Route 53 Resolver DNS logs → S3 directly for Athena
################################################################################

# Get current AWS account ID
data "aws_caller_identity" "current" {}

##############################
# S3 Bucket for DNS Logs
##############################
resource "aws_s3_bucket" "dns_log_bucket" {
  bucket        = "dnsexfil-demo-athena-logs"
  force_destroy = true

  # Remove the object_ownership block if your provider < 5.29
  # (new buckets are BucketOwnerEnforced by default)
  # If you later upgrade provider: use the block again or add a separate
  # aws_s3_bucket_ownership_controls resource.

  tags = {
    Name = "dns-query-logs-s3"
  }
}

# Note: Route 53 Resolver logs directly to S3, no Firehose needed

#####################################
# S3 Bucket for Athena Query Results
#####################################
resource "aws_s3_bucket" "athena_results" {
  bucket        = "dnsexfil-demo-athena-results"
  force_destroy = true

  tags = {
    Name = "athena-query-results"
  }
}

#####################################
# Athena Workgroup with Query Results Location
#####################################
resource "aws_athena_workgroup" "dns_analysis" {
  name = "dns-exfiltration-analysis"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.bucket}/"
      
      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }

  tags = {
    Name = "dns-exfiltration-workgroup"
  }
}

#####################################
# Glue Database & Table for Athena
#####################################
resource "aws_glue_catalog_database" "dns_logs_db" {
  name = "dns_logs_db"
}

resource "aws_glue_catalog_table" "resolver_dns_logs" {
  name          = "resolver_dns_logs"
  database_name = aws_glue_catalog_database.dns_logs_db.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.dns_log_bucket.bucket}/AWSLogs/${data.aws_caller_identity.current.account_id}/vpcdnsquerylogs/${aws_vpc.main.id}/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      serialization_library = "org.openx.data.jsonserde.JsonSerDe"
    }

    # Direct Route 53 Resolver logs schema (AWS documented format)
    columns {
      name = "version"
      type = "string"
    }
    columns {
      name = "account_id"
      type = "string"
    }
    columns {
      name = "region"
      type = "string"
    }
    columns {
      name = "vpc_id"
      type = "string"
    }
    columns {
      name = "query_timestamp"
      type = "string"
    }
    columns {
      name = "query_name"
      type = "string"
    }
    columns {
      name = "query_type"
      type = "string"
    }
    columns {
      name = "query_class"
      type = "string"
    }
    columns {
      name = "rcode"
      type = "string"
    }
    columns {
      name = "answers"
      type = "array<struct<Rdata:string,Type:string,Class:string>>"
    }
    columns {
      name = "srcaddr"
      type = "string"
    }
    columns {
      name = "srcport"
      type = "int"
    }
    columns {
      name = "transport"
      type = "string"
    }
    columns {
      name = "srcids"
      type = "struct<instance:string,resolver_endpoint:string>"
    }
    columns {
      name = "firewall_rule_action"
      type = "string"
    }
    columns {
      name = "firewall_rule_group_id"
      type = "string"
    }
    columns {
      name = "firewall_domain_list_id"
      type = "string"
    }
  }
}

# Public Suffix List table for proper apex domain extraction
resource "aws_glue_catalog_table" "public_suffixes" {
  name          = "public_suffixes"
  database_name = aws_glue_catalog_database.dns_logs_db.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.dns_log_bucket.bucket}/psl/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"
      parameters = {
        "field.delim" = ","
      }
    }

    columns {
      name = "suffix"
      type = "string"
    }
    columns {
      name = "labels"
      type = "int"
    }
  }
}

#####################################
# Saved Queries for DNS Analysis
#####################################

resource "aws_athena_named_query" "dns_exfiltration_detection" {
  name        = "DNS Exfiltration Detection"
  description = "Detects high frequency DNS queries to apex domains indicating data exfiltration"
  database    = aws_glue_catalog_database.dns_logs_db.name
  workgroup   = aws_athena_workgroup.dns_analysis.name

  query = <<-EOT
WITH dns AS (
  SELECT
    lower(trim(TRAILING '.' FROM query_name)) AS fqdn,
    srcaddr,
    from_iso8601_timestamp(query_timestamp) AS ts
  FROM dns_logs_db.resolver_dns_logs
  WHERE from_iso8601_timestamp(query_timestamp) >= CURRENT_TIMESTAMP - INTERVAL '5' MINUTE
),
parts AS (
  SELECT
    fqdn,
    srcaddr,
    ts,
    split(fqdn, '.') AS labels
  FROM dns
),
match AS (
  SELECT
    p.*,
    s.suffix,
    s.labels AS suffix_len
  FROM parts p
  JOIN dns_logs_db.public_suffixes s
    ON (p.fqdn LIKE '%.' || s.suffix OR p.fqdn = s.suffix)
),
best AS (
  SELECT *
  FROM (
    SELECT *, 
           row_number() OVER (PARTITION BY fqdn ORDER BY suffix_len DESC, ts DESC) AS rn
    FROM match
  )
  WHERE rn = 1
)
SELECT
  CASE 
    WHEN cardinality(labels) > suffix_len THEN
      concat(
        element_at(labels, cardinality(labels) - suffix_len),
        '.', suffix
      )
    ELSE suffix
  END AS apex_domain,
  count(*) AS query_count,
  count(DISTINCT srcaddr) AS source_count,
  count(DISTINCT fqdn) AS unique_subdomains,
  min(ts) AS first_seen,
  max(ts) AS last_seen,
  'HIGH_FREQUENCY' AS threat_type,
  CASE 
    WHEN count(*) > 100 THEN 'CRITICAL'
    WHEN count(*) > 50 THEN 'HIGH' 
    WHEN count(*) > 20 THEN 'MEDIUM'
    ELSE 'LOW'
  END AS severity
FROM best
WHERE cardinality(labels) > suffix_len + 1  -- Only domains with subdomains (not direct apex queries)
GROUP BY 
  CASE 
    WHEN cardinality(labels) > suffix_len THEN
      concat(element_at(labels, cardinality(labels) - suffix_len), '.', suffix)
    ELSE suffix
  END
HAVING count(*) > 20  -- Threshold for 5-minute window
ORDER BY query_count DESC
LIMIT 50;
EOT
}

resource "aws_athena_named_query" "dns_data_encoding_detection" {
  name        = "DNS Data Encoding Detection"
  description = "Detects encoded data in DNS subdomain names (Base64, Hex patterns)"
  database    = aws_glue_catalog_database.dns_logs_db.name
  workgroup   = aws_athena_workgroup.dns_analysis.name

  query = <<-EOT
WITH dns AS (
  SELECT
    lower(trim(TRAILING '.' FROM query_name)) AS fqdn,
    srcaddr,
    from_iso8601_timestamp(query_timestamp) AS ts,
    split(lower(trim(TRAILING '.' FROM query_name)), '.') AS labels
  FROM dns_logs_db.resolver_dns_logs
  WHERE from_iso8601_timestamp(query_timestamp) >= CURRENT_TIMESTAMP - INTERVAL '5' MINUTE
),
apex_domains AS (
  SELECT 
    fqdn,
    srcaddr,
    ts,
    labels,
    element_at(labels, 1) AS first_label,
    CASE 
      WHEN cardinality(labels) >= 3 THEN
        concat(element_at(labels, cardinality(labels) - 1), '.', element_at(labels, cardinality(labels)))
      ELSE fqdn
    END AS apex_domain
  FROM dns
  WHERE length(element_at(labels, 1)) > 15  -- Focus on long subdomains
)
SELECT 
  apex_domain,
  count(*) AS query_count,
  count(DISTINCT srcaddr) AS source_count,
  count(DISTINCT first_label) AS unique_encoded_values,
  min(ts) AS first_seen,
  max(ts) AS last_seen,
  CASE 
    WHEN avg(length(first_label)) > 30 THEN 'DATA_ENCODING'
    ELSE 'LONG_SUBDOMAIN'
  END AS threat_type,
  CASE 
    WHEN count(*) > 50 THEN 'CRITICAL'
    WHEN count(*) > 20 THEN 'HIGH'
    WHEN count(*) > 10 THEN 'MEDIUM'
    ELSE 'LOW'
  END AS severity,
  round(avg(length(first_label))) AS avg_label_length,
  array_agg(DISTINCT 
    CASE 
      WHEN regexp_like(first_label, '^[A-Fa-f0-9]{16,}$') THEN 'HEX'
      WHEN regexp_like(first_label, '^[A-Za-z0-9+/]{16,}={0,2}$') THEN 'BASE64'
      ELSE 'UNKNOWN'
    END
  ) AS encoding_patterns
FROM apex_domains
GROUP BY apex_domain
HAVING count(*) > 5  -- Lower threshold for encoding detection
ORDER BY query_count DESC, avg_label_length DESC
LIMIT 25;
EOT
}

resource "aws_athena_named_query" "subdomain_enumeration" {
  name        = "Subdomain Enumeration Detection"
  description = "Detects high numbers of unique subdomains per apex domain - potential reconnaissance"
  database    = aws_glue_catalog_database.dns_logs_db.name
  workgroup   = aws_athena_workgroup.dns_analysis.name

  query = <<-EOT
WITH dns AS (
  SELECT
    lower(trim(TRAILING '.' FROM query_name)) AS fqdn,
    srcaddr,
    from_iso8601_timestamp(query_timestamp) AS ts
  FROM dns_logs_db.resolver_dns_logs
  WHERE from_iso8601_timestamp(query_timestamp) >= CURRENT_TIMESTAMP - INTERVAL '24' HOUR
),
aggregated AS (
  SELECT 
    fqdn,
    count(*) as query_count,
    count(DISTINCT srcaddr) as source_count,
    min(ts) as first_seen,
    max(ts) as last_seen,
    split(fqdn, '.') AS labels
  FROM dns
  GROUP BY fqdn
),
match AS (
  SELECT
    a.*,
    s.suffix,
    s.labels AS suffix_len
  FROM aggregated a
  JOIN dns_logs_db.public_suffixes s
    ON (a.fqdn LIKE '%.' || s.suffix OR a.fqdn = s.suffix)
),
best AS (
  SELECT *
  FROM (
    SELECT *, 
           row_number() OVER (PARTITION BY fqdn ORDER BY suffix_len DESC) AS rn
    FROM match
  )
  WHERE rn = 1
)
SELECT
  CASE 
    WHEN cardinality(labels) > suffix_len THEN
      concat(element_at(labels, cardinality(labels) - suffix_len), '.', suffix)
    ELSE suffix
  END AS apex_domain,
  count(DISTINCT fqdn) AS unique_subdomains,
  sum(query_count) AS total_queries,
  max(source_count) AS source_count,
  min(first_seen) AS first_seen,
  max(last_seen) AS last_seen
FROM best
WHERE cardinality(labels) > suffix_len + 1
GROUP BY 
  CASE 
    WHEN cardinality(labels) > suffix_len THEN
      concat(element_at(labels, cardinality(labels) - suffix_len), '.', suffix)
    ELSE suffix
  END
HAVING count(DISTINCT fqdn) > 5
ORDER BY unique_subdomains DESC
LIMIT 50;
EOT
}

