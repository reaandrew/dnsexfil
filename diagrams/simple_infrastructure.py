#!/usr/bin/env python3
"""
Simple DNS Exfiltration Detection System - Infrastructure Diagram
Creates a clean, simplified visual representation of the AWS architecture
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.analytics import Glue, Athena
from diagrams.aws.storage import S3
from diagrams.aws.network import Route53
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.management import Cloudwatch
from diagrams.onprem.network import Internet

# Create the simplified infrastructure diagram
with Diagram("DNS Exfiltration Detection System", 
             filename="simple_dns_infrastructure", 
             show=False,
             direction="LR",
             graph_attr={"fontsize": "16", "bgcolor": "white", "pad": "0.1", "margin": "0.1", "style": "invis"}):  
    
    # External traffic source
    internet = Internet("Internet")
    
    # VPC with EC2
    with Cluster("VPC", graph_attr={"style": "dotted", "pad": "0.8", "margin": "0.5"}):
        ec2 = EC2("EC2")
    
    # DNS Services
    with Cluster("DNS Services", graph_attr={"style": "dotted", "pad": "0.8", "margin": "0.5"}):
        firewall = Route53("DNS Firewall")
        resolver = Route53("DNS Resolver")
    
    # Storage Layer
    with Cluster("Storage", graph_attr={"style": "dotted", "pad": "0.8", "margin": "0.5"}):
        dns_logs = S3("DNS Logs")
        results = S3("Results")
    
    # Analytics and Processing
    with Cluster("Analytics & Processing", graph_attr={"style": "dotted", "pad": "0.8", "margin": "0.5"}):
        glue_db = Glue("Glue DB")
        athena = Athena("Athena")
        partition_lambda = Lambda("Partition Repair")
        threat_lambda = Lambda("Threat Detection")
        cloudwatch = Cloudwatch("CloudWatch")
    
    # Data Flow - Clean and simple (Outbound DNS Protection)
    ec2 >> Edge(label="DNS Queries", style="bold", color="red") >> firewall
    firewall >> Edge(label="Filtered") >> resolver
    resolver >> Edge(label="Allowed Queries") >> internet
    resolver >> Edge(label="Query Logs") >> dns_logs
    dns_logs >> partition_lambda
    partition_lambda >> glue_db
    
    # Analysis Flow
    cloudwatch >> threat_lambda
    threat_lambda >> athena
    athena >> results
    glue_db >> athena
    
    # Response Flow
    threat_lambda >> Edge(label="Block Rules") >> firewall
    
    # Monitoring
    threat_lambda >> cloudwatch