from airflow.decorators import task

@task.virtualenv(
    use_dill=True,
    system_site_packages=True,
    requirements=[
        'pandas==1.3.5',
        'scikit-learn==1.0.2',
        'mlflow==1.28.0'
    ]
)
def train(input_data):
    import pandas as pd
    from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
    from airflow.models import Variable
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.pipeline import Pipeline, FeatureUnion
    import mlflow

    tracking_server = Variable.get('mlflow_server')
    local_input_path = '/tmp/wachttijden.csv'

    feature_names = [
        'TYPE_WACHTTIJD',
        'SPECIALISME',
        'ROAZ_REGIO',
        'TYPE_ZORGINSTELLING'
    ]

    mlflow.set_tracking_uri(tracking_server)
    mlflow.set_experiment('wachttijden')

    with mlflow.start_run() as run:
        encoders = [(feature_name, OneHotEncoder()) for feature_name in feature_names]

        model_pipeline = Pipeline([
            ("combine_features", FeatureUnion(encoders)),
            ("estimator", DecisionTreeRegressor())
        ])

        storage_hook = WasbHook('wasb_datalake', public_read=False)
        storage_hook.get_file(local_input_path, input_data['container'], input_data['filename'])

        df = pd.read_csv(local_input_path)
        df_train, df_test = train_test_split(df, test_size=0.2)

        df_train_features = df_train[feature_names]
        df_train_output = df_train['WACHTTIJD']

        df_test_features = df_test[feature_names]
        df_test_output = df_test['WACHTTIJD']

        model_pipeline.fit(df_train_features.to_numpy(), df_train_output.to_numpy())
        score = model_pipeline.score(df_test_features.to_numpy(), df_test_output.to_numpy())

        mlflow.log_metric('r2', score)

        mlflow.sklearn.log_model(model_pipeline, 'model', registered_model_name='wachttijden_tree')

        mlflow.end_run()