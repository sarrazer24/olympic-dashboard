import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Import styling module
from styles import get_theme_css

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Paris 2024 Olympic Games Dashboard",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== DATA LOADING ====================
@st.cache_data(show_spinner=False)
def load_data():
    """Load all CSV files from the data directory"""
    data_dir = Path(__file__).parent / "data"
    
    data = {}
    
    try:
        # Load main datasets
        data['athletes'] = pd.read_csv(data_dir / 'athletes.csv')
        data['coaches'] = pd.read_csv(data_dir / 'coaches.csv')
        data['events'] = pd.read_csv(data_dir / 'events.csv')
        data['medals'] = pd.read_csv(data_dir / 'medals.csv')
        data['medals_total'] = pd.read_csv(data_dir / 'medals_total.csv')
        data['medallists'] = pd.read_csv(data_dir / 'medallists.csv')
        data['nocs'] = pd.read_csv(data_dir / 'nocs.csv')
        data['schedules'] = pd.read_csv(data_dir / 'schedules.csv')
        data['teams'] = pd.read_csv(data_dir / 'teams.csv')
        data['technical_officials'] = pd.read_csv(data_dir / 'technical_officials.csv')
        data['venues'] = pd.read_csv(data_dir / 'venues.csv')
        data['torch_route'] = pd.read_csv(data_dir / 'torch_route.csv')
        
        # Create continent mapping
        continent_mapping = {
            'USA': 'North America', 'CAN': 'North America', 'MEX': 'North America',
            'FRA': 'Europe', 'GBR': 'Europe', 'GER': 'Europe', 'ITA': 'Europe', 'ESP': 'Europe',
            'NED': 'Europe', 'SWE': 'Europe', 'NOR': 'Europe', 'AUS': 'Oceania', 'NZL': 'Oceania',
            'CHN': 'Asia', 'JPN': 'Asia', 'KOR': 'Asia', 'IND': 'Asia', 'THA': 'Asia', 'PAK': 'Asia',
            'BRA': 'South America', 'ARG': 'South America', 'CHL': 'South America', 'COL': 'South America',
            'RSA': 'Africa', 'EGY': 'Africa', 'NGR': 'Africa', 'KEN': 'Africa', 'ETH': 'Africa',
            'RUS': 'Europe', 'KAZ': 'Asia', 'UZB': 'Asia', 'TUR': 'Europe', 'IRN': 'Asia', 'ISR': 'Asia',
        }
        
        # Add continent to medals_total
        if 'country_code' in data['medals_total'].columns:
            data['medals_total']['continent'] = data['medals_total']['country_code'].map(continent_mapping).fillna('Other')
        
        # Extract unique sports
        data['unique_sports'] = sorted(data['events']['sport'].unique().tolist()) if 'sport' in data['events'].columns else []
        
        return data
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {}

# ==================== THEME TOGGLE ====================
def render_theme_toggle():
    """Render theme toggle button at top right corner"""
    col1, col2, col3 = st.columns([1, 1, 0.15])
    
    with col3:
        current_theme = st.session_state.get("theme", "light")
        theme_emoji = "🌙" if current_theme == "light" else "☀️"
        theme_label = "Dark" if current_theme == "light" else "Light"
        
        if st.button(f"{theme_emoji}", help=f"Switch to {theme_label} Mode", key=f"theme_toggle_{id(st)}"):
            st.session_state["theme"] = "dark" if current_theme == "light" else "light"
            st.rerun()

# ==================== SIDEBAR FUNCTIONS ====================
def render_sidebar(active_page="dashboard", data=None):
    """Render consistent sidebar across all pages with navigation and filters"""
    if data is None:
        data = {}
    
    with st.sidebar:
        # Inject custom CSS for compact sidebar
        st.markdown("""
        <style>
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 8px !important;
            padding-bottom: 8px !important;
        }
        [data-testid="stSidebarNav"] {
            margin-bottom: 0px !important;
        }
        .css-1d391kg, .css-1v0mbdj, .css-1c7y2kd {
            margin-bottom: 2px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        import os
        logo_path = "figures/olympic_logo.png"
        st.markdown("""
        <div style='margin:0; padding:0; display:flex; flex-direction:column; align-items:center; justify-content:flex-start;'>
        """, unsafe_allow_html=True)
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)
        else:
            st.markdown("""
            <div style='width:100px; height:100px; background:#eee; border-radius:50%; display:flex; align-items:center; justify-content:center;'>
                <span style='font-size:2em;'>🏅</span>
            </div>
            <div style='color:#EE334E; font-size:0.8em; text-align:center;'>Olympic logo not found</div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # Group navigation in expander
        with st.expander("📍 Navigation", expanded=True):
            pages = {
                "dashboard": ("🏠 Dashboard", "app"),
                "overview": ("🏠 Overview", "1_🏠_Overview"),
                "global": ("🗺️ Global Analysis", "2_🗺️_Global_Analysis"),
                "athlete": ("👤 Athlete Performance", "3_👤_Athlete_Performance"),
                "sports": ("🏟️ Sports & Events", "4_🏟️_Sports_and_Events"),
            }
            for page_key, (label, page_file) in pages.items():
                if page_key == active_page:
                    st.markdown(f"<div style='background:linear-gradient(135deg,#0085CA 0%,#EE334E 100%);color:white;padding:8px 10px;border-radius:6px;margin-bottom:4px;font-weight:600;font-size:0.9em;border-left:3px solid #FFD700;'>{label} ✓</div>", unsafe_allow_html=True)
                else:
                    if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                        if page_key == "dashboard":
                            st.switch_page("app.py")
                        else:
                            st.switch_page(f"pages/{page_file}.py")

        # Group filters in expander
        with st.expander("🔍 Filters", expanded=True):
            countries = []
            if 'medals_total' in data:
                medals_df = data['medals_total']
                if 'country_long' in medals_df.columns:
                    countries = sorted(medals_df['country_long'].unique().tolist())
            selected_countries = st.multiselect(
                "🌍 Countries",
                options=countries,
                default=[],
                key="country_filter",
                help="Leave empty to show all countries",
            )

            sports = []
            if 'events' in data and 'sport' in data['events'].columns:
                sports = sorted(data['events']['sport'].unique().tolist())
            selected_sports = st.multiselect(
                "⚽ Sports",
                options=sports,
                default=[],
                key="sport_filter",
                help="Leave empty to show all sports",
            )

            continents = []
            if 'medals_total' in data and 'continent' in data['medals_total'].columns:
                continents = sorted(data['medals_total']['continent'].unique().tolist())
            selected_continent = st.multiselect(
                "🌎 Continents",
                options=continents,
                default=continents,
                key="continent_filter",
                help="Uncheck to exclude continents",
            )

            # Medal types
            col1, col2, col3 = st.columns(3, gap="small")
            with col1:
                include_gold = st.checkbox("Gold", value=True, key="medal_gold")
            with col2:
                include_silver = st.checkbox("Silver", value=True, key="medal_silver")
            with col3:
                include_bronze = st.checkbox("Bronze", value=True, key="medal_bronze")
            medal_filters = {
                'gold': include_gold,
                'silver': include_silver,
                'bronze': include_bronze
            }

    return selected_countries, selected_sports, selected_continent, medal_filters


# ==================== MAIN APP ====================
def main():
    # Inject improved CSS to fully remove sidebar navigation menu and top padding
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Load data
    with st.spinner("Loading data..."):
        data = load_data()

    # Store in session state
    st.session_state['data'] = data

    # Apply theme
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"

    if "animate_header" not in st.session_state:
        st.session_state["animate_header"] = True

    current_theme = st.session_state.get("theme", "light")
    animate_header = st.session_state.get("animate_header", True)
    st.markdown(get_theme_css(current_theme, animated=animate_header), unsafe_allow_html=True)

    # Theme toggle at top right
    render_theme_toggle()

    # Render complete sidebar (navigation + filters) - mark this page as "dashboard"
    selected_countries, selected_sports, selected_continent, medal_filters = render_sidebar(active_page="dashboard", data=data)
    st.session_state['selected_countries'] = selected_countries
    st.session_state['selected_sports'] = selected_sports
    st.session_state['selected_continent'] = selected_continent
    st.session_state['medal_filters'] = medal_filters

    # --- FILTER DATA BASED ON SELECTIONS ---
    # Athletes
    athletes_df = data.get('athletes', pd.DataFrame())
    if not athletes_df.empty:
        if selected_countries:
            if 'country_long' in athletes_df.columns:
                athletes_df = athletes_df[athletes_df['country_long'].isin(selected_countries)]
        if selected_sports:
            if 'sport' in athletes_df.columns:
                athletes_df = athletes_df[athletes_df['sport'].isin(selected_sports)]
        if selected_continent:
            if 'continent' in athletes_df.columns:
                athletes_df = athletes_df[athletes_df['continent'].isin(selected_continent)]

    # Countries
    nocs_df = data.get('nocs', pd.DataFrame())
    if not nocs_df.empty and selected_countries:
        if 'country' in nocs_df.columns:
            nocs_df = nocs_df[nocs_df['country'].isin(selected_countries)]

    # Sports
    events_df = data.get('events', pd.DataFrame())
    if not events_df.empty:
        if selected_sports:
            if 'sport' in events_df.columns:
                events_df = events_df[events_df['sport'].isin(selected_sports)]
        if selected_countries:
            if 'country_long' in events_df.columns:
                events_df = events_df[events_df['country_long'].isin(selected_countries)]

    # Medals
    medals_total_df = data.get('medals_total', pd.DataFrame())
    if not medals_total_df.empty:
        if selected_countries:
            if 'country_long' in medals_total_df.columns:
                medals_total_df = medals_total_df[medals_total_df['country_long'].isin(selected_countries)]
        if selected_continent:
            if 'continent' in medals_total_df.columns:
                medals_total_df = medals_total_df[medals_total_df['continent'].isin(selected_continent)]
        # Medal type filters
        medal_cols = []
        if 'Gold Medal' in medals_total_df.columns:
            if medal_filters.get('gold', True):
                medal_cols.append('Gold Medal')
            if medal_filters.get('silver', True):
                medal_cols.append('Silver Medal')
            if medal_filters.get('bronze', True):
                medal_cols.append('Bronze Medal')
        else:
            if medal_filters.get('gold', True):
                medal_cols.append('gold')
            if medal_filters.get('silver', True):
                medal_cols.append('silver')
            if medal_filters.get('bronze', True):
                medal_cols.append('bronze')

    # Main page header with animated colors
    banner_class = "olympic-banner-animated" if animate_header else "olympic-banner"
    st.markdown(f"""
        <div class="{banner_class}">
            <div class="olympic-rings">
                <span class="ring ring-blue"></span>
                <span class="ring ring-yellow"></span>
                <span class="ring ring-black"></span>
                <span class="ring ring-green"></span>
                <span class="ring ring-red"></span>
            </div>
            <div class="olympic-banner-text">
                <h1 class="main-header">🏅 Paris 2024 Olympic Games Dashboard</h1>
                <p class="sub-header">Interactive analysis of the world's greatest sporting event</p>
                <div class="olympic-chip">LA28 Volunteer Selection Challenge</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
   
    
    # Navigation cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0085CA, #0066A1);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            transition: transform 0.3s ease;
        ">
            <div style="font-size: 1.8em; margin-bottom: 8px;">🏠</div>
            <strong>Overview</strong>
            <p style="font-size: 0.85em; margin-bottom: 0; opacity: 0.9;">KPIs & Medal Distribution</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #FFD700, #E6C200);
            padding: 20px;
            border-radius: 10px;
            color: #333;
            text-align: center;
            transition: transform 0.3s ease;
        ">
            <div style="font-size: 1.8em; margin-bottom: 8px;">🗺️</div>
            <strong>Global Analysis</strong>
            <p style="font-size: 0.85em; margin-bottom: 0; opacity: 0.9;">Worldwide Patterns</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #EE334E, #CC1A33);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            transition: transform 0.3s ease;
        ">
            <div style="font-size: 1.8em; margin-bottom: 8px;">👤</div>
            <strong>Athlete Performance</strong>
            <p style="font-size: 0.85em; margin-bottom: 0; opacity: 0.9;">Profiles & Demographics</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #009F3D, #007A2F);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            transition: transform 0.3s ease;
        ">
            <div style="font-size: 1.8em; margin-bottom: 8px;">🏟️</div>
            <strong>Sports & Events</strong>
            <p style="font-size: 0.85em; margin-bottom: 0; opacity: 0.9;">Schedule & Venues</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick stats section
    st.markdown("""
    <div style="margin: 40px 0 20px 0;">
        <h2 style="font-weight: 800; color: #0085CA; border-bottom: 3px solid #FFD700; padding-bottom: 10px;">
            📊 Quick Statistics
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        total_athletes = len(athletes_df)
        st.markdown(f"""
        <div class="quick-stat">
            <div style="font-size: 2em; font-weight: bold; color: #0085CA;">{total_athletes:,}</div>
            <div style="font-size: 0.9em; color: #666;">🏃 Total Athletes</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        total_countries = len(nocs_df)
        st.markdown(f"""
        <div class="quick-stat">
            <div style="font-size: 2em; font-weight: bold; color: #009F3D;">{total_countries:,}</div>
            <div style="font-size: 0.9em; color: #666;">🌍 Total Countries</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        total_sports = events_df['sport'].nunique() if 'sport' in events_df.columns else 0
        st.markdown(f"""
        <div class="quick-stat">
            <div style="font-size: 2em; font-weight: bold; color: #EE334E;">{total_sports:,}</div>
            <div style="font-size: 0.9em; color: #666;">⚽ Total Sports</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        total_medals = medals_total_df[medal_cols].sum().sum() if medal_cols and not medals_total_df.empty else 0
        st.markdown(f"""
        <div class="quick-stat">
            <div style="font-size: 2em; font-weight: bold; color: #FFD700;">{int(total_medals):,}</div>
            <div style="font-size: 0.9em; color: #666;">🏅 Total Medals</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        total_events = len(events_df)
        st.markdown(f"""
        <div class="quick-stat">
            <div style="font-size: 2em; font-weight: bold; color: #0085CA;">{total_events:,}</div>
            <div style="font-size: 0.9em; color: #666;">🎯 Total Events</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Stats breakdown section
    st.markdown("---")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(0,133,202,0.08), rgba(238,51,46,0.08));
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #FFD700;
        margin-bottom: 30px;
    ">
        <h3 style="margin-top: 0; color: #0085CA;">📈 Dashboard Features</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <p><strong>🔍 Advanced Filters:</strong> Filter by country, sport, continent, and medal type</p>
                <p><strong>📊 Interactive Charts:</strong> Hover over visualizations to explore data</p>
            </div>
            <div>
                <p><strong>🌐 Global Insights:</strong> Analyze trends across continents</p>
                <p><strong>🎯 Real-time Updates:</strong> All charts update instantly with filters</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style="
        text-align: center; 
        color: #888; 
        font-size: 0.85rem; 
        margin-top: 50px;
        padding: 20px;
        background: linear-gradient(135deg, rgba(0,133,202,0.05), rgba(238,51,46,0.05));
        border-radius: 10px;
    ">
        <strong>🏅 LA28 Volunteer Selection Challenge</strong><br>
        <em>Built for the Paris 2024 Olympic Games Dashboard</em><br>
        Instructor: <strong>Dr. Belkacem KHALDI</strong> (b.khaldi@esi-sba.dz)<br>
        <small>Software Engineering For Data Science | 2025</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
