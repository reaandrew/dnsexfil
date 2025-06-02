import json
import boto3
import os
import logging
from typing import List, Dict, Any
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

athena = boto3.client('athena')
route53resolver = boto3.client('route53resolver')

def lambda_handler(event, context):
    """
    Scheduled threat detection Lambda that runs DNS threat detection queries
    and automatically blocks HIGH/CRITICAL severity domains in DNS Firewall.
    """
    
    database = os.environ['ATHENA_DATABASE']
    workgroup = os.environ['ATHENA_WORKGROUP']
    output_location = os.environ['ATHENA_OUTPUT_LOCATION']
    firewall_domain_list_id = os.environ['FIREWALL_DOMAIN_LIST_ID']
    
    try:
        logger.info("Starting DNS threat detection scan")
        
        # List of threat detection queries to run
        threat_queries = [
            "DNS Exfiltration Detection",
            "DNS Data Encoding Detection"
        ]
        
        all_threats = []
        
        # Run each threat detection query
        for query_name in threat_queries:
            logger.info(f"Running threat detection query: {query_name}")
            
            try:
                results = run_saved_query(query_name, database, workgroup, output_location)
                threats = parse_threat_results(results, query_name)
                all_threats.extend(threats)
                
                logger.info(f"Query '{query_name}' found {len(threats)} threats")
                
            except Exception as e:
                logger.error(f"Error running query '{query_name}': {str(e)}")
                continue
        
        # Filter for HIGH/CRITICAL severity threats
        high_severity_threats = [
            threat for threat in all_threats 
            if threat.get('severity') in ['HIGH', 'CRITICAL']
        ]
        
        logger.info(f"Found {len(high_severity_threats)} HIGH/CRITICAL threats for blocking")
        
        # Extract domains to block - get the actual patterns being abused
        domains_to_block = []
        for threat in high_severity_threats:
            # Get the specific domain pattern under attack
            domain_pattern = get_threat_domain_pattern(threat)
            if domain_pattern:
                domains_to_block.append(domain_pattern)
        
        domains_to_block = list(set(domains_to_block))
        
        if domains_to_block:
            # Update DNS Firewall blocked domains
            blocked_count = update_blocked_domains(firewall_domain_list_id, domains_to_block)
            logger.info(f"Added {blocked_count} new domains to DNS Firewall blocklist")
        else:
            logger.info("No new domains to block")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Threat detection completed successfully',
                'threats_found': len(all_threats),
                'high_severity_threats': len(high_severity_threats),
                'domains_blocked': len(domains_to_block) if domains_to_block else 0,
                'blocked_domains': domains_to_block
            })
        }
        
    except Exception as e:
        logger.error(f"Threat detection failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def run_saved_query(query_name: str, database: str, workgroup: str, output_location: str) -> List[Dict]:
    """
    Run a saved Athena query by name and return results.
    """
    try:
        # Get saved query
        saved_queries = athena.list_named_queries(WorkGroup=workgroup)
        
        query_id = None
        for query_id_candidate in saved_queries['NamedQueryIds']:
            query_details = athena.get_named_query(NamedQueryId=query_id_candidate)
            if query_details['NamedQuery']['Name'] == query_name:
                query_id = query_id_candidate
                break
        
        if not query_id:
            raise Exception(f"Saved query '{query_name}' not found")
        
        # Get query string
        query_details = athena.get_named_query(NamedQueryId=query_id)
        query_string = query_details['NamedQuery']['QueryString']
        
        # Execute query
        response = athena.start_query_execution(
            QueryString=query_string,
            QueryExecutionContext={'Database': database},
            WorkGroup=workgroup,
            ResultConfiguration={'OutputLocation': output_location}
        )
        
        execution_id = response['QueryExecutionId']
        
        # Wait for query completion
        while True:
            execution_details = athena.get_query_execution(QueryExecutionId=execution_id)
            status = execution_details['QueryExecution']['Status']['State']
            
            if status == 'SUCCEEDED':
                break
            elif status in ['FAILED', 'CANCELLED']:
                error_reason = execution_details['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                raise Exception(f"Query failed: {error_reason}")
            
            time.sleep(2)  # Wait 2 seconds before checking again
        
        # Get query results
        results = []
        paginator = athena.get_paginator('get_query_results')
        
        for page in paginator.paginate(QueryExecutionId=execution_id):
            for row in page['ResultSet']['Rows'][1:]:  # Skip header row
                row_data = {}
                for i, cell in enumerate(row['Data']):
                    column_name = page['ResultSet']['ResultSetMetadata']['ColumnInfo'][i]['Name']
                    row_data[column_name] = cell.get('VarCharValue', '')
                results.append(row_data)
        
        return results
        
    except Exception as e:
        logger.error(f"Error running saved query '{query_name}': {str(e)}")
        raise

def get_threat_domain_pattern(threat: Dict) -> str:
    """
    Determine the best domain pattern to block based on the threat.
    For DNS exfiltration, we want to block the subdomain pattern being abused.
    """
    apex_domain = threat.get('apex_domain')
    if not apex_domain:
        return None
    
    # For high-frequency attacks with many unique subdomains, 
    # block the wildcard pattern to catch all subdomains
    unique_subdomains = threat.get('unique_subdomains', 0)
    
    try:
        unique_count = int(unique_subdomains) if unique_subdomains else 0
    except (ValueError, TypeError):
        unique_count = 0
    
    # If there are many unique subdomains (>10), it's likely a subdomain exfiltration attack
    # Block the wildcard pattern to catch all subdomains under this apex domain
    if unique_count > 10:
        return f"*.{apex_domain}"
    else:
        # For fewer subdomains, just block the apex domain
        return apex_domain

def parse_threat_results(results: List[Dict], query_type: str) -> List[Dict]:
    """
    Parse threat detection results and standardize format.
    """
    threats = []
    
    for result in results:
        threat = {
            'apex_domain': result.get('apex_domain'),
            'query_type': query_type,
            'severity': result.get('severity'),
            'threat_type': result.get('threat_type'),
            'query_count': result.get('query_count'),
            'first_seen': result.get('first_seen'),
            'last_seen': result.get('last_seen')
        }
        
        # Add query-specific fields
        if 'unique_subdomains' in result:
            threat['unique_subdomains'] = result['unique_subdomains']
        if 'encoding_patterns' in result:
            threat['encoding_patterns'] = result['encoding_patterns']
        if 'source_count' in result:
            threat['source_count'] = result['source_count']
        
        threats.append(threat)
    
    return threats

def update_blocked_domains(domain_list_id: str, new_domains: List[str]) -> int:
    """
    Add new domains to DNS Firewall blocked domains list.
    Returns count of newly added domains.
    """
    try:
        # Get current blocked domains
        current_domains = set()
        
        # Get detailed domain list
        paginator = route53resolver.get_paginator('list_firewall_domains')
        
        for page in paginator.paginate(FirewallDomainListId=domain_list_id):
            for domain in page.get('Domains', []):
                current_domains.add(domain)
        
        # Find domains not already blocked and remove duplicates from new_domains
        unique_new_domains = list(set(new_domains))  # Remove duplicates from input
        domains_to_add = [domain for domain in unique_new_domains if domain not in current_domains]
        
        if not domains_to_add:
            logger.info("All threat domains are already blocked")
            return 0
        
        # Add new domains to blocklist
        logger.info(f"Adding {len(domains_to_add)} new domains to blocklist: {domains_to_add}")
        
        route53resolver.update_firewall_domains(
            FirewallDomainListId=domain_list_id,
            Operation='ADD',
            Domains=domains_to_add
        )
        
        return len(domains_to_add)
        
    except Exception as e:
        logger.error(f"Error updating blocked domains: {str(e)}")
        raise