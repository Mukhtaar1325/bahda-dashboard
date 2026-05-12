import pandas as pd
import os
from pathlib import Path

env_path = Path("config/secrets.env")
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip('"').strip("'")

url = os.environ.get("KOBO_CSV_URL")
print(f"Checking URL: {url}")
try:
    df = pd.read_csv(url, sep=";")
    print("Columns found:")
    print(df.columns.tolist())
    print("\nFirst row:")
    print(df.iloc[0].to_dict() if not df.empty else "Empty DataFrame")
except Exception as e:
    print(f"Error: {e}")
