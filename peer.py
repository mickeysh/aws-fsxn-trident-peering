import boto3
import botocore
import json
import sys
import logging

from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer,SvmPeer

logging.basicConfig(level=logging.INFO)

peer_data = {}
peer_data['source'] = {}
peer_data['destenation'] = {}

with open('./parms/parms.json', 'r') as f:
    parms = json.load(f)

logging.info(f"Preparing for peering FSxN Clusters")
logging.info(f"Source Cluster: {parms['source']['fsID']}, SVM: {parms['source']['svmName']}")
logging.info(f"Destenation Cluster: {parms['destenation']['fsID']}, SVM: {parms['destenation']['svmName']}")
logging.info(f"AWS Region: {parms['region']}")
logging.info(f"Create: {parms['create']}, Cleanup: {parms['cleanup']}")

client = boto3.client('secretsmanager',region_name=parms['region'])

try: 
    logging.info(f"Feching secret values from secretID: {parms['secretId']}")
    response = client.get_secret_value(
            SecretId=parms['secretId'])
    ontap_user = json.loads(response['SecretString'])['username']
    ontap_password = json.loads(response['SecretString'])['password']
except botocore.exceptions.ClientError as e:
    logging.error(e.response['Error']['Message'])
    sys.exit(1)


client = boto3.client('fsx',region_name=parms['region'])
try:
    logging.info(f"Fetching FSxN Clusters details")
    response = client.describe_file_systems(
            FileSystemIds=[
                parms['source']['fsID'],
                parms['destenation']['fsID']
                ],
            MaxResults=123
    )
    peer_data['source']['management_ip'] = response['FileSystems'][0]['OntapConfiguration']['Endpoints']['Management']['IpAddresses'][0]
    peer_data['source']['intercluster_ip'] = response['FileSystems'][0]['OntapConfiguration']['Endpoints']['Intercluster']['IpAddresses']
    peer_data['destenation']['management_ip'] = response['FileSystems'][1]['OntapConfiguration']['Endpoints']['Management']['IpAddresses'][0]
    peer_data['destenation']['intercluster_ip'] = response['FileSystems'][1]['OntapConfiguration']['Endpoints']['Intercluster']['IpAddresses']
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == 'FileSystemNotFound':
        logging.error(e.response['Error']['Message'])
    sys.exit(1)

logging.info(f"Logging into destination host at ip address: {peer_data['destenation']['management_ip']}")
with HostConnection(peer_data['destenation']['management_ip'], username="fsxadmin", password=ontap_password, verify=False):
    if parms['cleanup']:
        logging.info("Cleaning up destenation Peers")
        for peer in list(SvmPeer.get_collection()):
            resource = SvmPeer(uuid=peer['uuid'])
            resource.delete()
            logging.info(f"Deleted Destenation SVM Peer {resource.uuid}")
        for peer in list(ClusterPeer.get_collection()):
            resource = ClusterPeer(uuid=peer['uuid'])
            resource.delete()
            logging.info(f"Deleted Destenation Cluster Peer {resource.uuid}")
    if parms['create']:
        logging.info("Creating Destenation Cluster Peer")
        resource = ClusterPeer()
        resource.authentication = {"passphrase": "xyz12345"}
        resource.remote = {"ip_addresses": peer_data['source']['intercluster_ip']}
        resource.post(hydrate=True)
        peer_data['source']['name'] = resource.name
        logging.info(f"Created Destenation Cluster Peer UUID: {resource.uuid} at status {resource.status}")

logging.info(f"Logging into source host at ip address: {peer_data['source']['management_ip']}")
with HostConnection(peer_data['source']['management_ip'], username="fsxadmin", password=ontap_password, verify=False):
    if parms['cleanup']:
        logging.info("Cleaning up source Peers")
        for peer in list(SvmPeer.get_collection()):
            resource = SvmPeer(uuid=peer['uuid'])
            resource.delete()
            logging.info(f"Deleted Source SVM Peer {resource.uuid}")
        for peer in list(ClusterPeer.get_collection()):
            resource = ClusterPeer(uuid=peer['uuid'])
            resource.delete()
            logging.info(f"Deleted Source Cluster Peer {resource.uuid}")
    if parms['create']:
        logging.info("Creating Source Cluster Peer")
        resource = ClusterPeer()
        resource.authentication = {"passphrase": "xyz12345"}
        resource.remote = {"ip_addresses": peer_data['destenation']['intercluster_ip']}
        resource.post(hydrate=True)
        peer_data['destenation']['name'] = resource.name
        logging.info(f"Created Source Cluster Peer UUID: {resource.uuid} at status {resource.status}")

logging.info(f"Logging into destination host at ip address: {peer_data['destenation']['management_ip']}")
with HostConnection(peer_data['destenation']['management_ip'], username="fsxadmin", password=ontap_password, verify=False):
    if parms['create']:
        logging.info("Creating Destenation SVM Peer")
        resource = SvmPeer()
        resource.applications = ['snapmirror']
        resource.svm = {"name": parms['destenation']['svmName']}
        resource.peer  = {"svm": {"name": parms['source']['svmName']},"cluster":{"name": peer_data['source']['name']}}
        resource.post(hydrate=True)
        logging.info(f"Created Destenation SVM Peer UUID: {resource.uuid} at status {resource.state}")
        destenation_peer_uuid = resource.uuid

logging.info(f"Logging into source host at ip address: {peer_data['source']['management_ip']}")
with HostConnection(peer_data['source']['management_ip'], username="fsxadmin", password=ontap_password, verify=False):
    if parms['create']:
        logging.info("Creating Source SVM Peer")
        resource = SvmPeer(uuid=destenation_peer_uuid)
        resource.state = "peered"
        resource.patch(hydrate=True)
        logging.info(f"Created Source SVM Peer UUID: {resource.uuid} at status {resource.state}")