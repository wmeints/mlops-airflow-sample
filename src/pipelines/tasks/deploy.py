from airflow.decorators import task


@task.virtualenv(
    use_dill=True,
    system_site_packages=True,
    requirements=[
        'kubernetes==25.3.0',
        'kserve==0.9.0'
    ]
)
def deploy(input_data):
    from kubernetes import client
    from kserve import KServeClient
    from kserve import constants
    from kserve import V1beta1InferenceService
    from kserve import V1beta1InferenceServiceSpec
    from kserve import V1beta1PredictorSpec
    from kserve import V1beta1ModelSpec
    from kserve import V1beta1ModelFormat

    isvc = V1beta1InferenceService(api_version=constants.KSERVE_V1BETA1,
                                   kind=constants.KSERVE_KIND,
                                   metadata=client.V1ObjectMeta(
                                       name='mlflow-wachttijden-tree', namespace='knative-serving'),
                                   spec=V1beta1InferenceServiceSpec(
                                       predictor=V1beta1PredictorSpec(
                                           model=V1beta1ModelSpec(
                                               storage_uri=input_data['artifact_url'],
                                               model_format=V1beta1ModelFormat(name='mlflow'))))
                                   )

    KServe = KServeClient()
    KServe.create(isvc)
