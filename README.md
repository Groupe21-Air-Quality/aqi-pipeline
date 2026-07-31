# Pipeline AQI — Data Warehouse qualité de l'air

## Présentation

Ce projet met en place un pipeline de données permettant de collecter, nettoyer,
stocker et analyser des mesures de qualité de l'air (AQI).

Les données sont récupérées depuis l'API **OpenWeatherMap Air Pollution**, pour
plusieurs villes dans le monde, avec une collecte horaire.

Le pipeline suit plusieurs étapes :

1. Collecte des données brutes depuis l'API ;
2. Stockage des données originales dans `data/raw/` ;
3. Nettoyage et transformation des données ;
4. Génération d'un fichier propre unique ;
5. Chargement dans un Data Warehouse PostgreSQL pour l'analyse.

Les détails concernant les choix d'architecture et les décisions techniques
sont disponibles dans :

[`ARCHITECTURE.md`](ARCHITECTURE.md)

---

# Stack technique

| Composant | Technologie |
|---|---|
| Source de données | OpenWeatherMap Air Pollution API |
| Langage | Python |
| Stockage brut | JSON (`data/raw`) |
| Données nettoyées | CSV (`data/clean`) |
| Data Warehouse | PostgreSQL |
| Hébergement BDD | Neon |
| Modélisation | Schéma en étoile |
| Automatisation | GitHub Actions |
| Alternative d'orchestration | Airflow / Docker |

---

# Villes suivies

Le pipeline collecte actuellement les données de qualité de l'air pour 5 villes :

| Ville | Pays | Latitude | Longitude |
|---|---|---|---|
| Paris | France | 48.8566 | 2.3522 |
| Antananarivo | Madagascar | -18.8792 | 47.5079 |
| New Delhi | India | 28.6139 | 77.2090 |
| Beijing | China | 39.9042 | 116.4074 |
| Los Angeles | USA | 34.0522 | -118.2437 |

Ces villes permettent d'obtenir des situations variées de qualité de l'air.

---

# Structure du projet

```text
.
├── src/
│   ├── collect.py              # collecte depuis OpenWeatherMap
│   ├── build_clean.py          # nettoyage et génération du CSV clean
│   ├── validate_clean.py       # validation des données
│   └── load_warehouse.py       # chargement PostgreSQL
│
├── data/
│   ├── raw/                    # données brutes API
│   └── clean/
│       └── air_quality_clean.csv
│
├── dags/                       # DAGs Airflow
│
├── .github/
│   └── workflows/              # workflows GitHub Actions
│
├── src/schema.sql              # création du Data Warehouse
├── ARCHITECTURE.md             # documentation architecture
└── README.md
```

---

# Données nettoyées

Le fichier principal utilisé pour l'analyse est :

```
data/clean/air_quality_clean.csv
```

Chaque ligne correspond à une mesure :

```
1 ville + 1 heure
```

Les données sont triées chronologiquement et dédoublonnées selon :

```
(city, timestamp_utc)
```

## Exemple d'une ligne

```text
city=Paris
country=France
latitude=48.8566
longitude=2.3522
timestamp_utc=2026-04-26T07:00:00Z
aqi=2
pm2_5=1.82
pm10=3.10
```

---

# Contrat de données

Le fichier clean contient les colonnes suivantes :

| Colonne | Type | Description |
|---|---|---|
| city | string | Nom de la ville |
| country | string | Pays |
| latitude | float | Latitude du point de mesure |
| longitude | float | Longitude du point de mesure |
| timestamp_utc | ISO 8601 | Horodatage UTC |
| aqi | integer | Indice AQI OpenWeatherMap |
| co | float | Monoxyde de carbone |
| no | float | Monoxyde d'azote |
| no2 | float | Dioxyde d'azote |
| o3 | float | Ozone |
| so2 | float | Dioxyde de soufre |
| pm2_5 | float | Particules fines PM2.5 |
| pm10 | float | Particules PM10 |
| nh3 | float | Ammoniac |

L'AQI utilisé correspond à l'échelle OpenWeatherMap :

| Valeur | Signification |
|---|---|
| 1 | Bon |
| 2 | Correct |
| 3 | Modéré |
| 4 | Mauvais |
| 5 | Très mauvais |

---

# Data Warehouse

Le projet utilise un modèle dimensionnel en étoile avec PostgreSQL.

Le schéma SQL complet est disponible dans :

```
src/schema.sql
```

Le Data Warehouse contient une table de faits et deux dimensions.

---

## dim_city

Table contenant les informations sur les villes.

| Colonne | Description |
|---|---|
| city_id | Identifiant unique |
| city_name | Nom de la ville |
| country | Pays |
| latitude | Latitude |
| longitude | Longitude |

---

## dim_time

Table contenant les informations temporelles.

| Colonne | Description |
|---|---|
| time_id | Identifiant temporel |
| full_datetime | Date et heure complète UTC |
| date | Date |
| hour | Heure |
| day | Jour |
| month | Mois |
| year | Année |
| day_of_week | Jour de la semaine |
| is_weekend | Indique si c'est un weekend |
| week_of_year | Numéro de semaine |

---

## fact_air_quality

Table contenant les mesures de pollution.

| Colonne | Description |
|---|---|
| fact_id | Identifiant de mesure |
| city_id | Référence vers dim_city |
| time_id | Référence vers dim_time |
| aqi | Indice AQI |
| co | Monoxyde de carbone |
| no | Monoxyde d'azote |
| no2 | Dioxyde d'azote |
| o3 | Ozone |
| so2 | Dioxyde de soufre |
| pm2_5 | Particules PM2.5 |
| pm10 | Particules PM10 |
| nh3 | Ammoniac |

---

# Données actuellement disponibles

Période couverte :

```
Backfill : 26/04/2026 au 31/07/2026
Collecte horaire continue depuis le 31/07/2026
```

Nombre actuel de lignes :

```
10 807 lignes
```

Fichier :

```
data/clean/air_quality_clean.csv
```

Répartition :

| Ville | Nombre de lignes |
|---|---:|
| Paris | 2176 |
| Los Angeles | 2176 |
| Antananarivo | 2175 |
| Beijing | 2151 |
| New Delhi | 2129 |

Les différences entre villes peuvent provenir d'indisponibilités ponctuelles de
l'API lors de certaines collectes.

Derniers jours disponibles :

| Date |
|---|
| 2026-07-27 |
| 2026-07-28 |
| 2026-07-29 |
| 2026-07-30 |
| 2026-07-31 |

---

# Connexion au Data Warehouse

Le Data Warehouse utilise :

- PostgreSQL
- Hébergement Neon

La connexion est définie avec :

```env
DATABASE_URL
```

Cette variable est secrète et ne doit pas être ajoutée au dépôt Git.

Exemple de requête :

```sql
SELECT 
    c.city_name,
    t.date,
    AVG(f.aqi) AS aqi_moyen
FROM fact_air_quality f
JOIN dim_city c 
    ON c.city_id = f.city_id
JOIN dim_time t 
    ON t.time_id = f.time_id
GROUP BY c.city_name, t.date
ORDER BY t.date, c.city_name;
```

---

# Variables d'environnement

Créer un fichier `.env` :

```env
OWM_API_KEY=votre_cle_openweathermap
DATABASE_URL=votre_url_postgresql
```

Variables utilisées :

| Variable | Description |
|---|---|
| OWM_API_KEY | Clé API OpenWeatherMap |
| DATABASE_URL | Connexion PostgreSQL Neon |

---

# Installation locale

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Créer le fichier d'environnement :

```bash
cp .env.example .env
```

---

# Exécution manuelle

Collecte :

```bash
python src/collect.py
```

Nettoyage :

```bash
python src/build_clean.py
```

Validation :

```bash
python src/validate_clean.py
```

Chargement du Data Warehouse :

```bash
python src/load_warehouse.py
```

---

# Automatisation

La collecte automatique est réalisée avec GitHub Actions.

Le workflow permet :

- la récupération régulière des données ;
- la reconstruction du fichier nettoyé ;
- la mise à jour des données du dépôt.

Une variante Airflow/Docker est également disponible :

```
dags/
docker-compose.yaml
```

Elle est documentée dans :

[`ARCHITECTURE.md`](ARCHITECTURE.md)

---

# Documentation complémentaire

Pour les informations concernant :

- l'architecture globale ;
- les choix techniques ;
- l'organisation du pipeline ;
- les décisions de conception ;

consulter :

[`ARCHITECTURE.md`](ARCHITECTURE.md)