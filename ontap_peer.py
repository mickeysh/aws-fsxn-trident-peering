import logging

from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterPeer,SvmPeer

def fsxn_cleanup_peer(data):
    logging.info(f"Logging into host at ip address: {data['management_ip']}")
    with HostConnection(data['management_ip'], username="fsxadmin", password=data['password'], verify=False):
            logging.info("Cleaning up Peers")
            for peer in list(SvmPeer.get_collection()):
                resource = SvmPeer(uuid=peer['uuid'])
                resource.delete()
                logging.info(f"Deleted SVM Peer {resource.uuid}")
            for peer in list(ClusterPeer.get_collection()):
                resource = ClusterPeer(uuid=peer['uuid'])
                resource.delete()
                logging.info(f"Deleted Cluster Peer {resource.uuid}")

def fsxn_cluster_peer(data,peer_data):
    logging.info(f"Logging into host at ip address: {data['management_ip']}")
    with HostConnection(data['management_ip'], username="fsxadmin", password=data['password'], verify=False):
        logging.info("Creating Cluster Peer")
        resource = ClusterPeer()
        resource.authentication = {"passphrase": "xyz12345"}
        resource.remote = {"ip_addresses": peer_data['intercluster_ip']}
        resource.post(hydrate=True)
        logging.info(f"Created Cluster Peer UUID: {resource.uuid} at status {resource.status}")
        return resource.name

def fsxn_svm_peer(data,peer_data):
    logging.info(f"Logging into host at ip address: {data['management_ip']}")
    with HostConnection(data['management_ip'], username="fsxadmin", password=data['password'], verify=False):
        logging.info("Creating SVM Peer")
        resource = SvmPeer()
        resource.applications = ['snapmirror']
        resource.svm = {"name": data['svmName']}
        resource.peer  = {"svm": {"name": peer_data['svmName']},"cluster":{"name": peer_data['name']}}
        resource.post(hydrate=True)
        logging.info(f"Created SVM Peer UUID: {resource.uuid} at status {resource.state}")
        return resource.uuid

def fsxn_svm_peer_accept(data,destenation_peer_uuid):
    logging.info(f"Logging into host at ip address: {data['management_ip']}")
    with HostConnection(data['management_ip'], username="fsxadmin", password=data['password'], verify=False):
        logging.info("Accepting SVM Peer")
        resource = SvmPeer(uuid=destenation_peer_uuid)
        resource.state = "peered"
        resource.patch(hydrate=True)
        logging.info(f"Created Source SVM Peer UUID: {resource.uuid} at status {resource.state}")

