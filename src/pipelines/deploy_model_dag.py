from airflow.decorators import dag
import pendulum
from tasks.deploy_single_model import deploy_single_model


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2021,1,1,tz='UTC'),
    catchup=False,
    tags=['wachttijden']
)
def deploy_model():
    deploy_single_model({
        'artifact_url': '<artifact-url>'
    })


deploy_model_dag = deploy_model()