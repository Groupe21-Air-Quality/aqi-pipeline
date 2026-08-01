# README — Stockage & Data Warehouse (Pipeline AQI)

## Villes suivies

| Ville | Pays | Latitude | Longitude |
|---|---|---|---|
| Paris | France | 48.8566 | 2.3522 |
| Antananarivo | Madagascar | -18.8792 | 47.5079 |
| New Delhi | Inde | 28.6139 | 77.2090 |
| Beijing | Chine | 39.9042 | 116.4074 |
| Los Angeles | USA | 34.0522 | -118.2437 |

## Zone `data/raw/`

- Un fichier JSON par ville et par appel API, jamais modifié après écriture
- Chemin : `data/raw/<slug_ville>/<slug_ville>_<horodatage>.json`
- Contient la réponse brute d'OpenWeather Air Pollution API, enrichie du nom/pays/coordonnées de la ville
- Sert de source de vérité unique : `data/clean/` est entièrement reconstruit à partir de ces fichiers à chaque exécution

## Zone `data/clean/` — Contrat de données

Fichier unique : **`data/clean/air_quality_clean.csv`**

Une ligne = une ville + une heure. Trié chronologiquement (ville puis horodatage). Dédupliqué sur la clé `(city, timestamp_utc)` — en cas de doublon (ex: chevauchement backfill/collecte horaire), la dernière valeur observée est conservée.

| Colonne | Type | Unité / Format | Description |
|---|---|---|---|
| `city` | texte | — | Nom de la ville |
| `country` | texte | — | Pays |
| `latitude` | décimal | degrés | Latitude de la ville |
| `longitude` | décimal | degrés | Longitude de la ville |
| `timestamp_utc` | datetime | ISO 8601, UTC | Horodatage de la mesure |
| `aqi` | entier | indice OpenWeather 1 à 5 | 1 = Bon, 2 = Correct, 3 = Modéré, 4 = Mauvais, 5 = Très mauvais |
| `co` | décimal | µg/m³ | Monoxyde de carbone |
| `no` | décimal | µg/m³ | Monoxyde d'azote |
| `no2` | décimal | µg/m³ | Dioxyde d'azote |
| `o3` | décimal | µg/m³ | Ozone |
| `so2` | décimal | µg/m³ | Dioxyde de soufre |
| `pm2_5` | décimal | µg/m³ | Particules fines ≤ 2.5 µm |
| `pm10` | décimal | µg/m³ | Particules fines ≤ 10 µm |
| `nh3` | décimal | µg/m³ | Ammoniac |

 Note sur l'AQI OpenWeather : l'échelle va de **1 à 5** (pas l'échelle américaine 0-500 utilisée par d'autres fournisseurs) 

## Data Warehouse — Neon (PostgreSQL)

Schéma en **étoile** : `fact_air_quality` entourée de `dim_city` et `dim_time`.

### `dim_city`
| Colonne | Description |
|---|---|
| `city_id` | Clé primaire |
| `city_name` | Nom de la ville |
| `country` | Pays |
| `latitude` | Latitude |
| `longitude` | Longitude |

### `dim_time`
| Colonne | Description |
|---|---|
| `time_id` | Clé primaire (format `YYYYMMDDHH`) |
| `full_datetime` | Horodatage complet UTC |
| `date` | Date seule |
| `hour` | Heure (0-23) |
| `day`, `month`, `year` | Composants de la date |
| `day_of_week` | Nom du jour (ex: Monday) |
| `day_of_week_num` | 0 = lundi ... 6 = dimanche |
| `is_weekend` | Booléen |
| `week_of_year` | Numéro de semaine ISO |

### `fact_air_quality`
| Colonne | Description |
|---|---|
| `city_id` | Clé étrangère → `dim_city` |
| `time_id` | Clé étrangère → `dim_time` |
| `aqi`, `co`, `no`, `no2`, `o3`, `so2`, `pm2_5`, `pm10`, `nh3` | Mesures (mêmes unités que `clean/`, voir tableau ci-dessus) |

Le warehouse est **rechargé intégralement à chaque exécution** (`TRUNCATE` puis réinsertion depuis `clean/`) — cohérence garantie entre `clean/` et le warehouse à tout moment.

## Période couverte

- * : Backfill du `1/04/2026` au `31/07/2026` (90 jours), + collecte horaire continue depuis le `26/07/2026`.
- Dernière mise à jour : voir le dernier commit `chore(data): run automatique GitHub Actions ...` dans l'historique Git, ou la dernière exécution dans l'onglet **Actions** du repo.

## Trous connus dans les données

-  *"Aucun trou connu à ce jour, vérifié via `validate_clean.py`."*

## Cohérence des volumes

Nombre de lignes attendu ≈ 5 villes × nombre d'heures couvertes depuis le début du backfill.

- il y a en tous 10810 ligne de donne dans le fichier csv dans le dossier clean


## Orchestration

Voir `ARCHITECTURE.md` pour le détail des workflows GitHub Actions (`aqi_hourly.yml`, `aqi_backfill.yml`).
