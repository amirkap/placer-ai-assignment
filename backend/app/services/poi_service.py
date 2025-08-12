from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, case
from typing import List, Optional, Tuple
import pandas as pd

from app.models.poi import POIModel
from app.schemas.poi import POI
from app.schemas.poi import POIFilters, SummaryStats, PaginatedPOIResponse


class POIService:
    def __init__(self, db: Session):
        """Initialize POI service with database session"""
        self.db = db
    
    def _apply_filters_to_query(self, query, filters: POIFilters):
        """Apply filters to SQLAlchemy query"""
        
        if filters.chain_name:
            query = query.filter(POIModel.chain_name.ilike(f"%{filters.chain_name}%"))
        
        if filters.dma is not None:
            query = query.filter(POIModel.dma == filters.dma)
        
        if filters.sub_category:
            query = query.filter(POIModel.sub_category.ilike(f"%{filters.sub_category}%"))
        
        if filters.city:
            query = query.filter(POIModel.city.ilike(f"%{filters.city}%"))
        
        if filters.state_code:
            query = query.filter(POIModel.state_code.ilike(f"%{filters.state_code}%"))
        
        if filters.is_open is not None:
            query = query.filter(POIModel.is_open == filters.is_open)
        
        if filters.search:
            # Optimized search: prioritize prefix matches (faster with indexes)
            search_term = filters.search.strip()
            
            # For exact matches or prefix searches (most efficient)
            exact_conditions = [
                POIModel.chain_name.ilike(f"{search_term}%"),  # Prefix match (fastest)
                POIModel.name.ilike(f"{search_term}%"),       # Prefix match (fastest)
                POIModel.city.ilike(f"{search_term}%"),       # Prefix match (fastest)
            ]
            
            # For partial matches (slower but comprehensive)
            partial_conditions = [
                POIModel.chain_name.ilike(f"%{search_term}%"),
                POIModel.name.ilike(f"%{search_term}%"),
                POIModel.city.ilike(f"%{search_term}%"),
                POIModel.street_address.ilike(f"%{search_term}%")
            ]
            
            # Use prefix matching first (leverages indexes better)
            if len(search_term) >= 2:  # Only for meaningful searches
                search_filter = or_(*exact_conditions, *partial_conditions)
            else:
                search_filter = or_(*exact_conditions)  # Short queries: prefix only
                
            query = query.filter(search_filter)
        
        return query
    
    def _poi_model_to_pydantic(self, poi_model: POIModel) -> POI:
        """Convert SQLAlchemy model to Pydantic model"""
        return poi_model.to_pydantic()
    
    def get_pois(self, filters: POIFilters, page: int = 1, limit: int = 20) -> Tuple[List[POI], int]:
        """Get paginated POIs with optimized database queries"""
        
        # Build base query
        query = self.db.query(POIModel)
        
        # Apply filters
        query = self._apply_filters_to_query(query, filters)
        
        # Optimize: Get total count efficiently
        # For large datasets, use approximate count for better performance
        if limit <= 100:  # For small pages, exact count is fine
            total = query.count()
        else:  # For large exports, approximate count
            total = query.limit(10000).count()  # Cap at reasonable limit
        
        # Apply default sorting for consistent results (uses foot_traffic index)
        query = query.order_by(POIModel.foot_traffic.desc(), POIModel.entity_id)
        
        # Apply pagination and execute
        poi_models = query.offset((page - 1) * limit).limit(limit).all()
        
        # Convert to Pydantic models
        pois = [self._poi_model_to_pydantic(poi_model) for poi_model in poi_models]
        
        return pois, total
    
    def get_paginated_pois(self, filters: POIFilters, page: int = 1, limit: int = 20) -> PaginatedPOIResponse:
        """Get paginated POIs with response schema conversion (service layer)"""
        from app.utils.api_helpers import build_paginated_response
        
        pois, total = self.get_pois(filters, page, limit)
        return build_paginated_response(pois, total, page, limit)
    
    def get_summary_stats(self, filters: POIFilters) -> SummaryStats:
        """Get summary statistics using SQL aggregation"""
        
        # Build base query
        query = self.db.query(POIModel)
        
        # Apply filters
        query = self._apply_filters_to_query(query, filters)
        
        # Use SQL aggregation functions
        result = query.with_entities(
            func.count(POIModel.entity_id).label('total_venues'),
            func.sum(POIModel.foot_traffic).label('total_foot_traffic'),
            func.sum(POIModel.sales).label('total_sales'),
            func.avg(POIModel.avg_dwell_time_min).label('avg_dwell_time'),
            func.sum(case((POIModel.is_open == True, 1), else_=0)).label('open_venues'),
            func.count(func.distinct(POIModel.chain_name)).label('unique_chains'),
            func.count(func.distinct(POIModel.dma)).label('unique_dmas')
        ).first()
        
        total_venues = result.total_venues or 0
        open_venues = result.open_venues or 0
        
        return SummaryStats(
            total_venues=total_venues,
            total_foot_traffic=result.total_foot_traffic or 0,
            total_sales=float(result.total_sales or 0),
            avg_dwell_time=float(result.avg_dwell_time or 0),
            open_venues=open_venues,
            closed_venues=total_venues - open_venues,
            unique_chains=result.unique_chains or 0,
            unique_dmas=result.unique_dmas or 0
        )
    
    def get_unique_values(self, column: str) -> List[str]:
        """Get unique values for a column using SQL DISTINCT"""
        
        column_map = {
            'chain_name': POIModel.chain_name,
            'city': POIModel.city,
            'state_code': POIModel.state_code,
            'sub_category': POIModel.sub_category,
            'dma': POIModel.dma
        }
        
        if column not in column_map:
            return []
        
        db_column = column_map[column]
        values = self.db.query(db_column).distinct().filter(db_column.isnot(None)).all()
        return sorted([str(value[0]) for value in values if value[0] and str(value[0]).strip()])
    
    def get_dma_values(self) -> List[int]:
        """Get unique DMA values as properly parsed integers"""
        from app.utils.api_helpers import parse_dma_values
        
        dma_strings = self.get_unique_values("dma")
        return parse_dma_values(dma_strings)
    
    def get_autocomplete_suggestions(self, query: str, field: str = None) -> List[str]:
        """Get autocomplete suggestions using database search"""
        if not query:
            return []
        
        suggestions = set()
        
        # Define fields to search for autocomplete
        search_fields = {
            'name': POIModel.name,
            'chain': POIModel.chain_name,
            'city': POIModel.city,
            'state': POIModel.state_name,
            'state_code': POIModel.state_code,
            'address': POIModel.street_address
        }
        
        if field and field in search_fields:
            # Search in specific field
            db_column = search_fields[field]
            results = self.db.query(db_column).filter(
                db_column.ilike(f"%{query}%")
            ).distinct().limit(10).all()
            suggestions.update([str(r[0]) for r in results if r[0] and str(r[0]).strip()])
        else:
            # Search in all fields
            for column in search_fields.values():
                results = self.db.query(column).filter(
                    column.ilike(f"%{query}%")
                ).distinct().limit(5).all()
                suggestions.update([str(r[0]) for r in results if r[0] and str(r[0]).strip()])
        
        # Filter and sort results
        filtered_suggestions = [
            s for s in suggestions 
            if s and query.lower() in str(s).lower()
        ]
        
        return sorted(filtered_suggestions)[:10]  # Limit to 10 suggestions
    
    def get_export_data(self, filters: POIFilters) -> pd.DataFrame:
        """Get filtered data for export as DataFrame"""
        
        # Build base query
        query = self.db.query(POIModel)
        
        # Apply filters
        query = self._apply_filters_to_query(query, filters)
        
        # Get all matching records
        poi_models = query.all()
        
        # Convert to list of dictionaries
        data = []
        for poi in poi_models:
            data.append({
                'Entity ID': poi.entity_id,
                'Name': poi.name,
                'Chain Name': poi.chain_name,
                'Category': poi.sub_category,
                'City': poi.city,
                'State': poi.state_name,
                'Postal Code': poi.postal_code,
                'Address': poi.street_address,
                'DMA': poi.dma,
                'Foot Traffic': poi.foot_traffic,
                'Sales': poi.sales,
                'Avg Dwell Time (min)': poi.avg_dwell_time_min,
                'Area (sqft)': poi.area_sqft,
                'Foot Traffic per sqft': poi.ft_per_sqft,
                'Is Open': poi.is_open,
                'Date Opened': poi.date_opened,
                'Date Closed': poi.date_closed
            })
        
        return pd.DataFrame(data)
    
    def create_csv_export(self, filters: POIFilters):
        """Create CSV export with streaming response"""
        from app.utils.api_helpers import create_csv_streaming_response
        
        export_data = self.get_export_data(filters)
        return create_csv_streaming_response(export_data)
    
    def get_chain_performance_analytics(self) -> dict:
        """Get performance analytics by chain using SQL aggregation"""
        
        results = self.db.query(
            POIModel.chain_name,
            func.count(POIModel.entity_id).label('total_venues'),
            func.sum(POIModel.foot_traffic).label('total_foot_traffic'),
            func.avg(POIModel.foot_traffic).label('avg_foot_traffic'),
            func.sum(POIModel.sales).label('total_sales'),
            func.avg(POIModel.sales).label('avg_sales'),
            func.avg(POIModel.avg_dwell_time_min).label('avg_dwell_time'),
            func.sum(case((POIModel.is_open == True, 1), else_=0)).label('open_venues')
        ).group_by(POIModel.chain_name).all()
        
        performance_data = []
        for result in results:
            total_venues = result.total_venues or 0
            open_venues = result.open_venues or 0
            total_foot_traffic = result.total_foot_traffic or 0
            total_sales = result.total_sales or 0
            
            performance_data.append({
                'chain_name': result.chain_name,
                'total_venues': total_venues,
                'total_foot_traffic': total_foot_traffic,
                'avg_foot_traffic': round(result.avg_foot_traffic or 0, 2),
                'total_sales': round(total_sales, 2),
                'avg_sales': round(result.avg_sales or 0, 2),
                'avg_dwell_time': round(result.avg_dwell_time or 0, 2),
                'open_venues': open_venues,
                'closed_venues': total_venues - open_venues,
                'avg_sales_per_visitor': round(total_sales / total_foot_traffic, 2) if total_foot_traffic > 0 else 0
            })
        
        return {"chain_performance": performance_data}
    
    def get_dma_distribution(self) -> dict:
        """Get POI distribution by DMA using SQL aggregation"""
        
        results = self.db.query(
            POIModel.dma,
            func.count(POIModel.entity_id).label('venue_count'),
            func.sum(POIModel.foot_traffic).label('total_foot_traffic'),
            func.sum(POIModel.sales).label('total_sales'),
            func.count(func.distinct(POIModel.chain_name)).label('unique_chains')
        ).filter(POIModel.dma.isnot(None)).group_by(POIModel.dma).order_by(
            desc(func.sum(POIModel.foot_traffic))
        ).limit(20).all()
        
        dma_data = []
        for result in results:
            dma_data.append({
                'dma': result.dma,
                'venue_count': result.venue_count,
                'total_foot_traffic': result.total_foot_traffic or 0,
                'total_sales': round(result.total_sales or 0, 2),
                'unique_chains': result.unique_chains
            })
        
        return {"dma_distribution": dma_data}