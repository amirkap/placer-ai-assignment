"""
Utility functions for API route handlers to keep them thin and focused.
"""
from typing import Optional, List
from fastapi.responses import StreamingResponse
import math
import io
import pandas as pd

from app.schemas.poi import POIFilters, POIResponse, PaginatedPOIResponse, POI


def build_poi_filters(
    chain_name: Optional[str] = None,
    dma: Optional[int] = None,
    sub_category: Optional[str] = None,
    city: Optional[str] = None,
    state_code: Optional[str] = None,
    is_open: Optional[bool] = None,
    search: Optional[str] = None
) -> POIFilters:
    """Create POIFilters object from query parameters."""
    return POIFilters(
        chain_name=chain_name,
        dma=dma,
        sub_category=sub_category,
        city=city,
        state_code=state_code,
        is_open=is_open,
        search=search
    )


def convert_poi_to_response(poi: POI) -> POIResponse:
    """Convert internal POI model to API response schema."""
    return POIResponse(
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
    )


def build_paginated_response(
    pois: List[POI], 
    total: int, 
    page: int, 
    limit: int
) -> PaginatedPOIResponse:
    """Build paginated response with converted POI data."""
    # Convert POI models to response schemas
    poi_responses = [convert_poi_to_response(poi) for poi in pois]
    
    # Calculate pagination
    total_pages = math.ceil(total / limit) if total > 0 else 0
    
    return PaginatedPOIResponse(
        items=poi_responses,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )





def create_csv_streaming_response(
    export_data: pd.DataFrame, 
    filename: str = "poi_export.csv"
) -> StreamingResponse:
    """Create a streaming CSV response that handles large datasets gracefully.
    
    For millions of rows, this approach processes data in chunks to avoid
    memory issues.
    """
    
    def iter_csv():
        # Start with CSV header
        if not export_data.empty:
            yield export_data.iloc[:1].to_csv(index=False)  # Header row
            
            # Stream data in chunks to handle large datasets gracefully
            chunk_size = 1000  # Process 1000 rows at a time
            for i in range(1, len(export_data), chunk_size):
                chunk = export_data.iloc[i:i + chunk_size]
                # Skip header for subsequent chunks
                yield chunk.to_csv(index=False, header=False)
        else:
            # Empty dataset - just return header
            yield ",".join(export_data.columns) + "\n"
    
    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
