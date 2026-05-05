import streamlit as st
from pathlib import Path

# Define base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def show():
    # Premium CSS for landing page
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        .hero-section {
            background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
            padding: 4rem;
            border-radius: 2rem;
            color: white;
            text-align: left;
            margin-bottom: 2rem;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #FFFFFF 0%, #94A3B8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .hero-subtitle {
            font-size: 1.4rem;
            opacity: 0.8;
            margin-bottom: 0;
        }
        
        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 1.5rem;
            border-top: 5px solid #3B82F6;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            height: 100%;
            transition: transform 0.2s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .feature-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.5rem;
        }
        
        .feature-desc {
            color: #64748B;
            line-height: 1.5;
        }

        /* MOBILE OPTIMIZATION */
        @media (max-width: 768px) {
            .hero-section {
                padding: 2rem 1.5rem;
                border-radius: 1rem;
                text-align: center;
            }
            .hero-title {
                font-size: 2rem;
            }
            .hero-subtitle {
                font-size: 1rem;
            }
            .feature-card {
                padding: 1.5rem;
                margin-bottom: 1rem;
            }
            [data-testid="stMetric"] {
                padding: 0.5rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            # Look for logo in the assets folder (relative to project root)
            logo_path = BASE_DIR / "assets" / "logo.jpg"
            if logo_path.exists():
                st.image(str(logo_path), width=200)
            else:
                st.markdown("<h1 style='font-size: 100px; margin: 0;'>🏢</h1>", unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div class="hero-section">
                    <h1 class="hero-title">BAHDA Control Center</h1>
                    <p class="hero-subtitle">Next-Generation Data Intelligence for Institutional Surveying</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Navigation / Features Grid
    st.markdown("### 🛠️ Analytics Suite")
    
    # Define features and their required roles
    username = st.session_state.get("username", "guest")
    user_role = st.session_state.get("role", "viewer")

    features = [
        {"icon": "📈", "title": "Live Overview", "desc": "Monitor daily velocity, cluster performance, and faculty aggregation in real-time.", "color": "#3B82F6", "role": "viewer"},
        {"icon": "🌍", "title": "Geo View", "desc": "High-precision 3D mapping of all household locations with dynamic satellite tracking.", "color": "#10B981", "role": "admin"},
        {"icon": "🔍", "title": "Quality Control", "desc": "Automated validation engine detecting anomalies and potential errors instantly.", "color": "#F59E0B", "role": "admin"},
        {"icon": "🤖", "title": "AI Insights", "desc": "Deep pattern recognition and predictive modeling using advanced neural architectures.", "color": "#EC4899", "role": "admin"}
    ]
    
    cols = st.columns(len(features))
    
    for i, feature in enumerate(features):
        with cols[i]:
            if user_role == 'admin' or feature['role'] == 'viewer':
                st.markdown(f"""
                    <div class="feature-card" style="border-top-color: {feature['color']};">
                        <div class="feature-icon">{feature['icon']}</div>
                        <div class="feature-title">{feature['title']}</div>
                        <p class="feature-desc">{feature['desc']}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="feature-card" style="border-top-color: #CBD5E1; opacity: 0.6;">
                        <div class="feature-icon">🔒</div>
                        <div class="feature-title">{feature['title']}</div>
                        <p class="feature-desc">This module requires administrative privileges. Please contact the system owner.</p>
                    </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    show()
