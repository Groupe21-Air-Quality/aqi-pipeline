# Pipeline AQI — Data Warehouse qualité de l'air

## Présentation

Ce projet met en place un pipeline de collecte, transformation et stockage de données de qualité de l'air (AQI).

Le pipeline récupère des mesures horaires depuis l'API OpenWeatherMap pour 5 villes, stocke les données brutes, génère un fichier nettoyé, puis charge les données dans un Data Warehouse PostgreSQL pour l'analyse.

Les choix d'architecture, les composants techniques et les justifications sont disponibles dans :

[`ARCHITECTURE.md`](ARCHITECTURE.md)

---

# Stack technique

| Composant | Technologie |
|---|---|
| API | OpenWeatherMap Air Pollution API |
| Langage | Python |
| Stockage données | CSV (raw / clean) |
| Data Warehouse | PostgreSQL |
| Hébergement BDD | Neon |
| Modélisation | Schéma en étoile |
| Automatisation | GitHub Actions |
| Alternative | Airflow / Docker |

---

# Villes suivies

Le pipeline collecte actuellement les données pour 5 villes :

| Ville | Pays | Latitude | Longitude |
|---|---|---|---|
| Paris | France | 48.8566 | 2.3522 |
| Antananarivo | Madagascar | -18.8792 | 47.5079 |
| New Delhi | India | 28.6139 | 77.2090 |
| Beijing | China | 39.9042 | 116.4074 |
| Los Angeles | USA | 34.0522 | -118.2437 |

---

# Structure du projet

```text
.
├── src/
│   ├── collect.py              # récupération des données AQI
│   ├── build_clean.py          # nettoyage des données
│   ├── validate_clean.py       # validation du fichier clean
│   └── load_warehouse.py       # chargement PostgreSQL
│
├── data/
│   ├── raw/                    # données brutes API
│   └── clean/
│       └── air_quality_clean.csv
│
├── dags/                       # DAGs Airflow
├── .github/
│   └── workflows/              # automatisations
│
├── src/schema.sql              # schéma Data Warehouse
├── ARCHITECTURE.md             # documentation technique
└── README.md