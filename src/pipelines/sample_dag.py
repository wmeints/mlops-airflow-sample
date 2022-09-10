from re import M
from airflow.decorators import dag, task
import pendulum


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2021, 1, 1, tz='UTC'),
    catchup=False,
    tags=['sample']
)
def sample_etl():
    @task()
    def extract():
        pass

    @task()
    def transform():
        pass

    @task()
    def load():
        pass

    extract() >> transform() >> load()

sample_dag = sample_etl()