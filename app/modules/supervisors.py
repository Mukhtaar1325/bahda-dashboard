import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# Add project root to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from database.db_utils import fetch_data

st.set_page_config(page_title="BAHDA Dashboard | Supervisor Tracking", page_icon="🕵️", layout="wide")

# Autorefresh every 10 seconds
st_autorefresh(interval=10000, key="supervisor_refresh")

# Premium CSS for consistency
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
        margin: 2rem 0 1rem 0;
    }
    
    .status-pill {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .status-match { background: #DCFCE7; color: #166534; }
    .status-mismatch { background: #FEE2E2; color: #991B1B; }
    .status-missing { background: #F3F4F6; color: #374151; }
    </style>
""", unsafe_allow_html=True)

# Custom Header
st.markdown("""
    <div style="background: linear-gradient(90deg, #334155 0%, #475569 100%); padding: 2rem; border-radius: 1.5rem; margin-bottom: 2rem; color: white;">
        <h1 style="margin: 0; font-weight: 800; font-size: 2.5rem;">🕵️ Supervisor Tracking</h1>
        <p style="font-size: 1rem; opacity: 0.9; margin-top: 0.5rem;">Monitor field team performance, zone mapping, and ID consistency.</p>
    </div>
""", unsafe_allow_html=True)

def render_supervisor_tracking():
    try:
        # 1. Performance Summary Table
        st.markdown('<div class="section-header">📊 Detailed Supervisor Audit</div>', unsafe_allow_html=True)
        st.info("💡 Each row represents a unique combination of Supervisor, Cluster, and Faculty. Use this to spot incorrect entries.")
        
        # Fetch summary data
        summary_df = fetch_data("SELECT * FROM supervisor_summary ORDER BY total_submissions DESC")
        
        if not summary_df.empty:
            # Rename columns for display
            display_df = summary_df.rename(columns={
                "supervisor_id": "Supervisor ID",
                "total_submissions": "Submissions",
                "subzone_code": "Subzone",
                "faculty_school": "Faculty",
                "cluster_id": "Cluster"
            })
            
            # Reorder
            display_df = display_df[["Supervisor ID", "Subzone", "Cluster", "Faculty", "Submissions"]]
            
            # Premium Table with Column Config
            st.dataframe(
                display_df,
                column_config={
                    "Submissions": st.column_config.ProgressColumn(
                        "Submissions",
                        help="Total records submitted for this combination",
                        format="%d",
                        min_value=0,
                        max_value=int(display_df["Submissions"].max())
                    ),
                    "Supervisor ID": st.column_config.TextColumn(
                        "Supervisor ID",
                        help="7-digit Supervisor identifier"
                    ),
                    "Subzone": st.column_config.TextColumn(
                        "Subzone",
                        width="small"
                    )
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No supervisor data available yet.")

        # 2. Detailed Validation Table with Highlighting
        st.markdown('<div class="section-header">🚩 Alignment Validation</div>', unsafe_allow_html=True)
        
        detail_df = fetch_data("""
            SELECT 
                supervisor_id, subzone_letter || zone_num || '.' || subzone_num as subzone,
                cluster_id, faculty_school, cluster_match_flag
            FROM clean_submissions
            WHERE supervisor_id != 'MISSING'
            ORDER BY _id DESC
            LIMIT 50
        """)
        
        if not detail_df.empty:
            # Create a status string
            detail_df['Status'] = detail_df['cluster_match_flag'].apply(lambda x: "✅ Correct Zone" if x else "⚠️ Cluster Mismatch")
            
            # Show table with color coding
            st.dataframe(
                detail_df[["supervisor_id", "subzone", "cluster_id", "faculty_school", "Status"]],
                column_config={
                    "Status": st.column_config.TextColumn(
                        "Status",
                        help="Checks if the selected cluster matches the supervisor's assigned zone (A, B, C, D)"
                    )
                },
                use_container_width=True,
                hide_index=True
            )
            st.caption("Note: Mismatches occur when a supervisor from one zone (e.g., A) is recorded in a different cluster (e.g., Sh. Makahil).")

        # 3. Missing IDs Summary
        st.markdown('<div class="section-header">⚠️ Missing Supervisor IDs</div>', unsafe_allow_html=True)
        
        missing_df = fetch_data("""
            SELECT cluster_id as Cluster, faculty_school as Faculty, COUNT(*) as "Missing Count"
            FROM clean_submissions
            WHERE supervisor_id = 'MISSING'
            GROUP BY cluster_id, faculty_school
            ORDER BY "Missing Count" DESC
        """)
        
        if not missing_df.empty:
            st.metric("Total Records Missing Supervisor ID", missing_df['Missing Count'].sum(), delta="- Follow up required", delta_color="inverse")
            st.table(missing_df)
        else:
            st.success("All submissions have valid Supervisor IDs!")

    except Exception as e:
        st.error(f"Error loading supervisor tracking: {e}")

render_supervisor_tracking()
