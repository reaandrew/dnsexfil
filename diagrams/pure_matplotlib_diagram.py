#!/usr/bin/env python3
"""
Pure Matplotlib approach for creating AWS infrastructure diagrams
without any external dependencies beyond matplotlib.

This creates a custom layout using matplotlib patches and shapes to represent
AWS services and their connections.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Arrow
import numpy as np

def create_aws_architecture_matplotlib():
    """Create AWS architecture diagram using only matplotlib."""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_title('AWS DNS Exfiltration Detection Architecture\n(Pure Matplotlib Implementation)', 
                 fontsize=18, fontweight='bold', pad=30)
    
    # Define AWS service components with positions and styling
    services = {
        'vpc': {
            'pos': (8, 9), 'size': (12, 6), 'color': '#E8F4FD', 'border': '#146EB4',
            'label': 'VPC (10.0.0.0/16)', 'text_pos': (2, 11.5)
        },
        'ec2': {
            'pos': (4, 8), 'size': (2.5, 1.5), 'color': '#FF9900', 'border': '#CC7700',
            'label': 'EC2 Instance\n(m5.large)', 'text_pos': (5.25, 8.75)
        },
        'resolver': {
            'pos': (9, 8), 'size': (3, 1.5), 'color': '#146EB4', 'border': '#0F4A8C',
            'label': 'Route 53\nResolver', 'text_pos': (10.5, 8.75)
        },
        'firewall': {
            'pos': (13, 8), 'size': (2.5, 1.5), 'color': '#FF6B6B', 'border': '#CC5555',
            'label': 'DNS\nFirewall', 'text_pos': (14.25, 8.75)
        },
        's3_logs': {
            'pos': (3, 5), 'size': (3, 1.5), 'color': '#569A31', 'border': '#3E6B22',
            'label': 'S3 Bucket\n(DNS Logs)', 'text_pos': (4.5, 5.75)
        },
        's3_results': {
            'pos': (14, 5), 'size': (3, 1.5), 'color': '#569A31', 'border': '#3E6B22',
            'label': 'S3 Bucket\n(Query Results)', 'text_pos': (15.5, 5.75)
        },
        'glue': {
            'pos': (7, 3), 'size': (3, 1.5), 'color': '#FF9900', 'border': '#CC7700',
            'label': 'AWS Glue\nCatalog', 'text_pos': (8.5, 3.75)
        },
        'athena': {
            'pos': (11, 3), 'size': (3, 1.5), 'color': '#FF9900', 'border': '#CC7700',
            'label': 'Amazon\nAthena', 'text_pos': (12.5, 3.75)
        },
        'cloudwatch': {
            'pos': (9, 1), 'size': (3, 1.5), 'color': '#FF9900', 'border': '#CC7700',
            'label': 'CloudWatch\nLogs', 'text_pos': (10.5, 1.75)
        }
    }
    
    # Draw VPC container first (background)
    vpc = services['vpc']
    vpc_rect = FancyBboxPatch(
        vpc['pos'], vpc['size'][0], vpc['size'][1],
        boxstyle="round,pad=0.1",
        facecolor=vpc['color'], edgecolor=vpc['border'], linewidth=3
    )
    ax.add_patch(vpc_rect)
    ax.text(vpc['text_pos'][0], vpc['text_pos'][1], vpc['label'], 
            fontsize=14, fontweight='bold', color=vpc['border'])
    
    # Draw individual services
    for service_name, service in services.items():
        if service_name == 'vpc':  # Already drawn
            continue
            
        # Create service box
        if service_name in ['s3_logs', 's3_results']:
            # Cylindrical shape for S3 (storage)
            rect = FancyBboxPatch(
                service['pos'], service['size'][0], service['size'][1],
                boxstyle="round,pad=0.1",
                facecolor=service['color'], edgecolor=service['border'], linewidth=2
            )
            # Add storage indicator (top ellipse)
            ellipse = patches.Ellipse(
                (service['pos'][0] + service['size'][0]/2, service['pos'][1] + service['size'][1]), 
                service['size'][0], 0.3, 
                facecolor=service['color'], edgecolor=service['border'], linewidth=2
            )
            ax.add_patch(ellipse)
        else:
            # Regular boxes for other services
            rect = FancyBboxPatch(
                service['pos'], service['size'][0], service['size'][1],
                boxstyle="round,pad=0.1",
                facecolor=service['color'], edgecolor=service['border'], linewidth=2
            )
        
        ax.add_patch(rect)
        
        # Add service label
        ax.text(service['text_pos'][0], service['text_pos'][1], service['label'], 
                ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    
    # Define data flow connections
    connections = [
        # (from_service, to_service, label, style)
        ('ec2', 'resolver', 'DNS Queries', 'normal'),
        ('resolver', 'firewall', 'Firewall\nCheck', 'normal'),
        ('resolver', 's3_logs', 'Query\nLogs', 'data'),
        ('resolver', 'cloudwatch', 'Metrics', 'monitoring'),
        ('s3_logs', 'glue', 'Schema\nDefinition', 'data'),
        ('glue', 'athena', 'Query\nEngine', 'normal'),
        ('athena', 's3_results', 'Analysis\nResults', 'data'),
        ('firewall', 'cloudwatch', 'Block\nEvents', 'monitoring')
    ]
    
    # Draw connections
    for from_service, to_service, label, style in connections:
        from_pos = services[from_service]['pos']
        from_size = services[from_service]['size']
        to_pos = services[to_service]['pos']
        to_size = services[to_service]['size']
        
        # Calculate connection points (center of boxes)
        from_center = (from_pos[0] + from_size[0]/2, from_pos[1] + from_size[1]/2)
        to_center = (to_pos[0] + to_size[0]/2, to_pos[1] + to_size[1]/2)
        
        # Calculate edge points on boxes
        dx = to_center[0] - from_center[0]
        dy = to_center[1] - from_center[1]
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize direction
            dx_norm = dx / distance
            dy_norm = dy / distance
            
            # Calculate start and end points on box edges
            from_edge = (
                from_center[0] + (from_size[0]/2) * dx_norm,
                from_center[1] + (from_size[1]/2) * dy_norm
            )
            to_edge = (
                to_center[0] - (to_size[0]/2) * dx_norm,
                to_center[1] - (to_size[1]/2) * dy_norm
            )
            
            # Set arrow style based on connection type
            if style == 'data':
                arrow_props = dict(arrowstyle='->', lw=3, color='#2E8B57')
            elif style == 'monitoring':
                arrow_props = dict(arrowstyle='->', lw=2, color='#FF6B6B', linestyle='--')
            else:
                arrow_props = dict(arrowstyle='->', lw=2, color='#333333')
            
            # Draw arrow
            ax.annotate('', xy=to_edge, xytext=from_edge, arrowprops=arrow_props)
            
            # Add label
            mid_point = ((from_edge[0] + to_edge[0])/2, (from_edge[1] + to_edge[1])/2)
            
            # Offset label to avoid overlapping with arrow
            offset_x = -0.5 * dy_norm if abs(dy_norm) > 0.3 else 0.5
            offset_y = 0.5 * dx_norm if abs(dx_norm) > 0.3 else 0.5
            
            label_pos = (mid_point[0] + offset_x, mid_point[1] + offset_y)
            
            # Label style based on connection type
            if style == 'data':
                bbox_props = dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.8)
            elif style == 'monitoring':
                bbox_props = dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.8)
            else:
                bbox_props = dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8)
            
            ax.text(label_pos[0], label_pos[1], label, 
                   ha='center', va='center', fontsize=9,
                   bbox=bbox_props)
    
    # Add legend
    legend_elements = [
        patches.Patch(color='#FF9900', label='Compute & Analytics'),
        patches.Patch(color='#569A31', label='Storage Services'),
        patches.Patch(color='#146EB4', label='Network Services'),
        patches.Patch(color='#FF6B6B', label='Security Services'),
        plt.Line2D([0], [0], color='#2E8B57', lw=3, label='Data Flow'),
        plt.Line2D([0], [0], color='#FF6B6B', lw=2, linestyle='--', label='Monitoring'),
        plt.Line2D([0], [0], color='#333333', lw=2, label='Standard Flow')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1), fontsize=10)
    
    # Add detection scenarios as text
    scenarios_text = """
Detection Scenarios:
• High-frequency DNS queries to apex domains
• Encoded data in subdomain names (Base64/Hex)
• Subdomain enumeration patterns
• Abnormal query patterns and frequencies
    """
    
    ax.text(18, 10, scenarios_text, fontsize=11, va='top', ha='left',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', alpha=0.9))
    
    # Set axis properties
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 13)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    return fig

def create_threat_timeline_diagram():
    """Create a timeline diagram showing threat detection process."""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_title('DNS Exfiltration Detection Timeline', fontsize=16, fontweight='bold', pad=20)
    
    # Timeline events
    timeline_events = [
        {'time': 0, 'event': 'Malicious Actor\nStarts Exfiltration', 'color': '#FF6B6B', 'type': 'threat'},
        {'time': 1, 'event': 'High Frequency\nDNS Queries', 'color': '#FF9900', 'type': 'activity'},
        {'time': 2, 'event': 'DNS Resolver\nLogs Queries', 'color': '#146EB4', 'type': 'logging'},
        {'time': 3, 'event': 'Real-time Firewall\nBlocks Known Bad', 'color': '#FF6B6B', 'type': 'prevention'},
        {'time': 4, 'event': 'Logs Sent to S3\nfor Analysis', 'color': '#569A31', 'type': 'storage'},
        {'time': 5, 'event': 'Athena Queries\nDetect Patterns', 'color': '#FF9900', 'type': 'analysis'},
        {'time': 6, 'event': 'Alert Generated\nfor Investigation', 'color': '#FF6B6B', 'type': 'alert'}
    ]
    
    # Draw timeline base
    ax.plot([0, 7], [4, 4], 'k-', linewidth=3)
    
    # Draw timeline events
    for event in timeline_events:
        x = event['time'] + 0.5
        y = 4
        
        # Draw timeline marker
        circle = Circle((x, y), 0.2, facecolor=event['color'], edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        
        # Draw event box
        box_y = 5.5 if event['time'] % 2 == 0 else 2.5
        box_height = 1
        box_width = 1.2
        
        box = FancyBboxPatch(
            (x - box_width/2, box_y - box_height/2), box_width, box_height,
            boxstyle="round,pad=0.1",
            facecolor=event['color'], edgecolor='black', linewidth=1, alpha=0.8
        )
        ax.add_patch(box)
        
        # Add event text
        ax.text(x, box_y, event['event'], ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
        
        # Draw connector line
        ax.plot([x, x], [y + 0.2, box_y - box_height/2], 'k--', linewidth=1)
        
        # Add time label
        ax.text(x, y - 0.5, f"T+{event['time']}min", ha='center', va='center', 
                fontsize=10, fontweight='bold')
    
    # Add detection types on the side
    detection_types = [
        "Frequency Analysis:\n• >20 queries in 5 min window",
        "Encoding Detection:\n• Base64/Hex patterns in subdomains", 
        "Enumeration Detection:\n• >5 unique subdomains per domain"
    ]
    
    for i, detection in enumerate(detection_types):
        ax.text(8.5, 6 - i*1.5, detection, fontsize=10, va='top', ha='left',
                bbox=dict(boxstyle="round,pad=0.4", facecolor='lightblue', alpha=0.7))
    
    ax.text(8.5, 6.8, "Detection Methods:", fontsize=12, fontweight='bold', ha='left')
    
    # Set axis properties
    ax.set_xlim(-0.5, 12)
    ax.set_ylim(1, 7)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Create main architecture diagram
    print("Creating AWS Architecture Diagram using Pure Matplotlib...")
    fig1 = create_aws_architecture_matplotlib()
    plt.figure(fig1.number)
    plt.savefig('/media/psf/Home/vmshare/dnsexfil/diagrams/aws_architecture_matplotlib.png', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    # Create timeline diagram
    print("Creating Threat Detection Timeline...")
    fig2 = create_threat_timeline_diagram()
    plt.figure(fig2.number)
    plt.savefig('/media/psf/Home/vmshare/dnsexfil/diagrams/threat_timeline.png', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Diagrams saved to:")
    print("- /media/psf/Home/vmshare/dnsexfil/diagrams/aws_architecture_matplotlib.png")
    print("- /media/psf/Home/vmshare/dnsexfil/diagrams/threat_timeline.png")