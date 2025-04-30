import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster, HeatMap
import data_processing as dp

# Color palette
COLOR_PALETTE = px.colors.qualitative.D3

def create_yearly_trend_chart(data):
    """
    Create a yearly trend chart of migrant deaths and disappearances
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The filtered Missing Migrants dataset
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Yearly trend chart
    """
    yearly_data = dp.get_yearly_data(data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=yearly_data['Incident year'],
        y=yearly_data['Number of Dead'],
        name='Deaths',
        marker_color='#5470C6'
    ))
    
    fig.add_trace(go.Bar(
        x=yearly_data['Incident year'],
        y=yearly_data['Minimum Estimated Number of Missing'],
        name='Missing',
        marker_color='#91CC75'
    ))
    
    fig.add_trace(go.Scatter(
        x=yearly_data['Incident year'],
        y=yearly_data['Incident Count'],
        name='Incident Count',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#EE6666', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        barmode='stack',
        title='Yearly Trend of Migrant Deaths and Disappearances',
        xaxis=dict(title='Year', tickmode='linear'),
        yaxis=dict(title='Number of People'),
        yaxis2=dict(
            title='Number of Incidents',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hovermode='x unified',
        height=500
    )
    
    return fig

def create_monthly_chart(data):
    """
    Create a monthly distribution chart
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The filtered Missing Migrants dataset
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Monthly distribution chart
    """
    # Get monthly data
    monthly_data = dp.get_monthly_data(data)
    
    # Create a pivot table for heatmap
    pivot_data = monthly_data.pivot_table(
        index='Reported Month',
        columns='Incident year',
        values='Total Number of Dead and Missing',
        aggfunc='sum'
    ).fillna(0)
    
    # Get month order
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Reindex pivot table to ensure correct month order
    pivot_data = pivot_data.reindex(month_order)
    
    # Create heatmap
    fig = px.imshow(
        pivot_data,
        labels=dict(x="Year", y="Month", color="Number of Casualties"),
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale='RdBu_r',
        aspect="auto"
    )
    
    fig.update_layout(
        title='Monthly Distribution of Migrant Deaths and Disappearances',
        height=500,
        coloraxis_colorbar=dict(title="Number of Casualties")
    )
    
    return fig

def create_region_chart(data, region_column):
    """
    Create a region chart for either origin or incident region
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The filtered Missing Migrants dataset
    region_column : str
        The column name for region ('Region of Origin' or 'Region of Incident')
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Region chart
    """
    region_data = dp.get_region_data(data, region_column)
    
    # Get top 10 regions
    top_regions = region_data.head(10)
    
    fig = px.bar(
        top_regions,
        x='Total Number of Dead and Missing',
        y=region_column,
        orientation='h',
        color='Total Number of Dead and Missing',
        color_continuous_scale='Bluered',
        text='Total Number of Dead and Missing'
    )
    
    fig.update_traces(
        texttemplate='%{text:,}',
        textposition='outside'
    )
    
    title_text = 'Top Regions of Origin' if region_column == 'Region of Origin' else 'Top Regions of Incident'
    
    fig.update_layout(
        title=title_text,
        xaxis_title='Number of Dead and Missing',
        yaxis_title='',
        yaxis=dict(autorange="reversed"),
        height=500
    )
    
    return fig

def create_cause_chart(data):
    """
    Create a chart showing causes of death
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The filtered Missing Migrants dataset
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Cause of death chart
    """
    cause_data = dp.get_cause_data(data)
    
    fig = px.pie(
        cause_data,
        values='Total Number of Dead and Missing',
        names='Cause of Death',
        color_discrete_sequence=COLOR_PALETTE,
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}'
    )
    
    fig.update_layout(
        title='Causes of Death',
        height=500,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        )
    )
    
    return fig

def create_cause_year_chart(data):
    """
    Create a chart showing causes of death by year
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The filtered Missing Migrants dataset
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Cause of death by year chart
    """
    # Group data by year and cause of death
    yearly_cause_data = data.groupby(['Incident year', 'Cause of Death']).agg({
        'Total Number of Dead and Missing': 'sum'
    }).reset_index()
    
    fig = px.area(
        yearly_cause_data,
        x='Incident year',
        y='Total Number of Dead and Missing',
        color='Cause of Death',
        color_discrete_sequence=COLOR_PALETTE,
        line_shape='spline'
    )
    
    fig.update_layout(
        title='Causes of Death by Year',
        xaxis_title='Year',
        yaxis_title='Number of Dead and Missing',
        legend_title='Cause of Death',
        height=500
    )
    
    return fig

def create_route_chart(data):
    """
    Create a chart showing top migration routes
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The filtered Missing Migrants dataset
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Migration route chart
    """
    route_data = dp.get_route_data(data)
    
    # Find the route column name
    route_col = [col for col in route_data.columns if col.lower().replace('_', ' ') == 'migration route'][0]
    
    fig = px.bar(
        route_data,
        y=route_col,
        x='Total Number of Dead and Missing',
        orientation='h',
        color='Total Number of Dead and Missing',
        color_continuous_scale='Viridis',
        text='Total Number of Dead and Missing'
    )
    
    fig.update_traces(
        texttemplate='%{text:,}',
        textposition='outside'
    )
    
    fig.update_layout(
        title='Top Migration Routes by Number of Dead and Missing',
        xaxis_title='Number of Dead and Missing',
        yaxis_title='',
        yaxis=dict(autorange="reversed"),
        height=700
    )
    
    return fig

def create_gender_chart(data):
    """
    Create a chart showing gender distribution
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The filtered Missing Migrants dataset
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Gender distribution chart
    """
    demographic_data = dp.get_demographic_data(data)
    gender_data = demographic_data['gender']
    
    fig = px.pie(
        gender_data,
        values='Count',
        names='Gender',
        color='Gender',
        color_discrete_map={
            'Female': '#FF9AA2',
            'Male': '#A2D2FF',
            'Children': '#BAFFC9',
            'Unknown': '#E2E2E2'
        }
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}'
    )
    
    fig.update_layout(
        title='Gender Distribution',
        height=500
    )
    
    return fig

def create_age_chart(data):
    """
    Create a chart showing age group distribution
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The filtered Missing Migrants dataset
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Age group distribution chart
    """
    demographic_data = dp.get_demographic_data(data)
    age_data = demographic_data['age']
    
    fig = px.pie(
        age_data,
        values='Count',
        names='Age Group',
        color='Age Group',
        color_discrete_map={
            'Children (<18)': '#BAFFC9',
            'Adults (18+)': '#A2D2FF',
            'Unknown': '#E2E2E2'
        }
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}'
    )
    
    fig.update_layout(
        title='Age Group Distribution',
        height=500
    )
    
    return fig

def create_incident_map(data):
    """
    Create a map showing the geographic distribution of incidents
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The filtered Missing Migrants dataset
    
    Returns:
    --------
    folium.Map
        Map showing incidents
    """
    # Create a base map centered on the world
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB positron')
    
    # Find the latitude and longitude columns (handle case sensitivity)
    lat_col = None
    long_col = None
    
    # Check for various possible column names
    for col in data.columns:
        col_lower = col.lower()
        if 'lat' in col_lower:
            lat_col = col
        if 'lon' in col_lower:
            long_col = col
    
    # If coordinates columns are not found, return an empty map with a warning
    if lat_col is None or long_col is None:
        folium.map.Marker(
            [0, 0],
            popup="No coordinate data available",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        return m
    
    # Filter data with valid coordinates
    map_data = data.dropna(subset=[lat_col, long_col]).copy()
    
    # Rename columns for consistent access
    map_data = map_data.rename(columns={lat_col: 'map_latitude', long_col: 'map_longitude'})
    
    # Create a marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for each incident
    for idx, row in map_data.iterrows():
        # Calculate marker size based on casualties
        casualties = row['Total Number of Dead and Missing']
        radius = min(max(5, (casualties ** 0.5) * 1.5), 20)
        
        # Handle possible column name variations
        migration_route_col = 'Migration Route'
        if migration_route_col not in row.index:
            if 'Migration route' in row.index:
                migration_route_col = 'Migration route'
            elif 'migration_route' in row.index:
                migration_route_col = 'migration_route'
        
        # Create popup text
        popup_text = f"""
        <b>Date:</b> {row['Reported Month']} {int(row['Incident year'])}<br>
        <b>Region:</b> {row['Region of Incident']}<br>
        <b>Casualties:</b> {int(casualties)}<br>
        <b>Cause:</b> {row['Cause of Death']}<br>
        <b>Route:</b> {row.get(migration_route_col, 'Unknown')}
        """
        
        # Add marker to the cluster
        folium.CircleMarker(
            location=[row['map_latitude'], row['map_longitude']],
            radius=radius,
            popup=folium.Popup(popup_text, max_width=300),
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.6,
            weight=1
        ).add_to(marker_cluster)
    
    return m

def create_country_heatmap(data, country_column):
    """
    Create a heatmap of countries
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The filtered Missing Migrants dataset
    country_column : str
        The column name for country ('Country of Origin')
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Country heatmap
    """
    # Explode the Countries List column to count each country separately
    if country_column == 'Country of Origin' and 'Countries List' in data.columns:
        exploded_df = data.explode('Countries List')
        country_data = exploded_df.groupby('Countries List').agg({
            'Total Number of Dead and Missing': 'sum',
            'Incident Type': 'count'
        }).reset_index()
        country_data = country_data.rename(columns={
            'Countries List': 'Country',
            'Incident Type': 'Incident Count'
        })
    else:
        country_data = data.groupby(country_column).agg({
            'Total Number of Dead and Missing': 'sum',
            'Incident Type': 'count'
        }).reset_index()
        country_data = country_data.rename(columns={
            country_column: 'Country',
            'Incident Type': 'Incident Count'
        })
    
    # Sort and get top countries
    country_data = country_data.sort_values('Total Number of Dead and Missing', ascending=False)
    top_countries = country_data.head(30)
    
    fig = px.choropleth(
        top_countries,
        locations='Country',
        locationmode='country names',
        color='Total Number of Dead and Missing',
        hover_name='Country',
        color_continuous_scale='YlOrRd',
        projection='natural earth',
        height=600
    )
    
    fig.update_layout(
        title='Heatmap by Country of Origin (Top 30 Countries)',
        coloraxis_colorbar=dict(title="Number of Dead and Missing")
    )
    
    return fig
