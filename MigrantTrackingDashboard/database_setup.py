import os
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine

def connect_to_db():
    """Establish a connection to the PostgreSQL database"""
    conn = psycopg2.connect(
        dbname=os.environ['PGDATABASE'],
        user=os.environ['PGUSER'],
        password=os.environ['PGPASSWORD'],
        host=os.environ['PGHOST'],
        port=os.environ['PGPORT']
    )
    conn.autocommit = True
    return conn

def create_tables(conn):
    """Create the necessary tables for the missing migrants dataset"""
    cursor = conn.cursor()
    
    # Create main incidents table
    cursor.execute("""
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
    """)
    
    # Create countries table for countries of origin (many-to-many relationship)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        id SERIAL PRIMARY KEY,
        country_name VARCHAR(255) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Create linking table for incidents and countries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incident_countries (
        id SERIAL PRIMARY KEY,
        incident_id INTEGER REFERENCES incidents(id),
        country_id INTEGER REFERENCES countries(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.close()
    print("Tables created successfully.")

def clean_data(df):
    """Clean and preprocess the Missing Migrants dataset"""
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
    
    # Fill missing values in numeric columns
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
    
    return cleaned_df

def insert_data(conn, df):
    """Insert data into the database tables"""
    cursor = conn.cursor()
    
    # Insert data into incidents table
    for index, row in df.iterrows():
        cursor.execute("""
        INSERT INTO incidents (
            incident_type, incident_year, reported_month, month_number,
            region_of_origin, region_of_incident, country_of_origin,
            number_of_dead, minimum_estimated_number_of_missing, total_number_of_dead_and_missing,
            number_of_survivors, number_of_females, number_of_males, number_of_children,
            cause_of_death, migration_route, location_of_death, information_source,
            coordinates, unsd_geographical_grouping, latitude, longitude
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """, (
            row.get('Incident Type', None),
            int(row['Incident year']) if not pd.isna(row['Incident year']) else None,
            row.get('Reported Month', None),
            row.get('Month Number', None),
            row.get('Region of Origin', None),
            row.get('Region of Incident', None),
            row.get('Country of Origin', None),
            float(row['Number of Dead']) if not pd.isna(row['Number of Dead']) else 0,
            float(row['Minimum Estimated Number of Missing']) if not pd.isna(row['Minimum Estimated Number of Missing']) else 0,
            float(row['Total Number of Dead and Missing']) if not pd.isna(row['Total Number of Dead and Missing']) else 0,
            float(row['Number of Survivors']) if not pd.isna(row['Number of Survivors']) else 0,
            float(row['Number of Females']) if not pd.isna(row['Number of Females']) else 0,
            float(row['Number of Males']) if not pd.isna(row['Number of Males']) else 0,
            float(row['Number of Children']) if not pd.isna(row['Number of Children']) else 0,
            row.get('Cause of Death', None),
            row.get('Migration route', None),
            row.get('Location of death', None),
            row.get('Information Source', None),
            row.get('Coordinates', None),
            row.get('UNSD Geographical Grouping', None),
            float(row['Latitude']) if not pd.isna(row['Latitude']) else None,
            float(row['Longitude']) if not pd.isna(row['Longitude']) else None
        ))
        
        incident_id = cursor.fetchone()[0]
        
        # Process countries and create relationships
        if 'Countries List' in row and isinstance(row['Countries List'], list):
            for country_name in row['Countries List']:
                if pd.isna(country_name) or country_name == '':
                    continue
                    
                # Insert country if it doesn't exist
                cursor.execute("""
                INSERT INTO countries (country_name)
                VALUES (%s)
                ON CONFLICT (country_name) DO NOTHING
                RETURNING id;
                """, (country_name,))
                
                result = cursor.fetchone()
                if result:
                    country_id = result[0]
                else:
                    cursor.execute("SELECT id FROM countries WHERE country_name = %s", (country_name,))
                    country_id = cursor.fetchone()[0]
                
                # Create relationship between incident and country
                cursor.execute("""
                INSERT INTO incident_countries (incident_id, country_id)
                VALUES (%s, %s);
                """, (incident_id, country_id))
    
    cursor.close()
    print(f"Inserted {len(df)} records into the database.")

def main():
    print("Setting up database for Missing Migrants Analysis...")
    
    # Check if connection to database works
    try:
        conn = connect_to_db()
        print("Connected to PostgreSQL database successfully.")
        
        # Create the database tables
        create_tables(conn)
        
        # Read the data from CSV
        print("Loading and cleaning data...")
        df = pd.read_csv("attached_assets/Global Missing Migrants Dataset.csv")
        cleaned_df = clean_data(df)
        
        # Insert data into the database
        print("Inserting data into database...")
        insert_data(conn, cleaned_df)
        
        # Create an index on common query fields
        cursor = conn.cursor()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_incident_year ON incidents(incident_year);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_region_incident ON incidents(region_of_incident);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cause_death ON incidents(cause_of_death);")
        cursor.close()
        
        print("Database setup completed successfully!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    main()