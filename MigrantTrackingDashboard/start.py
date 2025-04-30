import os
import pandas as pd
from database_supabase import get_supabase_client, setup_tables, insert_data

def load_data():
    """Load data into Supabase database"""
    print("Loading data into Supabase database...")
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    # Create tables
    setup_tables(supabase)
    
    # Load and clean data
    print("Loading and cleaning data...")
    df = pd.read_csv("attached_assets/Global Missing Migrants Dataset.csv")
    
    # Insert data
    print("Inserting data into Supabase...")
    insert_data(supabase, df)
    
    print("Data loading complete!")

def main():
    """Main function to setup and start the application"""
    print("="*50)
    print("Starting Missing Migrants Dashboard Setup")
    print("="*50)
    
    # Check for required environment variables
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("\nError: Missing required environment variables!")
        print("Please set the following environment variables:")
        print("- SUPABASE_URL: Your Supabase project URL")
        print("- SUPABASE_KEY: Your Supabase project API key")
        return
    
    # Step 1: Load data into Supabase
    try:
        load_data()
    except Exception as e:
        print(f"\nError loading data: {e}")
        return
    
    # Step 2: Provide instructions
    print("\nSetup complete!")
    print("\nTo run the application:")
    print("1. Make sure you have the required Python packages installed:")
    print("   pip install -r requirements.txt")
    print("\n2. Run the Streamlit application:")
    print("   streamlit run app.py")
    print("\nThe dashboard will be available at http://localhost:5000")
    print("\nThank you for using the Missing Migrants Dashboard!")

if __name__ == "__main__":
    main()