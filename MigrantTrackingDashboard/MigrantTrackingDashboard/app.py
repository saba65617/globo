import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import folium
from streamlit_folium import folium_static
from supabase import create_client
import data_processing as dp
import visualization as viz
import utils
import os
import json
from datetime import datetime
import time
import dash
from dash import html, dcc
from dash.dependencies import Input, Output

# Set environment variables if they don't exist
if not os.getenv('SUPABASE_URL'):
    os.environ['SUPABASE_URL'] = "https://edgdygqnvtxkifrwfvwr.supabase.co"
if not os.getenv('SUPABASE_KEY'):
    os.environ['SUPABASE_KEY'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVkZ2R5Z3FudnR4a2lmcndmdndyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU5Mzg0MDgsImV4cCI6MjA2MTUxNDQwOH0.JmcAT6SzCg1lzRIVPDwtvi2hl7pUGlOpDqRhQqEuv18"

# Set page configuration with modern theme
st.set_page_config(
    page_title="Missing Migrants Analysis (2014-2024)",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for modern UI matching our R Shiny design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Base Styles */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main container styles */
.main {
    background-color: #f0f2f5;
}

/* Header styling */
h1 {
    font-weight: 700;
    color: #334155;
    font-size: 28px;
    margin-bottom: 20px;
}

h2 {
    font-weight: 600;
    color: #334155;
    font-size: 22px;
    margin-top: 10px;
    margin-bottom: 15px;
}

h3 {
    font-weight: 600;
    color: #334155;
    font-size: 18px;
}

/* Sidebar styling */
.css-1d391kg {
    background-color: #1c2333;
}

/* Sidebar title */
.css-1d391kg h1 {
    color: white;
    font-size: 24px;
    font-weight: 600;
    padding-top: 15px;
    padding-bottom: 15px;
}

/* Sidebar text */
.css-1d391kg .css-1qg05tj {
    color: #a0aec0;
}

/* Sidebar selectbox label */
.css-1d391kg label {
    color: #e2e8f0;
    font-size: 13px;
    font-weight: 500;
}

/* Dashboard Cards */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    margin-bottom: 20px;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}

.metric-card.purple {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
}

.metric-card.teal {
    background: linear-gradient(135deg, #14b8a6, #2dd4bf);
    color: white;
}

.metric-card.orange {
    background: linear-gradient(135deg, #f97316, #fb923c);
    color: white;
}

.metric-card.green {
    background: linear-gradient(135deg, #22c55e, #4ade80);
    color: white;
}

.metric-value {
    font-size: 32px;
    font-weight: 700;
    margin-top: 5px;
}

.metric-title {
    font-size: 14px;
    opacity: 0.9;
    font-weight: 500;
}

/* Chart container */
.chart-container {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    margin-bottom: 25px;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #f8f9fa;
    border-radius: 8px 8px 0 0;
    color: #64748b;
    border: none;
    padding: 12px 20px;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    background-color: white;
    color: #6366f1;
    font-weight: 600;
    border-bottom: 3px solid #6366f1;
}

/* Data source footer */
.footer-text {
    color: #64748b;
    font-size: 14px;
    margin-top: 30px;
    border-top: 1px solid #e2e8f0;
    padding-top: 20px;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Custom header component
def header_section():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1>Missing Migrants Analysis</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; align-items: center; margin-top: 15px;">
            <span style="color: #64748b; margin-right: 20px;">Last updated: April 29, 2025</span>
            <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #e2e8f0; 
                display: flex; align-items: center; justify-content: center; color: #6366f1; font-weight: bold;">P</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Description panel
    st.markdown("""
    <div class="chart-container" style="margin-bottom: 25px;">
        <h4 style="margin-top: 0; color: #334155;">About this Dashboard</h4>
        <p style="color: #475569; line-height: 1.6;">
            This dashboard analyzes global data on missing and deceased migrants between 2014 and 2024. 
            The aim is to explore trends in migrant deaths, highlight affected regions, understand common causes, 
            and visualize the locations where these tragic incidents occurred.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Load and process data
@st.cache_data
def load_data():
    try:
        # Load the dataset
        df = pd.read_csv("attached_assets/Global Missing Migrants Dataset.csv")
        
        # Process the data
        cleaned_df = dp.clean_data(df)
        
        return cleaned_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Initialize Supabase client
def init_supabase():
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        
        return create_client(url, key)
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Load data from database
@st.cache_data(ttl=3600)
def load_data_from_db():
    try:
        supabase = init_supabase()
        if supabase is None:
            return load_data()
        
        # Load data from Supabase
        result = supabase.table('incidents').select('*').execute()
        df = pd.DataFrame(result.data)
        
        # Rename columns to match CSV format if needed
        column_mapping = {
            'incident_year': 'Incident year',
            'reported_month': 'Reported Month',
            'month_number': 'Month Number',
            'incident_type': 'Incident Type',
            'number_of_dead': 'Number of Dead',
            'minimum_estimated_number_of_missing': 'Minimum Estimated Number of Missing',
            'total_number_of_dead_and_missing': 'Total Number of Dead and Missing',
            'number_of_survivors': 'Number of Survivors',
            'number_of_females': 'Number of Females',
            'number_of_males': 'Number of Males',
            'number_of_children': 'Number of Children',
            'cause_of_death': 'Cause of Death',
            'migration_route': 'Migration Route',
            'location_of_death': 'Location of Death',
            'information_source': 'Information Source',
            'coordinates': 'Coordinates',
            'region_of_origin': 'Region of Origin',
            'country_of_origin': 'Country of Origin',
            'region_of_incident': 'Region of Incident',
            'unsd_geographical_grouping': 'UNSD Geographical Grouping'
        }
        
        # Only rename columns that exist
        existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_columns)
        
        # If we don't have data in Supabase yet, fall back to CSV
        if df.empty or 'incident_year' not in df.columns:
            return load_data()
            
        return df
    except Exception as e:
        return load_data()

# Main function
def main():
    # Display custom header
    header_section()
    
    # Load data
    data = load_data_from_db()
    
    if data is None:
        st.error("Failed to load data. Please check the dataset file or database connection.")
        return
    
    # Get the time range for the dataset
    try:
        min_year = int(data['Incident year'].min())
        max_year = int(data['Incident year'].max())
    except KeyError:
        st.error("Failed to load required data columns. Please check the dataset format.")
        return
    
    # Sidebar filters
    st.sidebar.title("Filters")
    
    # Add a sidebar image
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <img src="https://cdn-icons-png.flaticon.com/512/4090/4090218.png" width="80">
        <h3 style="color: white; margin-top: 10px;">Global Missing Migrants</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Year range filter
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
    
    # Region filter
    all_regions = ["All Regions"] + sorted(data['Region of Incident'].unique().tolist())
    selected_region = st.sidebar.selectbox("Select Region", all_regions)
    
    # Cause of death filter
    all_causes = ["All Causes"] + sorted(data['Cause of Death'].unique().tolist())
    selected_cause = st.sidebar.selectbox("Select Cause of Death", all_causes)
    
    # Apply filters
    filtered_data = data.copy()
    
    # Filter by year range
    filtered_data = filtered_data[(filtered_data['Incident year'] >= year_range[0]) & 
                                 (filtered_data['Incident year'] <= year_range[1])]
    
    # Filter by region if not "All Regions"
    if selected_region != "All Regions":
        filtered_data = filtered_data[filtered_data['Region of Incident'] == selected_region]
    
    # Filter by cause of death if not "All Causes"
    if selected_cause != "All Causes":
        filtered_data = filtered_data[filtered_data['Cause of Death'] == selected_cause]
    
    # Display key metrics with modern UI
    st.markdown("<h2>Key Statistics</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_incidents = filtered_data.shape[0]
        st.markdown(f"""
        <div class="metric-card purple">
            <div class="metric-title">Total Incidents</div>
            <div class="metric-value">{total_incidents:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_dead = filtered_data['Number of Dead'].sum()
        st.markdown(f"""
        <div class="metric-card teal">
            <div class="metric-title">Total Deaths</div>
            <div class="metric-value">{int(total_dead):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_missing = filtered_data['Minimum Estimated Number of Missing'].sum()
        st.markdown(f"""
        <div class="metric-card orange">
            <div class="metric-title">Total Missing</div>
            <div class="metric-value">{int(total_missing):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_casualties = filtered_data['Total Number of Dead and Missing'].sum()
        st.markdown(f"""
        <div class="metric-card green">
            <div class="metric-title">Total Casualties</div>
            <div class="metric-value">{int(total_casualties):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Visualizations
    st.markdown("<h2>Visualizations</h2>", unsafe_allow_html=True)
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Yearly Trends", 
        "🌎 Regional Analysis", 
        "⚠️ Causes of Death", 
        "👥 Demographics",
        "🗺️ Geographic Distribution"
    ])
    
    with tab1:
        st.markdown("""
        <div class="chart-container">
            <h3 style="margin-top: 0;">Yearly Trends of Migrant Deaths and Disappearances</h3>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">
                This chart shows the yearly trends of deaths and disappearances, revealing patterns over time.
            </p>
        """, unsafe_allow_html=True)
        yearly_trend_chart = viz.create_yearly_trend_chart(filtered_data)
        st.plotly_chart(yearly_trend_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="chart-container">
            <h3 style="margin-top: 0;">Monthly Distribution</h3>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">
                The distribution of incidents by month, showing seasonal patterns in migrant casualties.
            </p>
        """, unsafe_allow_html=True)
        monthly_chart = viz.create_monthly_chart(filtered_data)
        st.plotly_chart(monthly_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <div class="chart-container">
            <h3 style="margin-top: 0;">Regional Analysis</h3>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">
                Compare the distribution of incidents by region of origin and region where incidents occurred.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="chart-container">
                <h4 style="margin-top: 0;">Incidents by Region of Origin</h4>
            """, unsafe_allow_html=True)
            origin_chart = viz.create_region_chart(filtered_data, 'Region of Origin')
            st.plotly_chart(origin_chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="chart-container">
                <h4 style="margin-top: 0;">Incidents by Region of Incident</h4>
            """, unsafe_allow_html=True)
            incident_chart = viz.create_region_chart(filtered_data, 'Region of Incident')
            st.plotly_chart(incident_chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="chart-container">
            <h3 style="margin-top: 0;">Top Migration Routes</h3>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">
                The most common migration routes associated with incidents, based on available data.
            </p>
        """, unsafe_allow_html=True)
        route_chart = viz.create_route_chart(filtered_data)
        st.plotly_chart(route_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
        <div class="chart-container">
            <h3 style="margin-top: 0;">Causes of Death</h3>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">
                Primary causes of migrant deaths and disappearances based on recorded incidents.
            </p>
        """, unsafe_allow_html=True)
        cause_chart = viz.create_cause_chart(filtered_data)
        st.plotly_chart(cause_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="chart-container">
            <h3 style="margin-top: 0;">Causes of Death by Year</h3>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">
                How different causes of death have changed over time, showing evolving patterns and risks.
            </p>
        """, unsafe_allow_html=True)
        cause_year_chart = viz.create_cause_year_chart(filtered_data)
        st.plotly_chart(cause_year_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab4:
        st.markdown("""
        <div class="chart-container">
            <h3 style="margin-top: 0;">Demographics Analysis</h3>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">
                Breakdown of migrant casualties by gender and age groups, where this information is available.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="chart-container">
                <h4 style="margin-top: 0;">Gender Distribution</h4>
            """, unsafe_allow_html=True)
            gender_chart = viz.create_gender_chart(filtered_data)
            st.plotly_chart(gender_chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="chart-container">
                <h4 style="margin-top: 0;">Age Group Distribution</h4>
            """, unsafe_allow_html=True)
            age_chart = viz.create_age_chart(filtered_data)
            st.plotly_chart(age_chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab5:
        st.markdown("""
        <div class="chart-container">
            <h3 style="margin-top: 0;">Geographic Distribution of Incidents</h3>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">
                Interactive map showing the locations of incidents. Each point represents an incident, with the 
                size indicating the number of casualties. Zoom and click on clusters to explore specific incidents.
            </p>
        """, unsafe_allow_html=True)
        
        map_data = viz.create_incident_map(filtered_data)
        folium_static(map_data, width=1000)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="chart-container">
            <h3 style="margin-top: 0;">Heatmap by Country of Origin</h3>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">
                Geographic distribution showing the countries of origin for migrants involved in recorded incidents.
            </p>
        """, unsafe_allow_html=True)
        country_heatmap = viz.create_country_heatmap(filtered_data, 'Country of Origin')
        st.plotly_chart(country_heatmap, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Add information about the data source with modern footer
    st.markdown("""
    <div class="footer-text">
        <h4 style="margin-top: 0; color: #334155;">About this Dashboard</h4>
        <p style="color: #475569; line-height: 1.6;">
            <strong>Data Source:</strong> Global Missing Migrants Dataset<br>
            This dashboard visualizes data on migrant deaths and disappearances worldwide, aiming to raise awareness 
            about the humanitarian crisis faced by migrants around the world.
        </p>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px;">
            <span style="color: #64748b; font-size: 12px;">
                Last updated: April 29, 2025 | College Project
            </span>
            <span style="color: #64748b; font-size: 12px;">
                Made with ❤️ on Replit
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Initialize the Dash app
app = dash.Dash(__name__, title='Migrant Tracking Dashboard')
server = app.server

# Define the layout
app.layout = html.Div([
    html.H1('Migrant Tracking Dashboard', className='dashboard-title'),
    
    html.Div([
        html.Div([
            dcc.Graph(id='yearly-trend',
                     figure=viz.create_yearly_incidents_chart(data))
        ], className='chart-container'),
        
        html.Div([
            dcc.Graph(id='region-distribution',
                     figure=viz.create_region_distribution_chart(data))
        ], className='chart-container'),
    ], className='row'),
    
    html.Div([
        html.Div([
            dcc.Graph(id='casualties-route',
                     figure=viz.create_casualties_by_route(data))
        ], className='chart-container'),
        
        html.Div([
            dcc.Graph(id='cause-of-death',
                     figure=viz.create_cause_of_death_chart(data))
        ], className='chart-container'),
    ], className='row'),
    
    html.Div([
        html.Div([
            dcc.Graph(id='gender-distribution',
                     figure=viz.create_gender_distribution(data))
        ], className='chart-container'),
        
        html.Div([
            dcc.Graph(id='monthly-trend',
                     figure=viz.create_monthly_trend(data))
        ], className='chart-container'),
    ], className='row'),
])

# Add CSS styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .dashboard-title {
                text-align: center;
                padding: 20px;
                color: #2c3e50;
                font-family: 'Arial', sans-serif;
            }
            .row {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-around;
                margin: 20px 0;
            }
            .chart-container {
                width: 45%;
                margin: 10px;
                padding: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                background-color: white;
            }
            body {
                background-color: #f5f6fa;
                margin: 0;
                padding: 20px;
                font-family: 'Arial', sans-serif;
            }
            @media (max-width: 1200px) {
                .chart-container {
                    width: 95%;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True)
