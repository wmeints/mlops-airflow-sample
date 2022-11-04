from airflow.models import Variable

def try_get_variable(var_name):
    try:
        var = Variable.get(var_name)
        return var
    except KeyError:
        return None