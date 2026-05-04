import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "database" / "bahda.db"

# KoboToolbox API Config
KOBO_BASE_URL = "https://kf.kobotoolbox.org/api/v2"

# Database path string for SQLAlchemy or sqlite3
DB_URI = f"sqlite:///{DB_PATH}"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BASE_DIR / "database", exist_ok=True)
