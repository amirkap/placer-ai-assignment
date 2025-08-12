from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class POIResponse(BaseModel):
    entity_id: str
    name: str
    chain_name: str
    sub_category: str
    dma: Optional[int]
    city: str
    state_name: str
    foot_traffic: int
    is_open: bool
    sales: float
    avg_dwell_time_min: float
    area_sqft: float
    ft_per_sqft: float
    street_address: str
    postal_code: str
    date_opened: Optional[datetime]
    date_closed: Optional[datetime]


class POIFilters(BaseModel):
    chain_name: Optional[str] = None
    dma: Optional[int] = None
    sub_category: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    is_open: Optional[bool] = None
    search: Optional[str] = None


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedPOIResponse(BaseModel):
    items: List[POIResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class SummaryStats(BaseModel):
    total_venues: int
    total_foot_traffic: int
    total_sales: float
    avg_dwell_time: float
    open_venues: int
    closed_venues: int
    unique_chains: int
    unique_dmas: int
