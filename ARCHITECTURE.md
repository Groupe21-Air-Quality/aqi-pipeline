# ARCHITECTURE.md

## Vue d'ensemble

```
OpenWeatherMap Air Pollution API (5 villes)
        │  collecte horaire + backfill (3-12 mois)
        ▼
Airflow (Docker Compose, LocalExecutor, sur une machine du groupe)
        ▼
STOCKAGE (dans le repo Git, poussé par le DAG à chaque run)
  data/raw/    fichiers JSON bruts, jamais modifiés
  data/clean/  1 fichier CSV unique, reconstruit à chaque run depuis raw/
        ▼
PostgreSQL (Supabase/Neon) — Data Warehouse en étoile
  dim_city + dim_time + fact_air_quality
```

> **Deux variantes du même code sont fournies dans ce repo :**
> - `.github/workflows/` : orchestrateur GitHub Actions (cloud, aucune machine à maintenir)
> - `docker-compose.yaml` + `dags/` : orchestrateur Airflow en local via Docker
>
> Les deux réutilisent exactement les mêmes scripts `src/*.py` — seule la
> couche d'orchestration change. **Un seul des deux doit être actif en
> production** pour éviter les doubles écritures dans le warehouse (désactiver
> le déclenchement automatique de l'autre : mettre le workflow GitHub Actions
> en pause, ou ne pas lancer le scheduler Airflow, selon celui que vous gardez).

## Choix techniques et justifications

| Composant | Choix | Justification |
|---|---|---|
| **API AQI** | OpenWeatherMap Air Pollution (current + history) | Gratuite, couvre les 5 villes, fournit un historique jusqu'à plusieurs années, et livre à la fois un indice AQI global et le détail par polluant (CO, NO, NO2, O3, SO2, PM2.5, PM10, NH3). |
| **Orchestrateur** | Airflow (Docker Compose, LocalExecutor) sur une machine du groupe | Choix pédagogique aligné sur l'outil vu en cours (DAGs, scheduler, UI de suivi des runs) ; entièrement conteneurisé donc reproductible par n'importe quel membre (`docker compose up`) ; `docker-compose.yaml` et les DAGs sont versionnés dans le repo. **Contrepartie assumée** : contrairement à un orchestrateur cloud, la machine hôte doit rester allumée, connectée et sans veille 24h/24 pour respecter la contrainte "le pipeline continue à tourner après le rendu" — voir mitigations ci-dessous. |
| **Stockage raw/clean** | Fichiers dans le repo Git (`data/raw/`, `data/clean/`) | Simplicité, gratuité, traçabilité par les commits automatiques du bot ; chaque run du pipeline laisse une trace vérifiable dans l'historique Git. |
| **Data Warehouse** | PostgreSQL hébergé (Supabase ou Neon, offre gratuite) | Accessible à distance en continu (contrairement à SQLite), ce qui permet à IA1 de s'y connecter directement au fil de l'eau ; supporte nativement les clés étrangères et contraintes d'unicité nécessaires au schéma en étoile. |
| **Modélisation** | Schéma en étoile (1 table de faits + 2 dimensions) | Les deux axes d'analyse demandés (temps, ville) sont indépendants et non hiérarchiques entre eux : pas besoin de flocon. Respecte les règles du cours : aucune mesure (AQI, polluants) dans les dimensions, aucune colonne descriptive (nom de ville, jour de semaine...) dans la table de faits — uniquement des clés étrangères et des mesures numériques. |
| **Secret de la clé API** | Secret GitHub Actions (`secrets.OWM_API_KEY`) + variable d'environnement | Jamais écrite en dur dans le code ni commitée ; injectée uniquement au moment de l'exécution du workflow. |

## Flux d'exécution (chaque run horaire)

1. `collect.py` : appelle l'API pour les 5 villes → écrit 5 fichiers JSON dans `data/raw/<ville>/`
2. `build_clean.py` : relit **tous** les fichiers de `data/raw/` (récursivement) → reconstruit `data/clean/air_quality_clean.csv` en entier, dédoublonné et trié
3. `validate_clean.py` : vérifie le contrat de données (colonnes, doublons, tri, plages de valeurs) ; le workflow s'arrête si la validation échoue
4. `load_warehouse.py` : vide et recharge entièrement le warehouse PostgreSQL depuis `clean/`
5. Le bot commit et push les nouveaux fichiers `data/raw/` et `data/clean/` dans le repo

Le backfill (`backfill.py`) suit le même principe mais interroge l'endpoint `history` de l'API, découpé en tranches de 30 jours, et est déclenché manuellement une seule fois (ou à la demande) via le DAG `aqi_backfill` (Airflow) ou `workflow_dispatch` (GitHub Actions).

## Risque "machine locale" et mitigations (variante Airflow/Docker)

Faire tourner l'orchestrateur sur l'ordinateur d'un membre du groupe expose à un
risque réel : mise en veille, redémarrage, coupure de courant/réseau ou
extinction après la soutenance arrêtent la collecte, et un warehouse qui ne
répond plus vaut zéro selon les règles de l'exam. Mitigations retenues :

- **Le warehouse reste hébergé à distance** (Supabase/Neon) : il répond en
  continu même si l'ordinateur du groupe est éteint. Seule la *collecte de
  nouvelles données* s'arrête, pas l'accès aux données déjà chargées.
- **`data/raw/` et `data/clean/` sont poussés sur GitHub à chaque run** : même
  si la machine s'éteint après le rendu, l'historique de commits prouve que le
  pipeline a bien tourné sur plusieurs jours à des heures automatiques.
- Réglages recommandés sur la machine hôte : désactiver la mise en veille
  automatique, brancher sur secteur, préférer une machine dédiée (mini-PC,
  ancien PC, Raspberry Pi) plutôt qu'un laptop utilisé quotidiennement.
- En cas de doute sur la disponibilité de la machine le jour du rendu, le
  workflow GitHub Actions fourni en parallèle peut servir de filet de
  sécurité (il suffit de le réactiver).
