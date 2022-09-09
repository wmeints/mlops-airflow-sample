
import pendulum
from pathlib import Path
from airflow.decorators import dag, task
from airflow.providers.microsoft.azure.hooks.data_lake import AzureDataLakeHook


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
        requirements=['pandas==1.4.3']
    )
    def select_features():
        import pandas as pd

        now = pendulum.now(tc='UTC')

        remote_input_path = Path('/raw/wachttijden/2022/09/09/wachttijden.csv')
        local_input_path = Path('/tmp/wachttijden.csv')

        remote_output_path = Path(f'/intermediate/wachttijden/{now.year}/{now.month}/{now.day}/wachttijden.csv')
        local_output_path = Path('/tmp/wachttijden_processed.csv')

        feature_names = [
            'WACHTTIJD'
            'TYPE_WACHTTIJD',
            'SPECIALISME',
            'ROAZ_REGIO',
            'TYPE_ZORGINSTELLING'
        ]

        datalake_hook = AzureDataLakeHook()
        datalake_hook.download_file(local_input_path, remote_input_path)

        df = pd.read_csv(local_input_path)
        df = df[feature_names]

        df.to_csv(local_output_path)

        datalake_hook.upload_file(local_output_path, remote_output_path)

    select_features()

prepare_dataset_dag = prepare_dataset()