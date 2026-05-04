import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = BASE_DIR / "app" / "modules"

st.set_page_config(
    page_title="BAHDA Survey Control Center",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Authentication logic
auth_config_path = BASE_DIR / "config" / "auth.yaml"
with open(auth_config_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Render the login widget
authenticator.login()

if st.session_state["authentication_status"]:
    username = st.session_state["username"]
    name = st.session_state["name"]
    user_role = config['credentials']['usernames'][username].get('role', 'viewer')
    st.session_state["role"] = user_role # Store for use in modules

    # Sidebar Logout & Info
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.write(f'Welcome *{name}*')
    
    if user_role != 'admin':
        st.sidebar.info("💡 Viewer Mode: Administrative modules are hidden.")

    # --- ADVANCED NAVIGATION CONTROL ---
    
    # Define module paths
    m_dir = Path(__file__).parent / "modules"
    
    # 1. Define all possible pages
    home_page = st.Page(str(m_dir / "home.py"), title="Home", icon="🏠", default=True)
    overview_page = st.Page(str(m_dir / "overview.py"), title="Live Overview", icon="📈")
    map_page = st.Page(str(m_dir / "map.py"), title="Geo View", icon="🌍")
    quality_page = st.Page(str(m_dir / "quality.py"), title="Quality Control", icon="🔍")
    ai_page = st.Page(str(m_dir / "ai_insights.py"), title="AI Insights", icon="🤖")

    # 2. Filter pages based on role
    if user_role == 'admin':
        pages = [home_page, overview_page, map_page, quality_page, ai_page]
    else:
        # IT Support / Viewers ONLY see Home and Overview
        pages = [home_page, overview_page]

    # 3. Initialize and run navigation
    pg = st.navigation(pages)
    pg.run()

    # Footer status (only on sidebar)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 System Status")
    st.sidebar.code(f"User: {username.upper()}\nRole: {user_role.upper()}\nPipeline: ACTIVE")

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
    st.info("New installation? Contact the BAHDA Administrator for credentials.")
