#!/bin/bash

# Download and process Public Suffix List for Athena
echo "Downloading Public Suffix List..."
curl -s https://publicsuffix.org/list/public_suffix_list.dat > /tmp/psl.dat

# Convert to CSV format
echo "Converting to CSV..."
cat > /tmp/process_psl.py << 'EOF'
import sys

suffixes = []

with open('/tmp/psl.dat', 'r') as f:
    for line in f:
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('//'):
            continue
            
        # Handle wildcard and exception rules
        if line.startswith('*.') or line.startswith('!'):
            continue
        else:
            # Regular suffix
            suffix = line.lower()
            label_count = len(suffix.split('.'))
            print(f"{suffix},{label_count}")

EOF

python3 /tmp/process_psl.py > /tmp/public_suffixes.csv

echo "Uploading to S3..."
aws s3 cp /tmp/public_suffixes.csv s3://dnsexfil-demo-athena-logs/psl/public_suffixes.csv

echo "Cleaning up..."
rm -f /tmp/psl.dat /tmp/process_psl.py /tmp/public_suffixes.csv

echo "Done! PSL data uploaded to S3."