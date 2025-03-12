import logging
import json

from aws_peer import get_secret_value,get_fsxn_data
from ontap_peer import fsxn_cleanup_peer,fsxn_cluster_peer,fsxn_svm_peer,fsxn_svm_peer_accept

logging.basicConfig(level=logging.INFO)

def main():
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
    peer_data['source']['svmName'] = parms['source']['svmName']
    peer_data['destenation']['svmName'] = parms['destenation']['svmName']

    peer_data['source']['user'],peer_data['source']['password'] = get_secret_value(parms['source']['secretId'],parms['region'])
    peer_data['destenation']['user'],peer_data['destenation']['password'] = get_secret_value(parms['destenation']['secretId'],parms['region'])

    peer_data['source']['management_ip'],peer_data['source']['intercluster_ip'] = get_fsxn_data(parms['source']['fsID'],parms['region'])
    peer_data['destenation']['management_ip'],peer_data['destenation']['intercluster_ip'] = get_fsxn_data(parms['destenation']['fsID'],parms['region'])

    if parms['cleanup']:
        fsxn_cleanup_peer(peer_data['destenation'])
        fsxn_cleanup_peer(peer_data['source'])
    if parms['create']:
        peer_data['source']['name'] = fsxn_cluster_peer(peer_data['destenation'],peer_data['source'])
        peer_data['destenation']['name'] = fsxn_cluster_peer(peer_data['source'],peer_data['destenation'])
        destenation_peer_uuid = fsxn_svm_peer(peer_data['destenation'],peer_data['source'])
        fsxn_svm_peer_accept(peer_data['source'],destenation_peer_uuid)
if __name__ == "__main__":
    main()