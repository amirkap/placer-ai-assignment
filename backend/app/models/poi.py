from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Index
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class POIModel(Base):
    """SQLAlchemy model for POI data storage"""
    __tablename__ = "pois"
    
    # Primary key
    entity_id = Column(String, primary_key=True, index=True)
    
    # Basic information
    entity_type = Column(String, nullable=False, default="venue")
    name = Column(String, nullable=False, index=True)
    chain_name = Column(String, nullable=False, index=True)
    chain_id = Column(String, nullable=False)
    store_id = Column(String, nullable=True)
    
    # Location data
    city = Column(String, nullable=False, index=True)
    state_code = Column(String, nullable=False, index=True)
    state_name = Column(String, nullable=False)
    postal_code = Column(String)
    formatted_city = Column(String)
    street_address = Column(Text)
    geolocation = Column(Text)
    country = Column(String, default="United States")
    dma = Column(Integer, nullable=True, index=True)
    cbsa = Column(Integer, nullable=True)
    
    # Metrics
    foot_traffic = Column(Integer, default=0, index=True)
    sales = Column(Float, default=0.0)
    avg_dwell_time_min = Column(Float, default=0.0)
    area_sqft = Column(Float, default=0.0)
    ft_per_sqft = Column(Float, default=0.0)
    
    # Categories and status
    sub_category = Column(String, index=True)
    is_open = Column(Boolean, default=True, index=True)
    date_opened = Column(DateTime, nullable=True)
    date_closed = Column(DateTime, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<POI(id={self.entity_id}, name={self.name}, chain={self.chain_name})>"

    def to_pydantic(self):
        """Convert SQLAlchemy model to Pydantic POI model"""
        from app.schemas.poi import POI
        return POI.from_db_model(self)

# Composite indexes for better query performance

# Core filter combinations from assignment requirements
Index('idx_poi_chain_dma', POIModel.chain_name, POIModel.dma)        # Chain + Market area
Index('idx_poi_city_state', POIModel.city, POIModel.state_code)      # Location filtering
Index('idx_poi_chain_open', POIModel.chain_name, POIModel.is_open)   # Chain + Status
