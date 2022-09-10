import pytest


def test_import_errors(dag_bag):
    """
    Tests that the pipelines can indeed be imported into Airflow.

    - No errors are thrown when importing the pipelines
    - There are no cycles in the pipelines
    """
    assert len(dag_bag.import_errors) == 0


def test_dags_have_tasks(dag_bag):
    """
    Tests that the pipelines loaded tasks and we don't have any empty pipelines.
    """
    for dag in dag_bag.dags.values():
        assert len(dag.tasks) > 0
