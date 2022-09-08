FROM python:3.9
RUN apt update && apt install -y python3-venv gcc
RUN apt-get install -y python3-dev build-essential

ENV VENV=/.venv/myenv
RUN python3 -m venv ${VENV}
RUN mkdir -p $VENV/src
ENV PATH=$VENV/bin:$PATH
RUN pip install -U pip
RUN pip install psycopg2 mlflow

# Expose the port that the MLFlow tracking server runs on
EXPOSE 5000
# Default database credentials
ENV DB_USERNAME=
ENV DB_PASSWORD=
ENV DB_SERVER=
ENV DB_NAME=

ENTRYPOINT mlflow server \
        --default-artifact-root /opt/artifacts \
        --backend-store-uri "postgresql://${DB_USER}:${DB_PASSWORD}@$DB_SERVER/$DB_NAME" \
        --host 0.0.0.0