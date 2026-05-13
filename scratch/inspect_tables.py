import sqlite3
import pandas as pd
from pathlib import Path

db_path = Path("database/bahda.db")
conn = sqlite3.connect(db_path)
print("--- Daily Summary Table ---")
try:
    df = pd.read_sql("SELECT * FROM daily_summary", conn)
    print(df)
except Exception as e:
    print(f"Error: {e}")

print("\n--- Clean Submissions (First 5) ---")
try:
    df = pd.read_sql("SELECT _id, enumerator_id, cluster_id, interview_date FROM clean_submissions LIMIT 5", conn)
    print(df)
except Exception as e:
    print(f"Error: {e}")
conn.close()
