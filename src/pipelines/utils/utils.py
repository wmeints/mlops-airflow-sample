from airflow.exceptions import AirflowBadRequest

def check_default_artifact_url(default_artifact_url, artifact_url):
    if artifact_url == default_artifact_url:
        raise AirflowBadRequest(f'Cannot deploy model with default artifact_url: {artifact_url}')