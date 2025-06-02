import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

athena = boto3.client('athena')

def lambda_handler(event, context):
    """
    Triggered when new DNS log files arrive in S3.
    Runs MSCK REPAIR TABLE to discover new partitions.
    """
    
    database = os.environ['ATHENA_DATABASE']
    workgroup = os.environ['ATHENA_WORKGROUP']
    output_location = os.environ['ATHENA_OUTPUT_LOCATION']
    
    # Only process DNS log files, not other S3 events
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        # Check if this is a DNS query log file
        if 'vpcdnsquerylogs' in key and key.endswith('.log.gz'):
            logger.info(f"New DNS log file detected: {key}")
            
            try:
                # Run MSCK REPAIR TABLE
                query = "MSCK REPAIR TABLE resolver_dns_logs;"
                
                response = athena.start_query_execution(
                    QueryString=query,
                    QueryExecutionContext={'Database': database},
                    WorkGroup=workgroup,
                    ResultConfiguration={'OutputLocation': output_location}
                )
                
                execution_id = response['QueryExecutionId']
                logger.info(f"MSCK REPAIR started: {execution_id}")
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Partition repair initiated',
                        'executionId': execution_id,
                        'triggeredBy': key
                    })
                }
                
            except Exception as e:
                logger.error(f"Error running MSCK REPAIR: {str(e)}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': str(e)})
                }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'No DNS log files to process'})
    }