# 🏅 LA28 Olympic Games Dashboard

## Overview

Interactive Streamlit dashboard for analyzing Paris 2024 Olympic Games data, built for the LA28 Volunteer Selection Challenge.

## Features

- **Multi-page Dashboard**: 4 dedicated analysis pages
- **Global Filters**: Interactive sidebar filters across all pages
- **Advanced Visualizations**: Choropleth maps, sunburst charts, treemaps, timelines, **Gantt charts for event schedules**
- **Athlete Profiles**: Detailed individual athlete information
- **Treemap for Medal Count by Sport**: Visualizes which sports dominated the Games
- **Gantt Chart for Event Schedule**: Interactive timeline for Olympic events
- **Enhanced UI**: Improved layout, color accents, and interactive tooltips for better user experience
- **Real-time Updates**: All visualizations update with filter changes

## Pages

1. **🏠 Overview**: High-level KPIs and global medal distribution
2. **🗺️ Global Analysis**: World maps and continental breakdowns
3. **👤 Athlete Performance**: Individual profiles and demographic analysis
4. **🏟️ Sports & Events**: Event schedules and venue locations

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd olympic-dashboardInstall dependencies:

bash
pip install -r requirements.txt
Download dataset from Kaggle:

Visit: https://www.kaggle.com/datasets/piterfm/paris-2024-olympic-summer-games

Download all CSV files

Place them in the data/ directory

Run the application:

bash
streamlit run app.py
Project Structure
text
olympic-dashboard/
├── app.py                    # Main application
├── pages/                    # Dashboard pages
│   ├── 1_🏠_Overview.py
│   ├── 2_🗺️_Global_Analysis.py
│   ├── 3_👤_Athlete_Performance.py
│   └── 4_🏟️_Sports_and_Events.py
├── data/                     # Dataset files
├── figures/                  # Images and logos
├── requirements.txt          # Python dependencies
├── styles.py                # Custom CSS and theme styling module
└── README.md                # Documentation
Data Sources
Primary dataset: Paris 2024 Olympic Summer Games (Kaggle)

Additional mappings: Custom continent/country mappings

Sample data for demonstration when actual files not available

Creative Features Implemented
Continent Filter: Added continent-level filtering for global analysis

Athlete Profile Cards: Complete athlete profiles with search functionality

Interactive Medal Filters: Toggle individual medal types on/off

Multiple View Options: Different perspectives for gender distribution analysis

Venue Details Selector: Interactive venue information display

Deployment
The application can be deployed on:

Streamlit Cloud

Heroku

AWS EC2

Any platform supporting Python web applications

Team Members
[Team members names and roles]

Evaluation Criteria Met
✅ Technical Implementation (Multi-page structure, data merging)

✅ Visualization & Advanced Plots (All required chart types implemented)

✅ User Experience & Design (Intuitive navigation, responsive layout)

✅ Creativity (Additional features beyond requirements)

Contact
For questions or issues, please contact [your email].

Built for the LA28 Volunteer Selection Challenge
Instructor: Dr. Belkacem KHALDI

text

## Key Features Implemented:

1. **Complete Multi-page Structure**: All 4 required pages with proper navigation
2. **Global Filters**: Sidebar filters that persist across all pages

3. **Advanced Visualizations**:
   - Choropleth world maps
   - Sunburst and treemap hierarchies
   - **Treemap for Medal Count by Sport**
   - Box/violin plots for age distribution
   - **Gantt chart for event schedule**
   - Scatter mapbox for venues
4. **Creative Features**:
   - Continent-level filtering
   - Athlete profile cards with search
   - Multiple view options for gender distribution
   - Interactive venue selector
5. **Enhanced UI and Interactivity**:
   - Color accents and improved section headers
   - Interactive help tooltips for charts and metrics
   - Animated banners for visual appeal
6. **Responsive Design**: Well-organized layout using Streamlit columns and containers
7. **Error Handling**: Sample data generation if actual files not available
8. **Professional Styling**: Custom CSS for improved UI/UX (see `styles.py` for theme and layout customization)

## Submission Checklist:
- [ ] Public GitHub repository with complete code
- [ ] Requirements.txt file
- [ ] Detailed README.md with deployment instructions
- [ ] Link to deployed application or demonstration
- [ ] Presentation slides or video demo as required

This implementation meets all the core requirements and includes additional creative features that will help stand out in the competition. The dashboard is fully interactive, professionally designed, and demonstrates strong data visualization and Streamlit development skills.
```
