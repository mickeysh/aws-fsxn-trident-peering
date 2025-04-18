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

#### Input Parameters
The script accesspt paramters as input in the `parms.json` file. If you run the script as a job the input will be saves as a ConfigMap. 

This is a sample json file:
```json
{
    "source": {
        "fsID": "<source-fsxn-fsid>",
        "svmName": "<source-svm-name>",
        "secretId": "<fsxn-aws-secret-manager-id>"
    }, 
    "destenation":{
        "fsID": "<destenation-fsxn-fsid>",
        "svmName": "<destenation-svm-name>",
        "secretId": "<fsxn-aws-secret-manager-id>"
    },
    "cleanup": true,
    "create": true,
    "region": "<aws-region>"
}
```

|parameter|description|example|
|---|---|---|
| source.fsID | The source FSxN cluster file-system id | fs-0362cf28b24508b91 |
| source.svmName | The source SVM name | ekssvm |
| source.secretId | SecretID to the AWS Secret Manager secret containing the source cluster fsxadmin password| fsxn-password-secret-Nk45k4W5
| destenation.fsID | The destenation FSxN cluster file-system id | fs-084a19d439a81b8a9 |
| destenation.svmName | The destenation SVM name | ekssvmdr |
| destenation.secretId | SecretID to the AWS Secret Manager secret containing the destenation cluster fsxadmin password| fsxn-password-secret-Nk45k4W5
| cleanup | If true the it will cleanup all peering relationship in these clusters | |
| create | If true it will create the peering relationships between the clusters and SVMs (false is usefull together with cleanup to clear all previous relationships) |
| region | AWS region to run in | us-east-1 |

#### Execution 
To run this in kubernetes first create the [parms.json](parms.json) file as a ConfigMap using this the [parmcm.yaml](parmcm.yaml) sample manifest. 

Once the ConfigMap is available run the peering using the [peerjob.yaml](peerjob.yaml) sample manifest. 

In mounts the parms.json from the ConfigMap we just created and runs the script from public repo. You can use the sample [Dockerfile](Dockerfile) to build your own version of the image. 

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: peer-clusters
  namespace: trident
spec:
  template:
    spec:
      serviceAccountName: trident-controller
      containers:
      - name: python
        image: 139763910815.dkr.ecr.us-east-1.amazonaws.com/fsxn/ontap-peer:latest
        volumeMounts:
          - name: parms
            mountPath: /usr/src/app/parms
      restartPolicy: Never
      volumes:
        - name: parms
          configMap:
            name: peer-parms

```
To access to log outputs from the job you can use the following kubectl command:
```shell
kubectl logs job.batch/peer-clusters -n trident
```

License

Licensed under the Apache License, Version 2.0 (the "License").

You may obtain a copy of the License at apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" basis, without WARRANTIES or conditions of any kind, either express or implied.

See the License for the specific language governing permissions and limitations under the License.