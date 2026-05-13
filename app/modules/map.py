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
                supervisor_id,
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
        
        # 1. Zone/District Filter (A, B, C, D) based on naming convention
        zone_options = ["All Zones", "A - Sh. Osman", "B - Sh. Ali Jauhar", "C - Sh. Ahmed Salan", "D - Sh. Makahil"]
        selected_zone_label = st.sidebar.selectbox("Select Zone (District)", zone_options)
        selected_zone_prefix = selected_zone_label[0] if selected_zone_label != "All Zones" else None

        # 2. Cluster Filter
        all_clusters = sorted(df['cluster_id'].unique().tolist())
        selected_cluster = st.sidebar.selectbox(
            "Select Specific Cluster",
            ["All Clusters"] + all_clusters
        )
        
        # Apply filters to plot_df
        plot_df = df.copy()
        
        # coordinate validation
        plot_df = plot_df[
            (plot_df['lat'].abs() > 0.1) & 
            (plot_df['lat'] > 8.0) & (plot_df['lat'] < 12.0) &
            (plot_df['lon'] > 42.0) & (plot_df['lon'] < 49.0)
        ]
        
        if selected_zone_prefix:
            # Note: We use the cluster_id mapping or subzone_letter column if available.
            # For simplicity, if we are filtering the MAP, we want to see records in that Zone.
            # In clean_submissions, we have subzone_letter.
            plot_df = plot_df[plot_df['cluster_id'].str.contains(selected_zone_label.split(' - ')[1], case=False, na=False)]

        if selected_cluster != "All Clusters":
            plot_df = plot_df[plot_df['cluster_id'] == selected_cluster]
        
        if not plot_df.empty:
            # Create the map centered on the filtered location
            avg_lat = plot_df['lat'].mean()
            avg_lon = plot_df['lon'].mean()
            
            # Zoom level
            zoom = 16 if selected_cluster != "All Clusters" else (15 if selected_zone_prefix else 14)
            
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

            # --- ADD KML SUB-ZONE BOUNDARIES ---
            try:
                import json
                zones_path = Path(__file__).resolve().parent.parent.parent / "database" / "sub_zones.json"
                if zones_path.exists():
                    with open(zones_path, 'r') as f:
                        zones = json.load(f)
                    
                    # Create a feature group for boundaries
                    fg_zones = folium.FeatureGroup(name="Sub-Zone Boundaries")
                    for zone in zones:
                        # Filter zones by prefix if selected
                        if selected_zone_prefix and not zone['name'].startswith(selected_zone_prefix):
                            continue
                            
                        folium.Polygon(
                            locations=zone['coordinates'],
                            color="#10B981",
                            weight=2,
                            fill=True,
                            fill_color="#10B981",
                            fill_opacity=0.1,
                            tooltip=f"Sub-Zone: {zone['name']}"
                        ).add_to(fg_zones)
                    fg_zones.add_to(m)
            except Exception as kml_err:
                st.sidebar.error(f"KML Overlay Error: {kml_err}")

            # Add markers
            for _, row in plot_df.iterrows():
                # Fallback for None values
                e_id = str(row['enumerator_id']) if row['enumerator_id'] else "Missing"
                s_id = str(row['supervisor_id']) if row['supervisor_id'] else "Missing"
                
                # Better tooltip for hover
                hover_text = f"Sup: {s_id} | Enum: {e_id}"
                
                popup_html = f"""
                    <div style="font-family: 'Outfit', sans-serif; min-width: 200px; padding: 5px;">
                        <h4 style="margin:0; color:#3B82F6;">ID: {e_id}</h4>
                        <hr style="margin: 8px 0; border: 0.5px solid #E2E8F0;">
                        <table style="width: 100%; font-size: 13px;">
                            <tr><td><b>Supervisor:</b></td><td><span style="color:#10B981; font-weight:bold;">{s_id}</span></td></tr>
                            <tr><td><b>Cluster:</b></td><td>{row['cluster_id']}</td></tr>
                            <tr><td><b>Faculty:</b></td><td>{row['faculty_school']}</td></tr>
                            <tr><td><b>Date:</b></td><td>{row['interview_date']}</td></tr>
                        </table>
                    </div>
                """
                
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=8,
                    color="#3B82F6",
                    fill=True,
                    fill_color="#3B82F6",
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_html, max_width=350),
                    tooltip=hover_text
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
