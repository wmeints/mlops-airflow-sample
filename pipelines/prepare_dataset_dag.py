
import pendulum
from pathlib import Path
from airflow.decorators import dag, task


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2021,1,1, tz='UTC'),
    catchup=False,
    tags=['wachttijden']
)
def prepare_dataset():

    @task.virtualenv(
        use_dill=True,
        system_site_packages=True,
        requirements=[
            'pandas==1.4.3',
            'apache-airflow-providers-microsoft-azure==4.2.0'
        ]
    )
    def select_features():
        import pandas as pd
        from airflow.providers.microsoft.azure.hooks.wasb import WasbHook

        now = pendulum.now(tc='UTC')

        remote_input_path = Path('/raw/wachttijden/2022/09/09/wachttijden.csv')
        local_input_path = Path('/tmp/wachttijden.csv')

        remote_output_path = f'/intermediate/wachttijden/{now.year}/{now.month}/{now.day}/wachttijden.csv'
        local_output_path = Path('/tmp/wachttijden_processed.csv')

        feature_names = [
            'WACHTTIJD'
            'TYPE_WACHTTIJD',
            'SPECIALISME',
            'ROAZ_REGIO',
            'TYPE_ZORGINSTELLING'
        ]

        storage_hook = WasbHook('wasb_datalake', public_read=False)

        storage_hook.get_file(local_input_path, 'raw', remote_input_path)

        df = pd.read_csv(local_input_path)
        df = df[feature_names]

        df.to_csv(local_output_path)

        with open(local_output_path, 'rb') as output_file:
            storage_hook.upload('intermediate', remote_output_path, output_file)

    select_features()

prepare_dataset_dag = prepare_dataset()