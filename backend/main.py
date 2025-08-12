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
    """Initialize database on startup"""
    create_tables()
    print("Database tables created/verified")

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
