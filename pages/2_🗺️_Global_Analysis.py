import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px  # Add this import
from datetime import datetime
from app import get_theme_css, render_sidebar, render_theme_toggle

# Page configuration
st.set_page_config(
    page_title="Global Analysis - Olympic Dashboard",
    layout="wide"
)

# Initialize theme
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

current_theme = st.session_state.get("theme", "light")
if "animate_header" not in st.session_state:
    st.session_state["animate_header"] = True
animate_header = st.session_state.get("animate_header", True)

# Apply theme CSS
st.markdown(get_theme_css(current_theme, animated=animate_header), unsafe_allow_html=True)

# Theme toggle at top right - ONLY ONCE
render_theme_toggle()

data = st.session_state.get("data", {})

# Sidebar filters
selected_countries, selected_sports, selected_continent, medal_filters = render_sidebar(active_page="global", data=data)
st.session_state['selected_countries'] = selected_countries
st.session_state['selected_sports'] = selected_sports
st.session_state['selected_continent'] = selected_continent
st.session_state['medal_filters'] = medal_filters

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
            <h1 class="main-header">🗺️ Global Analysis</h1>
            <p class="sub-header">Worldwide patterns and continental insights</p>
            <div class="olympic-chip">Geographical View &nbsp;•&nbsp; Continental Analysis</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Get filtered data
medals_total_data = data.get('medals_total', pd.DataFrame())
nocs_data = data.get('nocs', pd.DataFrame())

# Apply filters
filtered_medals = medals_total_data.copy()
if selected_countries:
    if 'country_long' in filtered_medals.columns:
        filtered_medals = filtered_medals[filtered_medals['country_long'].isin(selected_countries)]
if selected_continent:
    if 'continent' in filtered_medals.columns:
        filtered_medals = filtered_medals[filtered_medals['continent'].isin(selected_continent)]

# --- World Medal Map (Choropleth) ---
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">🌍 World Medal Map <span title='Choropleth map of medal distribution' style='cursor:help;'>ℹ️</span></h2>
</div>
""", unsafe_allow_html=True)

if not filtered_medals.empty:
    # Prepare data for choropleth
    if 'country_long' in filtered_medals.columns and 'country_code' in filtered_medals.columns:
        # Calculate total medals
        medal_cols = ['Gold Medal', 'Silver Medal', 'Bronze Medal'] if 'Gold Medal' in filtered_medals.columns else ['gold', 'silver', 'bronze']
        medal_cols = [col for col in medal_cols if col in filtered_medals.columns]
        
        if medal_cols:
            filtered_medals['total_medals'] = filtered_medals[medal_cols].sum(axis=1)
            
            # Create choropleth
            fig = px.choropleth(
                filtered_medals,
                locations='country_code',
                color='total_medals',
                hover_name='country_long',
                color_continuous_scale=px.colors.sequential.Plasma,
                title='<b>World Medal Distribution</b>',
                projection='natural earth',
                labels={'total_medals': 'Total Medals'}
            )
            
            fig.update_layout(
                height=500,
                margin=dict(t=40, l=0, r=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No medal columns found for choropleth")
    else:
        st.warning("Country data not available for choropleth")
else:
    st.warning("No medal data available for choropleth")

st.markdown("---")

# --- Medal Hierarchy (Sunburst and Treemap) ---
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">🌐 Medal Hierarchy by Continent <span title='Sunburst and Treemap visualizations' style='cursor:help;'>ℹ️</span></h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Sunburst chart
    st.markdown("#### 🔄 Sunburst Chart")
    if not filtered_medals.empty and 'continent' in filtered_medals.columns and 'country_long' in filtered_medals.columns:
        # For sunburst, we need Continent -> Country -> Medal Type
        # Prepare hierarchical data
        hierarchical_data = []
        for _, row in filtered_medals.iterrows():
            continent = row.get('continent', 'Unknown')
            country = row.get('country_long', 'Unknown')
            
            gold_col = 'Gold Medal' if 'Gold Medal' in row else 'gold'
            silver_col = 'Silver Medal' if 'Silver Medal' in row else 'silver'
            bronze_col = 'Bronze Medal' if 'Bronze Medal' in row else 'bronze'
            
            if gold_col in row and row[gold_col] > 0:
                hierarchical_data.append({
                    'continent': continent,
                    'country': country,
                    'medal_type': 'Gold',
                    'count': row[gold_col]
                })
            if silver_col in row and row[silver_col] > 0:
                hierarchical_data.append({
                    'continent': continent,
                    'country': country,
                    'medal_type': 'Silver',
                    'count': row[silver_col]
                })
            if bronze_col in row and row[bronze_col] > 0:
                hierarchical_data.append({
                    'continent': continent,
                    'country': country,
                    'medal_type': 'Bronze',
                    'count': row[bronze_col]
                })
        
        if hierarchical_data:
            df_hierarchical = pd.DataFrame(hierarchical_data)
            fig = px.sunburst(
                df_hierarchical,
                path=['continent', 'country', 'medal_type'],
                values='count',
                color='continent',
                title='<b>Medal Hierarchy (Continent → Country → Medal Type)</b>'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hierarchical data available for Sunburst")
    else:
        st.info("Data not available for Sunburst chart")

with col2:
    # Treemap
    st.markdown("#### 📊 Treemap Chart")
    if not filtered_medals.empty and 'continent' in filtered_medals.columns:
        # Group by continent for treemap
        continent_summary = filtered_medals.groupby('continent').agg({
            'Gold Medal': 'sum' if 'Gold Medal' in filtered_medals.columns else None,
            'Silver Medal': 'sum' if 'Silver Medal' in filtered_medals.columns else None,
            'Bronze Medal': 'sum' if 'Bronze Medal' in filtered_medals.columns else None
        }).reset_index()
        
        # Calculate total medals per continent
        medal_cols = [col for col in ['Gold Medal', 'Silver Medal', 'Bronze Medal'] if col in continent_summary.columns]
        if medal_cols:
            continent_summary['total'] = continent_summary[medal_cols].sum(axis=1)
            
            fig = px.treemap(
                continent_summary,
                path=['continent'],
                values='total',
                color='total',
                color_continuous_scale='RdYlBu',
                title='<b>Medal Distribution by Continent</b>'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No medal columns found for Treemap")
    else:
        st.info("Continent data not available for Treemap")

st.markdown("---")

# --- Continent vs. Medals Bar Chart ---
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">📊 Continent vs. Medals <span title='Grouped bar chart by continent' style='cursor:help;'>ℹ️</span></h2>
</div>
""", unsafe_allow_html=True)

if not filtered_medals.empty and 'continent' in filtered_medals.columns:
    # Group by continent and sum medals
    continent_medals = filtered_medals.groupby('continent').agg({
        'Gold Medal': 'sum' if 'Gold Medal' in filtered_medals.columns else None,
        'Silver Medal': 'sum' if 'Silver Medal' in filtered_medals.columns else None,
        'Bronze Medal': 'sum' if 'Bronze Medal' in filtered_medals.columns else None
    }).reset_index()
    
    # Rename columns if using lowercase
    if 'gold' in filtered_medals.columns:
        continent_medals = filtered_medals.groupby('continent').agg({
            'gold': 'sum',
            'silver': 'sum',
            'bronze': 'sum'
        }).reset_index()
        continent_medals.columns = ['continent', 'Gold Medal', 'Silver Medal', 'Bronze Medal']
    
    # Create grouped bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=continent_medals['continent'],
        y=continent_medals['Gold Medal'],
        name='🥇 Gold',
        marker_color='#FFD700'
    ))
    
    fig.add_trace(go.Bar(
        x=continent_medals['continent'],
        y=continent_medals['Silver Medal'],
        name='🥈 Silver',
        marker_color='#C0C0C0'
    ))
    
    fig.add_trace(go.Bar(
        x=continent_medals['continent'],
        y=continent_medals['Bronze Medal'],
        name='🥉 Bronze',
        marker_color='#CD7F32'
    ))
    
    fig.update_layout(
        title_text="<b>Medal Count by Continent</b>",
        xaxis_title="Continent",
        yaxis_title="Number of Medals",
        barmode='group',
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No continent data available for visualization")

st.markdown("---")

# --- Country vs. Medals (Top 20) ---
st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em; color:#FFD700;">🏆 Top 20 Countries vs. Medals <span title='Grouped bar chart for top 20 countries' style='cursor:help;'>ℹ️</span></h2>
</div>
""", unsafe_allow_html=True)

if not filtered_medals.empty:
    # Calculate total medals for each country
    country_col = 'country_long' if 'country_long' in filtered_medals.columns else 'country'
    
    if country_col in filtered_medals.columns:
        # Determine medal columns
        gold_col = 'Gold Medal' if 'Gold Medal' in filtered_medals.columns else 'gold'
        silver_col = 'Silver Medal' if 'Silver Medal' in filtered_medals.columns else 'silver'
        bronze_col = 'Bronze Medal' if 'Bronze Medal' in filtered_medals.columns else 'bronze'
        
        if all(col in filtered_medals.columns for col in [gold_col, silver_col, bronze_col]):
            # Calculate total medals
            filtered_medals['total_medals'] = filtered_medals[gold_col] + filtered_medals[silver_col] + filtered_medals[bronze_col]
            
            # Get top 20 countries
            top_20 = filtered_medals.nlargest(20, 'total_medals')
            
            # Create grouped bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=top_20[country_col],
                y=top_20[gold_col],
                name='🥇 Gold',
                marker_color='#FFD700'
            ))
            
            fig.add_trace(go.Bar(
                x=top_20[country_col],
                y=top_20[silver_col],
                name='🥈 Silver',
                marker_color='#C0C0C0'
            ))
            
            fig.add_trace(go.Bar(
                x=top_20[country_col],
                y=top_20[bronze_col],
                name='🥉 Bronze',
                marker_color='#CD7F32'
            ))
            
            fig.update_layout(
                title_text="<b>Top 20 Countries by Medal Count</b>",
                xaxis_title="Country",
                yaxis_title="Number of Medals",
                barmode='group',
                height=600,
                hovermode='x unified',
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data table
            st.markdown("### 📋 Detailed Data (Top 20 Countries)")
            display_data = top_20[[country_col, gold_col, silver_col, bronze_col, 'total_medals']].copy()
            display_data.columns = ['Country', '🥇 Gold', '🥈 Silver', '🥉 Bronze', 'Total Medals']
            st.dataframe(display_data.sort_values('Total Medals', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.warning("Medal columns not found in data")
    else:
        st.warning("Country column not found in data")
else:
    st.warning("No medal data available for visualization")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: right; color: #888; font-size: 0.8rem;">
    Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)