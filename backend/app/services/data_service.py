import pandas as pd
from typing import List, Optional, Tuple
from datetime import datetime
import os
from app.models.poi import POI, EntityType
from app.schemas.poi import POIFilters, SummaryStats


class DataService:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load and preprocess the CSV data"""
        try:
            self.df = pd.read_csv(self.csv_path)
            
            # Clean and preprocess data
            self.df = self.df.fillna('')
            
            # Convert date columns
            for date_col in ['date_opened', 'date_closed']:
                self.df[date_col] = pd.to_datetime(
                    self.df[date_col], 
                    errors='coerce'
                ).dt.tz_localize(None)
            
            # Add is_open column
            self.df['is_open'] = self.df['date_closed'].isna()
            
            print(f"Loaded {len(self.df)} POI records")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def _apply_filters(self, df: pd.DataFrame, filters: POIFilters) -> pd.DataFrame:
        """Apply filters to the dataframe"""
        filtered_df = df.copy()
        
        if filters.chain_name:
            filtered_df = filtered_df[
                filtered_df['chain_name'].str.contains(filters.chain_name, case=False, na=False)
            ]
        
        if filters.dma is not None:
            filtered_df = filtered_df[filtered_df['dma'] == filters.dma]
        
        if filters.sub_category:
            filtered_df = filtered_df[
                filtered_df['sub_category'].str.contains(filters.sub_category, case=False, na=False)
            ]
        
        if filters.city:
            filtered_df = filtered_df[
                filtered_df['city'].str.contains(filters.city, case=False, na=False)
            ]
        
        if filters.state_code:
            filtered_df = filtered_df[
                filtered_df['state_code'].str.contains(filters.state_code, case=False, na=False)
            ]
        
        if filters.is_open is not None:
            filtered_df = filtered_df[filtered_df['is_open'] == filters.is_open]
        
        if filters.search:
            # Search across multiple text fields
            search_cols = ['name', 'chain_name', 'city', 'state_name', 'street_address']
            search_mask = pd.Series([False] * len(filtered_df))
            
            for col in search_cols:
                if col in filtered_df.columns:
                    search_mask = search_mask | filtered_df[col].str.contains(
                        filters.search, case=False, na=False
                    )
            
            filtered_df = filtered_df[search_mask]
        
        return filtered_df
    
    def get_pois(
        self, 
        filters: POIFilters, 
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[List[POI], int]:
        """Get paginated POIs with filters applied"""
        if self.df is None or self.df.empty:
            return [], 0
        
        # Apply filters
        filtered_df = self._apply_filters(self.df, filters)
        
        total = len(filtered_df)
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_df = filtered_df.iloc[start_idx:end_idx]
        
        # Convert to POI models
        pois = []
        for _, row in paginated_df.iterrows():
            try:
                poi_data = row.to_dict()
                
                # Handle NaN values and type conversions
                for key, value in poi_data.items():
                    if pd.isna(value):
                        if key in ['dma', 'cbsa']:
                            poi_data[key] = None
                        elif key in ['store_id']:
                            poi_data[key] = None
                        else:
                            poi_data[key] = '' if isinstance(value, str) else None
                    elif key == 'store_id' and value is not None:
                        # Convert store_id to string
                        poi_data[key] = str(int(value)) if not pd.isna(value) else None
                    elif key in ['dma', 'cbsa'] and value == '':
                        # Handle empty string values for integer fields
                        poi_data[key] = None
                
                # Convert entity_type to enum
                poi_data['entity_type'] = EntityType.VENUE
                
                poi = POI(**poi_data)
                pois.append(poi)
                
            except Exception as e:
                print(f"Error creating POI from row: {e}")
                continue
        
        return pois, total
    
    def get_summary_stats(self, filters: POIFilters) -> SummaryStats:
        """Get summary statistics for filtered data"""
        if self.df is None or self.df.empty:
            return SummaryStats(
                total_venues=0,
                total_foot_traffic=0,
                total_sales=0.0,
                avg_dwell_time=0.0,
                open_venues=0,
                closed_venues=0,
                unique_chains=0,
                unique_dmas=0
            )
        
        # Apply filters
        filtered_df = self._apply_filters(self.df, filters)
        
        if filtered_df.empty:
            return SummaryStats(
                total_venues=0,
                total_foot_traffic=0,
                total_sales=0.0,
                avg_dwell_time=0.0,
                open_venues=0,
                closed_venues=0,
                unique_chains=0,
                unique_dmas=0
            )
        
        return SummaryStats(
            total_venues=len(filtered_df),
            total_foot_traffic=int(filtered_df['foot_traffic'].sum()),
            total_sales=float(filtered_df['sales'].sum()),
            avg_dwell_time=float(filtered_df['avg_dwell_time_min'].mean()),
            open_venues=int(filtered_df['is_open'].sum()),
            closed_venues=int((~filtered_df['is_open']).sum()),
            unique_chains=int(filtered_df['chain_name'].nunique()),
            unique_dmas=int(filtered_df['dma'].nunique())
        )
    
    def get_unique_values(self, column: str) -> List[str]:
        """Get unique values for a specific column (for filters)"""
        if self.df is None or column not in self.df.columns:
            return []
        
        unique_vals = self.df[column].dropna().unique().tolist()
        return sorted([str(val) for val in unique_vals if val])
    
    def get_autocomplete_suggestions(self, query: str, field: str = None) -> List[str]:
        """Get autocomplete suggestions for search"""
        if self.df is None or not query:
            return []
        
        suggestions = set()
        
        # Define fields to search for autocomplete
        search_fields = {
            'name': 'name',
            'chain': 'chain_name',
            'city': 'city',
            'state': 'state_name',
            'state_code': 'state_code',
            'address': 'street_address'
        }
        
        if field and field in search_fields:
            # Search in specific field
            col = search_fields[field]
            if col in self.df.columns:
                matches = self.df[col].dropna().str.contains(query, case=False, na=False)
                suggestions.update(self.df.loc[matches, col].unique().tolist())
        else:
            # Search in all fields
            for col in search_fields.values():
                if col in self.df.columns:
                    matches = self.df[col].dropna().str.contains(query, case=False, na=False)
                    suggestions.update(self.df.loc[matches, col].unique().tolist())
        
        # Filter and sort results
        filtered_suggestions = [
            s for s in suggestions 
            if s and query.lower() in str(s).lower()
        ]
        
        return sorted(filtered_suggestions)[:10]  # Limit to 10 suggestions
    
    def get_export_data(self, filters: POIFilters) -> pd.DataFrame:
        """Get filtered data for export"""
        if self.df is None or self.df.empty:
            return pd.DataFrame()
        
        # Apply filters
        filtered_df = self._apply_filters(self.df, filters)
        
        # Select and rename columns for export
        export_columns = {
            'entity_id': 'Entity ID',
            'name': 'Name',
            'chain_name': 'Chain Name',
            'sub_category': 'Category',
            'city': 'City',
            'state_name': 'State',
            'postal_code': 'Postal Code',
            'street_address': 'Address',
            'dma': 'DMA',
            'foot_traffic': 'Foot Traffic',
            'sales': 'Sales',
            'avg_dwell_time_min': 'Avg Dwell Time (min)',
            'area_sqft': 'Area (sqft)',
            'ft_per_sqft': 'Foot Traffic per sqft',
            'is_open': 'Is Open',
            'date_opened': 'Date Opened',
            'date_closed': 'Date Closed'
        }
        
        export_df = filtered_df[list(export_columns.keys())].copy()
        export_df.columns = list(export_columns.values())
        
        return export_df
    
    def get_chain_performance_analytics(self) -> dict:
        """Get performance analytics by chain"""
        if self.df is None or self.df.empty:
            return {"chain_performance": []}
        
        chain_stats = self.df.groupby('chain_name').agg({
            'entity_id': 'count',
            'foot_traffic': ['sum', 'mean'],
            'sales': ['sum', 'mean'],
            'avg_dwell_time_min': 'mean',
            'is_open': 'sum'
        }).round(2)
        
        # Flatten multi-level columns
        chain_stats.columns = [
            'total_venues', 'total_foot_traffic', 'avg_foot_traffic',
            'total_sales', 'avg_sales', 'avg_dwell_time', 'open_venues'
        ]
        
        # Calculate additional metrics
        chain_stats['closed_venues'] = chain_stats['total_venues'] - chain_stats['open_venues']
        chain_stats['avg_sales_per_visitor'] = (chain_stats['total_sales'] / chain_stats['total_foot_traffic']).round(2)
        
        # Reset index to make chain_name a column
        chain_stats = chain_stats.reset_index()
        
        # Convert to list of dictionaries
        performance_data = chain_stats.to_dict('records')
        
        return {"chain_performance": performance_data}
    
    def get_dma_distribution(self) -> dict:
        """Get POI distribution by DMA"""
        if self.df is None or self.df.empty:
            return {"dma_distribution": []}
        
        dma_stats = self.df.groupby('dma').agg({
            'entity_id': 'count',
            'foot_traffic': 'sum',
            'sales': 'sum',
            'chain_name': 'nunique'
        }).round(2)
        
        dma_stats.columns = ['venue_count', 'total_foot_traffic', 'total_sales', 'unique_chains']
        dma_stats = dma_stats.reset_index()
        
        # Sort by total foot traffic descending
        dma_stats = dma_stats.sort_values('total_foot_traffic', ascending=False)
        
        # Take top 20 DMAs for visualization
        top_dmas = dma_stats.head(20).to_dict('records')
        
        return {"dma_distribution": top_dmas}
