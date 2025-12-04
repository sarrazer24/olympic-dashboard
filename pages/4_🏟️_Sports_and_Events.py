import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Import styling
from app import get_theme_css, render_sidebar, render_theme_toggle

# Page configuration
st.set_page_config(
    page_title="Sports & Events - Olympic Dashboard",
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
data = st.session_state.get("data", {})
selected_countries, selected_sports, selected_continent, medal_filters = render_sidebar(active_page="sports", data=data)
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
            <h1 class="main-header">🏟️ Sports & Events</h1>
            <p class="sub-header">All sports, events, and competition details</p>
            <div class="olympic-chip">Sports Overview &nbsp;•&nbsp; Event Schedule</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">⚽ Sports Overview <span title='Summary of sports and events' style='cursor:help;'>ℹ️</span></h2>
</div>
""", unsafe_allow_html=True)

# Get events data
events_data = data.get('events', pd.DataFrame())
venues_data = data.get('venues', pd.DataFrame())

if events_data.empty:
    st.warning("No events data available")
else:
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        sports_count = events_data['sport'].nunique() if 'sport' in events_data.columns else 0
        st.metric("⚽ Total Sports", f"{sports_count:,}")
    with col2:
        st.metric("🎯 Total Events", f"{len(events_data):,}")
    with col3:
        if 'discipline' in events_data.columns:
            disciplines_count = events_data['discipline'].nunique()
            st.metric("🔬 Total Disciplines", f"{disciplines_count:,}")
        else:
            st.metric("🔬 Total Disciplines", "N/A")
    st.markdown("---")

    # Sports distribution
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ⚽ Events by Sport")
        if 'sport' in events_data.columns:
            sport_counts = events_data['sport'].value_counts().head(15)
            fig = px.bar(
                x=sport_counts.values,
                y=sport_counts.index,
                orientation='h',
                title='<b>Events by Sport (Top 15)</b>',
                color=sport_counts.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=500, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("### 📋 All Sports List")
        if 'sport' in events_data.columns:
            sports = sorted(events_data['sport'].unique())
            sport_list = "\n".join([f"• {i+1}. {sport}" for i, sport in enumerate(sports)])
            st.markdown(sport_list)
    st.markdown("---")

    # --- Treemap for Medal Count by Sport ---
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="font-weight: 700; color:#FFD700;">🌳 Medal Count by Sport (Treemap) <span title='Treemap of medals by sport' style='cursor:help;'>ℹ️</span></h3>
        <p style='color:#555;'>Visualize the total medals awarded for each sport. Explore which sports dominated the Games!</p>
    </div>
    """, unsafe_allow_html=True)
    medals_total_data = data.get('medals_total', pd.DataFrame())
    if not medals_total_data.empty and 'sport' in events_data.columns:
        # Merge medals with events to get sport info
        if 'country_long' in medals_total_data.columns and 'country_long' in events_data.columns:
            merged = pd.merge(medals_total_data, events_data, on='country_long', how='left')
        else:
            merged = events_data.copy()
        # Group by sport and sum medals
        medal_cols = ['Gold Medal', 'Silver Medal', 'Bronze Medal']
        medal_cols = [col for col in medal_cols if col in merged.columns]
        if medal_cols:
            merged['Total_Medals'] = merged[medal_cols].sum(axis=1)
            sport_medals = merged.groupby('sport')['Total_Medals'].sum().reset_index()
            fig = px.treemap(
                sport_medals,
                path=['sport'],
                values='Total_Medals',
                color='Total_Medals',
                color_continuous_scale='RdYlGn',
                title='Medal Count by Sport (Treemap)'
            )
            fig.update_layout(margin=dict(t=40, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Medal columns not found for Treemap.")
    else:
        st.info("Medal or sport data not available for Treemap.")

    st.markdown("---")

    # Events detail table
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="font-weight: 700; color:#FFD700;">📅 Events Detail <span title='Table of events' style='cursor:help;'>ℹ️</span></h3>
    </div>
    """, unsafe_allow_html=True)
    display_cols = ['sport', 'event'] if 'event' in events_data.columns else ['sport']
    available_cols = [col for col in display_cols if col in events_data.columns]
    if available_cols:
        st.dataframe(events_data[available_cols].head(50), width='stretch', hide_index=True)
    else:
        st.dataframe(events_data.head(50), width='stretch', hide_index=True)

    # --- Gantt Chart for Event Schedule ---
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="font-weight: 700; color:#FFD700;">⏱️ Event Schedule (Gantt Chart) <span title='Gantt chart of event schedule' style='cursor:help;'>ℹ️</span></h3>
        <p style='color:#555;'>Visualize the schedule of events for a selected sport or venue. Explore the Olympic timeline!</p>
    </div>
    """, unsafe_allow_html=True)
    schedule_data = data.get('schedules', pd.DataFrame())
    if not schedule_data.empty and 'sport' in schedule_data.columns and 'start_date' in schedule_data.columns and 'end_date' in schedule_data.columns:
        # User selects sport or venue
        selected_sport = st.selectbox("Select Sport for Schedule", sorted(schedule_data['sport'].unique()))
        filtered_schedule = schedule_data[schedule_data['sport'] == selected_sport]
        if not filtered_schedule.empty:
            fig = px.timeline(
                filtered_schedule,
                x_start='start_date',
                x_end='end_date',
                y='event',
                color='venue' if 'venue' in filtered_schedule.columns else None,
                title=f'Olympic Event Schedule: {selected_sport}'
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(height=500, margin=dict(t=40, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No schedule data for selected sport.")
    else:
        st.info("Schedule data not available for Gantt chart.")

# Venues section
if not venues_data.empty:
    st.markdown("---")
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em;">🏟️ Olympic Venues</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🏟️ Total Venues", len(venues_data))
    
    with col2:
        if 'sports' in venues_data.columns:
            total_sports_at_venues = venues_data['sports'].nunique()
            st.metric("⚽ Sports at Venues", total_sports_at_venues)
    
    st.markdown("---")
    
    # Venues table
    st.markdown("### 📍 All Venues")
    display_cols = ['name', 'sports'] if 'name' in venues_data.columns else list(venues_data.columns)[:3]
    available_cols = [col for col in display_cols if col in venues_data.columns]
    
    if available_cols:
        st.dataframe(venues_data[available_cols], width='stretch', hide_index=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: right; color: #888; font-size: 0.8rem;">
    Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)
