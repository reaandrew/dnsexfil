#!/usr/bin/env python3
"""
NetworkX + Matplotlib approach for creating AWS infrastructure diagrams
without requiring graphviz system dependency.

This creates a visual representation of the DNS exfiltration detection infrastructure
using pure Python libraries (NetworkX for graph structure, Matplotlib for rendering).
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_aws_infrastructure_diagram():
    """Create AWS infrastructure diagram using NetworkX and Matplotlib."""
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Define AWS services as nodes
    services = {
        'EC2': {'pos': (2, 4), 'color': '#FF9900', 'service_type': 'compute'},
        'VPC': {'pos': (2, 3), 'color': '#146EB4', 'service_type': 'network'},
        'Route53_Resolver': {'pos': (1, 2), 'color': '#146EB4', 'service_type': 'dns'},
        'DNS_Firewall': {'pos': (3, 2), 'color': '#146EB4', 'service_type': 'security'},
        'S3_DNS_Logs': {'pos': (0, 1), 'color': '#569A31', 'service_type': 'storage'},
        'S3_Athena_Results': {'pos': (4, 1), 'color': '#569A31', 'service_type': 'storage'},
        'Glue_Catalog': {'pos': (1, 0), 'color': '#FF9900', 'service_type': 'analytics'},
        'Athena': {'pos': (3, 0), 'color': '#FF9900', 'service_type': 'analytics'},
        'CloudWatch': {'pos': (2, 1), 'color': '#FF9900', 'service_type': 'monitoring'}
    }
    
    # Add nodes to graph
    for service, attrs in services.items():
        G.add_node(service, **attrs)
    
    # Define data flow connections
    connections = [
        ('EC2', 'VPC', 'DNS Queries'),
        ('VPC', 'Route53_Resolver', 'DNS Resolution'),
        ('Route53_Resolver', 'DNS_Firewall', 'Firewall Check'),
        ('Route53_Resolver', 'S3_DNS_Logs', 'Query Logs'),
        ('Route53_Resolver', 'CloudWatch', 'Metrics'),
        ('S3_DNS_Logs', 'Glue_Catalog', 'Schema'),
        ('Glue_Catalog', 'Athena', 'Query Engine'),
        ('Athena', 'S3_Athena_Results', 'Query Results'),
        ('DNS_Firewall', 'CloudWatch', 'Block Events')
    ]
    
    # Add edges to graph
    for source, target, label in connections:
        G.add_edge(source, target, label=label)
    
    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_title('AWS DNS Exfiltration Detection Infrastructure', fontsize=16, fontweight='bold', pad=20)
    
    # Extract positions
    pos = nx.get_node_attributes(G, 'pos')
    
    # Draw AWS service boxes instead of simple nodes
    for node, (x, y) in pos.items():
        attrs = services[node]
        color = attrs['color']
        service_type = attrs['service_type']
        
        # Create fancy boxes for different service types
        if service_type == 'compute':
            box = FancyBboxPatch((x-0.3, y-0.15), 0.6, 0.3, 
                               boxstyle="round,pad=0.02", 
                               facecolor=color, edgecolor='black', linewidth=2)
        elif service_type == 'storage':
            box = FancyBboxPatch((x-0.3, y-0.15), 0.6, 0.3, 
                               boxstyle="square,pad=0.02", 
                               facecolor=color, edgecolor='black', linewidth=2)
        elif service_type == 'analytics':
            box = FancyBboxPatch((x-0.3, y-0.15), 0.6, 0.3, 
                               boxstyle="sawtooth,pad=0.02", 
                               facecolor=color, edgecolor='black', linewidth=2)
        else:  # network, dns, security
            box = FancyBboxPatch((x-0.3, y-0.15), 0.6, 0.3, 
                               boxstyle="round,pad=0.02", 
                               facecolor=color, edgecolor='black', linewidth=2)
        
        ax.add_patch(box)
        
        # Add service name text
        ax.text(x, y, node.replace('_', '\n'), 
                horizontalalignment='center', verticalalignment='center',
                fontsize=9, fontweight='bold', color='white')
    
    # Draw edges with arrows and labels
    for edge in G.edges(data=True):
        source, target, data = edge
        x1, y1 = pos[source]
        x2, y2 = pos[target]
        
        # Calculate arrow positions (start and end points on box edges)
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx**2 + dy**2)
        
        # Normalize and adjust for box sizes
        if length > 0:
            dx_norm = dx / length
            dy_norm = dy / length
            
            # Start point (edge of source box)
            start_x = x1 + 0.3 * dx_norm
            start_y = y1 + 0.15 * dy_norm
            
            # End point (edge of target box)
            end_x = x2 - 0.3 * dx_norm
            end_y = y2 - 0.15 * dy_norm
            
            # Draw arrow
            ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                       arrowprops=dict(arrowstyle='->', lw=2, color='#333333'))
            
            # Add edge label
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            
            # Offset label slightly to avoid overlapping with arrow
            offset_x = -0.1 * dy_norm if abs(dy_norm) > 0.1 else 0.1
            offset_y = 0.1 * dx_norm if abs(dx_norm) > 0.1 else 0.1
            
            ax.text(mid_x + offset_x, mid_y + offset_y, data['label'], 
                   fontsize=8, ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Create legend
    legend_elements = [
        patches.Patch(color='#FF9900', label='Compute & Analytics'),
        patches.Patch(color='#569A31', label='Storage'),
        patches.Patch(color='#146EB4', label='Network & Security')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    # Set axis properties
    ax.set_xlim(-0.8, 4.8)
    ax.set_ylim(-0.5, 4.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add data flow direction note
    ax.text(0, 4.3, 'Data Flow Direction: DNS Queries → Logging → Analysis', 
            fontsize=12, style='italic', bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow'))
    
    plt.tight_layout()
    return fig

def create_threat_detection_flow():
    """Create a focused diagram showing the threat detection data flow."""
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_title('DNS Exfiltration Detection Data Flow', fontsize=16, fontweight='bold')
    
    # Define the detection flow stages
    stages = [
        {'name': 'Malicious\nDNS Query', 'pos': (1, 6), 'color': '#FF6B6B', 'type': 'threat'},
        {'name': 'EC2 Instance', 'pos': (1, 5), 'color': '#FF9900', 'type': 'source'},
        {'name': 'Route 53\nResolver', 'pos': (1, 4), 'color': '#146EB4', 'type': 'resolver'},
        {'name': 'DNS Firewall\n(Real-time)', 'pos': (3, 4), 'color': '#FF6B6B', 'type': 'firewall'},
        {'name': 'Query Logs\n(S3)', 'pos': (1, 3), 'color': '#569A31', 'type': 'storage'},
        {'name': 'Glue Catalog\n(Schema)', 'pos': (1, 2), 'color': '#FF9900', 'type': 'catalog'},
        {'name': 'Athena Analysis\n(Batch)', 'pos': (1, 1), 'color': '#FF9900', 'type': 'analytics'},
        {'name': 'Threat Detection\nResults', 'pos': (3, 1), 'color': '#FF6B6B', 'type': 'results'}
    ]
    
    # Draw stages
    for stage in stages:
        x, y = stage['pos']
        color = stage['color']
        
        # Different shapes for different types
        if stage['type'] == 'threat':
            # Diamond shape for threats
            diamond = patches.RegularPolygon((x, y), 4, radius=0.4, 
                                           orientation=np.pi/4, 
                                           facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(diamond)
        elif stage['type'] == 'storage':
            # Cylinder for storage
            rect = patches.Rectangle((x-0.3, y-0.2), 0.6, 0.4, 
                                   facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(rect)
        else:
            # Rectangle for others
            rect = patches.FancyBboxPatch((x-0.3, y-0.2), 0.6, 0.4, 
                                        boxstyle="round,pad=0.02", 
                                        facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(rect)
        
        # Add text
        ax.text(x, y, stage['name'], ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
    
    # Draw arrows showing flow
    flows = [
        ((1, 6), (1, 5), 'DNS Query'),
        ((1, 5), (1, 4), 'Resolution'),
        ((1, 4), (3, 4), 'Firewall Check'),
        ((1, 4), (1, 3), 'Log Entry'),
        ((1, 3), (1, 2), 'Schema Definition'),
        ((1, 2), (1, 1), 'Query Execution'),
        ((1, 1), (3, 1), 'Detection Results')
    ]
    
    for (x1, y1), (x2, y2), label in flows:
        # Calculate arrow positions
        if x1 == x2:  # Vertical arrow
            start_y = y1 - 0.2 if y1 > y2 else y1 + 0.2
            end_y = y2 + 0.2 if y1 > y2 else y2 - 0.2
            ax.annotate('', xy=(x2, end_y), xytext=(x1, start_y),
                       arrowprops=dict(arrowstyle='->', lw=2, color='#333333'))
            # Label
            ax.text((x1 + x2)/2 + 0.5, (start_y + end_y)/2, label, 
                   fontsize=8, ha='left', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        else:  # Horizontal arrow
            start_x = x1 + 0.3 if x1 < x2 else x1 - 0.3
            end_x = x2 - 0.3 if x1 < x2 else x2 + 0.3
            ax.annotate('', xy=(end_x, y2), xytext=(start_x, y1),
                       arrowprops=dict(arrowstyle='->', lw=2, color='#333333'))
            # Label
            ax.text((start_x + end_x)/2, (y1 + y2)/2 + 0.3, label, 
                   fontsize=8, ha='center', va='bottom',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Add detection types as text boxes
    detection_info = [
        "High Frequency Queries",
        "Data Encoding Detection", 
        "Subdomain Enumeration"
    ]
    
    for i, detection in enumerate(detection_info):
        ax.text(4.5, 3 - i*0.5, f"• {detection}", fontsize=10, ha='left', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
    
    ax.text(4.5, 3.5, "Detection Types:", fontsize=12, fontweight='bold', ha='left')
    
    # Set axis properties
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 7)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Create main infrastructure diagram
    print("Creating AWS Infrastructure Diagram using NetworkX + Matplotlib...")
    fig1 = create_aws_infrastructure_diagram()
    plt.figure(fig1.number)
    plt.savefig('/media/psf/Home/vmshare/dnsexfil/diagrams/aws_infrastructure_networkx.png', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    # Create threat detection flow diagram
    print("Creating Threat Detection Flow Diagram...")
    fig2 = create_threat_detection_flow()
    plt.figure(fig2.number)
    plt.savefig('/media/psf/Home/vmshare/dnsexfil/diagrams/threat_detection_flow.png', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Diagrams saved to:")
    print("- /media/psf/Home/vmshare/dnsexfil/diagrams/aws_infrastructure_networkx.png")
    print("- /media/psf/Home/vmshare/dnsexfil/diagrams/threat_detection_flow.png")