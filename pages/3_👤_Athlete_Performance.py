import streamlit as st
import pandas as pd
from app import get_theme_css, render_sidebar, render_theme_toggle

st.set_page_config(
    page_title="Athlete Performance - Olympic Dashboard",
    layout="wide"
)

current_theme = st.session_state.get("theme", "dark")
st.markdown(get_theme_css(current_theme), unsafe_allow_html=True)
render_theme_toggle()

data = st.session_state.get("data", {})
selected_countries, selected_sports, selected_continent, medal_filters = render_sidebar(active_page="athlete", data=data)
st.session_state['selected_countries'] = selected_countries
st.session_state['selected_sports'] = selected_sports
st.session_state['selected_continent'] = selected_continent
st.session_state['medal_filters'] = medal_filters

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
            <p class="sub-header">Individual athlete profiles and demographics</p>
            <div class="olympic-chip">Athletes &nbsp;•&nbsp; Gender & Age Analysis</div>
        </div>
    </div>
""", unsafe_allow_html=True)
athletes_data = data.get('athletes', pd.DataFrame())

st.markdown("""
<div style="margin: 2rem 0;">
    <h2 style="font-weight: 700; margin-bottom: 1.5rem; letter-spacing: -0.01em;">👥 Athlete Demographics</h2>
</div>
""", unsafe_allow_html=True)
