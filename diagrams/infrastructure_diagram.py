#!/usr/bin/env python3
"""
DNS Exfiltration Detection System - Infrastructure Diagram
Creates a visual representation of the AWS architecture with automated threat detection
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.analytics import Glue, Athena
from diagrams.aws.storage import S3
from diagrams.aws.network import Route53, VPC
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.security import Guardduty
from diagrams.aws.management import Cloudwatch
from diagrams.aws.integration import Eventbridge

# Create the infrastructure diagram
with Diagram("DNS Exfiltration Detection & Auto-Blocking System", 
             filename="dns_exfiltration_infrastructure", 
             show=False,
             direction="TB",
             graph_attr={"fontsize": "20", "bgcolor": "white"}):
    
    # VPC and EC2 instances generating DNS queries
    with Cluster("VPC Network"):
        vpc = VPC("Main VPC\nvpc-05125b63af35afb97")
        ec2_test = EC2("Test Instance\nDNS Exfiltration Client")
        
        # DNS Firewall Protection
        dns_firewall = Route53("DNS Firewall\nAuto-blocking")
    
    # DNS Resolution & Logging
    route53_resolver = Route53("Route 53 Resolver\nQuery Logs → S3")
    
    # Storage Layer
    with Cluster("Storage & Data"):
        dns_logs_bucket = S3("DNS Logs\ndnsexfil-demo-athena-logs")
        athena_results_bucket = S3("Athena Results\ndnsexfil-demo-athena-results")
        psl_data = S3("Public Suffix List\n(PSL Data)")
    
    # Data Catalog and Analytics
    with Cluster("Analytics Engine"):
        glue_database = Glue("Glue Catalog\ndns_logs_db")
        athena_workgroup = Athena("Athena Workgroup\n3 Detection Queries")
    
    # Automated Detection & Response
    with Cluster("Threat Detection Automation"):
        cloudwatch_events = Eventbridge("EventBridge\n1-minute schedule")
        threat_lambda = Lambda("Threat Detection\nLambda (5-min windows)")
        partition_lambda = Lambda("Partition Repair\nLambda (S3 triggered)")
    
    # Monitoring & Logging
    with Cluster("Monitoring & Alerts"):
        guardduty = Guardduty("GuardDuty\nDNS Threat Detection")
        cloudwatch_logs = Cloudwatch("CloudWatch Logs\nLambda & DNS Logs")
    
    # Data Flow Connections - DNS Query Path
    ec2_test >> Edge(label="DNS Queries\n(Exfiltration Test)", style="bold", color="red") >> dns_firewall
    dns_firewall >> Edge(label="Allowed Queries", style="bold") >> route53_resolver
    route53_resolver >> Edge(label="DNS Logs\n(JSON Format)", color="blue") >> dns_logs_bucket
    
    # Analytics Pipeline
    dns_logs_bucket >> Edge(label="New Partitions", color="green") >> partition_lambda
    partition_lambda >> Edge(label="MSCK REPAIR", style="dashed") >> glue_database
    glue_database >> Edge(label="Schema Access", color="purple") >> athena_workgroup
    psl_data >> Edge(label="Apex Domain\nExtraction", color="orange") >> athena_workgroup
    
    # Automated Threat Detection
    cloudwatch_events >> Edge(label="Every 1 minute", color="red") >> threat_lambda
    threat_lambda >> Edge(label="SQL Queries\n(5-min windows)", color="purple") >> athena_workgroup
    athena_workgroup >> Edge(label="Threat Results", color="orange") >> threat_lambda
    threat_lambda >> Edge(label="Block Domains\n(HIGH/CRITICAL)", color="red", style="bold") >> dns_firewall
    
    # Results Storage
    athena_workgroup >> Edge(label="Query Results", color="orange") >> athena_results_bucket
    
    # Monitoring Flow
    threat_lambda >> Edge(label="Execution Logs", style="dashed") >> cloudwatch_logs
    partition_lambda >> Edge(label="Execution Logs", style="dashed") >> cloudwatch_logs
    dns_logs_bucket >> Edge(label="DNS Analysis", style="dashed") >> guardduty
    
    # S3 Event Trigger
    dns_logs_bucket >> Edge(label="S3 Events\n(New Objects)", style="dotted") >> partition_lambda