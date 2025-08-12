from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.poi import (
    POIResponse, 
    PaginatedPOIResponse, 
    POIFilters, 
    SummaryStats
)
from app.services.poi_service import POIService
from app.database import get_db
from app.utils.api_helpers import build_poi_filters

router = APIRouter(prefix="/api/v1", tags=["POI"])

# Database dependency injection - no global service needed


@router.get("/pois", response_model=PaginatedPOIResponse)
def get_pois(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    chain_name: Optional[str] = Query(None, description="Filter by chain name"),
    dma: Optional[int] = Query(None, description="Filter by DMA"),
    sub_category: Optional[str] = Query(None, description="Filter by sub category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    is_open: Optional[bool] = Query(None, description="Filter by open/closed status"),
    search: Optional[str] = Query(None, description="Search across multiple fields"),
    db: Session = Depends(get_db)
):
    """Get paginated list of POIs with filtering options"""
    filters = build_poi_filters(chain_name, dma, sub_category, city, state_code, is_open, search)
    service = POIService(db)
    return service.get_paginated_pois(filters, page, limit)


@router.get("/pois/summary", response_model=SummaryStats)
def get_summary_stats(
    chain_name: Optional[str] = Query(None, description="Filter by chain name"),
    dma: Optional[int] = Query(None, description="Filter by DMA"),
    sub_category: Optional[str] = Query(None, description="Filter by sub category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    is_open: Optional[bool] = Query(None, description="Filter by open/closed status"),
    search: Optional[str] = Query(None, description="Search across multiple fields"),
    db: Session = Depends(get_db)
):
    """Get summary statistics for POIs with filtering applied"""
    filters = build_poi_filters(chain_name, dma, sub_category, city, state_code, is_open, search)
    service = POIService(db)
    return service.get_summary_stats(filters)


@router.get("/pois/filters/chains")
def get_chain_names(db: Session = Depends(get_db)):
    """Get list of unique chain names for filtering"""
    service = POIService(db)
    return {"chains": service.get_unique_values("chain_name")}


@router.get("/pois/filters/dmas")
def get_dmas(db: Session = Depends(get_db)):
    """Get list of unique DMAs for filtering"""
    service = POIService(db)
    return {"dmas": service.get_dma_values()}


@router.get("/pois/filters/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get list of unique categories for filtering"""
    service = POIService(db)
    return {"categories": service.get_unique_values("sub_category")}


@router.get("/pois/filters/cities")
def get_cities(db: Session = Depends(get_db)):
    """Get list of unique cities for filtering"""
    service = POIService(db)
    return {"cities": service.get_unique_values("city")}


@router.get("/pois/filters/states")
def get_states(db: Session = Depends(get_db)):
    """Get list of unique states for filtering"""
    service = POIService(db)
    return {"states": service.get_unique_values("state_code")}


@router.get("/pois/autocomplete")
def get_autocomplete_suggestions(
    query: str = Query(..., min_length=1, description="Search query"),
    field: Optional[str] = Query(None, description="Specific field to search in"),
    db: Session = Depends(get_db)
):
    """Get autocomplete suggestions for search"""
    service = POIService(db)
    suggestions = service.get_autocomplete_suggestions(query, field)
    return {"suggestions": suggestions}


@router.get("/pois/export/csv")
def export_pois_csv(
    chain_name: Optional[str] = Query(None, description="Filter by chain name"),
    dma: Optional[int] = Query(None, description="Filter by DMA"),
    sub_category: Optional[str] = Query(None, description="Filter by sub category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    is_open: Optional[bool] = Query(None, description="Filter by open/closed status"),
    search: Optional[str] = Query(None, description="Search across multiple fields"),
    db: Session = Depends(get_db)
):
    """Export filtered POI data as CSV"""
    filters = build_poi_filters(chain_name, dma, sub_category, city, state_code, is_open, search)
    service = POIService(db)
    return service.create_csv_export(filters)


@router.get("/pois/analytics/chain-performance")
def get_chain_performance(
    db: Session = Depends(get_db)
):
    """Get performance analytics by chain"""
    service = POIService(db)
    return service.get_chain_performance_analytics()


@router.get("/pois/analytics/dma-distribution")
def get_dma_distribution(
    db: Session = Depends(get_db)
):
    """Get POI distribution by DMA for visualization"""
    service = POIService(db)
    return service.get_dma_distribution()
