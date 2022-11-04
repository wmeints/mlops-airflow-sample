from airflow.decorators import dag
import pendulum
from tasks.deploy_single_model import deploy_single_model
from tasks.deploy_sequence_graph import deploy_sequence_graph
from utils.utils import try_get_variable


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2021, 1, 1, tz='UTC'),
    catchup=False,
    tags=['wachttijden']
)
def deploy_traffic_mirroring(
        traffic_mirroring_model1_artifact_url: str = try_get_variable('traffic_mirroring_model1_artifact_url') or '<artifact-url>',
        traffic_mirroring_model1_model_name: str = try_get_variable('traffic_mirroring_model1_model_name') or 'mlflow-wachttijden-tree',
        traffic_mirroring_model2_artifact_url: str = try_get_variable('traffic_mirroring_model2_artifact_url') or '<artifact-url>',
        traffic_mirroring_model2_model_name: str = try_get_variable('traffic_mirroring_model2_model_name') or 'mlflow-wachttijden-tree-v2',
        traffic_mirroring_sequence_graph_name: str = try_get_variable('traffic_mirroring_sequence_graph_name') or 'sequence-model'):

    deploy_first_model = deploy_single_model({
        'artifact_url': traffic_mirroring_model1_artifact_url,
        'model_name': traffic_mirroring_model1_model_name
    })

    deploy_second_model = deploy_single_model({
        'artifact_url': traffic_mirroring_model2_artifact_url,
        'model_name': traffic_mirroring_model2_model_name
    })

    deploy_ig = deploy_sequence_graph({
        'model1_name': traffic_mirroring_model1_model_name,
        'model2_name': traffic_mirroring_model2_model_name,
        'sequence_graph_name': traffic_mirroring_sequence_graph_name
    })

    [deploy_first_model, deploy_second_model] >> deploy_ig


deploy_traffic_mirroring_dag = deploy_traffic_mirroring()
