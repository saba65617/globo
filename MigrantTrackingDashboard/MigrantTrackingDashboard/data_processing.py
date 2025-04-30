import pandas as pd
import numpy as np

def clean_data(df):
    """Clean and preprocess the dataset"""
    try:
        # Create a copy of the dataframe
        cleaned_df = df.copy()
        
        # Convert numeric columns to appropriate types
        numeric_columns = [
            'Number of Dead',
            'Minimum Estimated Number of Missing',
            'Total Number of Dead and Missing',
            'Number of Survivors',
            'Number of Females',
            'Number of Males',
            'Number of Children'
        ]
        
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce').fillna(0)
        
        # Convert year to integer
        if 'Incident year' in cleaned_df.columns:
            cleaned_df['Incident year'] = pd.to_numeric(cleaned_df['Incident year'], errors='coerce').fillna(0).astype(int)
        
        # Handle missing values
        cleaned_df = cleaned_df.fillna({
            'Region of Origin': 'Unknown',
            'Region of Incident': 'Unknown',
            'Country of Origin': 'Unknown',
            'Cause of Death': 'Unknown',
            'Migration route': 'Unknown',
            'Location of death': 'Unknown'
        })
        
        return cleaned_df
        
    except Exception as e:
        print(f"Error in data cleaning: {e}")
        return df  # Return original dataframe if cleaning fails 