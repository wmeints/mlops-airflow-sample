kubectl apply -n airflow -f ./deploy/mlflow
kubectl apply -n airflow -f ./deploy/mlflow/database-server
kubectl apply -n airflow -f ./deploy/mlflow/tracking-server