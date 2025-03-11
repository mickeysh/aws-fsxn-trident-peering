## AWS FSx for ONTAP peering for Trident
The following script can help you peer 2 FSxN cluter from EKS/K8s as a prerequisite for trident TMR or trident protect functionality. 

### Prerequisites
- Two FSxN clusters `source` and `destenation` and SVMs created in each cluster.
- Network connectivity between the `source` and `destenation` FSxN clusters. You need to be able to reach the cluster inter-connects and management interfaces. 
- EKS/K8s environment with network connectivity to both FSxN clusters (Management interfaces)
- Trident installed on EKS clusters and configured for FSxN backend


### Setup Peering between the clusters
The script will create both Cluster peering and SVM peering between the two FSxN clusters and SVMs. 

The script can run on any server with network access to the FSxN cluster or on the EKS clusters as a job. 

The script accesspt paramters as input in the `parms.json` file. If you run the script as a job the input will be saves as a ConfigMap. 

This is a sample json file:
```json
{
    "secretId": "<fsxn-aws-secret-manager-id>",
    "source": {
        "fsID": "<source-fsxn-fsid>",
        "svmName": "<source-svm-name>"
    }, 
    "destenation":{
        "fsID": "<destenation-fsxn-fsid>",
        "svmName": "<destenation-svm-name>r"
    },
    "cleanup": true,
    "create": true,
    "region": "<aws-region>"
}
```
|parameter|description|example|
|---|---|---|
| secretId | SecretID to the AWS Secret Manager secret containing the fsxadmin password| fsxn-password-secret-Nk45k4W5
| source.fsID | The source FSxN cluster file-system id | fs-0362cf28b24508b91 |
| source.svmName | The source SVM name | ekssvm |
| destenation.fsID | The destenation FSxN cluster file-system id | fs-084a19d439a81b8a9 |
| destenation.svmName | The destenation SVM name | ekssvmdr |
| cleanup | If true the it will cleanup all peering relationship in these clusters | |
| create | If true it will create the peering relationships between the clusters and SVMs (false is usefull together with cleanup to clear all previous relationships) |
| region | AWS region to run in | us-east-1 |