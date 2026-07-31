import os
import json
import datetime
from pathlib import Path

import requests

from config import CITIES

API_KEY = os.environ.get("OWM_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def collect_current() -> int:
    if not API_KEY:
        raise RuntimeError(
            "OWM_API_KEY absente de l'environnement. "
            "Ne JAMAIS mettre la clé en dur dans le code : utiliser les secrets GitHub."
        )

    run_ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    n_ok = 0

    for city in CITIES:
        params = {"lat": city["lat"], "lon": city["lon"], "appid": API_KEY}
        try:
            resp = requests.get(BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            print(f"[ERREUR] {city['name']}: {e}")
            continue

        payload = {
            "city": city["name"],
            "country": city["country"],
            "lat": city["lat"],
            "lon": city["lon"],
            "collected_at_utc": run_ts,
            "source": "openweathermap_air_pollution_current",
            "raw_response": data,
        }

        city_dir = RAW_DIR / city["slug"]
        city_dir.mkdir(parents=True, exist_ok=True)
        out_path = city_dir / f"{city['slug']}_{run_ts}.json"

        
        if out_path.exists():
            print(f"[SKIP] {out_path} existe déjà")
            continue

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        print(f"[OK] {city['name']} -> {out_path}")
        n_ok += 1

    return n_ok


if __name__ == "__main__":
    n = collect_current()
    print(f"Collecte terminée : {n} fichiers écrits.")
