from airflow.decorators import task

@task.virtualenv(
    use_dill=True,
    system_site_packages=True,
    requirements=[
        'pandas==1.3.5',
        'apache-airflow-providers-microsoft-azure==4.2.0',
        'pendulum==2.1.2'
    ]
)
def fix_missing_values(input_data):
    import pandas as pd
    from pathlib import Path
    from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
    import pendulum

    now = pendulum.now(tz='UTC')
    local_input_path = Path('/tmp/wachttijden.csv')
    storage_hook = WasbHook('wasb_datalake', public_read=False)

    storage_hook.get_file(local_input_path, input_data['container'], input_data['filename'])

    df = pd.read_csv(local_input_path)

    df = df.dropna(subset=['WACHTTIJD'])    
    df['TYPE_ZORGINSTELLING'] = df['TYPE_ZORGINSTELLING'].fillna('Kliniek')

    df.to_csv(local_output_path, index=False)

    remote_output_path = 'wachttijden/{}/{}/{}/wachttijden.csv'.format(now.year, now.month, now.day)
    local_output_path = Path('/tmp/wachttijden_processed.csv')

    with open(local_output_path, 'rb') as output_file:
        storage_hook.upload('preprocessed', remote_output_path, output_file, overwrite=True)

    return {
        'container': 'preprocessed',
        'filename': remote_output_path
    }