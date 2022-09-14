import pendulum
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
from tasks.select_features import select_features
from tasks.fix_missing_values import fix_missing_values


default_args = {
    'datalake_connection': 'wasb_datalake',
    'depends_on_past': False,
    'retries': 3
}


with DAG(
    dag_id='prepare_dataset',
    schedule_interval='@daily',
    start_date=pendulum.datetime(2021, 9, 9)
) as dag:

    select_features_task = PythonVirtualenvOperator(
        python_callable=select_features,
        task_id='select_features',
        requirements=[
            'pandas==1.3.5',
            'apache-airflow-providers-microsoft-azure==4.2.0',
            'pendulum==2.1.2'
        ],
        system_site_packages=True,
    )

    fix_missing_values_task = PythonVirtualenvOperator(
        python_callable=fix_missing_values,
        task_id='fix_missing_values',
        requirements=[
            'pandas==1.3.5',
            'apache-airflow-providers-microsoft-azure==4.2.0',
            'pendulum==2.1.2'
        ],
        system_site_packages=True,
        op_kwargs={ 
            'input_path': '{{xcom.pull(task_ids="select_features", key="output_path")}}', 
            'input_container': '{{xcom.pull(task_ids="select_features", key="container")}}' 
        }
    )

    select_features_task >> fix_missing_values_task