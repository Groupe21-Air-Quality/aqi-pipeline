import json
import datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"
CLEAN_FILE = CLEAN_DIR / "air_quality_clean.csv"

COLUMNS = [
    "city", "country", "latitude", "longitude", "timestamp_utc",
    "aqi", "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3",
]


def extract_rows(payload: dict) -> list[dict]:
    rows = []
    city = payload["city"]
    country = payload["country"]
    lat = payload["lat"]
    lon = payload["lon"]

    for entry in payload.get("raw_response", {}).get("list", []):
        ts = datetime.datetime.fromtimestamp(entry["dt"], tz=datetime.timezone.utc)
        comp = entry.get("components", {})
        rows.append({
            "city": city,
            "country": country,
            "latitude": lat,
            "longitude": lon,
            "timestamp_utc": ts.isoformat(),
            "aqi": entry.get("main", {}).get("aqi"),
            "co": comp.get("co"),
            "no": comp.get("no"),
            "no2": comp.get("no2"),
            "o3": comp.get("o3"),
            "so2": comp.get("so2"),
            "pm2_5": comp.get("pm2_5"),
            "pm10": comp.get("pm10"),
            "nh3": comp.get("nh3"),
        })
    return rows


def build_clean() -> pd.DataFrame:
    all_rows = []
    json_files = list(RAW_DIR.rglob("*.json"))

    if not json_files:
        raise RuntimeError(f"Aucun fichier JSON trouvé dans {RAW_DIR}. Lancer collect.py / backfill.py d'abord.")

    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                payload = json.load(f)
            all_rows.extend(extract_rows(payload))
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[AVERTISSEMENT] fichier ignoré (corrompu ou format inattendu) {jf}: {e}")

    df = pd.DataFrame(all_rows, columns=COLUMNS)

    
    df = df.drop_duplicates(subset=["city", "timestamp_utc"], keep="last")

    df = df.sort_values(["city", "timestamp_utc"]).reset_index(drop=True)

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_FILE, index=False, encoding="utf-8")

    return df


if __name__ == "__main__":
    df = build_clean()
    print(f"clean/ reconstruit : {len(df)} lignes -> {CLEAN_FILE}")
    print(df.groupby("city")["timestamp_utc"].agg(["min", "max", "count"]))
