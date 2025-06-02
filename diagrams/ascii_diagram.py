#!/usr/bin/env python3
"""
ASCII Art diagram approach for creating infrastructure diagrams
that work in any terminal without graphical dependencies.

This creates text-based diagrams that can be embedded in documentation,
displayed in terminals, or included in code comments.
"""

def create_aws_infrastructure_ascii():
    """Create ASCII art representation of AWS infrastructure."""
    
    diagram = """
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                          AWS DNS Exfiltration Detection Infrastructure                   ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    VPC (10.0.0.0/16)                                   │
│                                                                                         │
│  ┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐        │
│  │                 │   DNS   │                  │ Firewall│                 │        │
│  │   EC2 Instance  │ Queries │ Route 53 Resolver│  Check  │  DNS Firewall   │        │
│  │   (m5.large)    │────────▶│                  │────────▶│                 │        │
│  │                 │         │                  │         │                 │        │
│  └─────────────────┘         └──────────────────┘         └─────────────────┘        │
│                                        │                           │                  │
│                                        │ Query Logs               │ Block Events     │
│                                        ▼                           ▼                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                         │                           │
                                         ▼                           ▼
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│   S3 Bucket     │ Schema  │   AWS Glue       │ Query   │  CloudWatch     │
│  (DNS Logs)     │ Defn.   │   Catalog        │ Engine  │    Logs         │
│                 │────────▶│                  │────────▶│                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                         │
                                         ▼
                            ┌──────────────────┐         ┌─────────────────┐
                            │                  │ Results │                 │
                            │  Amazon Athena   │────────▶│   S3 Bucket     │
                            │  (Analytics)     │         │ (Query Results) │
                            │                  │         │                 │
                            └──────────────────┘         └─────────────────┘

Legend:
═══════════════════════════════════════════════════════════════════════════════════════════
🟠 Compute & Analytics:  EC2, Athena, Glue, CloudWatch
🟢 Storage Services:     S3 Buckets
🔵 Network Services:     VPC, Route 53 Resolver  
🔴 Security Services:    DNS Firewall

Data Flow:
───────────────────────────────────────────────────────────────────────────────────────────
1. EC2 instance makes DNS queries
2. Route 53 Resolver processes queries and logs to S3
3. DNS Firewall performs real-time threat blocking
4. Glue Catalog defines schema for stored logs
5. Athena analyzes logs for threat patterns
6. Results stored in S3 for further investigation

Detection Methods:
───────────────────────────────────────────────────────────────────────────────────────────
• High Frequency Analysis:    >20 queries per apex domain in 5-minute window
• Data Encoding Detection:    Base64/Hex patterns in subdomain names  
• Subdomain Enumeration:      >5 unique subdomains per apex domain
"""
    return diagram

def create_threat_detection_ascii():
    """Create ASCII timeline of threat detection process."""
    
    timeline = """
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                            DNS Exfiltration Detection Timeline                           ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

Time:     T+0        T+1        T+2        T+3        T+4        T+5        T+6
          │          │          │          │          │          │          │
          ▼          ▼          ▼          ▼          ▼          ▼          ▼

     ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
     │ 🔴 Mal. │ │ 🟠 High │ │ 🔵 DNS  │ │ 🔴 Real │ │ 🟢 Logs │ │ 🟠 Query│ │ 🔴 Alert│
     │ Actor   │ │ Freq.   │ │Resolver │ │  Time   │ │ to S3   │ │Analysis │ │Generated│
     │ Starts  │ │ DNS     │ │ Logs    │ │Firewall │ │ for     │ │ Detects │ │  for    │
     │ Exfil.  │ │Queries  │ │Queries  │ │ Blocks  │ │Analysis │ │Patterns │ │ Invest. │
     └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘

═════════════════════════════════════════════════════════════════════════════════════════════
                              Prevention & Detection Layers
═════════════════════════════════════════════════════════════════════════════════════════════

Layer 1: Real-time DNS Firewall
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ • Blocks known malicious domains immediately                                           │
│ • Uses static blocklists and threat intelligence                                       │
│ • Response time: < 1 second                                                            │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Layer 2: Behavioral Analysis (Athena Queries)
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ Query Type 1: High Frequency Detection                                                 │
│ ┌─ SELECT apex_domain, count(*) as query_count                                        │
│ │  FROM dns_logs WHERE timestamp > now() - 5min                                       │
│ └─ HAVING count(*) > 20                                                               │
│                                                                                         │
│ Query Type 2: Data Encoding Detection                                                  │
│ ┌─ SELECT fqdn FROM dns_logs                                                          │
│ │  WHERE regexp_like(subdomain, '^[A-Za-z0-9+/]{16,}={0,2}$')  -- Base64             │
│ └─ OR regexp_like(subdomain, '^[A-Fa-f0-9]{16,}$')             -- Hex                │
│                                                                                         │
│ Query Type 3: Subdomain Enumeration                                                    │
│ ┌─ SELECT apex_domain, count(DISTINCT subdomain) as unique_subs                       │
│ │  FROM dns_logs GROUP BY apex_domain                                                  │
│ └─ HAVING count(DISTINCT subdomain) > 5                                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Severity Levels:
┌─────────────┬─────────────────┬─────────────────────────────────────────────────────────┐
│   Level     │   Threshold     │                    Response                             │
├─────────────┼─────────────────┼─────────────────────────────────────────────────────────┤
│ 🔴 CRITICAL │ >100 queries    │ Immediate investigation, potential blocking             │
│ 🟠 HIGH     │ >50 queries     │ Alert security team, monitor closely                   │
│ 🟡 MEDIUM   │ >20 queries     │ Log for analysis, trend monitoring                      │
│ 🟢 LOW      │ <20 queries     │ Normal logging, baseline establishment                  │
└─────────────┴─────────────────┴─────────────────────────────────────────────────────────┘
"""
    return timeline

def create_data_flow_ascii():
    """Create ASCII representation of data flow architecture."""
    
    data_flow = """
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                                DNS Exfiltration Data Flow                                ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

🏢 Enterprise Network                          ☁️  AWS Cloud Infrastructure
┌─────────────────────────┐                   ┌─────────────────────────────────────────────┐
│                         │                   │                                             │
│  💻 Compromised Host    │ DNS Queries       │  🌐 Route 53 Resolver                      │
│     ┌─────────────────┐ │  ┌─────────────┐  │     ┌─────────────────────────────────────┐ │
│     │ Malware Process │ │  │ Encoded     │  │     │ Query: abc123def.evil.com          │ │
│     │ ┌─────────────┐ │ │  │ Data:       │  │     │ Type: A                             │ │
│     │ │ Data:       │ │ │  │ YWJjMTIz... │  │     │ Source: 10.0.1.100                 │ │
│     │ │ "secret123" │ │ │──┤ ZGVm...     │──┼─────│ Timestamp: 2024-01-01T10:30:00Z    │ │
│     │ │             │ │ │  │ evil.com    │  │     └─────────────────────────────────────┘ │
│     │ └─────────────┘ │ │  └─────────────┘  │                        │                    │
│     └─────────────────┘ │                   │                        ▼                    │
│                         │                   │  📊 Log Entry (JSON)                       │
└─────────────────────────┘                   │     ┌─────────────────────────────────────┐ │
                                              │     │ {                                   │ │
                                              │     │   "query_name": "abc123def.evil.com"│ │
                                              │     │   "query_type": "A",                │ │
                                              │     │   "srcaddr": "10.0.1.100",         │ │
                                              │     │   "query_timestamp": "2024-01-..."  │ │
                                              │     │ }                                   │ │
                                              │     └─────────────────────────────────────┘ │
                                              │                        │                    │
                                              │                        ▼                    │
                                              │  🪣 S3 Bucket (DNS Logs)                   │
                                              │     /AWSLogs/123456789/vpcdnsquerylogs/    │
                                              │     └── vpc-abc123/                        │
                                              │         └── 2024/01/01/                    │
                                              │             └── dns_logs.json              │
                                              └─────────────────────────────────────────────┘
                                                                 │
                                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            🔍 Athena Analysis Engine                                    │
│                                                                                         │
│  Query 1: Frequency Analysis                  Query 2: Encoding Detection              │
│  ┌───────────────────────────────────────┐   ┌───────────────────────────────────────┐ │
│  │ WITH apex_domains AS (                │   │ SELECT query_name FROM dns_logs       │ │
│  │   SELECT domain, count(*) as freq     │   │ WHERE regexp_like(                    │ │
│  │   FROM dns_logs                       │   │   split_part(query_name,'.',1),       │ │
│  │   WHERE ts > now() - 5min             │   │   '^[A-Za-z0-9+/]{16,}={0,2}$'        │ │
│  │   GROUP BY domain                     │   │ )  -- Base64 pattern                  │ │
│  │ )                                     │   │ OR regexp_like(                       │ │
│  │ SELECT * FROM apex_domains            │   │   split_part(query_name,'.',1),       │ │
│  │ WHERE freq > 20                       │   │   '^[A-Fa-f0-9]{16,}$'                │ │
│  │ ORDER BY freq DESC                    │   │ )  -- Hex pattern                     │ │
│  └───────────────────────────────────────┘   └───────────────────────────────────────┘ │
│                                                                                         │
│  Results:                                     Results:                                 │
│  ┌───────────────────────────────────────┐   ┌───────────────────────────────────────┐ │
│  │ evil.com: 47 queries (HIGH)           │   │ abc123def.evil.com (Base64 detected)  │ │
│  │ bad-site.net: 31 queries (MEDIUM)     │   │ ZGF0YWV4Zmlsc.attacker.org           │ │
│  │ malware.org: 89 queries (CRITICAL)    │   │ 48656c6c6f576f726c64.hex.com         │ │
│  └───────────────────────────────────────┘   └───────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                        🚨 Security Alert Generated
                        ┌─────────────────────────────┐
                        │ THREAT DETECTED             │
                        │ Domain: evil.com            │
                        │ Pattern: High Frequency     │
                        │ Severity: CRITICAL          │
                        │ Action: Investigate         │
                        └─────────────────────────────┘
"""
    return data_flow

def save_ascii_diagrams():
    """Save all ASCII diagrams to files."""
    
    diagrams = {
        'infrastructure': create_aws_infrastructure_ascii(),
        'timeline': create_threat_detection_ascii(),
        'data_flow': create_data_flow_ascii()
    }
    
    for name, diagram in diagrams.items():
        filename = f'/media/psf/Home/vmshare/dnsexfil/diagrams/ascii_{name}.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(diagram)
        print(f"ASCII diagram saved to: {filename}")

def display_ascii_diagrams():
    """Display all ASCII diagrams in terminal."""
    
    print("\n" + "="*90)
    print("ASCII INFRASTRUCTURE DIAGRAMS")
    print("="*90)
    
    print(create_aws_infrastructure_ascii())
    print("\n" + "="*90)
    print(create_threat_detection_ascii())
    print("\n" + "="*90)
    print(create_data_flow_ascii())

if __name__ == "__main__":
    # Display diagrams in terminal
    display_ascii_diagrams()
    
    # Save diagrams to files
    print("\nSaving ASCII diagrams to files...")
    save_ascii_diagrams()
    
    print("\nASCII diagrams can be:")
    print("- Displayed in any terminal")
    print("- Embedded in documentation")
    print("- Included in code comments")
    print("- Shared via email or chat")
    print("- Version controlled with code")