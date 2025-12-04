import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

# Import styling
from app import get_theme_css, render_sidebar, render_theme_toggle

# Page configuration
st.set_page_config(
    page_title="Athlete Performance - Olympic Dashboard",
    layout="wide"
)

# Load data from main app
if "data" not in st.session_state:
    st.info("Please go to the main page first to load data")
    st.stop()

data = st.session_state.get("data", {})

# Initialize theme
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

current_theme = st.session_state.get("theme", "light")
st.markdown(get_theme_css(current_theme), unsafe_allow_html=True)

# Theme toggle at top right
render_theme_toggle()

# Sidebar filters
selected_countries, selected_sports, selected_continent, medal_filters = render_sidebar(active_page="athlete", data=data)
st.session_state['selected_countries'] = selected_countries
st.session_state['selected_sports'] = selected_sports
st.session_state['selected_continent'] = selected_continent
st.session_state['medal_filters'] = medal_filters

# Page header
st.markdown("""
    <div class="olympic-banner">
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

# Debug: Afficher les colonnes disponibles
with st.expander("🔍 Debug: Voir les colonnes disponibles", expanded=False):
    if not athletes_data.empty:
        st.write("**Athletes columns:**", list(athletes_data.columns))
        st.write("**Sample athletes:**")
        st.dataframe(athletes_data[['name', 'country_long', 'height', 'weight', 'disciplines']].head(5), use_container_width=True)
    
    if not medallists_data.empty:
        st.write("**Medallists columns:**", list(medallists_data.columns))
        st.write("**Sample medallists:**")
        st.dataframe(medallists_data[['name', 'medal_type', 'event', 'discipline']].head(5), use_container_width=True)
    
    if not coaches_data.empty:
        st.write("**Coaches columns:**", list(coaches_data.columns))
    
    if not teams_data.empty:
        st.write("**Teams columns:**", list(teams_data.columns))

# Appliquer les filtres aux athlètes
filtered_athletes = athletes_data.copy()

# Identifier les colonnes correctes
country_col = 'country_long' if 'country_long' in filtered_athletes.columns else 'country'
name_col = 'name'  # On a confirmé que cette colonne existe
disciplines_col = 'disciplines' if 'disciplines' in filtered_athletes.columns else None

# Appliquer les filtres si les colonnes existent
if selected_countries and country_col in filtered_athletes.columns:
    filtered_athletes = filtered_athletes[filtered_athletes[country_col].isin(selected_countries)]

# Note: On ne peut pas filtrer par sport car la colonne n'existe pas dans athletes.csv
# On peut filtrer par discipline si nécessaire
if selected_sports and disciplines_col and disciplines_col in filtered_athletes.columns:
    # Vérifier si la discipline contient le sport sélectionné
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
        # Trier les noms pour faciliter la recherche
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
        athlete_info = athlete_rows.iloc[0]  # Prendre le premier résultat
        
        st.markdown("---")
        
        # Créer la carte de profil
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            # Image de profil avec initiales
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
            # Informations de base
            country_display = athlete_info.get(country_col, 'Unknown')
            disciplines_display = athlete_info.get(disciplines_col, 'Not specified')
            
            # Chercher le sport à partir des événements ou des médaillés
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
            # Statistiques physiques
            st.markdown("""
            <div style="padding: 20px;">
                <h4 style="color: #FFD700; margin-bottom: 10px;">Physical Stats</h4>
            """, unsafe_allow_html=True)
            
            height = athlete_info.get('height', 'N/A')
            weight = athlete_info.get('weight', 'N/A')
            
            # Formater les valeurs
            if pd.notna(height) and height != 'N/A':
                height_display = f"{height} cm" if isinstance(height, (int, float)) else str(height)
            else:
                height_display = "N/A"
                
            if pd.notna(weight) and weight != 'N/A':
                weight_display = f"{weight} kg" if isinstance(weight, (int, float)) else str(weight)
            else:
                weight_display = "N/A"
            
            st.metric("📏 Height", height_display)
            st.metric("⚖️ Weight", weight_display)
            
            # Afficher le genre si disponible
            gender = athlete_info.get('gender', 'N/A')
            if pd.notna(gender) and gender != 'N/A':
                st.metric("👤 Gender", gender)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Détails supplémentaires
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Informations sur l'entraîneur
            st.markdown("### 👨‍🏫 Coach Information")
            if not coaches_data.empty:
                # Chercher les entraîneurs par pays
                coaches_from_country = coaches_data[coaches_data[country_col] == country_display]
                
                if not coaches_from_country.empty:
                    # Prendre les 5 premiers entraîneurs
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
            # Informations additionnelles
            st.markdown("### 📝 Additional Information")
            
            # Date de naissance
            birth_date = athlete_info.get('birth_date', 'N/A')
            if pd.notna(birth_date) and birth_date != 'N/A':
                st.write(f"**Birth Date:** {birth_date}")
            
            # Lieu de naissance
            birth_place = athlete_info.get('birth_place', 'N/A')
            if pd.notna(birth_place) and birth_place != 'N/A':
                st.write(f"**Birth Place:** {birth_place}")
            
            # Nationalité
            nationality = athlete_info.get('nationality_long', athlete_info.get('nationality', 'N/A'))
            if pd.notna(nationality) and nationality != 'N/A':
                st.write(f"**Nationality:** {nationality}")
            
            # Événements
            events = athlete_info.get('events', 'N/A')
            if pd.notna(events) and events != 'N/A':
                st.write(f"**Events:** {events}")
            
            # Team information - essayer de trouver dans teams.csv
            if not teams_data.empty and 'name' in teams_data.columns:
                athlete_teams = teams_data[teams_data['name'] == selected_athlete]
                if not athlete_teams.empty:
                    st.write("**Team(s):**")
                    for _, team in athlete_teams.iterrows():
                        team_name = team.get('team_name', team.get('team', 'Unknown'))
                        st.write(f"• {team_name}")
        
        # Informations sur les médailles
        st.markdown("---")
        st.markdown("### 🏅 Medal Achievements")
        
        if not medallists_data.empty and 'name' in medallists_data.columns:
            athlete_medals = medallists_data[medallists_data['name'] == selected_athlete]
            
            if not athlete_medals.empty:
                # Compter les médailles par type
                medal_counts = athlete_medals['medal_type'].value_counts()
                
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
                
                # Afficher les détails des médailles
                st.markdown("#### Medal Details")
                display_cols = ['medal_type', 'event', 'discipline', 'medal_date']
                available_cols = [col for col in display_cols if col in athlete_medals.columns]
                
                if available_cols:
                    st.dataframe(
                        athlete_medals[available_cols].sort_values('medal_type', ascending=False),
                        use_container_width=True,
                        hide_index=True
                    )
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

if not filtered_athletes.empty:
    # Essayer de calculer l'âge à partir de la date de naissance
    if 'birth_date' in filtered_athletes.columns:
        try:
            # Convertir la date de naissance
            filtered_athletes['birth_date_parsed'] = pd.to_datetime(filtered_athletes['birth_date'], errors='coerce')
            current_year = 2024  # Année des Jeux Olympiques
            filtered_athletes['age'] = current_year - filtered_athletes['birth_date_parsed'].dt.year
            
            # Nettoyer les âges invalides
            filtered_athletes = filtered_athletes[filtered_athletes['age'].between(10, 60)]
            
            if not filtered_athletes.empty and filtered_athletes['age'].notna().sum() > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Box plot par genre
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
                        # Histogramme simple
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
                    # Statistiques d'âge
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
                    
                    # Distribution par groupe d'âge
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

if not filtered_athletes.empty and 'gender' in filtered_athletes.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution globale
        gender_counts = filtered_athletes['gender'].value_counts()
        
        # Normaliser les labels
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
        # Distribution par pays (Top 10)
        if country_col in filtered_athletes.columns:
            # Préparer les données pour le top 10 des pays
            top_countries = filtered_athletes[country_col].value_counts().head(10).index.tolist()
            country_gender_data = filtered_athletes[filtered_athletes[country_col].isin(top_countries)]
            
            if not country_gender_data.empty:
                # Grouper par pays et genre
                gender_by_country = country_gender_data.groupby([country_col, 'gender']).size().reset_index(name='count')
                
                # Normaliser les labels de genre
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
    # Préparer les données pour les médailles
    # Grouper par athlète et compter les médailles
    medal_summary = medallists_data.groupby('name').apply(lambda x: pd.Series({
        'Gold': (x['medal_type'] == 'Gold').sum(),
        'Silver': (x['medal_type'] == 'Silver').sum(),
        'Bronze': (x['medal_type'] == 'Bronze').sum(),
        'Total': len(x)
    })).reset_index()
    
    # Filtrer par pays si sélectionné
    if selected_countries and 'country_long' in medallists_data.columns:
        # Obtenir les athlètes du pays sélectionné
        country_athletes = medallists_data[medallists_data['country_long'].isin(selected_countries)]['name'].unique()
        medal_summary = medal_summary[medal_summary['name'].isin(country_athletes)]
    
    # Prendre les 10 meilleurs athlètes
    top_athletes = medal_summary.nlargest(10, 'Total')
    
    if not top_athletes.empty:
        # Créer le graphique
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
        
        # Tableau détaillé
        st.markdown("### 📋 Top Athletes Details")
        
        # Ajouter le pays si disponible
        display_data = top_athletes.copy()
        
        # Essayer d'ajouter le pays
        if 'country_long' in medallists_data.columns:
            country_map = medallists_data.groupby('name')['country_long'].first()
            display_data['Country'] = display_data['name'].map(country_map).fillna('Unknown')
            display_columns = ['name', 'Country', 'Gold', 'Silver', 'Bronze', 'Total']
        else:
            display_columns = ['name', 'Gold', 'Silver', 'Bronze', 'Total']
        
        display_data = display_data[display_columns]
        display_data.columns = ['Athlete', 'Country', '🥇 Gold', '🥈 Silver', '🥉 Bronze', 'Total Medals'] if 'Country' in display_columns else ['Athlete', '🥇 Gold', '🥈 Silver', '🥉 Bronze', 'Total Medals']
        
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