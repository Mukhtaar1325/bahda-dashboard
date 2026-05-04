import sqlite3
import os

db_path = r'c:\Users\rhaag\.gemini\antigravity\scratch\bahda_dashboard\database\bahda.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT cluster_id FROM clean_submissions")
    rows = cursor.fetchall()
    print("Distinct cluster_ids:")
    for row in rows:
        print(row[0])
    
    cursor.execute("SELECT COUNT(*) FROM clean_submissions WHERE gps_lat IS NULL OR ABS(gps_lat) < 0.1")
    count = cursor.fetchone()[0]
    print(f"\nSubmissions with missing/invalid GPS: {count}")
    
    conn.close()
else:
    print(f"DB not found at {db_path}")
