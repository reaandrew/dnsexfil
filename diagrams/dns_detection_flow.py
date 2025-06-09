#!/usr/bin/env python3
"""
DNS Exfiltration Detection Flow Diagram
Creates a logical flow diagram showing the DNS threat detection system architecture
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_dns_detection_flow():
    """Create a comprehensive flow diagram of the DNS exfiltration detection system"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define colors
    colors = {
        'data_collection': '#E8F4FD',
        'analysis': '#FFF2CC', 
        'response': '#FFE6CC',
        'storage': '#D5E8D4',
        'compute': '#F8CECC',
        'arrow': '#666666',
        'text': '#333333'
    }
    
    # Title
    ax.text(5, 9.5, 'DNS Exfiltration Detection & Auto-Block System', 
            fontsize=18, fontweight='bold', ha='center', color=colors['text'])
    
    # Layer 1: Data Collection (Top)
    layer1_y = 8.5
    ax.text(0.5, layer1_y + 0.3, 'DATA COLLECTION LAYER', fontsize=12, fontweight='bold', 
            color=colors['text'])
    
    # EC2 Instance
    ec2_box = FancyBboxPatch((0.5, layer1_y - 0.3), 1.5, 0.6, 
                            boxstyle="round,pad=0.05", 
                            facecolor=colors['compute'], edgecolor='black', linewidth=1)
    ax.add_patch(ec2_box)
    ax.text(1.25, layer1_y, 'EC2 Instance\n(m5.large)', ha='center', va='center', fontsize=9)
    
    # VPC DNS Resolver
    dns_box = FancyBboxPatch((2.5, layer1_y - 0.3), 1.8, 0.6,
                            boxstyle="round,pad=0.05",
                            facecolor=colors['data_collection'], edgecolor='black', linewidth=1)
    ax.add_patch(dns_box)
    ax.text(3.4, layer1_y, 'Route 53 Resolver\nVPC DNS Logging', ha='center', va='center', fontsize=9)
    
    # S3 DNS Logs
    s3_logs_box = FancyBboxPatch((5, layer1_y - 0.3), 1.8, 0.6,
                                boxstyle="round,pad=0.05",
                                facecolor=colors['storage'], edgecolor='black', linewidth=1)
    ax.add_patch(s3_logs_box)
    ax.text(5.9, layer1_y, 'S3 Bucket\nDNS Logs', ha='center', va='center', fontsize=9)
    
    # S3 Results
    s3_results_box = FancyBboxPatch((7.5, layer1_y - 0.3), 1.8, 0.6,
                                   boxstyle="round,pad=0.05",
                                   facecolor=colors['storage'], edgecolor='black', linewidth=1)
    ax.add_patch(s3_results_box)
    ax.text(8.4, layer1_y, 'S3 Bucket\nAthena Results', ha='center', va='center', fontsize=9)
    
    # Layer 2: Analysis (Middle)
    layer2_y = 6.5
    ax.text(0.5, layer2_y + 0.8, 'ANALYSIS LAYER', fontsize=12, fontweight='bold', 
            color=colors['text'])
    
    # Partition Repair Lambda
    partition_lambda_box = FancyBboxPatch((0.5, layer2_y + 0.2), 2, 0.6,
                                         boxstyle="round,pad=0.05",
                                         facecolor=colors['compute'], edgecolor='black', linewidth=1)
    ax.add_patch(partition_lambda_box)
    ax.text(1.5, layer2_y + 0.5, 'Partition Repair\nLambda', ha='center', va='center', fontsize=9)
    
    # Glue Catalog
    glue_box = FancyBboxPatch((3, layer2_y + 0.2), 1.5, 0.6,
                             boxstyle="round,pad=0.05",
                             facecolor=colors['analysis'], edgecolor='black', linewidth=1)
    ax.add_patch(glue_box)
    ax.text(3.75, layer2_y + 0.5, 'AWS Glue\nCatalog + PSL', ha='center', va='center', fontsize=9)
    
    # Athena Workgroup
    athena_box = FancyBboxPatch((5, layer2_y + 0.2), 2, 0.6,
                               boxstyle="round,pad=0.05",
                               facecolor=colors['analysis'], edgecolor='black', linewidth=1)
    ax.add_patch(athena_box)
    ax.text(6, layer2_y + 0.5, 'Athena Workgroup\nThreat Detection Queries', ha='center', va='center', fontsize=9)
    
    # Threat Detection Lambda
    threat_lambda_box = FancyBboxPatch((7.5, layer2_y + 0.2), 2, 0.6,
                                      boxstyle="round,pad=0.05",
                                      facecolor=colors['compute'], edgecolor='black', linewidth=1)
    ax.add_patch(threat_lambda_box)
    ax.text(8.5, layer2_y + 0.5, 'Threat Detection\nLambda (1min schedule)', ha='center', va='center', fontsize=9)
    
    # Detection Patterns
    patterns_box = FancyBboxPatch((1, layer2_y - 1), 6, 0.8,
                                 boxstyle="round,pad=0.05",
                                 facecolor=colors['analysis'], edgecolor='black', linewidth=1)
    ax.add_patch(patterns_box)
    ax.text(4, layer2_y - 0.6, 'THREAT DETECTION PATTERNS\n• High-Frequency Exfiltration (>20 queries/5min)\n• Data Encoding Detection (Base64/Hex patterns)\n• Subdomain Enumeration (>5 unique subdomains/24hr)', 
            ha='center', va='center', fontsize=9)
    
    # Layer 3: Response (Bottom)
    layer3_y = 3.5
    ax.text(0.5, layer3_y + 0.3, 'RESPONSE LAYER', fontsize=12, fontweight='bold', 
            color=colors['text'])
    
    # DNS Firewall
    firewall_box = FancyBboxPatch((2, layer3_y - 0.3), 2.5, 0.6,
                                 boxstyle="round,pad=0.05",
                                 facecolor=colors['response'], edgecolor='black', linewidth=1)
    ax.add_patch(firewall_box)
    ax.text(3.25, layer3_y, 'Route 53 DNS Firewall\nAuto-Block Domains', ha='center', va='center', fontsize=9)
    
    # CloudWatch
    cloudwatch_box = FancyBboxPatch((5.5, layer3_y - 0.3), 2, 0.6,
                                   boxstyle="round,pad=0.05",
                                   facecolor=colors['response'], edgecolor='black', linewidth=1)
    ax.add_patch(cloudwatch_box)
    ax.text(6.5, layer3_y, 'CloudWatch\nMonitoring & Logs', ha='center', va='center', fontsize=9)
    
    # Blocking Logic
    logic_box = FancyBboxPatch((1, layer3_y - 1.5), 6, 0.8,
                              boxstyle="round,pad=0.05",
                              facecolor=colors['response'], edgecolor='black', linewidth=1)
    ax.add_patch(logic_box)
    ax.text(4, layer3_y - 1.1, 'SMART BLOCKING LOGIC\n• >10 unique subdomains → Wildcard block (*.domain.com)\n• ≤10 subdomains → Apex domain block (domain.com)\n• Only HIGH/CRITICAL severity threats blocked', 
            ha='center', va='center', fontsize=9)
    
    # Arrows - Data Flow
    arrow_props = dict(arrowstyle='->', lw=2, color=colors['arrow'])
    
    # EC2 to DNS Resolver
    ax.annotate('', xy=(2.5, layer1_y), xytext=(2, layer1_y), arrowprops=arrow_props)
    ax.text(2.25, layer1_y + 0.2, 'DNS\nQueries', ha='center', fontsize=8, color=colors['text'])
    
    # DNS Resolver to S3 Logs
    ax.annotate('', xy=(5, layer1_y), xytext=(4.3, layer1_y), arrowprops=arrow_props)
    ax.text(4.65, layer1_y + 0.2, 'Direct\nLogging', ha='center', fontsize=8, color=colors['text'])
    
    # S3 Logs to Partition Lambda (S3 trigger)
    ax.annotate('', xy=(1.5, layer2_y + 0.8), xytext=(5.5, layer1_y - 0.3), 
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['arrow'], connectionstyle="arc3,rad=0.3"))
    ax.text(3, layer1_y - 0.8, 'S3 Event\nTrigger', ha='center', fontsize=8, color=colors['text'])
    
    # Partition Lambda to Glue
    ax.annotate('', xy=(3, layer2_y + 0.5), xytext=(2.5, layer2_y + 0.5), arrowprops=arrow_props)
    ax.text(2.75, layer2_y + 0.7, 'MSCK\nREPAIR', ha='center', fontsize=8, color=colors['text'])
    
    # Glue to Athena
    ax.annotate('', xy=(5, layer2_y + 0.5), xytext=(4.5, layer2_y + 0.5), arrowprops=arrow_props)
    
    # Athena to Threat Lambda (scheduled)
    ax.annotate('', xy=(7.5, layer2_y + 0.5), xytext=(7, layer2_y + 0.5), arrowprops=arrow_props)
    ax.text(7.25, layer2_y + 0.7, 'Query\nExecution', ha='center', fontsize=8, color=colors['text'])
    
    # Threat Lambda to S3 Results
    ax.annotate('', xy=(8.4, layer1_y - 0.3), xytext=(8.5, layer2_y + 0.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['arrow'], connectionstyle="arc3,rad=-0.2"))
    
    # Threat Lambda to DNS Firewall
    ax.annotate('', xy=(3.25, layer3_y + 0.3), xytext=(8, layer2_y + 0.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['arrow'], connectionstyle="arc3,rad=0.4"))
    ax.text(5.5, layer3_y + 1.2, 'Auto-Block\nHIGH/CRITICAL', ha='center', fontsize=8, color=colors['text'])
    
    # DNS Firewall back to EC2 (blocking effect)
    ax.annotate('', xy=(1.25, layer1_y - 0.3), xytext=(2.5, layer3_y + 0.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='red', connectionstyle="arc3,rad=-0.5"))
    ax.text(0.8, layer2_y, 'DNS\nBlocking', ha='center', fontsize=8, color='red', rotation=90)
    
    # CloudWatch Events (1-minute schedule)
    ax.annotate('', xy=(8.5, layer2_y + 0.8), xytext=(6.5, layer3_y + 0.3), 
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['arrow'], connectionstyle="arc3,rad=-0.3"))
    ax.text(7.8, layer3_y + 1, '1-min\nSchedule', ha='center', fontsize=8, color=colors['text'])
    
    # Time windows annotation
    ax.text(9.5, layer2_y - 0.5, 'TIME WINDOWS:\n• Analysis: 5-min\n• Enumeration: 24-hr\n• Detection: 1-min', 
            fontsize=8, color=colors['text'], bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='gray'))
    
    # Example flow annotation
    ax.text(0.5, 1.5, 'EXAMPLE ATTACK FLOW:\n1. Malware: data1.evil.com, data2.evil.com...\n2. Detection: >20 queries to evil.com in 5 minutes\n3. Response: Block *.evil.com automatically', 
            fontsize=9, color=colors['text'], 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFEEEE', edgecolor='red'))
    
    plt.tight_layout()
    return fig

def main():
    """Generate and save the DNS detection flow diagram"""
    print("Generating DNS Exfiltration Detection Flow Diagram...")
    
    fig = create_dns_detection_flow()
    
    # Save the diagram
    output_path = '/media/psf/Home/vmshare/dnsexfil/diagrams/dns_detection_flow.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"Diagram saved to: {output_path}")
    
    # Show the diagram
    plt.show()

if __name__ == "__main__":
    main()