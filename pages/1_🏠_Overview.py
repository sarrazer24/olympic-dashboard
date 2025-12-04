import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Import styling
from app import get_theme_css, render_sidebar, render_theme_toggle, filter_medals_data, filter_athletes_data, filter_events_data

# Page configuration
st.set_page_config(
    page_title="Overview - Olympic Dashboard",
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
selected_countries, selected_sports, selected_continent, medal_filters = render_sidebar(active_page="overview", data=data)
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
            <h1 class="main-header">🏠 Overview</h1>
            <p class="sub-header">High-level summary and key performance indicators</p>
            <div class="olympic-chip">Command Center • At-a-Glance Summary</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">📊 Key Performance Indicators <span title='These metrics update with sidebar filters' style='cursor:help;'>ℹ️</span></h2>
</div>
""", unsafe_allow_html=True)

# Get data
athletes_data = data.get('athletes', pd.DataFrame())
nocs_data = data.get('nocs', pd.DataFrame())
events_data = data.get('events', pd.DataFrame())
medals_total_data = data.get('medals_total', pd.DataFrame())

# Apply filters using imported functions
filtered_athletes = filter_athletes_data(
    athletes_data,
    selected_countries,
    selected_sports,
    selected_continent
)

filtered_nocs = nocs_data.copy()
if not filtered_nocs.empty and selected_countries:
    if 'country' in filtered_nocs.columns:
        filtered_nocs = filtered_nocs[filtered_nocs['country'].isin(selected_countries)]

filtered_events = filter_events_data(
    events_data,
    selected_sports,
    selected_countries
)

# Convert medal_filters dict to list for compatibility
medal_filter_list = []
if isinstance(medal_filters, dict):
    if medal_filters.get('gold', True):
        medal_filter_list.append('Gold')
    if medal_filters.get('silver', True):
        medal_filter_list.append('Silver')
    if medal_filters.get('bronze', True):
        medal_filter_list.append('Bronze')
else:
    medal_filter_list = medal_filters

filtered_medals, medal_cols = filter_medals_data(
    medals_total_data,
    medal_filter_list,
    selected_countries,
    selected_continent
)

# Calculate KPIs
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_athletes = len(filtered_athletes)
    st.metric(
        "🏃 Total Athletes",
        f"{total_athletes:,}",
        delta=None,
        help="All athletes participating in Paris 2024"
    )

with col2:
    total_countries = len(filtered_nocs)
    st.metric(
        "🌍 Total Countries",
        f"{total_countries:,}",
        delta=None,
        help="National Olympic Committees represented"
    )

with col3:
    total_sports = filtered_events['sport'].nunique() if 'sport' in filtered_events.columns and not filtered_events.empty else 0
    st.metric(
        "⚽ Total Sports",
        f"{total_sports:,}",
        delta=None,
        help="Different sports in the Games"
    )

with col4:
    total_medals_awarded = 0
    if not filtered_medals.empty and medal_cols:
        total_medals_awarded = filtered_medals[medal_cols].sum().sum()
    st.metric(
        "🏅 Total Medals Awarded",
        f"{int(total_medals_awarded):,}",
        delta=None,
        help="Gold, Silver, and Bronze medals combined"
    )

with col5:
    total_events = len(filtered_events)
    st.metric(
        "🎯 Number of Events",
        f"{total_events:,}",
        delta=None,
        help="Competitive events held"
    )

st.markdown("---")

# Medal distribution
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">🏆 Global Medal Distribution <span title='Pie/Donut chart of medals' style='cursor:help;'>ℹ️</span></h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1.5])

with col1:
    # Pie/Donut chart of medal types
    if not filtered_medals.empty and medal_cols:
        # Calculate medal totals
        gold_total = silver_total = bronze_total = 0
        
        for col in medal_cols:
            col_lower = col.lower()
            if 'gold' in col_lower:
                gold_total += filtered_medals[col].sum()
            elif 'silver' in col_lower:
                silver_total += filtered_medals[col].sum()
            elif 'bronze' in col_lower:
                bronze_total += filtered_medals[col].sum()
        
        # Create the chart
        fig = go.Figure(data=[go.Pie(
            labels=['🥇 Gold', '🥈 Silver', '🥉 Bronze'],
            values=[gold_total, silver_total, bronze_total],
            hole=0.4,
            marker=dict(colors=['#FFD700', '#C0C0C0', '#CD7F32']),
            textinfo='label+percent+value',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title_text="<b>Medal Type Distribution (Donut Chart)</b>",
            height=400,
            font=dict(size=12),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, l=0, r=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No medal data available with current filters")

with col2:
    # Stats breakdown
    st.markdown("""
    <div style="padding: 20px; background: linear-gradient(135deg, rgba(255,215,0,0.1) 0%, rgba(205,127,50,0.1) 100%); 
                border-radius: 10px; border-left: 4px solid #FFD700;">
        <h4 style="margin-top: 0;">Medal Statistics</h4>
    """, unsafe_allow_html=True)
    
    if not filtered_medals.empty and medal_cols:
        gold_total = silver_total = bronze_total = 0
        
        for col in medal_cols:
            col_lower = col.lower()
            if 'gold' in col_lower:
                gold_total += int(filtered_medals[col].sum())
            elif 'silver' in col_lower:
                silver_total += int(filtered_medals[col].sum())
            elif 'bronze' in col_lower:
                bronze_total += int(filtered_medals[col].sum())
        
        total_all = gold_total + silver_total + bronze_total
        
        if total_all > 0:
            st.write(f"**🥇 Gold Medals:** {gold_total:,} ({100*gold_total/total_all:.1f}%)")
            st.write(f"**🥈 Silver Medals:** {silver_total:,} ({100*silver_total/total_all:.1f}%)")
            st.write(f"**🥉 Bronze Medals:** {bronze_total:,} ({100*bronze_total/total_all:.1f}%)")
            st.write(f"**📊 Total Medals:** {total_all:,}")
        else:
            st.write("No medals with current filters")
    else:
        st.write("No medal data available")
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# Top 10 Medal Standings
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">🏆 Top 10 Medal Standings <span title='Bar chart of top countries' style='cursor:help;'>ℹ️</span></h2>
</div>
""", unsafe_allow_html=True)

if not filtered_medals.empty and medal_cols:
    # Calculate total medals per country
    filtered_medals_copy = filtered_medals.copy()
    
    # Determine country column
    country_col = 'country_long' if 'country_long' in filtered_medals_copy.columns else 'country'
    if country_col not in filtered_medals_copy.columns and len(filtered_medals_copy.columns) > 0:
        country_col = filtered_medals_copy.columns[0]
    
    # Calculate total medals for each country
    filtered_medals_copy['total_medals'] = filtered_medals_copy[medal_cols].sum(axis=1)
    
    # Get top 10 countries
    top_10 = filtered_medals_copy.nlargest(10, 'total_medals')
    
    # Prepare data for visualization
    plot_data = []
    for _, row in top_10.iterrows():
        country = row[country_col]
        gold = silver = bronze = 0
        
        for col in medal_cols:
            col_lower = col.lower()
            if 'gold' in col_lower:
                gold += row[col]
            elif 'silver' in col_lower:
                silver += row[col]
            elif 'bronze' in col_lower:
                bronze += row[col]
        
        plot_data.append({
            'Country': country,
            '🥇 Gold': gold,
            '🥈 Silver': silver,
            '🥉 Bronze': bronze,
            'Total': gold + silver + bronze
        })
    
    if plot_data:
        plot_df = pd.DataFrame(plot_data)
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=plot_df['Country'],
            x=plot_df['🥇 Gold'],
            name='🥇 Gold',
            marker=dict(color='#FFD700'),
            hovertemplate='<b>%{y}</b><br>Gold: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            y=plot_df['Country'],
            x=plot_df['🥈 Silver'],
            name='🥈 Silver',
            marker=dict(color='#C0C0C0'),
            hovertemplate='<b>%{y}</b><br>Silver: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            y=plot_df['Country'],
            x=plot_df['🥉 Bronze'],
            name='🥉 Bronze',
            marker=dict(color='#CD7F32'),
            hovertemplate='<b>%{y}</b><br>Bronze: %{x}<extra></extra>'
        ))
        
        fig.update_layout(
            barmode='stack',
            title_text="<b>Top 10 Countries by Medal Count</b>",
            xaxis_title="Number of Medals",
            yaxis_title="Country",
            height=500,
            hovermode='y unified',
            margin=dict(l=0, r=0, t=40, b=0),
            font=dict(size=11),
            showlegend=True,
            legend=dict(x=0.5, y=-0.15, orientation="h"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_yaxes(autorange="reversed")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.markdown("### 📋 Detailed Medal Standings")
        st.dataframe(plot_df, use_container_width=True, hide_index=True)
    else:
        st.info("No medal data to display with current filters")
else:
    st.info("No medal data available for visualization")

# Additional KPIs Section
st.markdown("---")
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">📈 Additional Insights</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Athletes per country (top 10)
    if not filtered_athletes.empty:
        st.markdown("### 🏃 Athletes Distribution")
        if 'country_long' in filtered_athletes.columns:
            athletes_by_country = filtered_athletes['country_long'].value_counts().head(10)
            
            fig = px.bar(
                x=athletes_by_country.values,
                y=athletes_by_country.index,
                orientation='h',
                title='<b>Top 10 Countries by Athlete Count</b>',
                labels={'x': 'Number of Athletes', 'y': 'Country'},
                color=athletes_by_country.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=40, l=0, r=0, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Country data not available for athletes")

with col2:
    # Events per sport (top 10)
    if not filtered_events.empty and 'sport' in filtered_events.columns:
        st.markdown("### ⚽ Sports Event Distribution")
        events_by_sport = filtered_events['sport'].value_counts().head(10)
        
        fig = px.pie(
            values=events_by_sport.values,
            names=events_by_sport.index,
            title='<b>Events Distribution by Sport (Top 10)</b>',
            hole=0.3
        )
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, l=0, r=0, b=0),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sport data not available for events")

# Summary Statistics
st.markdown("---")
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">📋 Summary Statistics</h2>
</div>
""", unsafe_allow_html=True)

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.markdown("### 🏅 Medal Summary")
    if not filtered_medals.empty and medal_cols:
        # Calculate totals
        medal_totals = filtered_medals[medal_cols].sum()
        total_medals = medal_totals.sum()
        
        st.markdown(f"""
        <div style="padding: 15px; background: rgba(0,133,202,0.05); border-radius: 10px; margin-bottom: 10px;">
            <strong>Total Medals:</strong> {int(total_medals):,}
        </div>
        """, unsafe_allow_html=True)
        
        gold_total = medal_totals[[col for col in medal_totals.index if 'gold' in col.lower()]].sum()
        silver_total = medal_totals[[col for col in medal_totals.index if 'silver' in col.lower()]].sum()
        bronze_total = medal_totals[[col for col in medal_totals.index if 'bronze' in col.lower()]].sum()
        
        st.markdown(f"""
        <div style="padding: 15px; background: rgba(255,215,0,0.05); border-radius: 10px; margin-bottom: 10px;">
            <strong>🥇 Gold:</strong> {int(gold_total):,}
        </div>
        <div style="padding: 15px; background: rgba(192,192,192,0.05); border-radius: 10px; margin-bottom: 10px;">
            <strong>🥈 Silver:</strong> {int(silver_total):,}
        </div>
        <div style="padding: 15px; background: rgba(205,127,50,0.05); border-radius: 10px;">
            <strong>🥉 Bronze:</strong> {int(bronze_total):,}
        </div>
        """, unsafe_allow_html=True)

with summary_col2:
    st.markdown("### 🌍 Geographic Coverage")
    if not filtered_athletes.empty:
        unique_countries = filtered_athletes['country_long'].nunique() if 'country_long' in filtered_athletes.columns else 0
        unique_sports = filtered_athletes['sport'].nunique() if 'sport' in filtered_athletes.columns else 0
        
        st.markdown(f"""
        <div style="padding: 15px; background: rgba(0,159,61,0.05); border-radius: 10px; margin-bottom: 10px;">
            <strong>Countries Represented:</strong> {unique_countries:,}
        </div>
        <div style="padding: 15px; background: rgba(238,51,78,0.05); border-radius: 10px; margin-bottom: 10px;">
            <strong>Sports Represented:</strong> {unique_sports:,}
        </div>
        """, unsafe_allow_html=True)
    
    if not filtered_medals.empty and 'continent' in filtered_medals.columns:
        continent_count = filtered_medals['continent'].nunique()
        st.markdown(f"""
        <div style="padding: 15px; background: rgba(255,107,53,0.05); border-radius: 10px;">
            <strong>Continents Represented:</strong> {continent_count:,}
        </div>
        """, unsafe_allow_html=True)

with summary_col3:
    st.markdown("### 📊 Performance Metrics")
    if not filtered_medals.empty and medal_cols and not filtered_athletes.empty:
        # Calculate medals per athlete
        total_athletes_count = len(filtered_athletes)
        total_medals_count = filtered_medals[medal_cols].sum().sum()
        
        if total_athletes_count > 0:
            medals_per_athlete = total_medals_count / total_athletes_count
            
            st.markdown(f"""
            <div style="padding: 15px; background: rgba(155,81,224,0.05); border-radius: 10px; margin-bottom: 10px;">
                <strong>Medals per Athlete:</strong> {medals_per_athlete:.2f}
            </div>
            """, unsafe_allow_html=True)
    
    if not filtered_events.empty:
        events_count = len(filtered_events)
        sports_count = filtered_events['sport'].nunique() if 'sport' in filtered_events.columns else 0
        
        if sports_count > 0:
            events_per_sport = events_count / sports_count
            
            st.markdown(f"""
            <div style="padding: 15px; background: rgba(53,162,235,0.05); border-radius: 10px; margin-bottom: 10px;">
                <strong>Events per Sport:</strong> {events_per_sport:.1f}
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #888; font-size: 0.85rem; margin-top: 2rem;">
    <strong>🏅 Paris 2024 Olympic Games</strong><br>
    Overview Dashboard • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)