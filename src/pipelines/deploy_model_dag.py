from airflow.decorators import dag
import pendulum
from tasks.deploy import deploy


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2021,1,1,tz='UTC'),
    catchup=False,
    tags=['wachttijden']
)
def deploy_model():
    deploy({
        'artifact_url': '<artifact-url>'
    })


deploy_model_dag = deploy_model()