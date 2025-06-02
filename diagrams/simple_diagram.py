#!/usr/bin/env python3
"""
DNS Exfiltration Detection & Auto-Blocking System - Simplified Diagram
Creates a visual representation of the complete automated solution
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.analytics import Glue, Athena
from diagrams.aws.storage import S3
from diagrams.aws.network import Route53, VPC
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.integration import Eventbridge

# Create a simplified infrastructure diagram
with Diagram("DNS Exfiltration Detection & Auto-Blocking", 
             filename="dns_exfiltration_simple", 
             show=False,
             direction="TB",
             outformat="svg",  # Use SVG instead of PNG
             graph_attr={"fontsize": "16", "bgcolor": "white"}):
    
    # Test Client
    ec2_test = EC2("Test Client\n(Exfiltration)")
    
    # DNS Protection & Logging
    dns_firewall = Route53("DNS Firewall\n(Auto-blocking)")
    route53_resolver = Route53("Route 53 Resolver\n(Logging)")
    
    # Storage & Analytics
    with Cluster("Detection Engine"):
        dns_logs = S3("DNS Logs")
        athena = Athena("Threat Detection\n(3 Queries)")
        psl_data = S3("PSL Data")
    
    # Automation
    with Cluster("Automation"):
        scheduler = Eventbridge("1-min Schedule")
        threat_lambda = Lambda("Threat Detection\nLambda")
    
    # Data flow - Detection Pipeline
    ec2_test >> Edge(label="DNS Queries", color="red") >> dns_firewall
    dns_firewall >> Edge(label="Allowed", color="green") >> route53_resolver
    route53_resolver >> Edge(label="Logs", color="blue") >> dns_logs
    
    # Automated Analysis
    scheduler >> Edge(label="Trigger", color="orange") >> threat_lambda
    threat_lambda >> Edge(label="Analyze", color="purple") >> athena
    [dns_logs, psl_data] >> athena
    
    # Auto-blocking Response
    threat_lambda >> Edge(label="Block Threats", color="red", style="bold") >> dns_firewall

print("Diagram generation completed!")
print("Note: Requires 'dot' command from graphviz system package to generate actual image files.")