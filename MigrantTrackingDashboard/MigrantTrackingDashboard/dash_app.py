import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd

from data_processing import clean_data
from data_visualization import (
    create_yearly_incidents_chart,
    create_region_distribution_chart,
    create_casualties_by_route,
    create_cause_of_death_chart,
    create_gender_distribution,
    create_monthly_trend
)

# Initialize the Dash app
app = dash.Dash(__name__, title='Migrant Tracking Dashboard')
server = app.server

# Load and clean data
try:
    df = pd.read_csv('attached_assets/Global Missing Migrants Dataset.csv')
    df = clean_data(df)
except Exception as e:
    print(f"Error loading data: {e}")
    df = pd.DataFrame()

# Define the layout
app.layout = html.Div([
    html.H1('Missing Migrants Analysis (2014-2024)', className='dashboard-title'),
    
    html.Div([
        html.Div([
            html.P("""
                This dashboard analyzes global data on missing and deceased migrants between 2014 and 2024. 
                The aim is to explore trends in migrant deaths, highlight affected regions, understand common causes, 
                and visualize the locations where these tragic incidents occurred.
            """, className='dashboard-description')
        ], className='description-container'),
    ]),
    
    html.Div([
        html.Div([
            dcc.Graph(id='yearly-trend',
                     figure=create_yearly_incidents_chart(df))
        ], className='chart-container'),
        
        html.Div([
            dcc.Graph(id='region-distribution',
                     figure=create_region_distribution_chart(df))
        ], className='chart-container'),
    ], className='row'),
    
    html.Div([
        html.Div([
            dcc.Graph(id='casualties-route',
                     figure=create_casualties_by_route(df))
        ], className='chart-container'),
        
        html.Div([
            dcc.Graph(id='cause-of-death',
                     figure=create_cause_of_death_chart(df))
        ], className='chart-container'),
    ], className='row'),
    
    html.Div([
        html.Div([
            dcc.Graph(id='gender-distribution',
                     figure=create_gender_distribution(df))
        ], className='chart-container'),
        
        html.Div([
            dcc.Graph(id='monthly-trend',
                     figure=create_monthly_trend(df))
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
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            body {
                background-color: #f5f6fa;
                margin: 0;
                padding: 20px;
                font-family: 'Inter', sans-serif;
            }
            
            .dashboard-title {
                text-align: center;
                padding: 20px;
                color: #2c3e50;
                font-family: 'Inter', sans-serif;
                font-weight: 700;
                font-size: 28px;
                margin-bottom: 20px;
            }
            
            .description-container {
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 12px rgba(0,0,0,0.04);
            }
            
            .dashboard-description {
                color: #475569;
                line-height: 1.6;
                margin: 0;
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
                box-shadow: 0 2px 12px rgba(0,0,0,0.04);
                border-radius: 12px;
                background-color: white;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            .chart-container:hover {
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
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