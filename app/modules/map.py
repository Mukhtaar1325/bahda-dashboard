import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
import folium
from streamlit_folium import st_folium

# Add project root to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from database.db_utils import fetch_data

st.set_page_config(page_title="BAHDA Dashboard | Map", page_icon="🌍", layout="wide")

# Run the autorefresh about every 10 seconds
st_autorefresh(interval=10000, key="map_refresh")

# Premium Header
st.markdown("""
    <div style="background: linear-gradient(90deg, #1E293B 0%, #10B981 100%); padding: 2rem; border-radius: 1.5rem; margin-bottom: 2rem; color: white;">
        <h2 style="margin: 0; font-weight: 700;">🌍 Live Geospatial Intelligence</h2>
        <p style="opacity: 0.9; margin: 0;">Pinpointing every household assessment with high-precision Google Satellite imagery.</p>
    </div>
""", unsafe_allow_html=True)

def render_map():
    try:
        # Fetch data
        df = fetch_data("""
            SELECT 
                gps_lat as lat, 
                gps_lon as lon,
                enumerator_id,
                cluster_id,
                interview_date,
                water_source,
                faculty_school
            FROM clean_submissions 
            WHERE gps_lat IS NOT NULL 
        """)
        
        if df.empty:
            st.warning("📡 No submissions found in the database.")
            return

        # Filtering logic in sidebar
        st.sidebar.markdown("### 🔍 Map Controls")
        
        # Determine unique clusters and identify Borama ones
        all_clusters = sorted(df['cluster_id'].unique().tolist())
        
        # User wants "Focus on Borama"
        # Since we know Borama clusters are the main ones here, we can offer a quick filter
        focus_borama = st.sidebar.checkbox("Focus on Borama City", value=True)
        
        selected_cluster = st.sidebar.selectbox(
            "Select Specific Cluster",
            ["All Clusters"] + all_clusters
        )
        
        # Apply filters
        plot_df = df.copy()
        
        # If "Focus on Borama" is checked, we filter out coordinates near (0,0) and outside Somaliland
        # to ensure the map isn't zoomed out to the whole world
        plot_df = plot_df[
            (plot_df['lat'].abs() > 0.1) & 
            (plot_df['lat'] > 8.0) & (plot_df['lat'] < 12.0) &
            (plot_df['lon'] > 42.0) & (plot_df['lon'] < 49.0)
        ]
        
        if selected_cluster != "All Clusters":
            plot_df = plot_df[plot_df['cluster_id'] == selected_cluster]
        
        if not plot_df.empty:
            # Create the map centered on the filtered location
            avg_lat = plot_df['lat'].mean()
            avg_lon = plot_df['lon'].mean()
            
            # Zoom level: tighter if specific cluster selected
            zoom = 16 if selected_cluster != "All Clusters" else 14
            
            m = folium.Map(
                location=[avg_lat, avg_lon],
                zoom_start=zoom,
                control_scale=True,
                tiles=None
            )
            
            # Add Google Maps Tiles
            google_hybrid = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
            google_satellite = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
            google_roadmap = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
            
            folium.TileLayer(tiles=google_hybrid, attr="Google", name="Google Hybrid", overlay=False).add_to(m)
            folium.TileLayer(tiles=google_satellite, attr="Google", name="Google Satellite", overlay=False).add_to(m)
            folium.TileLayer(tiles=google_roadmap, attr="Google", name="Google Roadmap", overlay=False).add_to(m)

            # Add markers
            for _, row in plot_df.iterrows():
                popup_html = f"""
                    <div style="font-family: sans-serif; min-width: 180px;">
                        <h4 style="margin:0; color:#10B981;">{row['cluster_id']}</h4>
                        <hr style="margin: 5px 0; border: 0.5px solid #eee;">
                        <b>Enumerator:</b> {row['enumerator_id']}<br>
                        <b>Date:</b> {row['interview_date']}<br>
                        <b>Water:</b> {row['water_source']}<br>
                        <b>Faculty:</b> {row['faculty_school']}
                    </div>
                """
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=8,
                    color="#3B82F6",
                    fill=True,
                    fill_color="#3B82F6",
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"ID: {row['enumerator_id']}"
                ).add_to(m)
            
            folium.LayerControl().add_to(m)
            st_folium(m, width="100%", height=700, use_container_width=True)
            
            st.success(f"📍 Visualizing {len(plot_df)} points in {selected_cluster if selected_cluster != 'All Clusters' else 'Borama'}.")
            
            if len(df) > len(plot_df):
                st.warning(f"⚠️ {len(df) - len(plot_df)} records were hidden due to invalid GPS coordinates. Check Quality Control for details.")
        else:
            st.error("No valid GPS data to display for the current selection.")
    except Exception as e:
        st.error(f"Mapping Engine Error: {e}")
        st.code(str(e))

render_map()
