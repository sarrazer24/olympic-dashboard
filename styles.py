"""
Styling module for Olympic Games Dashboard
Contains all CSS and theme-related styling
"""

def get_theme_css(theme="light", animated=False):
    """
    Generate theme CSS for the application.
    
    Parameters:
    - theme: "light" or "dark"
    - animated: whether to apply animation to banner
    
    Returns:
    - HTML/CSS string to be rendered with st.markdown(..., unsafe_allow_html=True)
    """
    animation_css = """
            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            .olympic-banner-animated {
                background: linear-gradient(-45deg, #0085CA, #FFD700, #EE334E, #0085CA);
                background-size: 400% 400%;
                animation: gradientShift 8s ease infinite;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                color: white;
            }
    """ if animated else ""
    
    if theme == "dark":
        return f"""
        <style>
            :root {{
                --primary-color: #0085CA;
                --secondary-color: #FFD700;
                --accent-color: #EE334E;
                --text-primary: #ffffff;
                --text-secondary: #e0e0e0;
                --bg-primary: #0a0e27;
                --bg-secondary: #1a1f3a;
                --bg-tertiary: #252d4a;
            }}
            * {{ color: var(--text-primary) !important; }}
            body {{ background-color: var(--bg-primary) !important; }}
            header {{ display: none !important; }}
            .main {{ background-color: var(--bg-primary); color: var(--text-primary); }}
            .stSidebar {{ background-color: var(--bg-secondary); border-right: 2px solid #0085CA; border-radius: 0px; padding-top: 0 !important; }}
            .stSidebar > div:first-child {{ padding-top: 0 !important; margin-top: 0 !important; }}
            .stMainBlockContainer {{ background-color: var(--bg-primary); margin-top: 0 !important; padding-top: 0 !important; }}
            .stContainer {{ background-color: var(--bg-primary); }}
            
            /* Dropdown styling */
            [data-testid="stMultiSelect"] {{ color: #000000 !important; }}
            div[data-baseweb="select"] {{ color: #000000 !important; }}
            [data-testid="stSelectbox"] {{ color: #000000 !important; }}
            input, textarea, select {{ color: #000000 !important; background-color: #ffffff !important; }}
            
            /* Text Colors */
            h1, h2, h3, h4, h5, h6 {{ color: var(--text-primary); }}
            p, span, label, div {{ color: var(--text-primary); }}
            
            /* Cards and Containers */
            .stExpander {{ background-color: var(--bg-secondary); border: 1px solid rgba(0, 133, 202, 0.2); }}
            .stExpander > div > div > button {{ color: var(--text-primary); }}
            .stMetricLabel, .stMetricValue {{ color: var(--text-primary); }}
            
            /* Input Fields */
            input, textarea, select {{ background-color: var(--bg-tertiary); color: var(--text-primary); border: 1px solid rgba(0, 133, 202, 0.3); }}
            input:focus, textarea:focus, select:focus {{ background-color: var(--bg-tertiary); color: var(--text-primary); }}
            
            /* Banner and Headers */
            .olympic-banner {{ background: linear-gradient(135deg, #0085CA 0%, #FFD700 50%, #EE334E 100%); 
                            border-radius: 15px; padding: 30px; margin-bottom: 30px; color: white; }}
            .main-header {{ font-size: 2.5em; font-weight: 800; margin-bottom: 0.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3); color: white; }}
            .sub-header {{ font-size: 1.1em; opacity: 0.95; margin-bottom: 1rem; color: white; }}
            .olympic-chip {{ display: inline-block; background-color: rgba(255,255,255,0.2); 
                          padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9em; color: white; }}
            
            /* Cards */
            .metric-card {{ background: linear-gradient(135deg, rgba(0,133,202,0.15) 0%, rgba(238,51,46,0.15) 100%);
                         border-radius: 10px; padding: 20px; border-left: 4px solid #0085CA; transition: transform 0.3s ease; color: var(--text-primary); }}
            .metric-card:hover {{ transform: translateY(-5px); }}
            
                       /* Olympic Rings in correct order */
            .ring {{
                display: inline-block;
                width: 25px;
                height: 25px;
                border: 3px solid;
                border-radius: 50%;
                margin-right: 5px;
                vertical-align: middle;
            }}
            .ring-blue {{
                border-color: #0085CA;  /* Blue */
            }}
            .ring-yellow {{
                border-color: #FFD700;  /* Yellow */
            }}
            .ring-black {{
                border-color: #000000;  /* Black (not white) */
            }}
            .ring-green {{
                border-color: #009F3D;  /* Green */
            }}
            .ring-red {{
                border-color: #EE334E;  /* Red */
            }}
            .olympic-rings {{
                margin-bottom: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 8px;
            }}
            
            /* Sidebar */
            .sidebar-header {{ 
                background: linear-gradient(135deg, #0085CA 0%, #EE334E 100%);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 15px;
                color: white;
                font-weight: bold;
            }}
            .filter-section {{
                background: rgba(0, 133, 202, 0.15);
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 12px;
                border-left: 3px solid #0085CA;
                color: var(--text-primary);
            }}
            
            /* Quick Stats */
            .quick-stat {{
                background: linear-gradient(135deg, rgba(0,133,202,0.2) 0%, rgba(238,51,46,0.2) 100%);
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #FFD700;
                transition: all 0.3s ease;
                color: var(--text-primary);
            }}
            .quick-stat:hover {{
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0,133,202,0.3);
            }}
            
            /* Data Tables */
            .stDataFrame {{ background-color: var(--bg-secondary); }}
            table {{ background-color: var(--bg-secondary); color: var(--text-primary); }}
            thead {{ background-color: var(--bg-tertiary); color: var(--text-primary); }}
            tbody tr {{ background-color: var(--bg-secondary); color: var(--text-primary); }}
            tbody tr:hover {{ background-color: var(--bg-tertiary); }}
            
            /* Buttons */
            .stButton > button {{ background-color: #0085CA; color: white; border: 1px solid #0085CA; }}
            .stButton > button:hover {{ background-color: #006399; }}
            
            /* Selectbox and Multiselect */
            .stSelectbox, .stMultiSelect {{ color: #000000 !important; }}
            div[role="listbox"] {{ background-color: var(--bg-tertiary); color: #000000 !important; }}
            .stSelectbox > div > div > select {{ color: #000000 !important; }}
            .stMultiSelect > div > div > select {{ color: #000000 !important; }}
            
            /* Dropdown menus - always dark/black font */
            select, .stSelectbox select, .stMultiSelect select {{ color: #000000 !important; }}
            [role="option"] {{ color: #000000 !important; }}
            [role="listbox"] [role="option"] {{ color: #000000 !important; }}
            
            /* Hide Streamlit's automatic page menu */
            [data-testid="collapsedControl"] {{ display: none; }}
            .stPageLink {{ display: none; }}
            [data-testid="stSidebarNav"] {{ display: none; }}
            section[data-testid="stSidebarNav"] {{ display: none !important; }}
            {animation_css}
        </style>
        """
    else:  # light theme
        return f"""
        <style>
            :root {{
                --primary-color: #0085CA;
                --secondary-color: #FFD700;
                --accent-color: #EE334E;
                --text-primary: #333333;
                --text-secondary: #666666;
                --bg-primary: #ffffff;
                --bg-secondary: #f8f9fa;
                --bg-tertiary: #eeeeee;
            }}
            * {{ color: var(--text-primary) !important; }}
            body {{ background-color: var(--bg-primary) !important; }}
            header {{ display: none !important; }}
            .main {{ background-color: var(--bg-primary); color: var(--text-primary); }}
            .stSidebar {{ background-color: var(--bg-secondary); border-right: 2px solid #0085CA; padding-top: 0 !important; }}
            .stSidebar > div:first-child {{ padding-top: 0 !important; margin-top: 0 !important; }}
            .stMainBlockContainer {{ background-color: var(--bg-primary); margin-top: 0 !important; padding-top: 0 !important; }}
            .stContainer {{ background-color: var(--bg-primary); }}
            
            /* Dropdown styling */
            [data-testid="stMultiSelect"] {{ color: #000000 !important; }}
            div[data-baseweb="select"] {{ color: #000000 !important; }}
            [data-testid="stSelectbox"] {{ color: #000000 !important; }}
            input, textarea, select {{ color: #000000 !important; background-color: #ffffff !important; }}
            
            /* Text Colors */
            h1, h2, h3, h4, h5, h6 {{ color: var(--text-primary); }}
            p, span, label, div {{ color: var(--text-primary); }}
            
            /* Cards and Containers */
            .stExpander {{ background-color: var(--bg-secondary); border: 1px solid rgba(0, 133, 202, 0.2); }}
            .stExpander > div > div > button {{ color: var(--text-primary); }}
            .stMetricLabel, .stMetricValue {{ color: var(--text-primary); }}
            
            /* Input Fields */
            input, textarea, select {{ background-color: white; color: var(--text-primary); border: 1px solid #ddd; }}
            input:focus, textarea:focus, select:focus {{ background-color: white; color: var(--text-primary); border: 1px solid #0085CA; }}
            
            /* Banner and Headers */
            .olympic-banner {{ background: linear-gradient(135deg, #0085CA 0%, #FFD700 50%, #EE334E 100%); 
                            border-radius: 15px; padding: 30px; margin-bottom: 30px; color: white; }}
            .main-header {{ font-size: 2.5em; font-weight: 800; margin-bottom: 0.5rem; text-shadow: 0 1px 3px rgba(0,0,0,0.2); color: white; }}
            .sub-header {{ font-size: 1.1em; opacity: 0.95; margin-bottom: 1rem; color: white; }}
            .olympic-chip {{ display: inline-block; background-color: rgba(255,255,255,0.3); 
                          padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9em; color: white; }}
            
            /* Cards */
            .metric-card {{ background: linear-gradient(135deg, rgba(0,133,202,0.08) 0%, rgba(238,51,46,0.08) 100%);
                         border-radius: 10px; padding: 20px; border-left: 4px solid #0085CA; transition: transform 0.3s ease; color: var(--text-primary); }}
            .metric-card:hover {{ transform: translateY(-5px); }}
            
            /* Olympic Rings */
            .ring {{ display: inline-block; width: 25px; height: 25px; border: 3px solid; 
                   border-radius: 50%; margin-right: 5px; vertical-align: middle; }}
            .ring-blue {{ border-color: #0085CA; }}
            .ring-yellow {{ border-color: #FFD700; }}
            .ring-black {{ border-color: #000000; }}
            .ring-green {{ border-color: #009F3D; }}
            .ring-red {{ border-color: #EE334E; }}
            .olympic-rings {{ margin-bottom: 20px; }}
            .olympic-banner-text h1 {{ margin: 0; color: white; }}
            
            /* Sidebar */
            .sidebar-header {{ 
                background: linear-gradient(135deg, #0085CA 0%, #EE334E 100%);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 15px;
                color: white;
                font-weight: bold;
            }}
            .filter-section {{
                background: rgba(0, 133, 202, 0.08);
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 12px;
                border-left: 3px solid #0085CA;
                color: var(--text-primary);
            }}
            
            /* Quick Stats */
            .quick-stat {{
                background: linear-gradient(135deg, rgba(0,133,202,0.08) 0%, rgba(238,51,46,0.08) 100%);
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #FFD700;
                transition: all 0.3s ease;
                color: var(--text-primary);
            }}
            .quick-stat:hover {{
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0,133,202,0.15);
            }}
            
            /* Data Tables */
            .stDataFrame {{ background-color: var(--bg-secondary); }}
            table {{ background-color: var(--bg-primary); color: var(--text-primary); }}
            thead {{ background-color: var(--bg-tertiary); color: var(--text-primary); }}
            tbody tr {{ background-color: var(--bg-primary); color: var(--text-primary); }}
            tbody tr:hover {{ background-color: var(--bg-tertiary); }}
            
            /* Buttons */
            .stButton > button {{ background-color: #0085CA; color: white; border: 1px solid #0085CA; }}
            .stButton > button:hover {{ background-color: #006399; }}
            
            /* Selectbox and Multiselect */
            .stSelectbox, .stMultiSelect {{ color: #000000 !important; }}
            div[role="listbox"] {{ background-color: var(--bg-primary); color: #000000 !important; }}
            .stSelectbox > div > div > select {{ color: #000000 !important; }}
            .stMultiSelect > div > div > select {{ color: #000000 !important; }}
            
            /* Dropdown menus - always dark/black font */
            select, .stSelectbox select, .stMultiSelect select {{ color: #000000 !important; }}
            [role="option"] {{ color: #000000 !important; }}
            [role="listbox"] [role="option"] {{ color: #000000 !important; }}
            
            /* Hide Streamlit's automatic page menu */
            [data-testid="collapsedControl"] {{ display: none; }}
            .stPageLink {{ display: none; }}
            [data-testid="stSidebarNav"] {{ display: none; }}
            section[data-testid="stSidebarNav"] {{ display: none !important; }}
            {animation_css}
        </style>
        """
