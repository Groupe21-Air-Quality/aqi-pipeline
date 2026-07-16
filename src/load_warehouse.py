"""
Charge data/clean/air_quality_clean.csv dans le data warehouse PostgreSQL
(schéma en étoile : dim_city, dim_time, fact_air_quality).

Rejouable : le script est idempotent. À chaque exécution :
  1. crée les tables si elles n'existent pas (schema.sql)
  2. vide entièrement les 3 tables (TRUNCATE ... RESTART IDENTITY CASCADE)
  3. recharge tout depuis clean/ (source de vérité)
Cette approche "reconstruire à chaque run" évite toute dérive entre clean/ et
le warehouse.

Variable d'environnement requise : DATABASE_URL
  ex: postgresql://user:password@host:5432/dbname
"""
import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_FILE = BASE_DIR / "data" / "clean" / "air_quality_clean.csv"
SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"

DATABASE_URL = os.environ.get("DATABASE_URL")

DAYS_FR = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def build_time_dim(timestamps: pd.Series) -> pd.DataFrame:
    ts = pd.to_datetime(timestamps, utc=True).drop_duplicates().sort_values()
    df = pd.DataFrame({"full_datetime": ts})
    df["time_id"] = df["full_datetime"].dt.strftime("%Y%m%d%H").astype("int64")
    df["date"] = df["full_datetime"].dt.date
    df["hour"] = df["full_datetime"].dt.hour
    df["day"] = df["full_datetime"].dt.day
    df["month"] = df["full_datetime"].dt.month
    df["year"] = df["full_datetime"].dt.year
    df["day_of_week_num"] = df["full_datetime"].dt.dayofweek  # 0=lundi
    df["day_of_week"] = df["day_of_week_num"].apply(lambda i: DAYS_FR[i])
    df["is_weekend"] = df["day_of_week_num"].isin([5, 6])
    df["week_of_year"] = df["full_datetime"].dt.isocalendar().week.astype(int)
    return df


def main() -> None:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL absente de l'environnement.")
    if not CLEAN_FILE.exists():
        raise RuntimeError(f"{CLEAN_FILE} introuvable. Lancer build_clean.py d'abord.")

    df = pd.read_csv(CLEAN_FILE)
    if df.empty:
        raise RuntimeError("clean/air_quality_clean.csv est vide, rien à charger.")

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # 1. Création du schéma si besoin
            cur.execute(SCHEMA_FILE.read_text(encoding="utf-8"))

            # 2. Reset complet (warehouse reconstruit à chaque run, comme clean/)
            cur.execute("TRUNCATE TABLE fact_air_quality, dim_city, dim_time RESTART IDENTITY CASCADE;")

            # 3. dim_city
            cities = df[["city", "country", "latitude", "longitude"]].drop_duplicates()
            execute_values(
                cur,
                "INSERT INTO dim_city (city_name, country, latitude, longitude) VALUES %s "
                "ON CONFLICT (city_name, country) DO NOTHING",
                cities.values.tolist(),
            )
            cur.execute("SELECT city_id, city_name, country FROM dim_city;")
            city_map = {(name, country): cid for cid, name, country in cur.fetchall()}

            # 4. dim_time
            time_dim = build_time_dim(df["timestamp_utc"])
            time_rows = time_dim[[
                "time_id", "full_datetime", "date", "hour", "day", "month", "year",
                "day_of_week", "day_of_week_num", "is_weekend", "week_of_year",
            ]].values.tolist()
            execute_values(
                cur,
                "INSERT INTO dim_time (time_id, full_datetime, date, hour, day, month, year, "
                "day_of_week, day_of_week_num, is_weekend, week_of_year) VALUES %s "
                "ON CONFLICT (time_id) DO NOTHING",
                time_rows,
            )

            # 5. fact_air_quality
            df["_ts"] = pd.to_datetime(df["timestamp_utc"], utc=True)
            df["_time_id"] = df["_ts"].dt.strftime("%Y%m%d%H").astype("int64")
            df["_city_id"] = df.apply(lambda r: city_map[(r["city"], r["country"])], axis=1)

            fact_cols = ["_city_id", "_time_id", "aqi", "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3"]
            fact_rows = df[fact_cols].values.tolist()
            execute_values(
                cur,
                "INSERT INTO fact_air_quality (city_id, time_id, aqi, co, no, no2, o3, so2, pm2_5, pm10, nh3) "
                "VALUES %s ON CONFLICT (city_id, time_id) DO NOTHING",
                fact_rows,
            )

            cur.execute("SELECT COUNT(*) FROM fact_air_quality;")
            n_facts = cur.fetchone()[0]

        conn.commit()
        print(f"Warehouse rechargé : {len(cities)} villes, {len(time_dim)} horodatages, {n_facts} lignes de faits.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
