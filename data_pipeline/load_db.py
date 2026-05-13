import sys
import sqlite3
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from database.db_utils import get_connection

def insert_dataframe(df, table_name):
    """Inserts data by filtering out records that already exist in the database."""
    if df.empty:
        return
        
    with get_connection() as conn:
        try:
            # Get existing IDs to avoid duplicates
            if '_id' in df.columns:
                existing_ids = pd.read_sql(f"SELECT _id FROM {table_name}", conn)['_id'].tolist()
                df_to_insert = df[~df['_id'].astype(str).isin([str(x) for x in existing_ids])]
            else:
                df_to_insert = df
                
            if not df_to_insert.empty:
                df_to_insert.to_sql(table_name, conn, if_exists='append', index=False)
                print(f"Inserted {len(df_to_insert)} new records into {table_name}.")
            else:
                print(f"No new records for {table_name}.")
        except Exception as e:
            print(f"Db Error in {table_name}: {e}")

def load_data(raw_df, clean_df, indicators_df, daily_df, cluster_df, enum_df, faculty_df, quality_df, supervisor_df=None):
    print("Loading data into Database...")
    insert_dataframe(raw_df, 'raw_submissions')
    insert_dataframe(clean_df, 'clean_submissions')
    insert_dataframe(indicators_df, 'indicators_household')
    
    # Summaries and flags are safe to replace fully for a simple ETL
    with get_connection() as conn:
        if not daily_df.empty:
            daily_df.to_sql('daily_summary', conn, if_exists='replace', index=False)
        if not cluster_df.empty:
            cluster_df.to_sql('cluster_summary', conn, if_exists='replace', index=False)
        if not enum_df.empty:
            enum_df.to_sql('enumerator_summary', conn, if_exists='replace', index=False)
        if not faculty_df.empty:
            faculty_df.to_sql('faculty_summary', conn, if_exists='replace', index=False)
        if not quality_df.empty:
            quality_df.to_sql('quality_flags', conn, if_exists='replace', index=False)
        if supervisor_df is not None and not supervisor_df.empty:
            supervisor_df.to_sql('supervisor_summary', conn, if_exists='replace', index=False)
            
    print("Loading complete.")
