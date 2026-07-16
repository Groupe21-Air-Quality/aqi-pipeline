"""
Valide que data/clean/air_quality_clean.csv respecte le contrat de données :
- colonnes attendues présentes
- au moins 5 villes
- pas de doublon (city, timestamp_utc)
- tri chronologique par ville
- AQI dans l'intervalle attendu (échelle OpenWeatherMap : 1 à 5)
- pas de coordonnées manquantes

Sort avec un code de retour != 0 si une règle est violée (utilisable en CI).
"""
import sys
from pathlib import Path

import pandas as pd

CLEAN_FILE = Path(__file__).resolve().parent.parent / "data" / "clean" / "air_quality_clean.csv"

REQUIRED_COLUMNS = [
    "city", "country", "latitude", "longitude", "timestamp_utc",
    "aqi", "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3",
]


def validate() -> bool:
    errors = []

    if not CLEAN_FILE.exists():
        print(f"[ÉCHEC] Fichier introuvable : {CLEAN_FILE}")
        return False

    df = pd.read_csv(CLEAN_FILE)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"Colonnes manquantes : {missing_cols}")

    n_cities = df["city"].nunique() if "city" in df.columns else 0
    if n_cities < 5:
        errors.append(f"Moins de 5 villes présentes ({n_cities})")

    if {"city", "timestamp_utc"}.issubset(df.columns):
        dupes = df.duplicated(subset=["city", "timestamp_utc"]).sum()
        if dupes > 0:
            errors.append(f"{dupes} doublons (city, timestamp_utc) détectés")

        sorted_check = df.sort_values(["city", "timestamp_utc"]).reset_index(drop=True)
        if not df.reset_index(drop=True).equals(sorted_check):
            errors.append("Le fichier n'est pas trié chronologiquement par ville")

    if "aqi" in df.columns:
        bad_aqi = df[~df["aqi"].between(1, 5, inclusive="both") & df["aqi"].notna()]
        if len(bad_aqi) > 0:
            errors.append(f"{len(bad_aqi)} valeurs d'AQI hors de l'échelle OWM (1-5)")

    if {"latitude", "longitude"}.issubset(df.columns):
        missing_coords = df[df["latitude"].isna() | df["longitude"].isna()]
        if len(missing_coords) > 0:
            errors.append(f"{len(missing_coords)} lignes sans coordonnées")

    print(f"Lignes totales : {len(df)}")
    print(f"Villes         : {n_cities}")
    if "timestamp_utc" in df.columns and len(df) > 0:
        print(f"Période        : {df['timestamp_utc'].min()} -> {df['timestamp_utc'].max()}")

    if errors:
        print("\n[ÉCHEC] Validation KO :")
        for e in errors:
            print(f"  - {e}")
        return False

    print("\n[OK] Validation réussie : le fichier clean/ respecte le contrat de données.")
    return True


if __name__ == "__main__":
    ok = validate()
    sys.exit(0 if ok else 1)
