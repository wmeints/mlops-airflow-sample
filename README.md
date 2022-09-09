# MLOps environment with Airflow, MLFlow, and KServe

![Airflow dashboard in action](images/airflow-dashboard.png)

This repository contains a fully deployable environment for doing MLOps with 
Apache Airflow, MLFlow, and KServe.

## System requirements

We assume that you have the following:

- Access to a Kubernetes 1.22+ cluster 
- Python 3.9 or higher installed on your machine
- Kubectl must be installed on your machine
- Helm 3 or higher installed on your machine

## Deploying the sample

For the sample to work, you'll need to configure a set of things on top
of Kubernetes. Please follow the instructions in the following sections to
set things up.

### Deploying airflow

We're using Helm to deploy the airflow components to the Kubernetes cluster.
You'll need to perform a few preparation steps before deploying the 
components to the Kubernetes cluster.

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
    pass: <your-password>
```

Make sure you replace the `<your-key>` value with the base64 encoded version
of an SSH private key that has access to the repo you want to sync with airflow.

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
./deploy-airflow.ps1
```

It will take a few minutes to deploy the airflow components.

### Deploying MLFlow

In addition to Airflow, we're going to use a tracking solution for ML models. MLFlow is an open-source tool that allows
you to track experiments and trained models. 

Add a new file `secrets.yml` to the folder `./deploy/mlflow` and add the following content to it:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mlflow-secrets
type: Opaque
data:
  databasePassword: <your-password> 
```

Replace `<your-password>` with a base64-encoded password of your choice. Save the file when you're done.

Use the following command in your terminal to deploy MLFlow:

```shell
./deploy-mlflow.ps1
```

## Working with the sample

### Making changes to pipelines

When you've deployed all the components to your Kubernetes environment. You can
start building a pipeline. 

We've included a sample in the folder `pipelines`. This folder is
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

## Documentation

### Deployment architecture

This sample contains a pretty large number of moving parts. In this section we'll cover how these parts work together
inside the Kubernetes cluster.

![Deployment architecture](images/deployment-architecture.png)

After deploying all the components you'll have two namespaces on your Kubernetes cluster:

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

### Runtime view

This section covers the key runtime scenario's for the sample.

#### How DAGs are executed

Whenever you run a DAG, the Airflow scheduler will use the Kubernetes executor to run the individual tasks in the DAG.
Tasks don't exchange data, but they can exchange metadata such as the location of an output file or input file.

Log files generated by a task are collected through filebeat and sent to logstash. Logstash enriches the incoming
log data with extra fields needed by Airflow to display the log in the user interface. After enriching the data,
Logstash forwards the data to elastic search.

#### How DAGs are deployed

There are a few options to get DAGs into the Airflow environment. We'ved choosen to link Airflow to a GIT repository.
You're looking at the linked GIT repository right now. 

Whenever you commit and push files to GIT, the repository is synced with the Airflow environment. Please note, it
will take up to a minute for the environment to detect the new and modified DAGs.