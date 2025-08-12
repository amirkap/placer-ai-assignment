#!/usr/bin/env python3
"""
Migration script to import CSV data into the database
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Add the parent directory to Python path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, create_tables, drop_tables
from app.models.poi import POIModel

def clean_data_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare DataFrame for database insertion"""
    
    # Make a copy to avoid modifying original
    df_clean = df.copy()
    
    # Fill NaN values appropriately
    df_clean = df_clean.fillna('')
    
    # Convert date columns
    for date_col in ['date_opened', 'date_closed']:
        df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors='coerce')
    
    # Add computed columns
    df_clean['is_open'] = df_clean['date_closed'].isna()
    df_clean['formatted_city'] = df_clean['city']  # Use city as formatted_city
    df_clean['country'] = 'United States'  # Default country
    
    return df_clean

def migrate_csv_to_database(csv_path: str, drop_existing: bool = False):
    """
    Migrate CSV data to database
    
    Args:
        csv_path: Path to the CSV file
        drop_existing: Whether to drop existing tables first
    """
    
    print("🚀 Starting CSV to Database Migration...")
    
    # Drop existing tables if requested
    if drop_existing:
        print("🗑️ Dropping existing tables...")
        drop_tables()
    
    # Create tables
    print("📁 Creating database tables...")
    create_tables()
    
    # Load CSV data
    print(f"📊 Loading CSV data from: {csv_path}")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} records from CSV")
    
    # Clean data
    print("🧹 Cleaning data for database...")
    df_clean = clean_data_for_db(df)
    
    # Insert into database
    print("💾 Inserting data into database...")
    db = SessionLocal()
    
    try:
        batch_size = 100
        total_records = len(df_clean)
        
        for i in range(0, total_records, batch_size):
            batch_df = df_clean.iloc[i:i + batch_size]
            
            for _, row in batch_df.iterrows():
                # Convert row to dict
                poi_data = row.to_dict()
                
                # Handle special data type conversions
                for key, value in poi_data.items():
                    if pd.isna(value):
                        if key in ['dma', 'cbsa']:
                            poi_data[key] = None
                        elif key in ['store_id']:
                            poi_data[key] = None
                        elif key in ['date_opened', 'date_closed']:
                            poi_data[key] = None
                        else:
                            poi_data[key] = '' if key in ['postal_code', 'street_address', 'geolocation'] else None
                    elif key == 'store_id' and value != '':
                        # Convert store_id to string
                        try:
                            poi_data[key] = str(int(float(value))) if value != '' else None
                        except (ValueError, TypeError):
                            poi_data[key] = str(value) if value else None
                    elif key in ['dma', 'cbsa'] and value == '':
                        poi_data[key] = None
                
                # Create POI model instance
                poi = POIModel(**poi_data)
                db.add(poi)
            
            # Commit batch
            db.commit()
            print(f"   Processed {min(i + batch_size, total_records)}/{total_records} records")
        
        print(f"✅ Successfully migrated {total_records} POI records to database")
        
        # Verify the data
        count = db.query(POIModel).count()
        print(f"🔍 Database verification: {count} records stored")
        
        # Show some sample data
        sample_pois = db.query(POIModel).limit(3).all()
        print("\n📋 Sample records:")
        for poi in sample_pois:
            print(f"   - {poi.name} ({poi.chain_name}) in {poi.city}, {poi.state_code}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main migration function"""
    
    # Get CSV path
    script_dir = os.path.dirname(__file__)
    csv_path = os.path.join(script_dir, '..', '..', 'Bigbox Stores Metrics.csv')
    csv_path = os.path.abspath(csv_path)
    
    print(f"Looking for CSV file at: {csv_path}")
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at: {csv_path}")
        print("Please ensure the CSV file is in the correct location.")
        sys.exit(1)
    
    try:
        # Run migration
        migrate_csv_to_database(csv_path, drop_existing=True)
        print("\n🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"\n💥 Migration failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
