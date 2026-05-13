import sqlite3
import os
from pathlib import Path

db_path = Path("database/bahda.db")
if not db_path.exists():
    print(f"Database {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT count(*) FROM clean_submissions")
        count = cursor.fetchone()[0]
        print(f"Total clean submissions: {count}")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()
