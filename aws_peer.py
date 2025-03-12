import boto3
import botocore

import logging
import json
import sys

def get_secret_value(secretId,region):
    try: 
        client = boto3.client('secretsmanager',region_name=region)
        logging.info(f"Feching secret values from secretID: {secretId}")
        response = client.get_secret_value(
                SecretId=secretId)
        ontap_password = json.loads(response['SecretString'])['password']
        return ontap_password
    except botocore.exceptions.ClientError as e:
        logging.error(e.response['Error']['Message'])
        sys.exit(1)

def get_fsxn_data(file_system_id,region):
    try:
        client = boto3.client('fsx',region_name=region)
        logging.info(f"Fetching FSxN Clusters details")
        response = client.describe_file_systems(
                FileSystemIds=[
                    file_system_id
                    ],
                MaxResults=1
        )
        management_ip = response['FileSystems'][0]['OntapConfiguration']['Endpoints']['Management']['IpAddresses'][0]
        intercluster_ip = response['FileSystems'][0]['OntapConfiguration']['Endpoints']['Intercluster']['IpAddresses']
        return management_ip,intercluster_ip
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'FileSystemNotFound':
            logging.error(e.response['Error']['Message'])
        sys.exit(1)