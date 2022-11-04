from airflow.decorators import dag
import pendulum
from tasks.deploy_single_model import deploy_single_model
from utils.utils import try_get_variable


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2021, 1, 1, tz='UTC'),
    catchup=False,
    tags=['wachttijden']
)
def deploy_model(
        deploy_model_artifact_url: str = try_get_variable('deploy_model_artifact_url') or '<artifact-url>',
        deploy_model_model_name: str = try_get_variable('deploy_model_model_name') or 'mlflow-wachttijden-tree'):
    deploy_single_model({
        'artifact_url': deploy_model_artifact_url,
        'model_name': deploy_model_model_name
    })


deploy_model_dag = deploy_model()