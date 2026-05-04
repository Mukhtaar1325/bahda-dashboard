import sys
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
    generate_quality_flags
)
from data_pipeline.load_db import load_data

def run():
    print("--- Starting Pipeline ---")
    print("1. Fetching Data...")
    raw_df = fetch_submissions()
    
    if raw_df.empty:
        print("No new data fetched. Either none exist or API not configured. Exiting.")
        return
        
    print("2. Cleaning Data...")
    prepared_raw_df = prepare_raw_for_db(raw_df)
    clean_df = clean_submissions(raw_df)
    
    print("3. Transforming Data...")
    indicators_df = calculate_indicators(clean_df)
    daily_df = generate_daily_summary(clean_df)
    cluster_df = generate_cluster_summary(clean_df)
    enum_df = generate_enumerator_summary(clean_df)
    faculty_df = generate_faculty_summary(clean_df)
    quality_df = generate_quality_flags(clean_df)
    
    print("4. Loading to DB...")
    load_data(prepared_raw_df, clean_df, indicators_df, daily_df, cluster_df, enum_df, faculty_df, quality_df)
    print("--- Pipeline Finished ---")

if __name__ == '__main__':
    run()
