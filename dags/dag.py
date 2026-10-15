from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="amo_crm",
    start_date=datetime(2026, 10, 12),
    schedule=None,
    catchup=False,
) as dag:

    run_contacts = BashOperator(
        task_id="contacts",
        bash_command="cd /opt/airflow/dags/pipelines && python contacts.py",
    )

    run_company = BashOperator(
        task_id="company",
        bash_command="cd /opt/airflow/dags/pipelines && python company.py",
    )

    run_transactions = BashOperator(
        task_id="transactions",
        bash_command="cd /opt/airflow/dags/pipelines && python transactions.py",
    )

    run_contacts >> run_company >> run_transactions