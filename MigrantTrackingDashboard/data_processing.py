import pandas as pd
import numpy as np

def clean_data(df):
    """
    Clean and preprocess the Missing Migrants dataset
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The raw Missing Migrants dataset
    
    Returns:
    --------
    pandas.DataFrame
        The cleaned dataset
    """
    # Create a copy of the dataframe
    cleaned_df = df.copy()
    
    # Convert year to numeric
    cleaned_df['Incident year'] = pd.to_numeric(cleaned_df['Incident year'], errors='coerce')
    
    # Extract month number from 'Reported Month'
    month_mapping = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    cleaned_df['Month Number'] = cleaned_df['Reported Month'].map(month_mapping)
    
    # Fill missing values
    numeric_cols = [
        'Number of Dead', 'Minimum Estimated Number of Missing', 
        'Total Number of Dead and Missing', 'Number of Survivors',
        'Number of Females', 'Number of Males', 'Number of Children'
    ]
    
    for col in numeric_cols:
        cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce').fillna(0)
    
    # Extract coordinates for mapping
    cleaned_df['Coordinates'] = cleaned_df['Coordinates'].astype(str)
    
    def extract_coordinates(coord_str):
        try:
            if pd.isna(coord_str) or coord_str == 'nan':
                return np.nan, np.nan
            
            # Remove any extra spaces and split by comma
            parts = coord_str.replace(' ', '').split(',')
            
            if len(parts) >= 2:
                lat = float(parts[0])
                lon = float(parts[1])
                return lat, lon
            else:
                return np.nan, np.nan
        except:
            return np.nan, np.nan
    
    # Apply the function to extract coordinates
    cleaned_df['Latitude'], cleaned_df['Longitude'] = zip(*cleaned_df['Coordinates'].apply(extract_coordinates))
    
    # Clean region fields
    region_columns = ['Region of Origin', 'Region of Incident']
    for col in region_columns:
        # Fill missing values with 'Unknown'
        cleaned_df[col] = cleaned_df[col].fillna('Unknown')
        
        # Clean up values with special characters or annotations
        cleaned_df[col] = cleaned_df[col].str.replace(' (P)', '', regex=False)
    
    # Clean country of origin
    cleaned_df['Country of Origin'] = cleaned_df['Country of Origin'].fillna('Unknown')
    
    # Process countries with multiple entries
    def split_countries(country_str):
        if pd.isna(country_str) or country_str == 'Unknown':
            return ['Unknown']
        
        # Split by comma or other common separators
        if ',' in country_str:
            return [c.strip() for c in country_str.split(',')]
        return [country_str]
    
    # Create a list of countries for each entry
    cleaned_df['Countries List'] = cleaned_df['Country of Origin'].apply(split_countries)
    
    # Clean cause of death
    cleaned_df['Cause of Death'] = cleaned_df['Cause of Death'].fillna('Unknown')
    
    # Clean migration route
    cleaned_df['Migration route'] = cleaned_df['Migration route'].fillna('Unknown route')
    
    # Add a datetime column for time-based analysis
    cleaned_df['Date'] = pd.to_datetime(
        {
            'year': cleaned_df['Incident year'],
            'month': cleaned_df['Month Number'],
            'day': 1
        },
        errors='coerce'
    )
    
    return cleaned_df

def get_yearly_data(df):
    """
    Aggregate data by year
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The cleaned Missing Migrants dataset
    
    Returns:
    --------
    pandas.DataFrame
        Data aggregated by year
    """
    yearly_data = df.groupby('Incident year').agg({
        'Total Number of Dead and Missing': 'sum',
        'Number of Dead': 'sum',
        'Minimum Estimated Number of Missing': 'sum',
        'Incident Type': 'count'
    }).reset_index()
    
    yearly_data = yearly_data.rename(columns={'Incident Type': 'Incident Count'})
    
    return yearly_data

def get_monthly_data(df):
    """
    Aggregate data by month
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The cleaned Missing Migrants dataset
    
    Returns:
    --------
    pandas.DataFrame
        Data aggregated by month
    """
    monthly_data = df.groupby(['Incident year', 'Month Number', 'Reported Month']).agg({
        'Total Number of Dead and Missing': 'sum',
        'Incident Type': 'count'
    }).reset_index()
    
    monthly_data = monthly_data.rename(columns={'Incident Type': 'Incident Count'})
    
    return monthly_data

def get_region_data(df, region_column):
    """
    Aggregate data by region
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The cleaned Missing Migrants dataset
    region_column : str
        The column name for region ('Region of Origin' or 'Region of Incident')
    
    Returns:
    --------
    pandas.DataFrame
        Data aggregated by region
    """
    region_data = df.groupby(region_column).agg({
        'Total Number of Dead and Missing': 'sum',
        'Incident Type': 'count'
    }).reset_index()
    
    region_data = region_data.rename(columns={'Incident Type': 'Incident Count'})
    region_data = region_data.sort_values('Total Number of Dead and Missing', ascending=False)
    
    return region_data

def get_cause_data(df):
    """
    Aggregate data by cause of death
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The cleaned Missing Migrants dataset
    
    Returns:
    --------
    pandas.DataFrame
        Data aggregated by cause of death
    """
    cause_data = df.groupby('Cause of Death').agg({
        'Total Number of Dead and Missing': 'sum',
        'Incident Type': 'count'
    }).reset_index()
    
    cause_data = cause_data.rename(columns={'Incident Type': 'Incident Count'})
    cause_data = cause_data.sort_values('Total Number of Dead and Missing', ascending=False)
    
    return cause_data

def get_route_data(df):
    """
    Aggregate data by migration route
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The cleaned Missing Migrants dataset
    
    Returns:
    --------
    pandas.DataFrame
        Data aggregated by migration route
    """
    # Handle both possible column names for migration route
    migration_route_col = 'Migration Route'
    
    # Check if the column exists, if not, try alternate spellings
    if migration_route_col not in df.columns:
        if 'Migration route' in df.columns:
            migration_route_col = 'Migration route'
        elif 'migration_route' in df.columns:
            migration_route_col = 'migration_route'
    
    # Filter out unknown routes
    route_df = df[df[migration_route_col] != 'Unknown route'].copy()
    
    route_data = route_df.groupby(migration_route_col).agg({
        'Total Number of Dead and Missing': 'sum',
        'Incident Type': 'count'
    }).reset_index()
    
    route_data = route_data.rename(columns={'Incident Type': 'Incident Count'})
    route_data = route_data.sort_values('Total Number of Dead and Missing', ascending=False)
    
    # Get only top 15 routes
    top_routes = route_data.head(15)
    
    return top_routes

def get_demographic_data(df):
    """
    Prepare demographic data for gender and age analysis
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The cleaned Missing Migrants dataset
    
    Returns:
    --------
    dict
        Dictionary containing gender and age data
    """
    # Sum up the gender counts
    total_females = df['Number of Females'].sum()
    total_males = df['Number of Males'].sum()
    total_children = df['Number of Children'].sum()
    total_unknown = df['Total Number of Dead and Missing'].sum() - (total_females + total_males + total_children)
    
    # Create gender dataframe
    gender_data = pd.DataFrame({
        'Gender': ['Female', 'Male', 'Children', 'Unknown'],
        'Count': [total_females, total_males, total_children, total_unknown]
    })
    
    # Create age dataframe (assuming children are under 18)
    age_data = pd.DataFrame({
        'Age Group': ['Children (<18)', 'Adults (18+)', 'Unknown'],
        'Count': [
            total_children, 
            total_males + total_females, 
            total_unknown
        ]
    })
    
    return {
        'gender': gender_data,
        'age': age_data
    }
