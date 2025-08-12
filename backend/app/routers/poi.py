from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
from app.schemas.poi import (
    POIResponse, 
    PaginatedPOIResponse, 
    POIFilters, 
    PaginationParams,
    SummaryStats
)
from app.services.data_service import DataService
import math
import io
import pandas as pd

router = APIRouter(prefix="/api/v1", tags=["POI"])

# This will be injected as a dependency
data_service: Optional[DataService] = None


def get_data_service() -> DataService:
    if data_service is None:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return data_service


@router.get("/pois", response_model=PaginatedPOIResponse)
async def get_pois(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    chain_name: Optional[str] = Query(None, description="Filter by chain name"),
    dma: Optional[int] = Query(None, description="Filter by DMA"),
    sub_category: Optional[str] = Query(None, description="Filter by sub category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    is_open: Optional[bool] = Query(None, description="Filter by open/closed status"),
    search: Optional[str] = Query(None, description="Search across multiple fields"),
    service: DataService = Depends(get_data_service)
):
    """Get paginated list of POIs with filtering options"""
    
    filters = POIFilters(
        chain_name=chain_name,
        dma=dma,
        sub_category=sub_category,
        city=city,
        state_code=state_code,
        is_open=is_open,
        search=search
    )
    
    pois, total = service.get_pois(filters, page, limit)
    
    # Convert POI models to response schemas
    poi_responses = []
    for poi in pois:
        poi_responses.append(POIResponse(
            entity_id=poi.entity_id,
            name=poi.name,
            chain_name=poi.chain_name,
            sub_category=poi.sub_category,
            dma=poi.dma,
            city=poi.city,
            state_name=poi.state_name,
            foot_traffic=poi.foot_traffic,
            is_open=poi.is_open,
            sales=poi.sales,
            avg_dwell_time_min=poi.avg_dwell_time_min,
            area_sqft=poi.area_sqft,
            ft_per_sqft=poi.ft_per_sqft,
            street_address=poi.street_address,
            postal_code=poi.postal_code,
            date_opened=poi.date_opened,
            date_closed=poi.date_closed
        ))
    
    total_pages = math.ceil(total / limit) if total > 0 else 0
    
    return PaginatedPOIResponse(
        items=poi_responses,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/pois/summary", response_model=SummaryStats)
async def get_summary_stats(
    chain_name: Optional[str] = Query(None, description="Filter by chain name"),
    dma: Optional[int] = Query(None, description="Filter by DMA"),
    sub_category: Optional[str] = Query(None, description="Filter by sub category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    is_open: Optional[bool] = Query(None, description="Filter by open/closed status"),
    search: Optional[str] = Query(None, description="Search across multiple fields"),
    service: DataService = Depends(get_data_service)
):
    """Get summary statistics for POIs with filtering applied"""
    
    filters = POIFilters(
        chain_name=chain_name,
        dma=dma,
        sub_category=sub_category,
        city=city,
        state_code=state_code,
        is_open=is_open,
        search=search
    )
    
    return service.get_summary_stats(filters)


@router.get("/pois/filters/chains")
async def get_chain_names(service: DataService = Depends(get_data_service)):
    """Get list of unique chain names for filtering"""
    return {"chains": service.get_unique_values("chain_name")}


@router.get("/pois/filters/dmas")
async def get_dmas(service: DataService = Depends(get_data_service)):
    """Get list of unique DMAs for filtering"""
    dmas = service.get_unique_values("dma")
    # Convert to integers and filter out empty strings
    dma_ints = []
    for dma in dmas:
        try:
            if dma:
                dma_ints.append(int(float(dma)))
        except (ValueError, TypeError):
            continue
    return {"dmas": sorted(dma_ints)}


@router.get("/pois/filters/categories")
async def get_categories(service: DataService = Depends(get_data_service)):
    """Get list of unique categories for filtering"""
    return {"categories": service.get_unique_values("sub_category")}


@router.get("/pois/filters/cities")
async def get_cities(service: DataService = Depends(get_data_service)):
    """Get list of unique cities for filtering"""
    return {"cities": service.get_unique_values("city")}


@router.get("/pois/filters/states")
async def get_states(service: DataService = Depends(get_data_service)):
    """Get list of unique states for filtering"""
    return {"states": service.get_unique_values("state_code")}


@router.get("/pois/autocomplete")
async def get_autocomplete_suggestions(
    query: str = Query(..., min_length=1, description="Search query"),
    field: Optional[str] = Query(None, description="Specific field to search in"),
    service: DataService = Depends(get_data_service)
):
    """Get autocomplete suggestions for search"""
    suggestions = service.get_autocomplete_suggestions(query, field)
    return {"suggestions": suggestions}


@router.get("/pois/export/csv")
async def export_pois_csv(
    chain_name: Optional[str] = Query(None, description="Filter by chain name"),
    dma: Optional[int] = Query(None, description="Filter by DMA"),
    sub_category: Optional[str] = Query(None, description="Filter by sub category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    is_open: Optional[bool] = Query(None, description="Filter by open/closed status"),
    search: Optional[str] = Query(None, description="Search across multiple fields"),
    service: DataService = Depends(get_data_service)
):
    """Export filtered POI data as CSV"""
    
    filters = POIFilters(
        chain_name=chain_name,
        dma=dma,
        sub_category=sub_category,
        city=city,
        state_code=state_code,
        is_open=is_open,
        search=search
    )
    
    # Get all data (no pagination for export)
    export_data = service.get_export_data(filters)
    
    # Create CSV string
    output = io.StringIO()
    export_data.to_csv(output, index=False)
    output.seek(0)
    
    # Create streaming response
    def iter_csv():
        yield output.getvalue()
    
    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=poi_export.csv"}
    )


@router.get("/pois/analytics/chain-performance")
async def get_chain_performance(
    service: DataService = Depends(get_data_service)
):
    """Get performance analytics by chain"""
    return service.get_chain_performance_analytics()


@router.get("/pois/analytics/dma-distribution")
async def get_dma_distribution(
    service: DataService = Depends(get_data_service)
):
    """Get POI distribution by DMA for visualization"""
    return service.get_dma_distribution()
