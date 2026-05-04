import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from database.db_utils import fetch_data

st.set_page_config(page_title="Quality Control", page_icon="🚨")

st.markdown("""
    <div style="background: linear-gradient(90deg, #1E293B 0%, #EF4444 100%); padding: 2rem; border-radius: 1.5rem; margin-bottom: 2rem; color: white;">
        <h2 style="margin: 0; font-weight: 700;">🚨 Data Quality Audit</h2>
        <p style="opacity: 0.9; margin: 0;">Identifying anomalies, missing GPS coordinates, and potential data entry errors.</p>
    </div>
""", unsafe_allow_html=True)

try:
    # 1. Overview Metrics for Quality
    col1, col2, col3 = st.columns(3)
    
    flags_df = fetch_data("SELECT * FROM quality_flags")
    
    with col1:
        missing_gps = len(flags_df[flags_df['flag_type'] == 'Missing GPS'])
        st.metric("Missing GPS", missing_gps, delta=None, delta_color="inverse")
    
    with col2:
        out_of_bounds = len(flags_df[flags_df['flag_type'] == 'Out of Bounds GPS'])
        st.metric("Out of Bounds", out_of_bounds, delta=None, delta_color="inverse")
        
    with col3:
        mismatch = len(flags_df[flags_df['flag_type'] == 'Location Mismatch'])
        st.metric("Cluster Mismatch", mismatch, delta=None, delta_color="inverse")

    st.markdown("---")

    if not flags_df.empty:
        st.subheader("🚩 Flagged Submissions")
        st.write("The following records have been identified as having potential data quality issues:")
        
        # Merge with clean_submissions to get more info like enumerator_id and cluster_id
        details_df = fetch_data("""
            SELECT q.submission_id, q.flag_type, q.description, c.enumerator_id, c.cluster_id, c.interview_date
            FROM quality_flags q
            LEFT JOIN clean_submissions c ON q.submission_id = c._id
        """)
        
        st.dataframe(details_df, use_container_width=True)
        
        st.info("💡 Action Required: Please contact the enumerators listed above to verify the location of these assessments.")
    else:
        st.success("✅ No critical data quality issues found in current submissions.")

except Exception as e:
    st.error(f"Error loading quality data: {e}")
