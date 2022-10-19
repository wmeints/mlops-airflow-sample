# This script can be used to prepare the airflow environment when you're not using VSCode.

AIRFLOW_HOME=$PWD

rm -rf airflow.db
airflow db init
airflow users create --username admin --firstname admin --lastname admin --password admin --role Admin --email admin@example.org

if [ -f variables/dev/all.json ]; then airflow variables import variables/dev/all.json; fi
if [ -f connections/dev/all.json ]; then airflow connections import connections/dev/all.json; fi
