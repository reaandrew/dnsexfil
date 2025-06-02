# Infrastructure Diagrams

This directory contains Python scripts to generate infrastructure diagrams for the DNS Exfiltration Detection System.

## Prerequisites

Install the required dependencies:

```bash
# Install system dependency (Ubuntu/Debian)
sudo apt-get install graphviz

# Create virtual environment and install Python packages
python3 -m venv venv
source venv/bin/activate
pip install diagrams graphviz
```

## Generate Diagrams

### Full Infrastructure Diagram
Run the complete infrastructure diagram generator (requires graphviz system package):

```bash
source venv/bin/activate
python3 infrastructure_diagram.py
```

### Simplified Diagram  
If graphviz system package is not available, use the simplified version:

```bash
source venv/bin/activate
python3 simple_diagram.py
```

## Output Files

The diagrams show the complete AWS architecture including:

- **Route 53 Resolver** (DNS query logging)
- **VPC with EC2 instances** (query sources)
- **S3 buckets** for logs and results
- **AWS Glue catalog** (schema management)
- **Amazon Athena workgroup** (threat detection queries)
- **Security monitoring** (GuardDuty, CloudWatch)

## Data Flow

The diagram illustrates the detection pipeline:

1. **EC2 instances** generate DNS queries within the VPC
2. **Route 53 Resolver** captures and logs DNS queries
3. **S3 bucket** stores DNS logs in JSON format
4. **Glue catalog** provides schema for log analysis
5. **Athena** executes threat detection queries
6. **Results bucket** stores query outputs

## Troubleshooting

**Error: "failed to execute PosixPath('dot')"**
- Install graphviz system package: `sudo apt-get install graphviz`
- Or use the simplified diagram script instead

**Import errors for AWS services**
- Service names in diagrams library use lowercase: `Guardduty`, `Cloudwatch`