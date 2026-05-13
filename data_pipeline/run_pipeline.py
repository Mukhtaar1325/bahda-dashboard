import sys
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from data_pipeline.fetch_kobo import fetch_submissions
from data_pipeline.clean_data import clean_submissions, prepare_raw_for_db
from data_pipeline.transform_data import (
    calculate_indicators, 
    generate_daily_summary, 
    generate_cluster_summary, 
    generate_enumerator_summary,
    generate_faculty_summary,
    generate_quality_flags,
    generate_supervisor_summary
)
from data_pipeline.load_db import load_data

def run():
    print("--- Starting Pipeline ---")
    print("1. Fetching Data...")
    raw_df = fetch_submissions()
    
    if raw_df.empty:
        print("No new data fetched. Refreshing summaries from existing database records...")
        clean_df = pd.DataFrame()
        prepared_raw_df = pd.DataFrame()
    else:
        print("2. Cleaning Data...")
        prepared_raw_df = prepare_raw_for_db(raw_df)
        clean_df = clean_submissions(raw_df)
    
    print("3. Fetching existing clean data...")
    from database.db_utils import fetch_data
    existing_clean_df = fetch_data("SELECT * FROM clean_submissions")
    
    # Combine existing and new for summaries, avoiding duplicates
    if not existing_clean_df.empty:
        # Filter clean_df to only include records not already in DB
        new_records = clean_df[~clean_df['_id'].astype(str).isin(existing_clean_df['_id'].astype(str))]
        full_clean_df = pd.concat([existing_clean_df, new_records], ignore_index=True)
    else:
        full_clean_df = clean_df
    
    # Ensure date column is datetime for grouping
    if 'interview_date' in full_clean_df.columns:
        full_clean_df['interview_date'] = pd.to_datetime(full_clean_df['interview_date'], errors='coerce').dt.date

    print("4. Transforming Data (Global Summaries)...")
    indicators_df = calculate_indicators(clean_df) # Still calculate indicators for new batch
    daily_df = generate_daily_summary(full_clean_df)
    cluster_df = generate_cluster_summary(full_clean_df)
    enum_df = generate_enumerator_summary(full_clean_df)
    faculty_df = generate_faculty_summary(full_clean_df)
    quality_df = generate_quality_flags(full_clean_df)
    supervisor_df = generate_supervisor_summary(full_clean_df)
    
    print("5. Loading to DB...")
    load_data(prepared_raw_df, clean_df, indicators_df, daily_df, cluster_df, enum_df, faculty_df, quality_df, supervisor_df)
    print("--- Pipeline Finished ---")

if __name__ == '__main__':
    run()
