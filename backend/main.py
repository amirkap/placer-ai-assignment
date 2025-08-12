from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.routers import poi
from app.database import create_tables, get_db
from app.models.poi import POIModel
import os

# Initialize FastAPI app
app = FastAPI(
    title="Placer.ai POI Analytics API",
    description="API for analyzing Point of Interest (POI) data from Big Box Stores",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
@app.on_event("startup")
def startup_event():
    """Initialize database and load data on startup"""
    from app.models.poi import POIModel
    from app.database import SessionLocal
    import pandas as pd
    from datetime import datetime
    
    # Create tables
    create_tables()
    print("Database tables created/verified")
    
    # Check if data exists, if not load from CSV
    db = SessionLocal()
    try:
        poi_count = db.query(POIModel).count()
        if poi_count == 0:
            print("📊 No data found, loading from CSV...")
            load_csv_data_on_startup(db)
        else:
            print(f"✅ Database ready with {poi_count} POI records")
    finally:
        db.close()


def load_csv_data_on_startup(db):
    """Load CSV data into database on startup if empty"""
    import pandas as pd
    try:
        # Find CSV file
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'Bigbox Stores Metrics.csv')
        csv_path = os.path.abspath(csv_path)
        
        if not os.path.exists(csv_path):
            print(f"⚠️ CSV file not found at: {csv_path}")
            print("Skipping data loading - will serve empty results")
            return
        
        print(f"📂 Loading CSV data from: {csv_path}")
        
        # Read and clean CSV data
        df = pd.read_csv(csv_path)
        df = df.fillna('')
        
        # Add computed columns
        df['date_opened'] = pd.to_datetime(df['date_opened'], errors='coerce')
        df['date_closed'] = pd.to_datetime(df['date_closed'], errors='coerce')
        df['is_open'] = df['date_closed'].isna()
        df['formatted_city'] = df['city']
        df['country'] = 'United States'
        
        # Insert data in batches
        batch_size = 100
        total_records = len(df)
        
        for i in range(0, total_records, batch_size):
            batch_df = df.iloc[i:i + batch_size]
            
            for _, row in batch_df.iterrows():
                poi_data = row.to_dict()
                
                # Handle data type conversions
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
                        try:
                            poi_data[key] = str(int(float(value))) if value != '' else None
                        except (ValueError, TypeError):
                            poi_data[key] = str(value) if value else None
                    elif key in ['dma', 'cbsa'] and value == '':
                        poi_data[key] = None
                
                poi = POIModel(**poi_data)
                db.add(poi)
            
            db.commit()
            if i % 500 == 0:  # Progress update every 500 records
                print(f"   Loaded {min(i + batch_size, total_records)}/{total_records} records...")
        
        final_count = db.query(POIModel).count()
        print(f"✅ Successfully loaded {final_count} POI records from CSV")
        
    except Exception as e:
        print(f"❌ Failed to load CSV data: {e}")
        db.rollback()
        print("⚠️ App will start with empty database")

# Include routers
app.include_router(poi.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Placer.ai POI Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "pois": "/api/v1/pois",
            "summary": "/api/v1/pois/summary",
            "filters": {
                "chains": "/api/v1/pois/filters/chains",
                "dmas": "/api/v1/pois/filters/dmas",
                "categories": "/api/v1/pois/filters/categories",
                "cities": "/api/v1/pois/filters/cities",
                "states": "/api/v1/pois/filters/states"
            },
            "autocomplete": "/api/v1/pois/autocomplete"
        }
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database status"""
    try:
        # Check database connection and count POIs
        poi_count = db.query(POIModel).count()
        return {
            "status": "healthy",
            "database": "connected", 
            "data_loaded": poi_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
