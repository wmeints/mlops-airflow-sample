from airflow.decorators import dag
import pendulum
from tasks.deploy_single_model import deploy_single_model
from airflow.models import Variable
from utils.utils import check_default_artifact_url

default_artifact_url = '<artifact-url>'


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2021, 1, 1, tz='UTC'),
    catchup=False,
    tags=['wachttijden']
)
def deploy_model(
        deploy_model_artifact_url: str = Variable.get('deploy_model_artifact_url', default_var=default_artifact_url),
        deploy_model_model_name: str = Variable.get('deploy_model_model_name', default_var='mlflow-wachttijden-tree')):

    check_default_artifact_url(default_artifact_url, deploy_model_artifact_url)

    deploy_single_model({
        'artifact_url': deploy_model_artifact_url,
        'model_name': deploy_model_model_name
    })


deploy_model_dag = deploy_model()
