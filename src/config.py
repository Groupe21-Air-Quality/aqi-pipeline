"""
Configuration centrale du pipeline : liste des villes suivies.
Ajouter/retirer une ville ici suffit à propager le changement à tout le pipeline
(collecte, backfill, clean, warehouse).
"""

CITIES = [
    {"name": "Paris",        "country": "France",    "lat": 48.8566,  "lon": 2.3522,   "slug": "paris"},
    {"name": "Antananarivo", "country": "Madagascar", "lat": -18.8792, "lon": 47.5079, "slug": "antananarivo"},
    {"name": "New Delhi",    "country": "India",     "lat": 28.6139,  "lon": 77.2090,  "slug": "new_delhi"},
    {"name": "Beijing",      "country": "China",      "lat": 39.9042, "lon": 116.4074, "slug": "beijing"},
    {"name": "Los Angeles",  "country": "USA",        "lat": 34.0522, "lon": -118.2437, "slug": "los_angeles"},
]
