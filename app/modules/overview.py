import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import plotly.graph_objects as go

# Add project root to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from database.db_utils import fetch_data

st.set_page_config(page_title="BAHDA Dashboard | Overview", page_icon="💎", layout="wide")

# Run the autorefresh about every 10 seconds
st_autorefresh(interval=10000, key="overview_refresh")

# Premium CSS for Glassmorphism and modern aesthetics
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main {
        background: #F8FAFC;
    }
    
    /* Metric Card Styling */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        flex: 1;
        text-align: left;
        border-bottom: 5px solid #3B82F6;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-val {
        font-size: 3rem;
        font-weight: 700;
        color: #1E293B;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }

    /* MOBILE OPTIMIZATION */
    @media (max-width: 768px) {
        .metric-container {
            flex-direction: column;
            gap: 1rem;
        }
        .metric-card {
            padding: 1.5rem;
            border-radius: 1rem;
        }
        .metric-val {
            font-size: 2rem;
        }
        .section-header {
            font-size: 1.4rem;
        }
        .chart-container {
            padding: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Custom Header
st.markdown("""
    <div class="custom-header-container" style="background: linear-gradient(90deg, #1E293B 0%, #3B82F6 100%); padding: 2rem; border-radius: 1.5rem; margin-bottom: 2rem; color: white;">
        <h1 class="header-title" style="margin: 0; font-weight: 800; font-size: 2.5rem; letter-spacing: -0.02em;">📈 BAHDA Live Insights</h1>
        <p class="header-subtitle" style="font-size: 1rem; opacity: 0.9; margin-top: 0.5rem;">Real-time monitoring of household assessment progress across Somaliland.</p>
    </div>
    <style>
        @media (max-width: 768px) {
            .custom-header-container { padding: 1.5rem !important; border-radius: 1rem !important; }
            .header-title { font-size: 1.8rem !important; }
            .header-subtitle { font-size: 0.9rem !important; }
        }
    </style>
""", unsafe_allow_html=True)

def load_and_render_dashboard():
    try:
        daily_df = fetch_data("SELECT * FROM daily_summary ORDER BY date DESC")
        cluster_df = fetch_data("SELECT * FROM cluster_summary")
        faculty_df = fetch_data("SELECT * FROM faculty_summary")
        enum_df = fetch_data("SELECT * FROM enumerator_summary")
        
        total_interviews = daily_df['total_submissions'].sum() if not daily_df.empty else 0
        total_clusters = len(cluster_df) if not cluster_df.empty else 0
        active_enums = len(enum_df) if not enum_df.empty else 0

        # Top Metric Cards
        cols = st.columns(3)
        with cols[0]:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{total_interviews}</div><div class="metric-label">Total Submissions</div></div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f'<div class="metric-card" style="border-color: #10B981;"><div class="metric-val">{total_clusters}</div><div class="metric-label">Mapped Clusters</div></div>', unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f'<div class="metric-card" style="border-color: #F59E0B;"><div class="metric-val">{active_enums}</div><div class="metric-label">Active Field Staff</div></div>', unsafe_allow_html=True)
            
        # Daily Trends
        st.markdown('<div class="section-header">📅 Collection Velocity (Daily)</div>', unsafe_allow_html=True)
        if not daily_df.empty:
            fig_daily = px.area(daily_df, x="date", y="total_submissions", 
                               color_discrete_sequence=['#3B82F6'],
                               markers=True, text="total_submissions")
            fig_daily.update_traces(textposition="top center")
            fig_daily.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=30, b=20),
                height=350,
                xaxis=dict(showgrid=False, title=""),
                yaxis=dict(showgrid=True, gridcolor='#F1F5F9', title="")
            )
            st.plotly_chart(fig_daily, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Waiting for data stream...")
            
        # Bottom Grid
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown('<div class="section-header">🏘️ Distribution by District</div>', unsafe_allow_html=True)
            if not cluster_df.empty:
                # Sort for better visualization
                cluster_df = cluster_df.sort_values("total_submissions", ascending=True)
                fig_cluster = px.bar(cluster_df, y="cluster_id", x="total_submissions", orientation='h',
                                   color="total_submissions", color_continuous_scale="Blues",
                                   text="total_submissions")
                fig_cluster.update_traces(textposition='outside')
                fig_cluster.update_layout(
                    showlegend=False, height=450,
                    margin=dict(l=10, r=40, t=10, b=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='white',
                    yaxis=dict(title="", showgrid=False),
                    xaxis=dict(title="Submissions", showgrid=True, gridcolor='#F1F5F9'),
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_cluster, use_container_width=True, config={'displayModeBar': False})
                
        with col_right:
            st.markdown('<div class="section-header">👥 Submissions by Faculty</div>', unsafe_allow_html=True)
            if not faculty_df.empty:
                fig_fac = px.pie(faculty_df, values="total_submissions", names="faculty_school",
                               hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_fac.update_traces(textinfo='percent+label', pull=[0.05]*len(faculty_df))
                fig_fac.update_layout(
                    height=450, margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor='white',
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_fac, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No Faculty distribution data yet.")
            
    except Exception as e:
        st.error(f"Dashboard Refresh Error: {e}")

load_and_render_dashboard()
