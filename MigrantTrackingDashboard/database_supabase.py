import os
from supabase import create_client
import pandas as pd
from datetime import datetime

def get_supabase_client():
    """Create and return a Supabase client"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
    
    return create_client(url, key)

def setup_tables(supabase):
    """Create necessary tables in Supabase"""
    # Create incidents table
    incidents_query = """
    CREATE TABLE IF NOT EXISTS incidents (
        id SERIAL PRIMARY KEY,
        incident_type VARCHAR(255),
        incident_year INTEGER,
        reported_month VARCHAR(50),
        month_number INTEGER,
        region_of_origin VARCHAR(255),
        region_of_incident VARCHAR(255),
        country_of_origin TEXT,
        number_of_dead FLOAT,
        minimum_estimated_number_of_missing FLOAT,
        total_number_of_dead_and_missing FLOAT,
        number_of_survivors FLOAT,
        number_of_females FLOAT,
        number_of_males FLOAT,
        number_of_children FLOAT,
        cause_of_death VARCHAR(255),
        migration_route TEXT,
        location_of_death TEXT,
        information_source TEXT,
        coordinates TEXT,
        unsd_geographical_grouping VARCHAR(255),
        latitude FLOAT,
        longitude FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Create countries table
    countries_query = """
    CREATE TABLE IF NOT EXISTS countries (
        id SERIAL PRIMARY KEY,
        country_name VARCHAR(255) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Create linking table
    incident_countries_query = """
    CREATE TABLE IF NOT EXISTS incident_countries (
        id SERIAL PRIMARY KEY,
        incident_id INTEGER REFERENCES incidents(id),
        country_id INTEGER REFERENCES countries(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Execute queries using Supabase's REST API
    supabase.db.query(incidents_query).execute()
    supabase.db.query(countries_query).execute()
    supabase.db.query(incident_countries_query).execute()

def insert_data(supabase, df):
    """Insert data into Supabase tables"""
    # Process each row
    for _, row in df.iterrows():
        # Prepare incident data
        incident_data = {
            'incident_type': row.get('Incident Type'),
            'incident_year': int(row['Incident year']) if pd.notna(row['Incident year']) else None,
            'reported_month': row.get('Reported Month'),
            'month_number': row.get('Month Number'),
            'region_of_origin': row.get('Region of Origin'),
            'region_of_incident': row.get('Region of Incident'),
            'country_of_origin': row.get('Country of Origin'),
            'number_of_dead': float(row['Number of Dead']) if pd.notna(row['Number of Dead']) else 0,
            'minimum_estimated_number_of_missing': float(row['Minimum Estimated Number of Missing']) if pd.notna(row['Minimum Estimated Number of Missing']) else 0,
            'total_number_of_dead_and_missing': float(row['Total Number of Dead and Missing']) if pd.notna(row['Total Number of Dead and Missing']) else 0,
            'number_of_survivors': float(row['Number of Survivors']) if pd.notna(row['Number of Survivors']) else 0,
            'number_of_females': float(row['Number of Females']) if pd.notna(row['Number of Females']) else 0,
            'number_of_males': float(row['Number of Males']) if pd.notna(row['Number of Males']) else 0,
            'number_of_children': float(row['Number of Children']) if pd.notna(row['Number of Children']) else 0,
            'cause_of_death': row.get('Cause of Death'),
            'migration_route': row.get('Migration route'),
            'location_of_death': row.get('Location of death'),
            'information_source': row.get('Information Source'),
            'coordinates': row.get('Coordinates'),
            'unsd_geographical_grouping': row.get('UNSD Geographical Grouping'),
            'latitude': float(row['Latitude']) if pd.notna(row['Latitude']) else None,
            'longitude': float(row['Longitude']) if pd.notna(row['Longitude']) else None,
            'created_at': datetime.now().isoformat()
        }
        
        # Insert incident and get its ID
        result = supabase.table('incidents').insert(incident_data).execute()
        incident_id = result.data[0]['id']
        
        # Process countries
        if 'Countries List' in row and isinstance(row['Countries List'], list):
            for country_name in row['Countries List']:
                if pd.isna(country_name) or country_name == '':
                    continue
                
                # Insert country if it doesn't exist
                country_result = supabase.table('countries').insert({
                    'country_name': country_name
                }).execute()
                
                # Get country ID (either from insert or existing)
                if country_result.data:
                    country_id = country_result.data[0]['id']
                else:
                    # Get existing country ID
                    existing_country = supabase.table('countries').select('id').eq('country_name', country_name).execute()
                    country_id = existing_country.data[0]['id']
                
                # Create relationship
                supabase.table('incident_countries').insert({
                    'incident_id': incident_id,
                    'country_id': country_id
                }).execute()

def get_data(supabase, year_from=None, year_to=None, region=None, cause=None):
    """Get filtered data from Supabase"""
    query = supabase.table('incidents').select('*')
    
    if year_from and year_to:
        query = query.gte('incident_year', year_from).lte('incident_year', year_to)
    
    if region and region != "All Regions":
        query = query.eq('region_of_incident', region)
    
    if cause and cause != "All Causes":
        query = query.eq('cause_of_death', cause)
    
    result = query.execute()
    return pd.DataFrame(result.data)

def get_all_regions(supabase):
    """Get all unique regions from Supabase"""
    result = supabase.table('incidents').select('region_of_incident').execute()
    regions = pd.DataFrame(result.data)['region_of_incident'].unique()
    return ['All Regions'] + sorted([r for r in regions if r])

def get_all_causes(supabase):
    """Get all unique causes of death from Supabase"""
    result = supabase.table('incidents').select('cause_of_death').execute()
    causes = pd.DataFrame(result.data)['cause_of_death'].unique()
    return ['All Causes'] + sorted([c for c in causes if c])

def get_year_range(supabase):
    """Get the min and max years from the data"""
    min_year = supabase.table('incidents').select('incident_year').order('incident_year').limit(1).execute()
    max_year = supabase.table('incidents').select('incident_year').order('incident_year', desc=True).limit(1).execute()
    
    return {
        'min': min_year.data[0]['incident_year'],
        'max': max_year.data[0]['incident_year']
    } 