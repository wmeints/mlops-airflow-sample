CONNECTION_STRING=postgresql://${DB_USER}:${DB_PASSWORD}@$DB_SERVER/${DB_NAME}

echo $CONNECTION_STRING

mlflow server \
    --default-artifact-root /opt/artifacts \
    --backend-store-uri "${CONNECTION_STRING}" \
    --host 0.0.0.0
