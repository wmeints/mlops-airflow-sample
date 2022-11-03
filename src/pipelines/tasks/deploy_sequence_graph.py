from airflow.decorators import task


@task.virtualenv(
    use_dill=True,
    system_site_packages=True,
    requirements=[
        'kubernetes==25.3.0',
        'kserve==0.9.0'
    ]
)
def deploy_sequence_graph(input_data):
    from kubernetes import client
    from kserve import KServeClient
    from kserve import constants
    from kserve import V1alpha1InferenceRouter
    from kserve import V1alpha1InferenceStep
    from kserve import V1alpha1InferenceGraphSpec
    from kserve import V1alpha1InferenceGraph

    nodes = {"root": V1alpha1InferenceRouter(
        router_type="Sequence",
        steps=[
            V1alpha1InferenceStep(
                service_name=input_data['model1_name'],
            ),
            V1alpha1InferenceStep(
                service_name=input_data['model2_name'],
                data="$request",
            ),
        ],
    )}

    graph_spec = V1alpha1InferenceGraphSpec(
        nodes=nodes
    )

    ig = V1alpha1InferenceGraph(
        api_version=constants.KSERVE_V1ALPHA1,
        kind=constants.KSERVE_KIND_INFERENCEGRAPH,
        metadata=client.V1ObjectMeta(
            name=input_data['sequence_graph_name'],
            namespace='knative-serving'
        ),
        spec=graph_spec
    )

    KServe = KServeClient()
    KServe.create_inference_graph(ig)
    KServe.wait_ig_ready(input_data['sequence_graph_name'], namespace='knative-serving')
