import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Import styling
from app import get_theme_css, render_sidebar, render_theme_toggle

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

current_theme = st.session_state.get("theme", "light")
st.markdown(get_theme_css(current_theme), unsafe_allow_html=True)

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
st.markdown("""
    <div class="olympic-banner olympic-banner-animated">
        <div class="olympic-rings">
            <span class="ring ring-blue"></span>
            <span class="ring ring-yellow"></span>
            <span class="ring ring-black"></span>
            <span class="ring ring-green"></span>
            <span class="ring ring-red"></span>
        </div>
        <div class="olympic-banner-text">
            <h1 class="main-header" style="color:#0085CA;">🏠 Overview</h1>
            <p class="sub-header" style="font-size:1.2rem; color:#444;">High-level summary and key performance indicators</p>
            <div class="olympic-chip" style="background:#FFD700; color:#222; font-weight:600;">Command Center &nbsp;•&nbsp; At-a-Glance Summary</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">📊 Key Performance Indicators <span title='These metrics update with sidebar filters' style='cursor:help;'>ℹ️</span></h2>
</div>
""", unsafe_allow_html=True)

# Get filtered data
athletes_data = data.get('athletes', pd.DataFrame())
nocs_data = data.get('nocs', pd.DataFrame())
events_data = data.get('events', pd.DataFrame())
medals_total_data = data.get('medals_total', pd.DataFrame())

# Apply filters
filtered_medals = medals_total_data.copy()
if selected_countries:
    if 'country_long' in filtered_medals.columns:
        filtered_medals = filtered_medals[filtered_medals['country_long'].isin(selected_countries)]
if selected_continent:
    if 'continent' in filtered_medals.columns:
        filtered_medals = filtered_medals[filtered_medals['continent'].isin(selected_continent)]

# Calculate KPIs
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_athletes = len(athletes_data)
    st.metric(
        "🏃 Total Athletes",
        f"{total_athletes:,}",
        delta=None,
        help="All athletes participating in Paris 2024"
    )

with col2:
    total_countries = len(nocs_data)
    st.metric(
        "🌍 Total Countries",
        f"{total_countries:,}",
        delta=None,
        help="National Olympic Committees represented"
    )

with col3:
    total_sports = events_data['sport'].nunique() if 'sport' in events_data.columns else 0
    st.metric(
        "⚽ Total Sports",
        f"{total_sports:,}",
        delta=None,
        help="Different sports in the Games"
    )

with col4:
    if not filtered_medals.empty:
        medal_cols = ['Gold Medal', 'Silver Medal', 'Bronze Medal'] if 'Gold Medal' in filtered_medals.columns else ['gold', 'silver', 'bronze']
        medal_cols = [col for col in medal_cols if col in filtered_medals.columns]
        total_medals_awarded = filtered_medals[medal_cols].sum().sum() if medal_cols else 0
    else:
        total_medals_awarded = 0
    st.metric(
        "🏅 Total Medals Awarded",
        f"{int(total_medals_awarded):,}",
        delta=None,
        help="Gold, Silver, and Bronze medals combined"
    )

with col5:
    total_events = len(events_data)
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
    if not medals_total_data.empty:
        # Use correct column names
        gold_col = 'Gold Medal' if 'Gold Medal' in medals_total_data.columns else 'gold'
        silver_col = 'Silver Medal' if 'Silver Medal' in medals_total_data.columns else 'silver'
        bronze_col = 'Bronze Medal' if 'Bronze Medal' in medals_total_data.columns else 'bronze'
        
        gold_total = medals_total_data[gold_col].sum() if gold_col in medals_total_data.columns else 0
        silver_total = medals_total_data[silver_col].sum() if silver_col in medals_total_data.columns else 0
        bronze_total = medals_total_data[bronze_col].sum() if bronze_col in medals_total_data.columns else 0
        
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
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No medal data available")

with col2:
    # Stats breakdown
    st.markdown("""
    <div style="padding: 20px; background: linear-gradient(135deg, rgba(255,215,0,0.1) 0%, rgba(205,127,50,0.1) 100%); 
                border-radius: 10px; border-left: 4px solid #FFD700;">
        <h4 style="margin-top: 0;">Medal Statistics</h4>
    """, unsafe_allow_html=True)
    
    if not medals_total_data.empty:
        gold_col = 'Gold Medal' if 'Gold Medal' in medals_total_data.columns else 'gold'
        silver_col = 'Silver Medal' if 'Silver Medal' in medals_total_data.columns else 'silver'
        bronze_col = 'Bronze Medal' if 'Bronze Medal' in medals_total_data.columns else 'bronze'
        
        gold_total = int(medals_total_data[gold_col].sum()) if gold_col in medals_total_data.columns else 0
        silver_total = int(medals_total_data[silver_col].sum()) if silver_col in medals_total_data.columns else 0
        bronze_total = int(medals_total_data[bronze_col].sum()) if bronze_col in medals_total_data.columns else 0
        total_all = gold_total + silver_total + bronze_total
        
        if total_all > 0:
            st.write(f"**🥇 Gold Medals:** {gold_total:,} ({100*gold_total/total_all:.1f}%)")
            st.write(f"**🥈 Silver Medals:** {silver_total:,} ({100*silver_total/total_all:.1f}%)")
            st.write(f"**🥉 Bronze Medals:** {bronze_total:,} ({100*bronze_total/total_all:.1f}%)")
            st.write(f"**📊 Total Medals:** {total_all:,}")
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# Top 10 Medal Standings
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">🏆 Top 10 Medal Standings <span title='Bar chart of top countries' style='cursor:help;'>ℹ️</span></h2>
</div>
""", unsafe_allow_html=True)

if not medals_total_data.empty:
    # Sort by total medals
    total_col = 'Total' if 'Total' in medals_total_data.columns else 'total'
    if total_col not in medals_total_data.columns:
        st.warning("Total medal column not found in data")
    else:
        top_10 = medals_total_data.nlargest(10, total_col)
        
        # Determine column names
        country_col = 'country_long' if 'country_long' in top_10.columns else 'country'
        gold_col = 'Gold Medal' if 'Gold Medal' in top_10.columns else 'gold'
        silver_col = 'Silver Medal' if 'Silver Medal' in top_10.columns else 'silver'
        bronze_col = 'Bronze Medal' if 'Bronze Medal' in top_10.columns else 'bronze'
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=top_10[country_col],
            x=top_10[gold_col],
            name='🥇 Gold',
            marker=dict(color='#FFD700'),
            hovertemplate='<b>%{y}</b><br>Gold: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            y=top_10[country_col],
            x=top_10[silver_col],
            name='🥈 Silver',
            marker=dict(color='#C0C0C0'),
            hovertemplate='<b>%{y}</b><br>Silver: %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            y=top_10[country_col],
            x=top_10[bronze_col],
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
            margin=dict(l=200),
            font=dict(size=11),
            showlegend=True,
            legend=dict(x=0.5, y=-0.15, orientation="h")
        )
        
        fig.update_yaxes(autorange="reversed")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.markdown("### 📋 Detailed Medal Standings")
        
        display_data = top_10[[country_col, gold_col, silver_col, bronze_col, total_col]].copy()
        display_data.columns = ['Country', '🥇 Gold', '🥈 Silver', '🥉 Bronze', 'Total']
        
        st.dataframe(display_data, width='stretch', hide_index=True)
else:
    st.warning("No medal data available for visualization")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: right; color: #888; font-size: 0.8rem;">
    Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)
