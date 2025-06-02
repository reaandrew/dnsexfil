#!/usr/bin/env python3
"""
DNS Exfiltration Detection System - Simplified Infrastructure Diagram
Creates a visual representation without requiring graphviz system installation
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.analytics import Glue, Athena
from diagrams.aws.storage import S3
from diagrams.aws.network import Route53, VPC
from diagrams.aws.compute import EC2

# Create a simplified infrastructure diagram
with Diagram("DNS Exfiltration Detection System", 
             filename="dns_exfiltration_simple", 
             show=False,
             direction="TB",
             outformat="svg",  # Use SVG instead of PNG
             graph_attr={"fontsize": "16", "bgcolor": "white"}):
    
    # DNS Query Source
    route53_resolver = Route53("Route 53 Resolver")
    
    # VPC and EC2 instances
    with Cluster("VPC"):
        ec2_test = EC2("Test Client")
        ec2_app = EC2("App Server")
    
    # Storage
    with Cluster("Storage"):
        dns_logs = S3("DNS Logs")
        results = S3("Results")
    
    # Analytics
    with Cluster("Analytics"):
        glue = Glue("Glue Catalog")
        athena = Athena("Athena")
    
    # Simple data flow
    [ec2_test, ec2_app] >> route53_resolver >> dns_logs >> glue >> athena >> results

print("Diagram generation completed!")
print("Note: Requires 'dot' command from graphviz system package to generate actual image files.")