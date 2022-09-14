from airflow.operators.python import PythonVirtualenvOperator


def fix_missing_values(input_container, input_path, **kwargs):
    import pandas as pd
    from pathlib import Path
    from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
    from airflow.models import Variable
    import pendulum

    datalake_connection = kwargs['datalake_connection']
    execution_date = Variable.get('execution_date')

    local_input_path = Path('/tmp/wachttijden.csv')
    remote_output_path = 'wachttijden/{}/{}/{}/wachttijden.csv'.format(execution_date.year, execution_date.month, execution_date.day)
    local_output_path = Path('/tmp/wachttijden_processed.csv')

    storage_hook = WasbHook(datalake_connection, public_read=False)
    storage_hook.get_file(local_input_path, input_container, input_path)

    df = pd.read_csv(local_input_path)

    df = df.dropna(subset=['WACHTTIJD'])    
    df['TYPE_ZORGINSTELLING'] = df['TYPE_ZORGINSTELLING'].fillna('Kliniek')

    df.to_csv(local_output_path, index=False)

    with open(local_output_path, 'rb') as output_file:
        storage_hook.upload('preprocessed', remote_output_path, output_file, overwrite=True)

    return {
        'container': 'preprocessed',
        'filename': remote_output_path
    }   

