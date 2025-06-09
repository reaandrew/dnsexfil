#!/usr/bin/env python3
"""
DNS Exfiltration Detection: Step-by-Step S-Shaped Flow Diagram
Shows the complete 15-step process from malicious DNS queries to automated blocking
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_step_by_step_flow():
    """Create an S-shaped flow diagram showing all 15 steps"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 14))
    ax.set_xlim(-1, 12)
    ax.set_ylim(10, 22)
    ax.axis('off')
    
    # Define colors for different phases
    colors = {
        'ingestion': '#E8F4FD',      # Light blue
        'processing': '#FFF2CC',      # Light yellow  
        'analysis': '#FFE6CC',        # Light orange
        'response': '#D5E8D4',        # Light green
        'blocking': '#F8CECC',        # Light red
        'arrow': '#666666',
        'text': '#333333',
        'number': '#FFFFFF'
    }
    
    # Title
    ax.text(6, 21.5, 'DNS Exfiltration Detection: Ingestion to Blocking Flow', 
            fontsize=16, fontweight='bold', ha='center', color=colors['text'])
    
    # Define steps with their content, colors, and positions
    steps = [
        # Row 1 (left to right)
        {"num": 1, "text": "Malicious DNS Queries\nGenerated\n(data1.evil.com)", "color": colors['ingestion'], "pos": (1.5, 20)},
        {"num": 2, "text": "VPC DNS Resolver\nCaptures Queries", "color": colors['ingestion'], "pos": (4.5, 20)},
        {"num": 3, "text": "Direct S3 Logging\n(Bypass CloudWatch)", "color": colors['ingestion'], "pos": (7.5, 20)},
        {"num": 4, "text": "S3 Event Triggers\nPartition Repair", "color": colors['ingestion'], "pos": (10.5, 20)},
        
        # Row 2 (right to left)
        {"num": 5, "text": "Table Partition\nDiscovery\n(MSCK REPAIR)", "color": colors['processing'], "pos": (10.5, 17.5)},
        {"num": 6, "text": "Scheduled Threat\nDetection\n(1-minute timer)", "color": colors['processing'], "pos": (7.5, 17.5)},
        {"num": 7, "text": "Execute Saved\nAthena Queries", "color": colors['processing'], "pos": (4.5, 17.5)},
        {"num": 8, "text": "Apex Domain\nExtraction\n(Public Suffix List)", "color": colors['processing'], "pos": (1.5, 17.5)},
        
        # Row 3 (left to right)
        {"num": 9, "text": "Pattern Analysis\n• High-frequency", "color": colors['analysis'], "pos": (1.5, 15)},
        {"num": 10, "text": "Severity Assessment\nLOW/MEDIUM/\nHIGH/CRITICAL", "color": colors['analysis'], "pos": (4.5, 15)},
        {"num": 11, "text": "Filter High-Severity\nThreats\n(HIGH/CRITICAL only)", "color": colors['analysis'], "pos": (7.5, 15)},
        {"num": 12, "text": "Smart Blocking Logic\n>10 subs: *.domain\n≤10 subs: domain", "color": colors['analysis'], "pos": (10.5, 15)},
        
        # Row 4 (right to left)
        {"num": 13, "text": "Update DNS Firewall\n(Route 53 Resolver API)", "color": colors['blocking'], "pos": (10.5, 12.5)},
        {"num": 14, "text": "Immediate DNS\nBlocking\n(NODATA response)", "color": colors['blocking'], "pos": (7.5, 12.5)},
        {"num": 15, "text": "CloudWatch Logging\n& Monitoring", "color": colors['blocking'], "pos": (4.5, 12.5)},
    ]
    
    # Draw steps
    box_width = 2.2
    box_height = 1.8
    
    for step in steps:
        x, y = step["pos"]
        
        # Create rounded rectangle
        box = FancyBboxPatch((x - box_width/2, y - box_height/2), box_width, box_height,
                            boxstyle="round,pad=0.1",
                            facecolor=step["color"], 
                            edgecolor='black', 
                            linewidth=1.5)
        ax.add_patch(box)
        
        # Add step number circle
        circle = plt.Circle((x - box_width/2 + 0.3, y + box_height/2 - 0.3), 0.2, 
                           color='#333333', zorder=10)
        ax.add_patch(circle)
        ax.text(x - box_width/2 + 0.3, y + box_height/2 - 0.3, str(step["num"]), 
                ha='center', va='center', fontsize=10, fontweight='bold', 
                color=colors['number'], zorder=11)
        
        # Add step text
        ax.text(x, y - 0.1, step["text"], ha='center', va='center', 
                fontsize=9, color=colors['text'], wrap=True)
    
    # Define arrow connections following S-pattern
    arrow_props = dict(arrowstyle='->', lw=2.5, color=colors['arrow'])
    
    # Row 1 connections (left to right)
    for i in range(3):
        start_x = steps[i]["pos"][0] + box_width/2
        end_x = steps[i+1]["pos"][0] - box_width/2
        y = steps[i]["pos"][1]
        ax.annotate('', xy=(end_x, y), xytext=(start_x, y), arrowprops=arrow_props)
    
    # Transition from row 1 to row 2 (down and curve)
    ax.annotate('', xy=(steps[4]["pos"][0], steps[4]["pos"][1] + box_height/2), 
                xytext=(steps[3]["pos"][0], steps[3]["pos"][1] - box_height/2),
                arrowprops=dict(arrowstyle='->', lw=2.5, color=colors['arrow'], 
                               connectionstyle="arc3,rad=0.3"))
    
    # Row 2 connections (right to left)
    for i in range(4, 7):
        start_x = steps[i]["pos"][0] - box_width/2
        end_x = steps[i+1]["pos"][0] + box_width/2
        y = steps[i]["pos"][1]
        ax.annotate('', xy=(end_x, y), xytext=(start_x, y), arrowprops=arrow_props)
    
    # Transition from row 2 to row 3 (down and curve)
    ax.annotate('', xy=(steps[8]["pos"][0], steps[8]["pos"][1] + box_height/2), 
                xytext=(steps[7]["pos"][0], steps[7]["pos"][1] - box_height/2),
                arrowprops=dict(arrowstyle='->', lw=2.5, color=colors['arrow'], 
                               connectionstyle="arc3,rad=-0.3"))
    
    # Row 3 connections (left to right)
    for i in range(8, 11):
        start_x = steps[i]["pos"][0] + box_width/2
        end_x = steps[i+1]["pos"][0] - box_width/2
        y = steps[i]["pos"][1]
        ax.annotate('', xy=(end_x, y), xytext=(start_x, y), arrowprops=arrow_props)
    
    # Transition from row 3 to row 4 (down and curve)
    ax.annotate('', xy=(steps[12]["pos"][0], steps[12]["pos"][1] + box_height/2), 
                xytext=(steps[11]["pos"][0], steps[11]["pos"][1] - box_height/2),
                arrowprops=dict(arrowstyle='->', lw=2.5, color=colors['arrow'], 
                               connectionstyle="arc3,rad=0.3"))
    
    # Row 4 connections (right to left)
    for i in range(12, 14):
        start_x = steps[i]["pos"][0] - box_width/2
        end_x = steps[i+1]["pos"][0] + box_width/2
        y = steps[i]["pos"][1]
        ax.annotate('', xy=(end_x, y), xytext=(start_x, y), arrowprops=arrow_props)
    
    # Add phase labels on the left
    phase_labels = [
        {"text": "DATA INGESTION\n& TRIGGERING", "y": 20, "color": colors['ingestion']},
        {"text": "QUERY\nPROCESSING", "y": 17.5, "color": colors['processing']},
        {"text": "THREAT\nANALYSIS", "y": 15, "color": colors['analysis']},
        {"text": "RESPONSE &\nBLOCKING", "y": 12.5, "color": colors['blocking']}
    ]
    
    for label in phase_labels:
        ax.text(0, label["y"], label["text"], ha='center', va='center',
                fontsize=10, fontweight='bold', color=colors['text'],
                bbox=dict(boxstyle="round,pad=0.3", facecolor=label["color"], 
                         edgecolor='black', alpha=0.8))
    
    
    plt.tight_layout()
    return fig

def main():
    """Generate and save the step-by-step flow diagram"""
    print("Generating Step-by-Step DNS Detection Flow Diagram...")
    
    fig = create_step_by_step_flow()
    
    # Save the diagram
    output_path = '/media/psf/Home/vmshare/dnsexfil/diagrams/step_by_step_flow.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"Diagram saved to: {output_path}")
    
    # Show the diagram (if in interactive environment)
    plt.show()

if __name__ == "__main__":
    main()