def select_features():
    import pandas as pd
    from pathlib import Path
    from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
    import pendulum
    import json

    execution_date = pendulum.now(tz='UTC')

    remote_input_path = 'wachttijden/2022/09/09/wachttijden.csv'
    local_input_path = Path('/tmp/wachttijden.csv')

    remote_output_path = 'wachttijden/{}/{}/{}/wachttijden.csv'.format(execution_date.year, execution_date.month, execution_date.day)
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

    df = pd.read_csv(local_input_path, sep=';')
    df = df[feature_names]

    df.to_csv(local_output_path, sep=';')

    with open(local_output_path, 'rb') as output_file:
        storage_hook.upload('intermediate', remote_output_path, output_file, overwrite=True)

    return json.dumps({
        'container': 'intermediate',
        'filename': remote_output_path
    })

