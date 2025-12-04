import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Import styling from your main app
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
if "animate_header" not in st.session_state:
    st.session_state["animate_header"] = True
animate_header = st.session_state.get("animate_header", True)
st.markdown(get_theme_css(current_theme, animated=animate_header), unsafe_allow_html=True)

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
            <h1 class="main-header">🏟️ Sports & Events</h1>
            <p class="sub-header">Comprehensive overview of Olympic sports, events, and venues</p>
            <div class="olympic-chip">Competition Details & Schedule</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Get data
events_data = data.get('events', pd.DataFrame())
venues_data = data.get('venues', pd.DataFrame())
medals_total_data = data.get('medals_total', pd.DataFrame())
schedule_data = data.get('schedules', pd.DataFrame())

# ==================== OVERVIEW SECTION ====================
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">📊 Competition Overview</h2>
</div>
""", unsafe_allow_html=True)

if events_data.empty:
    st.warning("No events data available")
else:
    # Apply filters to events data
    filtered_events = events_data.copy()
    filtered_medals = medals_total_data.copy() if not medals_total_data.empty else pd.DataFrame()
    
    # Find sport column for filtering
    sport_col = None
    for col in filtered_events.columns:
        if col.lower() == 'sport':
            sport_col = col
            break
    
    # Apply sport filter from sidebar
    if selected_sports and sport_col:
        filtered_events = filtered_events[filtered_events[sport_col].isin(selected_sports)]
    
    # Apply country filter from sidebar
    if selected_countries:
        # Try to find country column
        country_col = None
        for col in filtered_events.columns:
            if 'country' in col.lower():
                country_col = col
                break
        
        if country_col and country_col in filtered_events.columns:
            filtered_events = filtered_events[filtered_events[country_col].isin(selected_countries)]
    
    # Apply continent filter to medals if available
    if selected_continent and not filtered_medals.empty and 'continent' in filtered_medals.columns:
        filtered_medals = filtered_medals[filtered_medals['continent'].isin(selected_continent)]
    
    # Apply country filter to medals
    if selected_countries and not filtered_medals.empty:
        country_col = 'country_long' if 'country_long' in filtered_medals.columns else 'country'
        if country_col in filtered_medals.columns:
            filtered_medals = filtered_medals[filtered_medals[country_col].isin(selected_countries)]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if sport_col:
            sports_count = filtered_events[sport_col].nunique()
        else:
            sports_count = 0
        st.metric("⚽ Total Sports", f"{sports_count:,}")
    with col2:
        events_count = len(filtered_events)
        st.metric("🎯 Total Events", f"{events_count:,}")
    with col3:
        if not venues_data.empty:
            venues_count = len(venues_data)
            st.metric("🏟️ Total Venues", f"{venues_count:,}")
        else:
            st.metric("🏟️ Total Venues", "N/A")
    with col4:
        if not schedule_data.empty and 'start_date' in schedule_data.columns:
            days_count = pd.to_datetime(schedule_data['start_date']).dt.date.nunique()
            st.metric("📅 Competition Days", f"{days_count}")
        else:
            st.metric("📅 Competition Days", "N/A")

    st.markdown("---")

    # ==================== SPORTS ANALYSIS SECTION ====================
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">⚽ Sports Analysis</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📈 Events Distribution by Sport")
        if sport_col and len(filtered_events) > 0:
            sport_counts = filtered_events[sport_col].value_counts().head(15)
            fig = px.bar(
                x=sport_counts.values,
                y=sport_counts.index,
                orientation='h',
                title='<b>Number of Events by Sport (Top 15)</b>',
                color=sport_counts.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                height=500,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Number of Events",
                yaxis_title="Sport",
                margin=dict(t=40, l=0, r=0, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sports data available with current filters")

    with col2:
        st.markdown("### 🏆 Medal Distribution by Country")
        if not filtered_medals.empty:
            # Get medal columns based on your data structure
            medal_cols = ['Gold Medal', 'Silver Medal', 'Bronze Medal', 'gold', 'silver', 'bronze']
            available_medal_cols = [col for col in medal_cols if col in filtered_medals.columns]
            
            # Apply medal type filters from sidebar
            if medal_filters:
                filtered_medal_cols = []
                for col in available_medal_cols:
                    if 'gold' in col.lower() and medal_filters.get('gold', True):
                        filtered_medal_cols.append(col)
                    elif 'silver' in col.lower() and medal_filters.get('silver', True):
                        filtered_medal_cols.append(col)
                    elif 'bronze' in col.lower() and medal_filters.get('bronze', True):
                        filtered_medal_cols.append(col)
                available_medal_cols = filtered_medal_cols

            if available_medal_cols:
                # Determine country column name
                country_col = 'country_long' if 'country_long' in filtered_medals.columns else 'country'
                if country_col not in filtered_medals.columns and len(filtered_medals.columns) > 0:
                    country_col = filtered_medals.columns[0]
                
                # Group medals by country
                country_medals = filtered_medals.groupby(country_col)[available_medal_cols].sum().sum(axis=1).sort_values(ascending=False).head(10)
                
                if len(country_medals) > 0:
                    fig = px.pie(
                        values=country_medals.values,
                        names=country_medals.index,
                        title='<b>Medal Distribution by Country (Top 10)</b>',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=True,
                        margin=dict(t=40, l=0, r=0, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No medal data available for selected filters")
            else:
                st.info("Medal data not available")
        else:
            st.info("No medal data available")

    # ==================== EVENTS SCHEDULE SECTION ====================
    st.markdown("---")
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">📅 Event Schedule & Timeline</h2>
    </div>
    """, unsafe_allow_html=True)

    if not schedule_data.empty:
        # Apply filters to schedule data from sidebar
        filtered_schedule = schedule_data.copy()
        
        # Apply sport filter from sidebar to schedule
        if selected_sports and 'sport' in filtered_schedule.columns:
            filtered_schedule = filtered_schedule[filtered_schedule['sport'].isin(selected_sports)]
        
        # Only keep venue and date filters (removed sport filter since it's in sidebar)
        col1, col2 = st.columns(2)

        with col1:
            available_venues = sorted([v for v in filtered_schedule['venue'].dropna().unique().tolist() if isinstance(v, str)]) if 'venue' in filtered_schedule.columns else []
            selected_schedule_venue = st.selectbox(
                "🏟️ Filter by Venue",
                ["All Venues"] + available_venues,
                key="schedule_venue_filter"
            )

        with col2:
            if 'start_date' in filtered_schedule.columns:
                dates = pd.to_datetime(filtered_schedule['start_date']).dt.date.unique()
                selected_date = st.selectbox(
                    "📆 Filter by Date",
                    ["All Dates"] + sorted(dates),
                    key="schedule_date_filter"
                )
            else:
                selected_date = "All Dates"

        # Apply venue filter
        if selected_schedule_venue != "All Venues":
            filtered_schedule = filtered_schedule[filtered_schedule['venue'] == selected_schedule_venue]

        # Apply date filter
        if selected_date != "All Dates":
            filtered_schedule = filtered_schedule[pd.to_datetime(filtered_schedule['start_date']).dt.date == selected_date]

        # View selector
        st.markdown("### 📊 Visualization Options")
        view_option = st.radio(
            "Choose view:",
            ["Timeline", "Calendar Heatmap"],
            horizontal=True,
            key="schedule_view_option"
        )

        # Timeline visualization
        if view_option == "Timeline":
            if not filtered_schedule.empty and 'start_date' in filtered_schedule.columns and 'end_date' in filtered_schedule.columns:
                st.markdown("### ⏱️ Competition Timeline")

                # Create timeline chart
                # Determine y-axis column
                y_col = 'event' if 'event' in filtered_schedule.columns else 'sport'
                color_col = 'venue' if 'venue' in filtered_schedule.columns else 'sport'
                
                fig = px.timeline(
                    filtered_schedule,
                    x_start='start_date',
                    x_end='end_date',
                    y=y_col,
                    color=color_col,
                    title=f'Event Schedule ({len(filtered_schedule)} events)',
                    height=600
                )
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=40, l=0, r=0, b=0),
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)

                # Schedule summary
                st.markdown("### 📋 Schedule Summary")
                summary_cols = ['sport', 'event', 'venue', 'start_date', 'end_date']
                available_summary_cols = [col for col in summary_cols if col in filtered_schedule.columns]

                if available_summary_cols:
                    display_df = filtered_schedule[available_summary_cols].copy()
                    if 'start_date' in display_df.columns:
                        display_df['start_date'] = pd.to_datetime(display_df['start_date']).dt.strftime('%Y-%m-%d %H:%M')
                    if 'end_date' in display_df.columns:
                        display_df['end_date'] = pd.to_datetime(display_df['end_date']).dt.strftime('%Y-%m-%d %H:%M')

                    st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No schedule data available for the selected filters")
        
        elif view_option == "Calendar Heatmap":
            st.markdown("### 📅 Calendar Heatmap")
            if not filtered_schedule.empty and 'start_date' in filtered_schedule.columns:
                # Create heatmap data
                filtered_schedule['date'] = pd.to_datetime(filtered_schedule['start_date']).dt.date
                heatmap_data = filtered_schedule.groupby('date').size().reset_index(name='count')
                heatmap_data['day_of_week'] = pd.to_datetime(heatmap_data['date']).dt.day_name()
                heatmap_data['week'] = pd.to_datetime(heatmap_data['date']).dt.isocalendar().week
                
                fig = px.density_heatmap(
                    heatmap_data,
                    x='day_of_week',
                    y='week',
                    z='count',
                    title='Event Distribution by Day of Week and Week',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Day of Week",
                    yaxis_title="Week Number",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No schedule data available for calendar heatmap")
    else:
        st.info("Schedule data not available")

# ==================== VENUES SECTION ====================
if not venues_data.empty:
    st.markdown("---")
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">🏟️ Olympic Venues</h2>
    </div>
    """, unsafe_allow_html=True)

   

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🏟️ Total Venues", len(venues_data))

    with col2:
        # Try to find sports column (case-insensitive)
        sports_col = None
        for col in venues_data.columns:
            if 'sport' in col.lower():
                sports_col = col
                break
        
        if sports_col:
            # Handle different formats: comma-separated, list, or single sport
            if venues_data[sports_col].dtype == 'object':
                # Split comma-separated sports
                sports_list = venues_data[sports_col].dropna().str.split(',').explode().str.strip()
                total_sports_at_venues = sports_list.nunique()
                st.metric("⚽ Sports Hosted", total_sports_at_venues)
            else:
                st.metric("⚽ Sports Hosted", venues_data[sports_col].nunique())
        else:
            st.metric("⚽ Sports Hosted", "N/A")

    with col3:
        # Try to find capacity column (case-insensitive)
        capacity_col = None
        for col in venues_data.columns:
            if 'capacity' in col.lower():
                capacity_col = col
                break
        
        if capacity_col:
            try:
                # Convert to numeric, handling any errors
                capacities = pd.to_numeric(venues_data[capacity_col], errors='coerce')
                avg_capacity = capacities.mean()
                if pd.notna(avg_capacity):
                    st.metric("👥 Avg Capacity", f"{avg_capacity:,.0f}")
                else:
                    st.metric("👥 Avg Capacity", "N/A")
            except:
                st.metric("👥 Avg Capacity", "N/A")
        else:
            st.metric("👥 Avg Capacity", "N/A")

    # Venues visualization
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 📍 Venue Details")
        
        # Find name column (case-insensitive)
        name_col = None
        for col in venues_data.columns:
            if 'name' in col.lower() or 'venue' in col.lower():
                name_col = col
                break
        
        # Create display columns list
        display_cols = []
        if name_col:
            display_cols.append(name_col)
        
        # Add sports column if found
        if sports_col:
            display_cols.append(sports_col)
        
        # Add capacity column if found
        if capacity_col:
            display_cols.append(capacity_col)
        
        # Add other columns if we don't have enough
        if len(display_cols) < 3:
            for col in venues_data.columns:
                if col not in display_cols and len(display_cols) < 3:
                    display_cols.append(col)
        
        if display_cols:
            # Clean up the display
            display_df = venues_data[display_cols].copy()
            
            # Truncate long text for display
            for col in display_df.columns:
                if display_df[col].dtype == 'object':
                    display_df[col] = display_df[col].apply(lambda x: str(x)[:50] + '...' if len(str(x)) > 50 else str(x))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
        else:
            st.dataframe(venues_data.head(10), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("### 🗺️ Sports Distribution by Venue")
        
        if name_col and sports_col:
            try:
                # Create a copy for manipulation
                venues_analysis = venues_data[[name_col, sports_col]].copy()
                venues_analysis = venues_analysis.dropna()
                
                # Clean sports data
                def clean_sports(sport_str):
                    if pd.isna(sport_str):
                        return []
                    if isinstance(sport_str, str):
                        # Split by comma, semicolon, or other delimiters
                        sports_list = []
                        for delimiter in [',', ';', '|', '/', '&']:
                            if delimiter in sport_str:
                                sports_list = [s.strip() for s in sport_str.split(delimiter) if s.strip()]
                                break
                        if not sports_list:
                            sports_list = [sport_str.strip()]
                        return sports_list
                    elif isinstance(sport_str, list):
                        return sport_str
                    else:
                        return [str(sport_str)]
                
                # Apply cleaning function
                venues_analysis['sports_list'] = venues_analysis[sports_col].apply(clean_sports)
                venues_analysis['sports_count'] = venues_analysis['sports_list'].apply(len)
                
                # Filter out venues with 0 sports
                venues_analysis = venues_analysis[venues_analysis['sports_count'] > 0]
                
                if len(venues_analysis) > 0:
                    # Sort by sports count and get top 15
                    venue_sports = venues_analysis.sort_values('sports_count', ascending=False).head(15)
                    
                    fig = px.bar(
                        venue_sports,
                        x='sports_count',
                        y=name_col,
                        orientation='h',
                        title='<b>Sports per Venue (Top 15)</b>',
                        color='sports_count',
                        color_continuous_scale='Blues',
                        hover_data={name_col: True, 'sports_count': True, sports_col: True}
                    )
                    fig.update_layout(
                        height=500,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="Number of Sports",
                        yaxis_title="Venue",
                        margin=dict(t=40, l=0, r=0, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Also show a summary
                    st.markdown("##### 📊 Sports Distribution Summary")
                    st.write(f"**Total venues with sports data:** {len(venues_analysis)}")
                    st.write(f"**Average sports per venue:** {venues_analysis['sports_count'].mean():.1f}")
                    st.write(f"**Max sports at a venue:** {venues_analysis['sports_count'].max()}")
                else:
                    st.info("No venue sports data available for visualization")
                    
            except Exception as e:
                st.error(f"Error creating sports distribution chart: {e}")
                st.info("Trying alternative visualization...")
                
                # Try simple count of venues by first sport
                try:
                    venues_analysis = venues_data[[name_col, sports_col]].copy()
                    venues_analysis = venues_analysis.dropna()
                    
                    # Extract first sport from each venue
                    venues_analysis['first_sport'] = venues_analysis[sports_col].apply(
                        lambda x: str(x).split(',')[0].strip() if isinstance(x, str) else str(x)
                    )
                    
                    sport_counts = venues_analysis['first_sport'].value_counts().head(10)
                    
                    fig = px.bar(
                        x=sport_counts.values,
                        y=sport_counts.index,
                        orientation='h',
                        title='<b>Top 10 Sports by Venue Count</b>',
                        color=sport_counts.values,
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(
                        height=400,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="Number of Venues",
                        yaxis_title="Sport",
                        margin=dict(t=40, l=0, r=0, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("Could not create sports distribution visualization")
        else:
            st.info("Venue name or sports column not found in data")
    # ==================== DETAILED EVENTS TABLE ====================
    st.markdown("---")
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">📋 Complete Events Directory</h2>
    </div>
    """, unsafe_allow_html=True)

    # Events table with search and filters
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### 🔍 Search Events")
        
        # Search by event name (kept for convenience within the page)
        if 'event' in filtered_events.columns:
            event_search = st.text_input("Search Events", placeholder="Type to search events...", key="event_search")
        else:
            event_search = ""

    with col2:
        # Apply search filter to events data for table
        table_events = filtered_events.copy()

        # Apply search filter
        if event_search and 'event' in table_events.columns:
            table_events = table_events[table_events['event'].str.contains(event_search, case=False, na=False)]

        st.markdown(f"### 📊 Events Table ({len(table_events)} events)")

        # Display events table
        if sport_col:
            display_cols = [sport_col, 'event', 'discipline', 'gender'] if 'event' in table_events.columns else [sport_col]
        else:
            display_cols = list(table_events.columns)[:4]
        
        available_cols = [col for col in display_cols if col in table_events.columns]

        if available_cols:
            st.dataframe(table_events[available_cols], use_container_width=True, hide_index=True)
        else:
            st.dataframe(table_events.head(50), use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #888; font-size: 0.85rem; margin-top: 2rem;">
    <strong>🏅 Paris 2024 Olympic Games</strong><br>
    Sports & Events Dashboard • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)