# MLOps environment with Airflow, MLFlow, and KServe

This repository contains a fully deployable environment for doing MLOps with 
Apache Airflow, MLFlow, and KServe.

## Getting started

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
./deploy-airflow.ps1
```

It will take a few minutes to deploy the airflow components.

