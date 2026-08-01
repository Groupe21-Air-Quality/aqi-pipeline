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

| Composant | Choix | Justification (une phrase par choix — À COMPLÉTER PAR L'ÉQUIPE) |
|---|---|---|
| **Source de données** | OpenWeather Air Pollution API | gratuite, fiable, fournit AQI + 8 polluants (CO, NO, NO2, O3, SO2, PM2.5, PM10, NH3) pour n'importe quelle coordonnée GPS |
| **Orchestrateur** | GitHub Actions | Nous sommes partis d'abord sur **Apache Airflow en local (Docker)**, mais aucun membre du groupe ne pouvait garantir de laisser un ordinateur allumé 24h/24 jusqu'après le rendu. Nous avons migré vers **GitHub Actions** (`schedule: cron`) pour une exécution planifiée hébergée par GitHub, indépendante de toute machine physique, avec un historique d'exécution directement consultable dans l'onglet *Actions* du repo.  |
| **Stockage raw/clean** | Fichiers dans le repo Git (`data/raw/`, `data/clean/`) | : simple, versionné, accessible publiquement via GitHub sans infrastructure supplémentaire à maintenir  |
| **Data Warehouse** | Neon (PostgreSQL serverless) |  gratuit, compatible SQL standard, accessible à distance (utile pour Power BI et pour IA1), pas de serveur à gérer |
| **Modélisation** | Schéma en étoile |  un seul niveau de dimensions (ville, temps) autour de la table de faits, suffisant vu le volume de données et plus simple à interroger qu'un flocon|

## Détail de l'orchestration (GitHub Actions)

Deux workflows dans `.github/workflows/` :

- **`aqi_hourly.yml`** — déclenché automatiquement toutes les heures (`cron: '0 * * * *'`). Enchaîne : collecte → reconstruction `clean/` → validation → chargement warehouse → commit/push des données.
- **`aqi_backfill.yml`** — déclenchement manuel (`workflow_dispatch`) avec un paramètre `days`, utilisé pour charger l'historique (90 jours au lancement du projet).

Les deux réutilisent exactement les mêmes scripts Python (`src/collect.py`, `src/build_clean.py`, `src/validate_clean.py`, `src/load_warehouse.py`), qu'ils aient été exécutés par Airflow (phase initiale de test) ou par GitHub Actions (version finale en production) — un seul code de transformation, comme demandé par le sujet.

## Secrets

Les identifiants suivants sont stockés en secrets GitHub (Settings → Secrets and variables → Actions), jamais dans le code :
- `OWM_API_KEY` — clé API OpenWeather
- `DATABASE_URL` — chaîne de connexion Neon

Le push automatique des données utilise le token intégré `GITHUB_TOKEN`, avec permission d'écriture activée sur le repo.

## Historique de la démarche (pour le rapport de projet)

1. Mise en place initiale sur **Apache Airflow** (Docker + Docker Compose, en local)
2. Constat que le pipeline devait tourner en continu même après le rendu, incompatible avec une machine locale
3. Migration vers **GitHub Actions**, avec réutilisation intégrale des scripts déjà écrits pour Airflow
4. Airflow reste disponible dans le repo pour la démonstration/historique, mais n'est plus l'orchestrateur en production


