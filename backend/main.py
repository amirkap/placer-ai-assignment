from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import poi
from app.services.data_service import DataService
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

# Initialize data service
csv_path = os.path.join(os.path.dirname(__file__), "..", "Bigbox Stores Metrics.csv")
data_service = DataService(csv_path)

# Inject data service into router
poi.data_service = data_service

# Include routers
app.include_router(poi.router)


@app.get("/")
async def root():
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
async def health_check():
    return {"status": "healthy", "data_loaded": len(data_service.df) if data_service.df is not None else 0}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
