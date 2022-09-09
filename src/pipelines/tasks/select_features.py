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
def select_features():
    import pandas as pd
    from pathlib import Path
    from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
    import pendulum
    
    now = pendulum.now(tz='UTC')

    remote_input_path = 'wachttijden/2022/09/09/wachttijden.csv'
    local_input_path = Path('/tmp/wachttijden.csv')

    remote_output_path = 'wachttijden/{}/{}/{}/wachttijden.csv'.format(now.year, now.month, now.day)
    local_output_path = Path('/tmp/wachttijden_processed.csv')

    feature_names = [
        'WACHTTIJD',
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
        storage_hook.upload('intermediate', remote_output_path, output_file, overwrite=True)

    return {
        'container': 'intermediate',
        'filename': remote_output_path
    }