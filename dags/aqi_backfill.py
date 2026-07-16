"""
DAG de backfill : à déclencher manuellement depuis l'UI Airflow (bouton "Trigger DAG"),
une fois au démarrage du projet (ou en cas de trou de données à combler).
"""
from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.models.param import Param
from airflow.operators.bash import BashOperator

REPO_DIR = "/opt/airflow/repo"

with DAG(
    dag_id="aqi_backfill",
    description="Backfill historique AQI (déclenchement manuel)",
    schedule=None,
    start_date=pendulum.datetime(2026, 7, 1, tz="UTC"),
    catchup=False,
    tags=["aqi", "backfill"],
    params={"days": Param(90, type="integer", description="Nombre de jours à backfiller (90=3 mois, 365=12 mois)")},
) as dag:

    backfill = BashOperator(
        task_id="backfill_raw",
        bash_command=f"cd {REPO_DIR}/src && python backfill.py --days {{{{ params.days }}}}",
    )

    build_clean = BashOperator(
        task_id="build_clean",
        bash_command=f"cd {REPO_DIR}/src && python build_clean.py",
    )

    validate_clean = BashOperator(
        task_id="validate_clean",
        bash_command=f"cd {REPO_DIR}/src && python validate_clean.py",
    )

    load_warehouse = BashOperator(
        task_id="load_warehouse",
        bash_command=f"cd {REPO_DIR}/src && python load_warehouse.py",
    )

    git_commit_push = BashOperator(
        task_id="git_commit_push",
        bash_command=f"""
        set -e
        cd {REPO_DIR}
        git config user.name "$GIT_USER_NAME"
        git config user.email "$GIT_USER_EMAIL"
        git add data/raw data/clean
        git diff --staged --quiet || git commit -m "chore(data): backfill airflow $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        git push "$GIT_REPO_URL" HEAD:main
        """,
    )

    backfill >> build_clean >> validate_clean >> load_warehouse >> git_commit_push
