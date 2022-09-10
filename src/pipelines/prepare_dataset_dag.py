import pendulum
from airflow.decorators import dag, task
from tasks.select_features import select_features
from tasks.fix_missing_values import fix_missing_values


@dag(
    schedule_interval='@daily',
    start_date=pendulum.datetime(2021,1,1, tz='UTC'),
    catchup=False,
    tags=['wachttijden']
)
def prepare_dataset():
    fix_missing_values(select_features())
    
prepare_dataset_dag = prepare_dataset()
