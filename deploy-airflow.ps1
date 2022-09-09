helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm upgrade --install airflow apache-airflow/airflow --namespace airflow -f deploy/airflow/values-override.yml -f deploy/airflow/values-secrets.yml