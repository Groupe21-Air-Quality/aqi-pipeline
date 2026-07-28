"""
DAG horaire du pipeline AQI : collecte -> clean -> validation -> warehouse -> push Git.

Tourne dans le conteneur Airflow (LocalExecutor), en s'appuyant sur les mêmes
scripts que la version GitHub Actions (src/collect.py, build_clean.py, etc.),
pour garder un seul code de transformation quel que soit l'orchestrateur.
"""
from __future__ import annotations

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

REPO_DIR = "/opt/airflow/repo"

default_args = {
    "retries": 2,
    "retry_delay": pendulum.duration(minutes=5),
}

with DAG(
    dag_id="aqi_hourly_pipeline",
    description="Collecte horaire AQI -> clean -> validation -> warehouse -> push Git",
    schedule="@hourly",
    start_date=pendulum.datetime(2026, 7, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["aqi", "warehouse"],
) as dag:

    collect_raw = BashOperator(
        task_id="collect_raw",
        bash_command=f"cd {REPO_DIR}/src && python collect.py",
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

    # Commit + push : garde une preuve d'exécution vérifiable dans l'historique
    # Git même si la machine locale s'éteint ensuite. Nécessite GIT_REPO_URL au
    # format https://<token>@github.com/<user>/<repo>.git (voir .env.example).
    git_commit_push = BashOperator(
        task_id="git_commit_push",
        bash_command=f"""
        set -e
       cd {REPO_DIR}
        git config --global --add safe.directory {REPO_DIR}
        git config user.name "$GIT_USER_NAME"
        git config user.email "$GIT_USER_EMAIL"
        git remote set-url origin "$GIT_REPO_URL"
        git add data/raw data/clean
        git diff --staged --quiet || git commit -m "chore(data): run automatique airflow $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        git push origin HEAD:main
        """,
    )

    collect_raw >> build_clean >> validate_clean >> load_warehouse >> git_commit_push
