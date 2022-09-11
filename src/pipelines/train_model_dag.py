from airflow.decorators import dag, task
import pendulum
from tasks.train import train


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2021,1,1,tz='UTC'),
    catchup=False,
    tags=['wachttijden']
)
def train_model():
    train({
        'container': 'preprocessed',
        'filename': 'wachttijden/2022/9/11/wachttijden.csv'
    })


train_model_dag = train_model()