#!/usr/bin/env python3
"""
DNS Exfiltration Detection System - Infrastructure Diagram
Creates a visual representation of the AWS architecture
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.analytics import Glue, Athena
from diagrams.aws.storage import S3
from diagrams.aws.network import Route53, VPC
from diagrams.aws.compute import EC2
from diagrams.aws.security import Guardduty
from diagrams.aws.management import Cloudwatch

# Create the infrastructure diagram
with Diagram("DNS Exfiltration Detection System", 
             filename="dns_exfiltration_infrastructure", 
             show=False,
             direction="TB",
             graph_attr={"fontsize": "20", "bgcolor": "white"}):
    
    # DNS Query Source
    route53_resolver = Route53("Route 53 Resolver\nDNS Query Logging")
    
    # VPC and EC2 instances generating DNS queries
    with Cluster("VPC Network"):
        vpc = VPC("Main VPC")
        with Cluster("EC2 Instances"):
            ec2_instances = [
                EC2("EC2 Instance 1\n(Test Client)"),
                EC2("EC2 Instance 2\n(App Server)")
            ]
    
    # Storage Layer
    with Cluster("Storage Layer"):
        dns_logs_bucket = S3("DNS Logs Bucket\ndnsexfil-demo-athena-logs")
        athena_results_bucket = S3("Athena Results\ndnsexfil-demo-athena-results")
    
    # Data Catalog and Analytics
    with Cluster("Analytics Layer"):
        glue_database = Glue("Glue Catalog\nDNS Logs Database")
        athena_workgroup = Athena("Athena Workgroup\ndns-exfiltration-analysis")
    
    # Security and Monitoring
    with Cluster("Security & Monitoring"):
        guardduty = Guardduty("GuardDuty\nThreat Detection")
        cloudwatch = Cloudwatch("CloudWatch\nMonitoring")
    
    # Data Flow Connections
    ec2_instances >> Edge(label="DNS Queries", style="bold") >> route53_resolver
    route53_resolver >> Edge(label="DNS Logs\n(JSON Format)", color="blue") >> dns_logs_bucket
    dns_logs_bucket >> Edge(label="Catalog Schema", color="green") >> glue_database
    glue_database >> Edge(label="Query Interface", color="purple") >> athena_workgroup
    athena_workgroup >> Edge(label="Query Results", color="orange") >> athena_results_bucket
    
    # Monitoring connections
    dns_logs_bucket >> Edge(label="Log Analysis", style="dashed") >> guardduty
    athena_workgroup >> Edge(label="Metrics", style="dashed") >> cloudwatch