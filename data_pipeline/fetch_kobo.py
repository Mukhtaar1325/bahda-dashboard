import pandas as pd
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import KOBO_BASE_URL

# Load secrets manually without python-dotenv
env_path = Path(__file__).resolve().parent.parent / "config" / "secrets.env"
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v

KOBO_API_TOKEN = os.environ.get("KOBO_API_TOKEN")
KOBO_ASSET_UID = os.environ.get("KOBO_ASSET_UID")
KOBO_CSV_URL = os.environ.get("KOBO_CSV_URL")

def fetch_submissions():
    """Fetches submissions from KoboToolbox API."""
    if KOBO_CSV_URL and "http" in KOBO_CSV_URL:
        print(f"Fetching from public CSV URL: {KOBO_CSV_URL}")
        try:
            # Kobo CSV exports typically use a semicolon separator
            df = pd.read_csv(KOBO_CSV_URL, sep=";")
            return df
        except Exception as e:
            print(f"Error fetching from CSV: {e}")
            return pd.DataFrame()
            
    # Original auth logic fallback
    if not KOBO_API_TOKEN or not KOBO_ASSET_UID or KOBO_API_TOKEN == 'your_kobotoolbox_api_token_here':
        print("Warning: Missing valid Kobo API credentials or CSV URL. Setup in config/secrets.env.")
        return pd.DataFrame()
        
    url = f"{KOBO_BASE_URL}/assets/{KOBO_ASSET_UID}/data/"
    headers = {"Authorization": f"Token {KOBO_API_TOKEN}"}
    import requests
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get('results', [])
        return pd.DataFrame(data)
    else:
        print(f"Error fetching data: {response.status_code}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = fetch_submissions()
    print(f"Fetched {len(df)} records.")
