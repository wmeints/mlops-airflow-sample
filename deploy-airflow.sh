#!/bin/sh

helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm upgrade --install airflow apache-airflow/airflow \
    --namespace airflow \
    -f deploy/airflow/values-override.yml \
    -f deploy/airflow/values-secrets.yml \
    --create-namespace

# create clusterrolebinding such that the Airflow worker serviceaccount can deploy KServe InferenceServices
kubectl create clusterrolebinding airflow-worker-kserve-manager-rolebinding --clusterrole=kserve-manager-role --serviceaccount=airflow:airflow-worker