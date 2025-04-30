import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_yearly_incidents_chart(df):
    """Create a line chart showing the number of incidents per year."""
    yearly_data = df.groupby('Year').size().reset_index(name='Incidents')
    fig = px.line(yearly_data, x='Year', y='Incidents',
                  title='Yearly Trend of Migration Incidents',
                  markers=True)
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Incidents",
        template="plotly_white",
        hovermode='x'
    )
    return fig

def create_region_distribution_chart(df):
    """Create a bar chart showing the distribution of incidents by region."""
    region_data = df['Region of Incident'].value_counts().reset_index()
    region_data.columns = ['Region', 'Count']
    
    fig = px.bar(region_data, x='Region', y='Count',
                 title='Regional Distribution of Incidents',
                 color='Count',
                 color_continuous_scale='Viridis')
    
    fig.update_layout(
        xaxis_title="Region",
        yaxis_title="Number of Incidents",
        template="plotly_white",
        xaxis_tickangle=-45
    )
    return fig

def create_casualties_by_route(df):
    """Create a pie chart showing the distribution of casualties by migration route."""
    route_data = df['Migration Route'].value_counts().reset_index()
    route_data.columns = ['Route', 'Casualties']
    
    fig = px.pie(route_data, values='Casualties', names='Route',
                 title='Casualties by Migration Route',
                 hole=0.3)
    
    fig.update_layout(
        template="plotly_white",
        showlegend=True
    )
    return fig

def create_cause_of_death_chart(df):
    """Create a horizontal bar chart showing the main causes of death."""
    cause_data = df['Cause of Death'].value_counts().head(10).reset_index()
    cause_data.columns = ['Cause', 'Count']
    
    fig = px.bar(cause_data, y='Cause', x='Count',
                 title='Top 10 Causes of Death',
                 orientation='h',
                 color='Count',
                 color_continuous_scale='Reds')
    
    fig.update_layout(
        xaxis_title="Number of Casualties",
        yaxis_title="Cause of Death",
        template="plotly_white"
    )
    return fig

def create_gender_distribution(df):
    """Create a donut chart showing the gender distribution of casualties."""
    gender_data = df['Number of Dead by Gender'].value_counts().reset_index()
    gender_data.columns = ['Gender', 'Count']
    
    fig = px.pie(gender_data, values='Count', names='Gender',
                 title='Gender Distribution of Casualties',
                 hole=0.6,
                 color_discrete_sequence=px.colors.qualitative.Set3)
    
    fig.update_layout(
        template="plotly_white",
        annotations=[dict(text='Gender<br>Distribution', x=0.5, y=0.5, font_size=12, showarrow=False)]
    )
    return fig

def create_monthly_trend(df):
    """Create a line chart showing the monthly trend of incidents."""
    df['Month'] = pd.to_datetime(df['Reported Date']).dt.month
    monthly_data = df.groupby('Month').size().reset_index(name='Incidents')
    
    fig = px.line(monthly_data, x='Month', y='Incidents',
                  title='Monthly Distribution of Incidents',
                  markers=True)
    
    # Add month names to x-axis
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fig.update_xaxes(ticktext=month_names, tickvals=list(range(1, 13)))
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Incidents",
        template="plotly_white",
        hovermode='x'
    )
    return fig 