# Pipeline AQI — Data Warehouse qualité de l'air

Pipeline automatisé collectant les données de qualité de l'air (AQI) pour 5 villes,
24h/24, via GitHub Actions, avec stockage brut, fichier clean unique et data
warehouse dimensionnel en PostgreSQL. Voir [`ARCHITECTURE.md`](ARCHITECTURE.md)
pour le détail des choix techniques.

## Villes suivies

| Ville | Pays | Latitude | Longitude |
|---|---|---|---|
| Paris | France | 48.8566 | 2.3522 |
| Antananarivo | Madagascar | -18.8792 | 47.5079 |
| New Delhi | India | 28.6139 | 77.2090 |
| Beijing | China | 39.9042 | 116.4074 |
| Los Angeles | USA | 34.0522 | -118.2437 |

Villes choisies pour couvrir une large plage de niveaux de pollution (de "bon" à
"très mauvais"), utile pour IA1.

## Contrat de données — `data/clean/air_quality_clean.csv`

Une ligne = une ville + une heure. Fichier trié chronologiquement par ville,
dédoublonné sur `(city, timestamp_utc)`.

| Colonne | Type | Unité / format | Description |
|---|---|---|---|
| `city` | string | — | Nom de la ville |
| `country` | string | — | Pays |
| `latitude` | float | degrés décimaux | Latitude du point de mesure |
| `longitude` | float | degrés décimaux | Longitude du point de mesure |
| `timestamp_utc` | string ISO 8601 | UTC | Horodatage de la mesure |
| `aqi` | int | **échelle OpenWeatherMap 1 à 5** | 1=Bon, 2=Correct, 3=Modéré, 4=Mauvais, 5=Très mauvais. ⚠️ Ce n'est PAS l'échelle US AQI 0-500. |
| `co` | float | µg/m³ | Monoxyde de carbone |
| `no` | float | µg/m³ | Monoxyde d'azote |
| `no2` | float | µg/m³ | Dioxyde d'azote |
| `o3` | float | µg/m³ | Ozone |
| `so2` | float | µg/m³ | Dioxyde de soufre |
| `pm2_5` | float | µg/m³ | Particules fines < 2.5 µm |
| `pm10` | float | µg/m³ | Particules fines < 10 µm |
| `nh3` | float | µg/m³ | Ammoniac |

## Schéma du Data Warehouse (étoile)

- **`dim_city`** : `city_id` (PK), `city_name`, `country`, `latitude`, `longitude`
- **`dim_time`** : `time_id` (PK, format AAAAMMJJHH), `full_datetime`, `date`, `hour`, `day`, `month`, `year`, `day_of_week`, `day_of_week_num`, `is_weekend`, `week_of_year`
- **`fact_air_quality`** : `fact_id` (PK), `city_id` (FK), `time_id` (FK), `aqi`, `co`, `no`, `no2`, `o3`, `so2`, `pm2_5`, `pm10`, `nh3`

Détail complet des types : [`src/schema.sql`](src/schema.sql).

Cohérence attendue : `COUNT(fact_air_quality) ≈ 5 villes × nb d'heures couvertes`.
Écarts possibles : indisponibilité ponctuelle de l'API, limite de rate-limit du
plan gratuit, ou trous dans l'historique fourni par OpenWeatherMap avant sa date
de début de couverture (fin novembre 2020).

## Période couverte

À compléter par le groupe après le premier backfill + les runs automatiques
(ex: "backfill du 11/04/2026 au 11/07/2026, puis collecte horaire continue depuis
le 11/07/2026").

## Trous connus

À documenter au fil de l'eau si des runs échouent (voir onglet *Actions* du repo
pour l'historique des exécutions).

## Connexion au warehouse (pour IA1)

- Moteur : PostgreSQL (hébergé sur Supabase / Neon)
- `DATABASE_URL` : à demander à un membre du groupe (secret, non versionné)
- Exemple de requête :

```sql
SELECT c.city_name, t.date, AVG(f.aqi) AS aqi_moyen
FROM fact_air_quality f
JOIN dim_city c ON c.city_id = f.city_id
JOIN dim_time t ON t.time_id = f.time_id
GROUP BY c.city_name, t.date
ORDER BY t.date, c.city_name;
```

## Faire tourner le pipeline avec Airflow (Docker)

```bash
cp .env.docker.example .env    # renseigner OWM_API_KEY, DATABASE_URL, GIT_REPO_URL (token GitHub), etc.
docker compose up -d --build airflow-init   # une seule fois : init de la base Airflow + création de l'admin
docker compose up -d                         # démarre webserver + scheduler en arrière-plan
```

- UI Airflow : http://localhost:8080 (login `admin` / `admin`)
- DAG `aqi_backfill` : à déclencher manuellement une fois (bouton "Trigger DAG", paramètre `days`)
- DAG `aqi_hourly_pipeline` : tourne automatiquement toutes les heures dès que le scheduler est actif
- Arrêter : `docker compose down` (les données restent dans `data/` sur la machine hôte)

⚠️ La machine qui héberge Docker doit rester allumée, connectée, et sans mise
en veille pour que la collecte continue après le rendu (voir la section
"Risque machine locale" dans [`ARCHITECTURE.md`](ARCHITECTURE.md)).

## Reproduire le pipeline manuellement (sans orchestrateur, debug)

```bash
cp .env.example .env   # puis renseigner OWM_API_KEY et DATABASE_URL
pip install -r requirements.txt

cd src
python backfill.py --days 90      # backfill initial (3 mois minimum)
python collect.py                  # un appel de collecte horaire
python build_clean.py              # reconstruit clean/ depuis raw/
python validate_clean.py           # valide le contrat de données
python load_warehouse.py           # charge le warehouse PostgreSQL
```

## Secrets requis (GitHub Actions)

Dans *Settings → Secrets and variables → Actions* du repo :
- `OWM_API_KEY` : clé API OpenWeatherMap
- `DATABASE_URL` : chaîne de connexion PostgreSQL

La clé n'est jamais présente dans le code ni dans l'historique Git.
