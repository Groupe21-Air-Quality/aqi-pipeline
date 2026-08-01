# ARCHITECTURE.md — Pipeline AQI

## Vue d'ensemble

```
OpenWeather Air Pollution API (5 villes)
        │  collecte horaire + backfill (90 jours)
        ▼
GitHub Actions (orchestrateur)
        ▼
STOCKAGE (dans le repo Git)
  data/raw/    fichiers JSON bruts, jamais modifiés
  data/clean/  air_quality_clean.csv (reconstruit à chaque run)
        ▼
DATA WAREHOUSE — Neon (PostgreSQL)
  Schéma en étoile : fact_air_quality + dim_city + dim_time
```

## Stack choisie

| Composant | Choix | Justification |
|---|---|---|
| **Source de données** | OpenWeather Air Pollution API | API gratuite et fiable permettant de récupérer automatiquement l'indice AQI ainsi que les principaux polluants atmosphériques (CO, NO, NO₂, O₃, SO₂, PM2.5, PM10 et NH₃) pour plusieurs villes à partir de leurs coordonnées GPS. |
| **Orchestrateur** | GitHub Actions | Nous sommes partis d'abord sur **Apache Airflow en local (Docker)**, mais aucun membre du groupe ne pouvait garantir de laisser un ordinateur allumé 24h/24 jusqu'après le rendu. Nous avons migré vers **GitHub Actions** (`schedule: cron`) afin d'automatiser l'exécution du pipeline dans le cloud, sans dépendre d'une machine locale, tout en conservant un historique des exécutions dans GitHub. |
| **Stockage raw/clean** | Fichiers dans le repo Git (`data/raw/`, `data/clean/`) | Les données brutes et nettoyées sont versionnées dans GitHub, ce qui facilite le suivi des modifications, le partage entre les membres de l'équipe et la reproductibilité des traitements. |
| **Data Warehouse** | Neon (PostgreSQL serverless) | Neon fournit une base PostgreSQL gratuite, accessible à distance, compatible avec les outils d'analyse comme Power BI et ne nécessite aucune administration de serveur. |
| **Modélisation** | Schéma en étoile | Le schéma en étoile simplifie les analyses décisionnelles en reliant une table de faits aux dimensions Ville et Temps, tout en offrant de bonnes performances pour les requêtes analytiques. |

## Détail de l'orchestration (GitHub Actions)

Deux workflows dans `.github/workflows/` :

- **`aqi_hourly.yml`** — déclenché automatiquement toutes les heures (`cron: '0 * * * *'`). Enchaîne : collecte → reconstruction `clean/` → validation → chargement warehouse → commit/push des données.
- **`aqi_backfill.yml`** — déclenchement manuel (`workflow_dispatch`) avec un paramètre `days`, utilisé pour charger l'historique (90 jours au lancement du projet).

Les deux réutilisent exactement les mêmes scripts Python (`src/collect.py`, `src/build_clean.py`, `src/validate_clean.py`, `src/load_warehouse.py`), qu'ils aient été exécutés par Airflow (phase initiale de test) ou par GitHub Actions (version finale en production), garantissant un unique pipeline de transformation conforme au sujet.

## Secrets

Les identifiants suivants sont stockés en secrets GitHub (Settings → Secrets and variables → Actions), jamais dans le code :

- `OWM_API_KEY` — clé API OpenWeather
- `DATABASE_URL` — chaîne de connexion Neon

Le push automatique des données utilise le token intégré `GITHUB_TOKEN`, avec permission d'écriture activée sur le dépôt GitHub.

## Historique de la démarche (pour le rapport de projet)

1. Mise en place initiale sur **Apache Airflow** (Docker + Docker Compose, en local).
2. Constat que le pipeline devait fonctionner automatiquement même après le rendu, ce qui était difficile à garantir avec une machine locale.
3. Migration vers **GitHub Actions**, en réutilisant les scripts Python développés pour Airflow.
4. Airflow est conservé dans le dépôt comme preuve de la démarche de développement, tandis que GitHub Actions constitue la solution retenue pour l'automatisation du pipeline.

---