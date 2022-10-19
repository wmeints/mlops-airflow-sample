def fix_missing_values(input_data, execution_date_str):
    import pandas as pd
    from pathlib import Path
    from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
    import json
    from datetime import datetime

    input_values = json.loads(input_data)
    execution_date = datetime.fromisoformat(execution_date_str)

    local_input_path = Path('/tmp/wachttijden.csv')
    remote_output_path = 'wachttijden/{}/{}/{}/wachttijden.csv'.format(execution_date.year, execution_date.month, execution_date.day)
    local_output_path = Path('/tmp/wachttijden_processed.csv')

    storage_hook = WasbHook('wasb_datalake', public_read=False)
    storage_hook.get_file(local_input_path, input_values['container'], input_values['filename'])

    df = pd.read_csv(local_input_path, sep=';')

    df = df.dropna(subset=['WACHTTIJD'])    
    df['TYPE_ZORGINSTELLING'] = df['TYPE_ZORGINSTELLING'].fillna('Kliniek')

    df.to_csv(local_output_path, index=False, sep=';')

    with open(local_output_path, 'rb') as output_file:
        storage_hook.upload('preprocessed', remote_output_path, output_file, overwrite=True)

    return json.dumps({
        'container': 'preprocessed',
        'filename': remote_output_path
    })

