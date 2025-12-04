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

        # Extract unique sports from events data
        if not data['events'].empty:
            # Try different column names for sport
            sport_column = None
            for col in data['events'].columns:
                if col.lower() == 'sport':
                    sport_column = col
                    break
            
            if sport_column:
                unique_sports = data['events'][sport_column].dropna().unique().tolist()
                data['unique_sports'] = sorted([s for s in unique_sports if isinstance(s, str)])
            else:
                data['unique_sports'] = []
        else:
            data['unique_sports'] = []

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

# ==================== FILTER FUNCTIONS ====================
def filter_medals_data(medals_df, medal_filters, selected_countries, selected_continent):
    """
    Filter medals data based on selected filters
    """
    if medals_df.empty:
        return medals_df, []
    
    filtered_df = medals_df.copy()
    
    # Filter by medal type
    medal_cols = []
    
    # Check what type of medal_filters we have (dictionary or list)
    if isinstance(medal_filters, dict):
        # It's a dictionary from the main app sidebar
        if medal_filters.get('gold', True):
            if 'gold_medals' in filtered_df.columns:
                medal_cols.append('gold_medals')
            elif 'Gold Medal' in filtered_df.columns:
                medal_cols.append('Gold Medal')
            elif 'gold' in filtered_df.columns:
                medal_cols.append('gold')
                
        if medal_filters.get('silver', True):
            if 'silver_medals' in filtered_df.columns:
                medal_cols.append('silver_medals')
            elif 'Silver Medal' in filtered_df.columns:
                medal_cols.append('Silver Medal')
            elif 'silver' in filtered_df.columns:
                medal_cols.append('silver')
                
        if medal_filters.get('bronze', True):
            if 'bronze_medals' in filtered_df.columns:
                medal_cols.append('bronze_medals')
            elif 'Bronze Medal' in filtered_df.columns:
                medal_cols.append('Bronze Medal')
            elif 'bronze' in filtered_df.columns:
                medal_cols.append('bronze')
    else:
        # It's a list from somewhere else
        for medal_type in medal_filters:
            if medal_type == 'Gold':
                if 'gold_medals' in filtered_df.columns:
                    medal_cols.append('gold_medals')
                elif 'Gold Medal' in filtered_df.columns:
                    medal_cols.append('Gold Medal')
                elif 'gold' in filtered_df.columns:
                    medal_cols.append('gold')
            elif medal_type == 'Silver':
                if 'silver_medals' in filtered_df.columns:
                    medal_cols.append('silver_medals')
                elif 'Silver Medal' in filtered_df.columns:
                    medal_cols.append('Silver Medal')
                elif 'silver' in filtered_df.columns:
                    medal_cols.append('silver')
            elif medal_type == 'Bronze':
                if 'bronze_medals' in filtered_df.columns:
                    medal_cols.append('bronze_medals')
                elif 'Bronze Medal' in filtered_df.columns:
                    medal_cols.append('Bronze Medal')
                elif 'bronze' in filtered_df.columns:
                    medal_cols.append('bronze')
            elif medal_type == 'Total' and 'total_medals' in filtered_df.columns:
                medal_cols.append('total_medals')
    
    # Filter by country
    if selected_countries:
        country_col = 'country_long' if 'country_long' in filtered_df.columns else 'country'
        if country_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[country_col].isin(selected_countries)]
    
    # Filter by continent
    if selected_continent:
        if isinstance(selected_continent, list):
            if selected_continent and selected_continent != ["All"] and 'continent' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['continent'].isin(selected_continent)]
        else:
            if selected_continent != "All" and 'continent' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['continent'] == selected_continent]
    
    return filtered_df, medal_cols

def filter_athletes_data(athletes_df, selected_countries, selected_sports, selected_continent):
    """
    Filter athletes data based on selected filters
    """
    if athletes_df.empty:
        return athletes_df
    
    filtered_df = athletes_df.copy()
    
    # Filter by country
    if selected_countries:
        country_col = 'country_long' if 'country_long' in filtered_df.columns else 'country'
        if country_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[country_col].isin(selected_countries)]
    
    # Filter by sport
    if selected_sports:
        if 'sport' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
    
    # Filter by continent (if continent column exists)
    if selected_continent and 'continent' in filtered_df.columns:
        if isinstance(selected_continent, list):
            if selected_continent:
                filtered_df = filtered_df[filtered_df['continent'].isin(selected_continent)]
        else:
            if selected_continent != "All":
                filtered_df = filtered_df[filtered_df['continent'] == selected_continent]
    
    return filtered_df

def filter_events_data(events_df, selected_sports, selected_countries):
    """
    Filter events data based on selected filters
    """
    if events_df.empty:
        return events_df
    
    filtered_df = events_df.copy()
    
    # Filter by sport
    if selected_sports:
        # Find sport column (case-insensitive)
        sport_col = None
        for col in filtered_df.columns:
            if col.lower() == 'sport':
                sport_col = col
                break
        
        if sport_col:
            filtered_df = filtered_df[filtered_df[sport_col].isin(selected_sports)]
    
    # Filter by country (if country column exists)
    if selected_countries:
        country_col = None
        for col in filtered_df.columns:
            if 'country' in col.lower():
                country_col = col
                break
        
        if country_col:
            filtered_df = filtered_df[filtered_df[country_col].isin(selected_countries)]
    
    return filtered_df

# ==================== SIDEBAR FUNCTIONS ====================
def render_sidebar(active_page="dashboard", data=None):
    """Render consistent sidebar across all pages with navigation and filters"""
    if data is None:
        data = {}

    with st.sidebar:
        # Inject custom CSS to remove ONLY the logo spacer, not the collapse button
        st.markdown("""
        <style>
        /* HIDE ONLY THE LOGO SPACER, NOT THE COLLAPSE BUTTON */
        [data-testid="stLogoSpacer"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        .st-emotion-cache-11ukie {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Keep the header and collapse button but adjust positioning */
        [data-testid="stSidebarHeader"] {
            padding-top: 0 !important;
            margin-top: 0 !important;
            min-height: 0 !important;
            height: auto !important;
        }
        
        .st-emotion-cache-10p9htt {
            padding-top: 0 !important;
            margin-top: 0 !important;
            min-height: 0 !important;
            height: auto !important;
        }
        
        /* Keep the collapse button visible and properly positioned */
        [data-testid="stSidebarCollapseButton"] {
            position: absolute !important;
            top: 10px !important;
            right: 10px !important;
            z-index: 1000 !important;
        }
        
        .st-emotion-cache-13veyas {
            position: absolute !important;
            top: 10px !important;
            right: 10px !important;
            z-index: 1000 !important;
        }
        
        /* Adjust the collapse button styling for better visibility */
        [data-testid="stSidebarCollapseButton"] button {
            background-color: rgba(0, 133, 202, 0.9) !important;
            border-radius: 50% !important;
            width: 30px !important;
            height: 30px !important;
            min-width: 30px !important;
            min-height: 30px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        /* Remove any residual padding from the sidebar */
        [data-testid="stSidebar"] {
            padding-top: 0 !important;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        
        /* Ensure the sidebar content starts at the very top */
        [data-testid="stSidebarUserContent"] {
            padding-top: 40px !important; /* Make room for the collapse button */
            margin-top: 0 !important;
        }
        
        /* Style for multiselect tags */
        .stMultiSelect [data-baseweb=tag] {
            background-color: #0085CA !important;
            color: white !important;
        }
        
        /* Force black text in dropdowns */
        .stSelectbox, .stMultiSelect {
            color: #000000 !important;
        }
        div[data-baseweb="select"] input, div[data-baseweb="select"] div {
            color: #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        import os
        logo_path = "figures/olympic_logo.png"
        
        # Display the logo with equal padding top and bottom
        if os.path.exists(logo_path):
            # Add equal padding top and bottom using markdown
            st.markdown("""
            <div style='padding: 10px 0 10px 0; text-align: center; margin: 0;'>
            """, unsafe_allow_html=True)
            
            # Use st.image directly with center alignment
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(logo_path, width=100, output_format="PNG")
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Fallback logo with equal padding
            st.markdown("""
            <div style='padding: 10px 0 10px 0; text-align: center; margin: 0;'>
                <div style='
                    width: 100px;
                    height: 100px;
                    background: linear-gradient(135deg, #0085CA, #EE334E);
                    border-radius: 50%;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                '>
                    <span style='font-size: 2.5em; color: white;'>🏅</span>
                </div>
                <div style='
                    color: #EE334E;
                    font-size: 0.8em;
                    text-align: center;
                    font-weight: 600;
                    margin-top: 5px;
                '>Olympic Games</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Group navigation in expander
        with st.expander("📍 Navigation", expanded=True):
            pages = {
                "dashboard": ("🏠 Dashboard", "app"),
                "overview": ("📊 Overview", "1_🏠_Overview"),
                "global": ("🗺️ Global Analysis", "2_🗺️_Global_Analysis"),
                "athlete": ("👤 Athlete Performance", "3_👤_Athlete_Performance"),
                "sports": ("🏟️ Sports & Events", "4_🏟️_Sports_and_Events"),
            }
            for page_key, (label, page_file) in pages.items():
                if page_key == active_page:
                    st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #0085CA 0%, #EE334E 100%);
                        color: white;
                        padding: 8px 12px;
                        border-radius: 8px;
                        margin: 2px 0;
                        font-weight: 600;
                        font-size: 0.9em;
                        border-left: 3px solid #FFD700;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    '>
                        {label} ✓
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                        if page_key == "dashboard":
                            st.switch_page("app.py")
                        else:
                            st.switch_page(f"pages/{page_file}.py")

        # Group filters in expander
        with st.expander("🔍 Filters", expanded=True):
            # Countries filter
            countries = []
            if 'medals_total' in data and not data['medals_total'].empty:
                medals_df = data['medals_total']
                if 'country_long' in medals_df.columns:
                    countries = sorted([c for c in medals_df['country_long'].dropna().unique().tolist() if isinstance(c, str)])
                elif 'country' in medals_df.columns:
                    countries = sorted([c for c in medals_df['country'].dropna().unique().tolist() if isinstance(c, str)])
            
            selected_countries = st.multiselect(
                "🌍 Countries",
                options=countries,
                default=[],
                key="country_filter",
                help="Leave empty to show all countries",
            )

            # Sports filter - Get from events data
            sports = []
            if 'events' in data and not data['events'].empty:
                events_df = data['events']
                # Find sport column (case-insensitive)
                sport_col = None
                for col in events_df.columns:
                    if col.lower() == 'sport':
                        sport_col = col
                        break
                
                if sport_col:
                    sports = sorted([s for s in events_df[sport_col].dropna().unique().tolist() if isinstance(s, str)])
            
            # If no sports found, try athletes data
            if not sports and 'athletes' in data and not data['athletes'].empty:
                athletes_df = data['athletes']
                if 'sport' in athletes_df.columns:
                    sports = sorted([s for s in athletes_df['sport'].dropna().unique().tolist() if isinstance(s, str)])
            
            # Create sports filter
            selected_sports = st.multiselect(
                "⚽ Sports",
                options=sports,
                default=[],
                key="sport_filter",
                help="Leave empty to show all sports",
            )

            # Continents filter
            continents = []
            if 'medals_total' in data and not data['medals_total'].empty and 'continent' in data['medals_total'].columns:
                continents = sorted([c for c in data['medals_total']['continent'].dropna().unique().tolist() if isinstance(c, str)])
            
            selected_continent = st.multiselect(
                "🌎 Continents",
                options=continents,
                default=continents if continents else [],
                key="continent_filter",
                help="Select continents to include",
            )

            # Medal types
            st.markdown("**Medal Types:**")
            col1, col2, col3 = st.columns(3, gap="small")
            with col1:
                include_gold = st.checkbox("🥇 Gold", value=True, key="medal_gold")
            with col2:
                include_silver = st.checkbox("🥈 Silver", value=True, key="medal_silver")
            with col3:
                include_bronze = st.checkbox("🥉 Bronze", value=True, key="medal_bronze")
            medal_filters = {
                'gold': include_gold,
                'silver': include_silver,
                'bronze': include_bronze
            }

    return selected_countries, selected_sports, selected_continent, medal_filters

# ==================== MAIN APP ====================
def main():
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
            # Find sport column
            sport_col = None
            for col in events_df.columns:
                if col.lower() == 'sport':
                    sport_col = col
                    break
            if sport_col:
                events_df = events_df[events_df[sport_col].isin(selected_sports)]
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

    st.markdown("""
    <style>
    .nav-card {
        width: 100%;
    }
    .nav-card .stButton > button {
        color: white !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border: none !important;
        text-align: center !important;
        font-size: 1em !important;
        width: 100% !important;
        height: auto !important;
        transition: transform 0.3s ease !important;
        white-space: pre-line !important;
    }
    .nav-card .stButton > button:hover {
        transform: translateY(-5px) !important;
    }
    .overview-card .stButton > button {
        background: linear-gradient(135deg, #0085CA, #0066A1) !important;
    }
    .global-card .stButton > button {
        background: linear-gradient(135deg, #FFD700, #E6C200) !important;
        color: #333 !important;
    }
    .athlete-card .stButton > button {
        background: linear-gradient(135deg, #EE334E, #CC1A33) !important;
    }
    .sports-card .stButton > button {
        background: linear-gradient(135deg, #009F3D, #007A2F) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Navigation cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="nav-card overview-card">', unsafe_allow_html=True)
        if st.button("🏠\nOverview\nKPIs & Medal Distribution", key="overview_card", use_container_width=True):
            st.switch_page("pages/1_🏠_Overview.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="nav-card global-card">', unsafe_allow_html=True)
        if st.button("🗺️\nGlobal Analysis\nWorldwide Patterns", key="global_card", use_container_width=True):
            st.switch_page("pages/2_🗺️_Global_Analysis.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="nav-card athlete-card">', unsafe_allow_html=True)
        if st.button("👤\nAthlete Performance\nProfiles & Demographics", key="athlete_card", use_container_width=True):
            st.switch_page("pages/3_👤_Athlete_Performance.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="nav-card sports-card">', unsafe_allow_html=True)
        if st.button("🏟️\nSports & Events\nSchedule & Venues", key="sports_card", use_container_width=True):
            st.switch_page("pages/4_🏟️_Sports_and_Events.py")
        st.markdown('</div>', unsafe_allow_html=True)

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