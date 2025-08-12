from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class EntityType(str, Enum):
    VENUE = "venue"


class POI(BaseModel):
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
    
    class Config:
        from_attributes = True
