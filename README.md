# MLOps environment with Airflow, MLFlow, and KServe

![Airflow dashboard in action](images/airflow-dashboard.png)

This repository contains a fully deployable environment for doing MLOps with 
Apache Airflow, MLFlow, and KServe.

## System requirements

We assume that you have the following:

- Access to a Kubernetes 1.22+ cluster with at least 4 CPU cores and 20Gb
- An Azure Storage account with hierarchical namespaces to use as feature storage and artifact storage
- The latest release of Anaconda on your machine
- Kubectl must be installed on your machine
- Helm 3 or higher installed on your machine
- Istio 1.11.6

Please note, this sample only works on WSL2 or Linux! This is due to a bug in
Airflow which prevents it from running locally with Sqlite.

We've tested the setup with Docker Desktop and WSL2. Other forms of Kubernetes
hosting may work, but remain untested for the time being.

## Deploying the sample

For the sample to work, you'll need to configure a set of services in
Kubernetes. Please follow the instructions in the following sections to
set things up.

### Installing Istio

The sample uses Istio to route traffic from outside the cluster and to support
canary releasing models. Please use the following command to install Istio:

```
istioctl install -y
```

### Deploying KServe

The model serving environment is implemented using KServe. The KServe tool
allows use to host models with a serverless philosophy. You can install KServe
using the following script: 

```shell
./deploy-kserve.sh
```

Please note, you'll need to set up a host entry in your host file for the 
KNative installation to work. You can get the external IP-address for your
cluster using the following command:

```shell
kubectl --namespace istio-system get service istio-ingressgateway
```

Add the following entry to your host file:

```text
<ip-address>    knative.mlopsdemo.local
```

Once you've configured the environment, you can access it on the URL you
just configured in the host file.

--------------------------------------------------------------------------------

Please note, you may get errors regarding cert manager not being able to service
a certificate request. This happens when cert manager isn't ready yet. You can
re-run the `./install-kserve.sh` script after a few minutes and it should work
as intended.

--------------------------------------------------------------------------------

### Deploying airflow

This section covers how to set up Apache Airflow on Kubernetes. Please follow
the instructions below.

Create a new file `deploy/airflow/values-secrets.yml` and add the following
content to it:

```yaml
extraSecrets:
  airflow-ssh-secret:
    data: |
      gitSshKey: '<your-key>'
webserverSecretKey: <random-string>
defaultUser.password: <your-password>
data:
  metadataConnection:
    user: postgres
    pass: <your-db-password>
postgresql:
  enabled: true
  postgresqlPassword: <your-db-password>
  postgresqlUsername: postgres
env:
  - name: 'AZURE_STORAGE_CONNECTION_STRING'
    value: '<your-connection-string>'
  - name: "AIRFLOW_VAR_MLFLOW_SERVER"
    value: "http://mlflow-tracking-server.airflow.svc.cluster.local:5000"
```

Make sure you replace the `<your-key>` value with the base64 encoded version
of an SSH private key that has access to the repo you want to sync with airflow.
Also replace the `<your connection string>` value with a connection string that has 
access to your Azure Storage account.

You can create a key using the following command from WSL2:
```shell
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```
Make sure to use an e-mailaddress that has access to the repository. The public key 
should then be added as a deploy key to the repository.

You can encode your key using the following command from WSL2:

```shell
base64 <your-key-file> -w 0 > temp.txt
```

You can grab the encoded key from `temp.txt`. Ensure a strong password for the 
admin account and a strong password for the database.

You'll also need to specify the secret for signing web sessions with the airflow
webserver. We recommend generating a GUID or another random string for this
secret value.

After completing the secrets, edit the file `deploy/airflow/values-override.yml`
and configure the URL of the GIT repo, the branch name, and the revision you
want to sync.

Once you've configured the values, run the following command to install 
Airflow:

```shell
kubectl create namespace airflow
./deploy-airflow.sh
```

It will take a few minutes to deploy the airflow components.

### Deploying MLFlow

In addition to Airflow, we're going to use a tracking solution for ML models. 
MLFlow is an open-source tool that allows you to track experiments and trained
models. 

Add a new file `secrets.yml` to the folder `./deploy/mlflow` and add the
following content to it:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mlflow-secrets
type: Opaque
data:
  databasePassword: <your-password> 
  storageAccountName:
  storageAccountKey:
  storageAccountConnectionString: 
```

Provide the following properties in base64-encoded form:

| Property                        | Value                                          |
|---------------------------------|------------------------------------------------|
| databasePassword                | Database for the postgres database             |
| storageAccountName              | Name of the Azure storage account to use       |
| storageAccountKey               | Key of the Azure storage account to use        |
| storageAccountConnectionString  | Connection string to the Azure Storage Account |

Also don't forget to add a container named `modelartifacts` to your Azure Blob storage account.
In this container, the artifacts will be stored.

Use the following command in your terminal to deploy MLFlow:

```shell
./deploy-mlflow.sh
```

### Deploying logging components

We've included logging through the ELK stack in the sample. You can deploy the
components needed for logging using the following command:

```shell
./deploy-elasticsearch.sh
```

It will take a few minutes for the logging components to come online. Once
they're ready and you run a DAG, the logs
will show up in elasticsearch. You can access them as normal in the Apache
Airflow UI.

## Working with the sample

This section covers how to work with the sample in your own environment.

### Configuring your machine

As with many Python projects, you'll need a virtual environment of some sort.
We recommend that you use anaconda since it features a lot of the packages
you'll need for data science.

You can create a new Anaconda environment using the following command:

```shell
conda create -n mlopsdemo python=3.7
```

This command creates an environment that matches the Python version used by 
Airflow. 

After creating the Anaconda environment, run the following commands to 
activate the environment and install the project dependencies:

```shell
conda activate mlopsdemo
pip install -r requirements.txt
```

### Configuring the connection to a datalake

We're using Azure blob storage with hierarchical namespaces as a data lake in
the sample. To access the data lake, you'll need to set up a connection in the
UI.

![Airflow UI with connection settings](images/datalake-connection.png)

If you're running on Azure, and you have managed identity set up for your 
Kubernetes cluster, you can choose to set an account name. For the purposes
of the sample, we recommend setting the Blob Storage Connection String instead.

Make sure to name the connection `wasb_datalake`. This is preconfigured in the
tasks in the sample pipeline.

In the configured storage account, you'll need the following containers:

* `raw` - This is where you need to store the raw dataset.
* `intermediate` - This is where intermediate results are stored.
* `preprocessed` - This is where the preprocessed data is stored.

You can get the sample dataset from [this website][DATASET_URL]. Upload it to
the `raw` container in the folder `wachttijden/2022/09/09/`. Make sure you
rename the file to `wachttijden.csv`.

### Making changes to pipelines

When you've deployed all the components to your Kubernetes environment. You can
start building a pipeline. 

We've included a sample in the folder `src/pipelines`. This folder is
automatically synced from the linked GIT repository.

Every time you push a change to your linked GIT repository, the changes are
picked up by the Airflow instance.

### Starting pipelines

We've used a manual schedule for each pipeline in the sample. You'll need to
login to the airflow instance to start the pipelines. 

First, you'll need to start a port-forward to the Airflow instance. Use the 
following command to start the port-forward:

```shell
kubectl port-forward -n airflow svc/airflow-webserver 8080:8080
``` 

After starting the port-forward, navigate to `http://localhost:8080` and log in
using the username `admin` and the password you configured during deployment.

You can now start the pipelines from the user interface.

### Training and deploying a model
After having completed all previous tasks, a model can be trained by consecutively running the prepare_dataset and the train_model pipelines. Afterwards a trained model should reside in `modelartifacts` container in the linked storage account.

#### Deployment using Airflow
A trained model can be deployed using Airflow by running the deploy_model DAG. A URL to the artifacts of the model should be provided by either modifying the config by running via `Trigger DAG w\ config` or by setting a `deploy_model_artifact_url` Variable in Airflow. Make sure to either make blobs in the model artifacts container publicly availabe or set up KServe authentication with a service principal with the [following guide](https://kserve.github.io/website/0.9/modelserving/storage/azure/azure/#using-private-blobs). If the latter option is chosen, the serviceAccountName should be added to V1beta1PredictorSpec in `src/pipelines/tasks/deploy.py` and please mind that this has not been tested during development of the current repo.

#### Manual deployment
In order to deploy the model using KServe, the URL to the `model/` folder in the storage account should be included in the `deploy/model/deploy-model.yml` file. Make sure to either make blobs in the container publicly availabe or set up KServe authentication with a service principal with the [following guide](https://kserve.github.io/website/0.9/modelserving/storage/azure/azure/#using-private-blobs). If the latter option is chosen, don't forget to include the serviceAccountName in `deploy/model/deploy-model.yml`. The model can then be deployed using the following command:
```shell
./deploy-model.sh
```

### Testing a deployed model
After the model has been succesfully deployed, the model can be tested with testdata that has been included in the project in the `src/tests/data/testdata.json` file. In order to do so, the following command should be run:
```shell
./perform-prediction.sh
```

### Traffic mirroring
In order to test a new version of a model, one could want to apply [traffic mirroring](https://istio.io/latest/docs/tasks/traffic-management/mirroring/). In this way, a new model can be tested without impacting the original prediction endpoint. With KServe, this kind of functionality can be implemented using an [InferenceGraph](https://github.com/kserve/kserve/tree/master/docs/samples/graph).

#### Deployment using Airflow
An example of traffic mirroring can be deployed using Airflow by running the deploy_traffic_mirroring DAG. URLs to the artifacts folder should be included in either the config by running via `Trigger DAG w\ config` or by setting the correct Airflow Variables. The minimum required variables are the following: `traffic_mirroring_model1_artifact_url` and `traffic_mirroring_model2_artifact_url`. 

#### Manual deployment
A sample in which two versions of a model are deployed in such a way can be executed with the following script:
```shell
./deploy-sequence.sh
```
Don't forget to first replace the `<artifact_url>` values in `deploy/model/deploy-sequence.yml` with URIs to model artifacts.

#### Testing deployed traffic mirroring sequence
After all resources have been deployed, i.e. the first model, the second model and the inference graph, a test with the InferenceGraph can be run using the following script:

```shell
./perform-prediction-sequence.sh
```

### Running tests

In the `src/tests` folder you'll find a couple of unit-tests for various parts
of the pipeline steps. You can run the tests using the following command:

```shell
AIRFLOW__CORE__DAGS_FOLDER=./src/pipelines python -m pytest -s ./src/
```

This command configures airflow so it loads the folder `src/pipelines` and then
starts pytest from the `src/` folder. 

### Debugging pipelines

This project includes a launch configuration for VSCode. You can find it in
`.vscode/launch.json`. Please make sure you set the correct path for the
`program` argument so it points to the location of the airflow executable. 
Also don't forget to initialize a connection when debugging locally. This can 
be done using the 
[following guide](https://fizzylogic.nl/2022/09/10/how-to-debug-airflow-dags-in-vscode#:~:text=You%20can%20store%20connections%20in,json%20connections/dev/all.json). Last, the environment variable
`AZURE_STORAGE_CONNECTION_STRING` should be set to a connection string that
has access to your Azure Blob Storage and when running either the deploy_model or the deploy_traffic_mirroring DAGs, values for the artifact URLs should be set in `variables/dev/all.json`. 

## Documentation

This section describes various design choices in the sample. You can use this if
you're looking to bring the ideas from this sample into your own project.

### Runtime view

This section covers the key runtime scenario's for the sample.

#### How DAGs are executed

Whenever you run a DAG, the Airflow scheduler will use the Kubernetes executor
to run the individual tasks in the DAG. Tasks don't exchange data, but they can
exchange metadata such as the location of an output file or input file.

Log files generated by a task are collected through filebeat and sent to
logstash. Logstash enriches the incoming log data with extra fields needed by
Airflow to display the log in the user interface. After enriching the data,
Logstash forwards the data to elastic search.

#### How DAGs are deployed

There are a few options to get DAGs into the Airflow environment. We've 
choosen to link Airflow to a GIT repository. You're looking at the linked GIT
repository right now. 

Whenever you commit and push files to GIT, the repository is synced with the
Airflow environment. Please note, it will take up to a minute for the
environment to detect the new and modified DAGs.

### Deployment architecture

This sample contains a pretty large number of moving parts. In this section
we'll cover how these parts work together inside the Kubernetes cluster.

![Deployment architecture](images/deployment-architecture.png)

After deploying all the components you'll have two namespaces on your
Kubernetes cluster:

| Namespace | Description                                        |
|-----------|----------------------------------------------------|
| airflow   | Contains all components related to Apache Airflow. |
| logging   | Contains all logging components.                   |

#### Airflow components

* webserver - Hosts the UI and the REST API.
* scheduler - Schedules DAGs and monitors progress.
* worker - Each task is deployed as a worker pod in the cluster.
* triggerer - Processes DAG triggers.

#### Logging components

* kibana - Dashboarding tool for elasticsearch.
* elasticsearch - Stores logging data.
* logstash - Enriches data before pushing it to elasticsearch.
* filebeat - Scrapes log data from the airflow components.

#### Machine learning components

* mlflow - Tracking of model training runs and stores registered models

[DATASET_URL]: https://puc.overheid.nl/PUC/Handlers/DownloadDocument.ashx?identifier=PUC_656543_22&versienummer=1
