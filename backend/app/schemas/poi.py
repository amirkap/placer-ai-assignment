from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EntityType(str, Enum):
    VENUE = "venue"


class POI(BaseModel):
    """Core POI model for internal use"""
    entity_id: str
    entity_type: EntityType
    name: str
    foot_traffic: int
    sales: float
    avg_dwell_time_min: float
    area_sqft: float
    ft_per_sqft: float
    geolocation: str
    country: str
    state_code: str
    state_name: str
    city: str
    postal_code: str
    formatted_city: str
    street_address: str
    sub_category: str
    dma: Optional[int] = None
    cbsa: Optional[int] = None
    chain_id: str
    chain_name: str
    store_id: Optional[str] = None
    date_opened: Optional[datetime] = None
    date_closed: Optional[datetime] = None
    
    @property
    def is_open(self) -> bool:
        """Determine if the POI is currently open based on date_closed"""
        return self.date_closed is None
    
    @classmethod
    def from_db_model(cls, db_model):
        """Create POI from SQLAlchemy model"""
        return cls(
            entity_id=db_model.entity_id,
            entity_type=EntityType.VENUE,
            name=db_model.name,
            foot_traffic=db_model.foot_traffic,
            sales=db_model.sales,
            avg_dwell_time_min=db_model.avg_dwell_time_min,
            area_sqft=db_model.area_sqft,
            ft_per_sqft=db_model.ft_per_sqft,
            geolocation=db_model.geolocation,
            country=db_model.country,
            state_code=db_model.state_code,
            state_name=db_model.state_name,
            city=db_model.city,
            postal_code=db_model.postal_code,
            formatted_city=db_model.formatted_city or db_model.city,
            street_address=db_model.street_address,
            sub_category=db_model.sub_category,
            dma=db_model.dma,
            cbsa=db_model.cbsa,
            chain_id=db_model.chain_id,
            chain_name=db_model.chain_name,
            store_id=db_model.store_id,
            date_opened=db_model.date_opened,
            date_closed=db_model.date_closed,
        )
    
    class Config:
        from_attributes = True


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
