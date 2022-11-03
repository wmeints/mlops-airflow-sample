from airflow.decorators import dag
import pendulum
from tasks.deploy_single_model import deploy_single_model
from tasks.deploy_sequence_graph import deploy_sequence_graph


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2021, 1, 1, tz='UTC'),
    catchup=False,
    tags=['wachttijden']
)
def deploy_traffic_mirroring():
    model1_name = 'mlflow-wachttijden-tree'
    model2_name = 'mlflow-wachttijden-tree-v2'
    sequence_graph_name = 'sequence-model'

    deploy_first_model = deploy_single_model({
        'artifact_url': '<artifact-url>',
        'model_name': model1_name
    })

    deploy_second_model = deploy_single_model({
        'artifact_url': '<artifact-url>',
        'model_name': model2_name
    })

    deploy_ig = deploy_sequence_graph({
        'model1_name': model1_name,
        'model2_name': model2_name,
        'sequence_graph_name': sequence_graph_name
    })

    [deploy_first_model, deploy_second_model] >> deploy_ig


deploy_traffic_mirroring_dag = deploy_traffic_mirroring()
