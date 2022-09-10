set -a
source <(cat .env | sed -e '/^#/d;/^\s*$/d' -e "s/'/'\\\''/g" -e "s/=\(.*\)/='\1'/g")
set +a

AIRFLOW__CORE__DAGS_FOLDER="${pwd.Path}/src/pipelines/"
AIRFLOW__CORE__EXECUTOR="SequentialExecutor"

airflow standalone