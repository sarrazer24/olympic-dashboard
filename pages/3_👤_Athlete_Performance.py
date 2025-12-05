import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np
import re
import ast

# Import styling
from app import get_theme_css, render_sidebar, render_theme_toggle

# Page configuration
st.set_page_config(
    page_title="Athlete Performance - Olympic Dashboard",
    layout="wide"
)

# Load data from main app
if "data" not in st.session_state:
    st.warning("⚠️ Please go to the Dashboard first to load data")
    if st.button("Go to Dashboard"):
        st.switch_page("app.py")
    st.stop()

data = st.session_state.get("data", {})

# Initialize theme
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

if "animate_header" not in st.session_state:
    st.session_state["animate_header"] = True

current_theme = st.session_state.get("theme", "dark")
animate_header = st.session_state.get("animate_header", True)
st.markdown(get_theme_css(current_theme, animated=animate_header), unsafe_allow_html=True)

# Theme toggle at top right
render_theme_toggle()

# Sidebar filters
selected_countries, selected_sports, selected_continent, medal_filters = render_sidebar(active_page="athlete", data=data)
st.session_state['selected_countries'] = selected_countries
st.session_state['selected_sports'] = selected_sports
st.session_state['selected_continent'] = selected_continent
st.session_state['medal_filters'] = medal_filters

# Page header
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
            <h1 class="main-header">👤 Athlete Performance</h1>
            <p class="sub-header">Individual profiles and demographic analysis</p>
            <div class="olympic-chip">Human Story &nbsp;•&nbsp; Athlete Insights</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Get data
athletes_data = data.get('athletes', pd.DataFrame())
coaches_data = data.get('coaches', pd.DataFrame())
teams_data = data.get('teams', pd.DataFrame())
medals_data = data.get('medals', pd.DataFrame())
medallists_data = data.get('medallists', pd.DataFrame())
events_data = data.get('events', pd.DataFrame())

# Vérifier si les données sont chargées
if athletes_data.empty:
    st.error("❌ No athlete data loaded. Please return to the Dashboard.")
    if st.button("Return to Dashboard"):
        st.switch_page("app.py")
    st.stop()

# ============================================================
# FONCTIONS POUR EXTRACTION DE DONNÉES
# ============================================================
def extract_weight_from_string(text):
    """
    Extrait le poids d'une chaîne de caractères.
    Exemples: "Men -60 kg", "Women's +78kg", "100kg", "68-73 kg"
    """
    if not isinstance(text, str) or pd.isna(text):
        return None
    
    text_lower = text.lower()
    
    # 1. Chercher les plages de poids (deux nombres séparés par un tiret)
    range_pattern = r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s*kg'
    range_match = re.search(range_pattern, text_lower)
    if range_match:
        try:
            weight1 = float(range_match.group(1))
            weight2 = float(range_match.group(2))
            avg_weight = (weight1 + weight2) / 2
            return round(avg_weight, 1)
        except:
            pass
    
    # 2. Chercher les poids simples
    simple_patterns = [
        r'[-+]*(\d+\.?\d*)\s*kg\b',  # -60 kg, +78kg, 100.5 kg
        r'(\d+\.?\d*)\s*kilograms?\b',
        r'(\d+\.?\d*)\s*kgs?\b',
    ]
    
    for pattern in simple_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                weight = float(match.group(1))
                return round(weight, 1)
            except:
                continue
    
    # 3. Chercher les livres et convertir
    lb_patterns = [
        r'(\d+)\s*lbs?\b',
        r'(\d+)\s*pounds?\b'
    ]
    
    for pattern in lb_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                weight_lbs = float(match.group(1))
                weight_kg = weight_lbs * 0.453592
                return round(weight_kg, 1)
            except:
                continue
    
    return None

def extract_height_from_string(text):
    """
    Extrait la taille d'une chaîne de caractères.
    Exemples: "180 cm", "1.80m", "5'11""
    """
    if not isinstance(text, str) or pd.isna(text):
        return None
    
    text_lower = text.lower()
    
    patterns = [
        r'(\d+\.?\d*)\s*cm\b',  # 180 cm
        r'(\d+\.?\d*)\s*centimeters?\b',
        r'(\d+)\.(\d+)\s*m\b',  # 1.80 m
        r'(\d+)\'(\d+)\s*["\']?\b',  # 5'11"
        r'height[:\s]*(\d+\.?\d*)\s*(cm|m)',
        r'(\d+)\s*(cm|centimeter|m|meter)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            try:
                if "'" in text_lower:  # Pieds/pouces
                    feet = float(matches[0][0])
                    inches = float(matches[0][1])
                    height_cm = (feet * 30.48) + (inches * 2.54)
                    return round(height_cm, 1)
                elif 'm' in text_lower and '.' in text_lower:  # Mètres
                    meters = float(f"{matches[0][0]}.{matches[0][1]}")
                    height_cm = meters * 100
                    return round(height_cm, 1)
                else:  # Centimètres
                    height = float(matches[0][0])
                    if 'm' in text_lower and height < 3:
                        height = height * 100
                    return round(height, 1)
            except:
                continue
    
    return None

def parse_events_string(events_str):
    """
    Parse la chaîne d'événements qui peut être une liste Python ou une chaîne simple.
    """
    if pd.isna(events_str):
        return []
    
    if isinstance(events_str, str):
        if events_str.startswith('[') and events_str.endswith(']'):
            try:
                return ast.literal_eval(events_str)
            except:
                pass
        return [events_str]
    
    if isinstance(events_str, list):
        return events_str
    
    return []

def get_athlete_weight_from_events(events_data):
    """
    Extrait le poids d'un athlète à partir de ses événements.
    """
    if pd.isna(events_data) or not events_data:
        return None
    
    events_list = parse_events_string(events_data)
    
    weights = []
    for event in events_list:
        event_str = str(event)
        weight = extract_weight_from_string(event_str)
        if weight and weight > 30:  # Filtre pour éviter les valeurs aberrantes
            weights.append(weight)
    
    if weights:
        avg_weight = sum(weights) / len(weights)
        return round(avg_weight, 1)
    
    return None

def get_athlete_height_from_data(height_data, events_data):
    """
    Extrait la taille d'un athlète.
    """
    if not pd.isna(height_data) and height_data != 0 and height_data != '0':
        try:
            height = float(height_data)
            if height > 100:  # Supposons que c'est en cm
                return round(height, 1)
            elif height > 1:  # Supposons que c'est en mètres
                return round(height * 100, 1)
        except:
            pass
    
    events_list = parse_events_string(events_data)
    heights = []
    
    for event in events_list:
        height = extract_height_from_string(str(event))
        if height and height > 100:  # Filtrer les valeurs < 100cm
            heights.append(height)
    
    if heights:
        avg_height = sum(heights) / len(heights)
        return round(avg_height, 1)
    
    return None

# ============================================================
# APPLIQUER LES FILTRES
# ============================================================
filtered_athletes = athletes_data.copy()

# Identifier les colonnes correctes
country_col = 'country_long' if 'country_long' in filtered_athletes.columns else 'country'
name_col = 'name'
disciplines_col = 'disciplines' if 'disciplines' in filtered_athletes.columns else None
events_col = 'events' if 'events' in filtered_athletes.columns else None
height_col = 'height' if 'height' in filtered_athletes.columns else None

# Appliquer les filtres si les colonnes existent
if selected_countries and country_col in filtered_athletes.columns:
    filtered_athletes = filtered_athletes[filtered_athletes[country_col].isin(selected_countries)]

if selected_sports and disciplines_col and disciplines_col in filtered_athletes.columns:
    filtered_athletes = filtered_athletes[
        filtered_athletes[disciplines_col].str.contains('|'.join(selected_sports), case=False, na=False)
    ]

# --- Athlete Detailed Profile Card ---
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">👤 Athlete Detailed Profile</h2>
</div>
""", unsafe_allow_html=True)

# Athlete search
col1, col2 = st.columns([2, 1])
with col1:
    if not filtered_athletes.empty and name_col:
        athlete_names = sorted(filtered_athletes[name_col].dropna().unique())
        selected_athlete = st.selectbox(
            "🔍 Search for an athlete:",
            options=athlete_names,
            index=0 if athlete_names else None,
            key="athlete_search"
        )
    else:
        selected_athlete = None
        st.info("No athlete data available")

with col2:
    st.markdown("""
    <div style="margin-top: 1.5rem; padding: 10px; background: rgba(0,133,202,0.1); border-radius: 8px;">
        <small>Select an athlete to view their detailed profile</small>
    </div>
    """, unsafe_allow_html=True)

# Display athlete profile
if selected_athlete and not filtered_athletes.empty:
    athlete_rows = filtered_athletes[filtered_athletes[name_col] == selected_athlete]
    
    if not athlete_rows.empty:
        athlete_info = athlete_rows.iloc[0]
        
        st.markdown("---")
        
        # Créer la carte de profil
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            initials = ''.join([name[0] for name in selected_athlete.split()[:2]]).upper() if ' ' in selected_athlete else selected_athlete[:2].upper()
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #0085CA, #EE334E);
                width: 150px;
                height: 150px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto;
            ">
                <span style="font-size: 2.5em; color: white; font-weight: bold;">{initials}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            country_display = athlete_info.get(country_col, 'Unknown')
            disciplines_display = athlete_info.get(disciplines_col, 'Not specified')
            
            sport_info = "Not specified"
            if not medallists_data.empty and 'name' in medallists_data.columns and 'discipline' in medallists_data.columns:
                athlete_disciplines = medallists_data[medallists_data['name'] == selected_athlete]['discipline'].unique()
                if len(athlete_disciplines) > 0:
                    sport_info = ", ".join(athlete_disciplines)
            
            st.markdown(f"""
            <div style="padding: 20px;">
                <h3 style="color: #0085CA; margin-bottom: 10px;">{selected_athlete}</h3>
                <p style="margin-bottom: 5px;"><strong>🏳️ Country:</strong> {country_display}</p>
                <p style="margin-bottom: 5px;"><strong>🎯 Discipline(s):</strong> {disciplines_display}</p>
                <p style="margin-bottom: 5px;"><strong>⚽ Sport(s):</strong> {sport_info}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="padding: 20px;">
                <h4 style="color: #FFD700; margin-bottom: 10px;">Physical Stats</h4>
            """, unsafe_allow_html=True)
            
            # Récupérer les données
            height_data = athlete_info.get(height_col) if height_col else None
            events_data = athlete_info.get(events_col) if events_col else None
            disciplines_data = athlete_info.get(disciplines_col, '')
            
            # 1. Calculer la taille
            calculated_height = get_athlete_height_from_data(height_data, events_data)
            
            if calculated_height:
                height_display = f"{calculated_height} cm"
                height_source = "extracted from data"
            else:
                height_display = "N/A"
                height_source = "data not available"
            
            # 2. Calculer le poids
            calculated_weight = get_athlete_weight_from_events(events_data)
            
            if calculated_weight:
                weight_display = f"{calculated_weight} kg"
                weight_source = "extracted from events"
            else:
                discipline_weight = extract_weight_from_string(str(disciplines_data))
                if discipline_weight and discipline_weight > 30:
                    weight_display = f"{discipline_weight} kg"
                    weight_source = "extracted from discipline"
                else:
                    weight_display = "N/A"
                    weight_source = "data not available"
            
            # Afficher les métriques avec tooltip
            st.metric("📏 Height", height_display, 
                     help=f"Source: {height_source}")
            st.metric("⚖️ Weight", weight_display,
                     help=f"Source: {weight_source}")
            
            gender = athlete_info.get('gender', 'N/A')
            if pd.notna(gender) and gender != 'N/A':
                st.metric("👤 Gender", gender)
            else:
                st.metric("👤 Gender", "N/A")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Détails supplémentaires
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👨‍🏫 Coach Information")
            if not coaches_data.empty and country_col in coaches_data.columns:
                coaches_from_country = coaches_data[coaches_data[country_col] == country_display]
                
                if not coaches_from_country.empty:
                    for idx, coach in coaches_from_country.head(5).iterrows():
                        coach_name = coach.get('name', 'Unknown')
                        coach_country = coach.get(country_col, 'Unknown')
                        st.write(f"• **{coach_name}**")
                        st.write(f"  Country: {coach_country}")
                        st.write("---")
                else:
                    st.info(f"No coaches found from {country_display}")
            else:
                st.info("Coach data not available")
        
        with col2:
            st.markdown("### 📝 Additional Information")
            
            birth_date = athlete_info.get('birth_date', 'N/A')
            if pd.notna(birth_date) and birth_date != 'N/A':
                st.write(f"**Birth Date:** {birth_date}")
            
            birth_place = athlete_info.get('birth_place', 'N/A')
            if pd.notna(birth_place) and birth_place != 'N/A':
                st.write(f"**Birth Place:** {birth_place}")
            
            nationality = athlete_info.get('nationality_long', athlete_info.get('nationality', 'N/A'))
            if pd.notna(nationality) and nationality != 'N/A':
                st.write(f"**Nationality:** {nationality}")
            
            # Afficher les événements formatés
            if events_col and events_col in athlete_info:
                events_data = athlete_info[events_col]
                if pd.notna(events_data) and events_data != 'N/A':
                    try:
                        if isinstance(events_data, str) and events_data.startswith('['):
                            events_list = ast.literal_eval(events_data)
                            if isinstance(events_list, list) and events_list:
                                st.write("**Events:**")
                                for event in events_list:
                                    event_str = str(event)
                                    weight = extract_weight_from_string(event_str)
                                    if weight and weight > 30:
                                        st.write(f"• {event_str} (≈{weight} kg)")
                                    else:
                                        st.write(f"• {event_str}")
                        else:
                            event_str = str(events_data)
                            weight = extract_weight_from_string(event_str)
                            if weight and weight > 30:
                                st.write(f"**Events:** {event_str} (≈{weight} kg)")
                            else:
                                st.write(f"**Events:** {event_str}")
                    except:
                        st.write(f"**Events:** {events_data}")
                else:
                    st.write("**Events:** N/A")
            else:
                st.write("**Events:** N/A")
            
            if not teams_data.empty and 'name' in teams_data.columns:
                athlete_teams = teams_data[teams_data['name'] == selected_athlete]
                if not athlete_teams.empty:
                    st.write("**Team(s):**")
                    for _, team in athlete_teams.iterrows():
                        team_name = team.get('team_name', team.get('team', 'Unknown'))
                        st.write(f"• {team_name}")
                else:
                    st.write("**Team(s):** N/A")
            else:
                st.write("**Team(s):** N/A")
        
        # Informations sur les médailles
        st.markdown("---")
        st.markdown("### 🏅 Medal Achievements")
        
        if not medallists_data.empty and 'name' in medallists_data.columns and 'medal_type' in medallists_data.columns:
            athlete_medals = medallists_data[medallists_data['name'] == selected_athlete]
            
            if not athlete_medals.empty:
                athlete_medals['medal_type_clean'] = athlete_medals['medal_type'].astype(str).str.strip()
                
                medal_counts = {
                    'Gold': (athlete_medals['medal_type_clean'] == 'Gold Medal').sum(),
                    'Silver': (athlete_medals['medal_type_clean'] == 'Silver Medal').sum(),
                    'Bronze': (athlete_medals['medal_type_clean'] == 'Bronze Medal').sum()
                }
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    gold_count = medal_counts.get('Gold', 0)
                    st.metric("🥇 Gold Medals", gold_count)
                with col2:
                    silver_count = medal_counts.get('Silver', 0)
                    st.metric("🥈 Silver Medals", silver_count)
                with col3:
                    bronze_count = medal_counts.get('Bronze', 0)
                    st.metric("🥉 Bronze Medals", bronze_count)
                
                st.markdown("#### Medal Details")
                if 'event' in athlete_medals.columns:
                    display_data = athlete_medals.copy()
                    
                    display_data['Weight (kg)'] = display_data.apply(
                        lambda row: extract_weight_from_string(str(row.get('event', ''))), 
                        axis=1
                    )
                    
                    display_data['Weight (kg)'] = display_data['Weight (kg)'].apply(
                        lambda x: x if x and x > 10 else None
                    )
                    
                    display_cols = ['medal_type', 'event', 'discipline', 'Weight (kg)', 'medal_date']
                    available_cols = [col for col in display_cols if col in display_data.columns]
                    
                    if available_cols:
                        st.dataframe(
                            display_data[available_cols].sort_values('medal_type', ascending=False),
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                'Weight (kg)': st.column_config.NumberColumn(
                                    format="%.1f kg"
                                )
                            }
                        )
                else:
                    st.info("No event details available")
            else:
                st.info(f"No medals found for {selected_athlete}")
        else:
            st.info("Medallists data not available")

st.markdown("---")

# --- Athlete Age Distribution ---
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">📊 Athlete Age Distribution</h2>
</div>
""", unsafe_allow_html=True)

# Recharger filtered_athletes pour l'analyse d'âge
filtered_athletes = athletes_data.copy()
if selected_countries and country_col in filtered_athletes.columns:
    filtered_athletes = filtered_athletes[filtered_athletes[country_col].isin(selected_countries)]
if selected_sports and disciplines_col and disciplines_col in filtered_athletes.columns:
    filtered_athletes = filtered_athletes[
        filtered_athletes[disciplines_col].str.contains('|'.join(selected_sports), case=False, na=False)
    ]

if not filtered_athletes.empty:
    if 'birth_date' in filtered_athletes.columns:
        try:
            filtered_athletes['birth_date_parsed'] = pd.to_datetime(filtered_athletes['birth_date'], errors='coerce')
            current_year = 2024
            filtered_athletes['age'] = current_year - filtered_athletes['birth_date_parsed'].dt.year
            
            filtered_athletes = filtered_athletes[filtered_athletes['age'].between(10, 60)]
            
            if not filtered_athletes.empty and filtered_athletes['age'].notna().sum() > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'gender' in filtered_athletes.columns:
                        fig = px.box(
                            filtered_athletes,
                            x='gender',
                            y='age',
                            title='<b>Age Distribution by Gender</b>',
                            color='gender',
                            color_discrete_map={'M': '#0085CA', 'F': '#EE334E', 'Male': '#0085CA', 'Female': '#EE334E'}
                        )
                        fig.update_layout(
                            height=500,
                            xaxis_title="Gender",
                            yaxis_title="Age",
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        fig = px.histogram(
                            filtered_athletes,
                            x='age',
                            nbins=30,
                            title='<b>Overall Age Distribution</b>',
                            color_discrete_sequence=['#0085CA']
                        )
                        fig.update_layout(height=500, xaxis_title="Age", yaxis_title="Count")
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("### 📈 Age Statistics")
                    
                    age_stats = filtered_athletes['age'].describe()
                    col_stat1, col_stat2 = st.columns(2)
                    
                    with col_stat1:
                        st.metric("👥 Total Athletes", int(age_stats['count']))
                        st.metric("📊 Average Age", f"{age_stats['mean']:.1f}")
                        st.metric("📈 Median Age", f"{age_stats['50%']:.1f}")
                    
                    with col_stat2:
                        st.metric("👶 Youngest", int(age_stats['min']))
                        st.metric("👴 Oldest", int(age_stats['max']))
                        st.metric("📐 Age Range", f"{int(age_stats['max'] - age_stats['min'])}")
                    
                    st.markdown("#### Age Groups")
                    age_bins = [10, 20, 25, 30, 35, 40, 50, 60]
                    age_labels = ['10-19', '20-24', '25-29', '30-34', '35-39', '40-49', '50-60']
                    
                    filtered_athletes['age_group'] = pd.cut(
                        filtered_athletes['age'], 
                        bins=age_bins, 
                        labels=age_labels, 
                        right=False
                    )
                    
                    age_group_counts = filtered_athletes['age_group'].value_counts().sort_index()
                    
                    fig = px.bar(
                        x=age_group_counts.index,
                        y=age_group_counts.values,
                        title='<b>Athletes by Age Group</b>',
                        color=age_group_counts.values,
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(
                        height=300,
                        xaxis_title="Age Group",
                        yaxis_title="Number of Athletes",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.info("No valid age data available after cleaning")
        
        except Exception as e:
            st.warning(f"Could not parse birth dates: {str(e)[:100]}...")
            st.info("Birth date format might be different or contain invalid values")
    else:
        st.info("Birth date column not found in athlete data")
else:
    st.info("No athlete data available for age analysis")

st.markdown("---")

# --- Gender Distribution ---
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">👥 Gender Distribution</h2>
</div>
""", unsafe_allow_html=True)

# Recharger filtered_athletes pour l'analyse de genre
filtered_athletes = athletes_data.copy()
if selected_countries and country_col in filtered_athletes.columns:
    filtered_athletes = filtered_athletes[filtered_athletes[country_col].isin(selected_countries)]
if selected_sports and disciplines_col and disciplines_col in filtered_athletes.columns:
    filtered_athletes = filtered_athletes[
        filtered_athletes[disciplines_col].str.contains('|'.join(selected_sports), case=False, na=False)
    ]

if not filtered_athletes.empty and 'gender' in filtered_athletes.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        gender_counts = filtered_athletes['gender'].value_counts()
        
        gender_labels = {
            'M': 'Male', 'F': 'Female',
            'Male': 'Male', 'Female': 'Female',
            'm': 'Male', 'f': 'Female'
        }
        gender_counts.index = gender_counts.index.map(lambda x: gender_labels.get(x, x))
        
        fig = px.pie(
            values=gender_counts.values,
            names=gender_counts.index,
            title='<b>Overall Gender Distribution</b>',
            color_discrete_sequence=['#0085CA', '#EE334E']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if country_col in filtered_athletes.columns:
            top_countries = filtered_athletes[country_col].value_counts().head(10).index.tolist()
            country_gender_data = filtered_athletes[filtered_athletes[country_col].isin(top_countries)]
            
            if not country_gender_data.empty:
                gender_by_country = country_gender_data.groupby([country_col, 'gender']).size().reset_index(name='count')
                gender_by_country['gender'] = gender_by_country['gender'].map(lambda x: gender_labels.get(x, x))
                
                fig = px.bar(
                    gender_by_country,
                    x=country_col,
                    y='count',
                    color='gender',
                    barmode='group',
                    title='<b>Gender Distribution by Country (Top 10)</b>',
                    color_discrete_map={'Male': '#0085CA', 'Female': '#EE334E'}
                )
                fig.update_layout(
                    height=400,
                    xaxis_title="Country",
                    yaxis_title="Number of Athletes",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No country data available for selected filters")
        else:
            st.info("Country column not found for gender distribution")
else:
    st.info("No gender data available")

st.markdown("---")

# --- Top Athletes by Medals ---
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">🏆 Top Athletes by Medals</h2>
</div>
""", unsafe_allow_html=True)

if not medallists_data.empty and 'name' in medallists_data.columns and 'medal_type' in medallists_data.columns:
    filtered_medallists = medallists_data.copy()
    
    if selected_countries:
        country_cols_to_try = ['country_long', 'country', 'country_name', 'nationality', 'Team_Country']
        country_col_found = None
        
        for col in country_cols_to_try:
            if col in filtered_medallists.columns:
                country_col_found = col
                break
        
        if country_col_found:
            filtered_medallists = filtered_medallists[
                filtered_medallists[country_col_found].isin(selected_countries)
            ]
    
    filtered_medallists['medal_type_clean'] = filtered_medallists['medal_type'].astype(str).str.strip()
    
    medal_summary = []
    
    for name in filtered_medallists['name'].unique():
        athlete_medals = filtered_medallists[filtered_medallists['name'] == name]
        
        gold_count = (athlete_medals['medal_type_clean'] == 'Gold Medal').sum()
        silver_count = (athlete_medals['medal_type_clean'] == 'Silver Medal').sum()
        bronze_count = (athlete_medals['medal_type_clean'] == 'Bronze Medal').sum()
        total_count = len(athlete_medals)
        
        medal_summary.append({
            'name': name,
            'Gold': gold_count,
            'Silver': silver_count,
            'Bronze': bronze_count,
            'Total': total_count
        })
    
    medal_summary_df = pd.DataFrame(medal_summary)
    
    if not medal_summary_df.empty:
        top_athletes = medal_summary_df.nlargest(10, 'Total')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=top_athletes['name'],
            y=top_athletes['Gold'],
            name='🥇 Gold',
            marker_color='#FFD700',
            text=top_athletes['Gold'],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            x=top_athletes['name'],
            y=top_athletes['Silver'],
            name='🥈 Silver',
            marker_color='#C0C0C0',
            text=top_athletes['Silver'],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            x=top_athletes['name'],
            y=top_athletes['Bronze'],
            name='🥉 Bronze',
            marker_color='#CD7F32',
            text=top_athletes['Bronze'],
            textposition='auto'
        ))
        
        fig.update_layout(
            title_text="<b>Top 10 Athletes by Medal Count</b>",
            xaxis_title="Athlete",
            yaxis_title="Number of Medals",
            barmode='stack',
            height=500,
            hovermode='x unified',
            xaxis_tickangle=-45,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📋 Top Athletes Details")
        
        display_data = top_athletes.copy()
        
        country_col_found = None
        country_cols_to_try = ['country_long', 'country', 'country_name', 'nationality', 'Team_Country']
        
        for col in country_cols_to_try:
            if col in filtered_medallists.columns:
                country_col_found = col
                break
        
        if country_col_found:
            country_mapping = {}
            for name in display_data['name']:
                athlete_data = filtered_medallists[filtered_medallists['name'] == name]
                if not athlete_data.empty:
                    country = athlete_data.iloc[0][country_col_found]
                    country_mapping[name] = country
                else:
                    country_mapping[name] = 'Unknown'
            
            display_data['Country'] = display_data['name'].map(country_mapping)
            display_columns = ['name', 'Country', 'Gold', 'Silver', 'Bronze', 'Total']
            column_names = ['Athlete', 'Country', '🥇 Gold', '🥈 Silver', '🥉 Bronze', 'Total Medals']
        else:
            display_columns = ['name', 'Gold', 'Silver', 'Bronze', 'Total']
            column_names = ['Athlete', '🥇 Gold', '🥈 Silver', '🥉 Bronze', 'Total Medals']
        
        display_data = display_data[display_columns]
        display_data.columns = column_names
        
        st.dataframe(
            display_data.sort_values('Total Medals', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No medal data available for the selected filters")
else:
    st.info("Medallists data not available for top athletes analysis")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: right; color: #888; font-size: 0.8rem;">
    Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)