"""
Backfill historique : récupère jusqu'à N jours d'historique AQI pour chaque ville
via l'API OpenWeatherMap Air Pollution History, découpée en tranches de 30 jours
(limite pratique pour rester sur des payloads raisonnables).

Rejouable : si un fichier de tranche existe déjà, il n'est pas re-téléchargé
(idempotence), ce qui permet de relancer le script après une coupure sans dupliquer
les appels API.

Usage :
    python src/backfill.py --days 90    # 3 mois (minimum demandé)
    python src/backfill.py --days 365   # 12 mois (idéal)
"""
import os
import json
import time
import argparse
import datetime
from pathlib import Path

import requests

from config import CITIES

API_KEY = os.environ.get("OWM_API_KEY")
HIST_URL = "https://api.openweathermap.org/data/2.5/air_pollution/history"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
CHUNK_DAYS = 30


def backfill(days: int = 90) -> None:
    if not API_KEY:
        raise RuntimeError("OWM_API_KEY absente de l'environnement.")

    end = datetime.datetime.now(datetime.timezone.utc)
    start_global = end - datetime.timedelta(days=days)

    for city in CITIES:
        city_dir = RAW_DIR / city["slug"] / "backfill"
        city_dir.mkdir(parents=True, exist_ok=True)

        chunk_start = start_global
        while chunk_start < end:
            chunk_end = min(chunk_start + datetime.timedelta(days=CHUNK_DAYS), end)
            start_ts, end_ts = int(chunk_start.timestamp()), int(chunk_end.timestamp())
            fname = city_dir / f"{city['slug']}_{start_ts}_{end_ts}.json"

            if fname.exists():
                print(f"[SKIP déjà présent] {fname.name}")
                chunk_start = chunk_end
                continue

            params = {
                "lat": city["lat"], "lon": city["lon"],
                "start": start_ts, "end": end_ts, "appid": API_KEY,
            }
            try:
                resp = requests.get(HIST_URL, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
            except requests.RequestException as e:
                print(f"[ERREUR] {city['name']} {chunk_start.date()}->{chunk_end.date()}: {e}")
                chunk_start = chunk_end
                time.sleep(1)
                continue

            payload = {
                "city": city["name"],
                "country": city["country"],
                "lat": city["lat"],
                "lon": city["lon"],
                "period_start_utc": chunk_start.isoformat(),
                "period_end_utc": chunk_end.isoformat(),
                "source": "openweathermap_air_pollution_history",
                "raw_response": data,
            }
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            print(f"[OK] {city['name']} {chunk_start.date()} -> {chunk_end.date()} "
                  f"({len(data.get('list', []))} points)")
            chunk_start = chunk_end
            time.sleep(1)  # ménager le rate-limit de l'API gratuite


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill historique AQI")
    parser.add_argument("--days", type=int, default=90,
                         help="Nombre de jours à backfiller (90=3 mois minimum, 365=12 mois idéal)")
    args = parser.parse_args()
    backfill(args.days)
    print("Backfill terminé.")
