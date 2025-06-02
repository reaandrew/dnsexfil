#!/usr/bin/env python3
"""
Plotly approach for creating interactive AWS infrastructure diagrams
without requiring graphviz system dependency.

This creates interactive diagrams that can be viewed in web browsers
and support zooming, hovering, and dynamic interactions.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
import networkx as nx
import numpy as np

def create_interactive_aws_diagram():
    """Create interactive AWS infrastructure diagram using Plotly."""
    
    # Create network graph
    G = nx.DiGraph()
    
    # Define AWS services with metadata
    services = {
        'EC2': {'type': 'compute', 'color': '#FF9900', 'size': 30, 'pos': (1, 4)},
        'VPC': {'type': 'network', 'color': '#146EB4', 'size': 25, 'pos': (1, 3)},
        'Route53_Resolver': {'type': 'dns', 'color': '#146EB4', 'size': 30, 'pos': (2, 3)},
        'DNS_Firewall': {'type': 'security', 'color': '#FF6B6B', 'size': 25, 'pos': (3, 3)},
        'S3_DNS_Logs': {'type': 'storage', 'color': '#569A31', 'size': 30, 'pos': (0, 2)},
        'S3_Athena_Results': {'type': 'storage', 'color': '#569A31', 'size': 30, 'pos': (4, 2)},
        'Glue_Catalog': {'type': 'analytics', 'color': '#FF9900', 'size': 25, 'pos': (1, 1)},
        'Athena': {'type': 'analytics', 'color': '#FF9900', 'size': 30, 'pos': (3, 1)},
        'CloudWatch': {'type': 'monitoring', 'color': '#FF9900', 'size': 25, 'pos': (2, 0)}
    }
    
    # Add nodes with attributes
    for service, attrs in services.items():
        G.add_node(service, **attrs)
    
    # Define connections with detailed information
    connections = [
        ('EC2', 'VPC', {'type': 'DNS Queries', 'bandwidth': 'High', 'latency': '<1ms'}),
        ('VPC', 'Route53_Resolver', {'type': 'DNS Resolution', 'bandwidth': 'High', 'latency': '<5ms'}),
        ('Route53_Resolver', 'DNS_Firewall', {'type': 'Firewall Check', 'bandwidth': 'Medium', 'latency': '<10ms'}),
        ('Route53_Resolver', 'S3_DNS_Logs', {'type': 'Query Logs', 'bandwidth': 'Medium', 'latency': 'Async'}),
        ('Route53_Resolver', 'CloudWatch', {'type': 'Metrics', 'bandwidth': 'Low', 'latency': 'Async'}),
        ('S3_DNS_Logs', 'Glue_Catalog', {'type': 'Schema Definition', 'bandwidth': 'Low', 'latency': 'Batch'}),
        ('Glue_Catalog', 'Athena', {'type': 'Query Engine', 'bandwidth': 'Medium', 'latency': 'On-demand'}),
        ('Athena', 'S3_Athena_Results', {'type': 'Query Results', 'bandwidth': 'Medium', 'latency': 'Batch'}),
        ('DNS_Firewall', 'CloudWatch', {'type': 'Block Events', 'bandwidth': 'Low', 'latency': 'Real-time'})
    ]
    
    # Add edges
    for source, target, attrs in connections:
        G.add_edge(source, target, **attrs)
    
    # Extract positions and create coordinate lists
    pos = {node: services[node]['pos'] for node in G.nodes()}
    
    # Prepare node traces
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_colors = [services[node]['color'] for node in G.nodes()]
    node_sizes = [services[node]['size'] for node in G.nodes()]
    
    # Create hover text with detailed information
    node_text = []
    for node in G.nodes():
        service = services[node]
        connections_in = [f"← {G[pred][node]['type']}" for pred in G.predecessors(node)]
        connections_out = [f"→ {G[node][succ]['type']}" for succ in G.successors(node)]
        
        hover_text = f"<b>{node}</b><br>"
        hover_text += f"Type: {service['type'].title()}<br>"
        if connections_in:
            hover_text += f"Incoming: {', '.join(connections_in)}<br>"
        if connections_out:
            hover_text += f"Outgoing: {', '.join(connections_out)}"
        
        node_text.append(hover_text)
    
    # Create edge traces
    edge_x = []
    edge_y = []
    edge_info = []
    
    for edge in G.edges(data=True):
        source, target, data = edge
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Create edge hover information
        edge_info.append(f"{source} → {target}<br>{data['type']}<br>Bandwidth: {data['bandwidth']}<br>Latency: {data['latency']}")
    
    # Create the main plot
    fig = go.Figure()
    
    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888888'),
        hoverinfo='none',
        mode='lines',
        showlegend=False
    ))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white'),
            opacity=0.8
        ),
        text=[node.replace('_', '<br>') for node in G.nodes()],
        textposition="middle center",
        textfont=dict(color="white", size=10),
        hovertext=node_text,
        hoverinfo='text',
        showlegend=False
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': "Interactive AWS DNS Exfiltration Detection Infrastructure",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=True,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        annotations=[
            dict(
                text="Hover over nodes and edges for detailed information. Use mouse to pan and zoom.",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='gray', size=12)
            )
        ],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white'
    )
    
    return fig

def create_threat_detection_dashboard():
    """Create interactive dashboard showing threat detection metrics."""
    
    # Create subplot figure
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Query Frequency Over Time', 'Top Threat Domains', 
                       'Detection Types Distribution', 'Severity Levels'),
        specs=[[{"secondary_y": True}, {"type": "bar"}],
               [{"type": "pie"}, {"type": "bar"}]]
    )
    
    # Sample time series data for query frequency
    time_data = ['2024-01-01 ' + f"{h:02d}:00" for h in range(24)]
    normal_queries = np.random.poisson(50, 24)
    suspicious_queries = np.random.poisson(5, 24)
    
    # Add query frequency plot
    fig.add_trace(
        go.Scatter(x=time_data, y=normal_queries, name='Normal Queries', 
                  line=dict(color='green'), opacity=0.7),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=time_data, y=suspicious_queries, name='Suspicious Queries', 
                  line=dict(color='red'), fill='tonexty'),
        row=1, col=1
    )
    
    # Top threat domains
    threat_domains = ['evil.com', 'malware.org', 'bad-site.net', 'phishing.biz', 'attacker.io']
    threat_counts = [89, 67, 45, 32, 28]
    threat_colors = ['#FF6B6B' if count > 50 else '#FF9900' if count > 30 else '#FFA500' 
                    for count in threat_counts]
    
    fig.add_trace(
        go.Bar(x=threat_domains, y=threat_counts, name='Threat Queries',
               marker_color=threat_colors,
               hovertemplate='<b>%{x}</b><br>Queries: %{y}<br><extra></extra>'),
        row=1, col=2
    )
    
    # Detection types pie chart
    detection_types = ['High Frequency', 'Data Encoding', 'Subdomain Enumeration', 'Known Bad Domains']
    detection_counts = [45, 23, 18, 14]
    colors = ['#FF6B6B', '#FF9900', '#146EB4', '#569A31']
    
    fig.add_trace(
        go.Pie(labels=detection_types, values=detection_counts,
               marker_colors=colors, name="Detection Types"),
        row=2, col=1
    )
    
    # Severity levels
    severity_levels = ['Critical', 'High', 'Medium', 'Low']
    severity_counts = [8, 15, 32, 45]
    severity_colors = ['#8B0000', '#FF6B6B', '#FF9900', '#90EE90']
    
    fig.add_trace(
        go.Bar(x=severity_levels, y=severity_counts, name='Severity Distribution',
               marker_color=severity_colors,
               hovertemplate='<b>%{x}</b><br>Count: %{y}<br><extra></extra>'),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=700,
        title={
            'text': "DNS Exfiltration Detection Dashboard",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=True
    )
    
    # Update individual subplot properties
    fig.update_xaxes(title_text="Time", row=1, col=1)
    fig.update_yaxes(title_text="Query Count", row=1, col=1)
    fig.update_xaxes(title_text="Domain", row=1, col=2)
    fig.update_yaxes(title_text="Threat Score", row=1, col=2)
    fig.update_xaxes(title_text="Severity", row=2, col=2)
    fig.update_yaxes(title_text="Alert Count", row=2, col=2)
    
    return fig

def create_network_topology_3d():
    """Create 3D network topology visualization."""
    
    # Create 3D positions for services
    services_3d = {
        'Internet': {'pos': (0, 0, 5), 'color': '#666666', 'size': 20},
        'EC2': {'pos': (2, 2, 4), 'color': '#FF9900', 'size': 25},
        'VPC': {'pos': (0, 0, 3), 'color': '#146EB4', 'size': 30},
        'Route53_Resolver': {'pos': (-2, 0, 3), 'color': '#146EB4', 'size': 25},
        'DNS_Firewall': {'pos': (2, 0, 3), 'color': '#FF6B6B', 'size': 20},
        'S3_Logs': {'pos': (-3, -2, 2), 'color': '#569A31', 'size': 25},
        'S3_Results': {'pos': (3, -2, 2), 'color': '#569A31', 'size': 25},
        'Glue': {'pos': (-1, -3, 1), 'color': '#FF9900', 'size': 20},
        'Athena': {'pos': (1, -3, 1), 'color': '#FF9900', 'size': 25},
        'CloudWatch': {'pos': (0, -1, 0), 'color': '#FF9900', 'size': 20}
    }
    
    # Extract 3D coordinates
    x_coords = [services_3d[service]['pos'][0] for service in services_3d]
    y_coords = [services_3d[service]['pos'][1] for service in services_3d]
    z_coords = [services_3d[service]['pos'][2] for service in services_3d]
    colors = [services_3d[service]['color'] for service in services_3d]
    sizes = [services_3d[service]['size'] for service in services_3d]
    labels = list(services_3d.keys())
    
    # Create 3D scatter plot
    fig = go.Figure(data=[go.Scatter3d(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        mode='markers+text',
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.8,
            line=dict(color='white', width=2)
        ),
        text=labels,
        textposition="middle center",
        textfont=dict(color="white", size=12),
        hovertemplate='<b>%{text}</b><br>Layer: %{z}<br><extra></extra>',
        name='AWS Services'
    )])
    
    # Add connections as lines
    connections_3d = [
        ('Internet', 'EC2'),
        ('EC2', 'VPC'),
        ('VPC', 'Route53_Resolver'),
        ('Route53_Resolver', 'DNS_Firewall'),
        ('Route53_Resolver', 'S3_Logs'),
        ('S3_Logs', 'Glue'),
        ('Glue', 'Athena'),
        ('Athena', 'S3_Results'),
        ('Route53_Resolver', 'CloudWatch'),
        ('DNS_Firewall', 'CloudWatch')
    ]
    
    for source, target in connections_3d:
        src_pos = services_3d[source]['pos']
        tgt_pos = services_3d[target]['pos']
        
        fig.add_trace(go.Scatter3d(
            x=[src_pos[0], tgt_pos[0]],
            y=[src_pos[1], tgt_pos[1]],
            z=[src_pos[2], tgt_pos[2]],
            mode='lines',
            line=dict(color='gray', width=4),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Update layout for 3D
    fig.update_layout(
        title={
            'text': "3D Network Topology - AWS DNS Security Architecture",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Network Layer",
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            ),
            annotations=[
                dict(
                    x=0, y=0, z=5,
                    text="Layer 5: Internet",
                    showarrow=False,
                    font=dict(color="black", size=10)
                ),
                dict(
                    x=0, y=0, z=3,
                    text="Layer 3: VPC/Network",
                    showarrow=False,
                    font=dict(color="black", size=10)
                ),
                dict(
                    x=0, y=0, z=1,
                    text="Layer 1: Analytics",
                    showarrow=False,
                    font=dict(color="black", size=10)
                )
            ]
        ),
        width=800,
        height=600
    )
    
    return fig

def save_interactive_diagrams():
    """Save all interactive diagrams as HTML files."""
    
    diagrams = {
        'infrastructure': create_interactive_aws_diagram(),
        'dashboard': create_threat_detection_dashboard(),
        'topology_3d': create_network_topology_3d()
    }
    
    for name, fig in diagrams.items():
        filename = f'/media/psf/Home/vmshare/dnsexfil/diagrams/interactive_{name}.html'
        pyo.plot(fig, filename=filename, auto_open=False)
        print(f"Interactive diagram saved to: {filename}")

if __name__ == "__main__":
    print("Creating interactive AWS infrastructure diagrams using Plotly...")
    
    # Create and display diagrams
    save_interactive_diagrams()
    
    print("\nInteractive diagrams created:")
    print("- /media/psf/Home/vmshare/dnsexfil/diagrams/interactive_infrastructure.html")
    print("- /media/psf/Home/vmshare/dnsexfil/diagrams/interactive_dashboard.html") 
    print("- /media/psf/Home/vmshare/dnsexfil/diagrams/interactive_topology_3d.html")
    print("\nThese HTML files can be:")
    print("- Opened in any web browser")
    print("- Embedded in web applications")
    print("- Shared via email or web hosting")
    print("- Used for interactive presentations")
    print("- Integrated into dashboards")