import sqlite3
import pandas as pd
import sys
from pathlib import Path

# Fix path to permit importing config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.settings import DB_PATH

def get_connection():
    """Returns a SQLite connection to the standard database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema from schema.sql."""
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    with get_connection() as conn:
        with open(schema_path, "r") as f:
            conn.executescript(f.read())
    print(f"Database initialized at {DB_PATH}")

def execute_query(query: str, params: tuple = ()):
    """Executes a query that doesn't return data (INSERT, UPDATE)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid

def fetch_data(query: str, params: tuple = ()):
    """Fetches data and returns it as a pandas DataFrame."""
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

if __name__ == "__main__":
    init_db()
