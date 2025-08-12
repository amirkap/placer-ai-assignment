"""
Simple service layer tests - covers core business logic.
"""
import pytest
from app.database import SessionLocal
from app.services.poi_service import POIService
from app.schemas.poi import POIFilters


class TestPOIService:
    """Test POI service business logic"""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing"""
        db = SessionLocal()
        return POIService(db)
    
    def test_get_pois_basic(self, service):
        """Test basic POI retrieval"""
        pois, total = service.get_pois(POIFilters(), page=1, limit=5)
        
        assert isinstance(pois, list)
        assert isinstance(total, int)
        assert len(pois) <= 5
        assert total > 0
        
        # Check POI structure
        if pois:
            poi = pois[0]
            assert hasattr(poi, 'entity_id')
            assert hasattr(poi, 'name')
            assert hasattr(poi, 'chain_name')
            assert hasattr(poi, 'is_open')
    
    def test_chain_filtering(self, service):
        """Test chain name filtering works"""
        filters = POIFilters(chain_name="Walmart")
        pois, total = service.get_pois(filters, page=1, limit=10)
        
        # All results should contain Walmart
        for poi in pois:
            assert "walmart" in poi.chain_name.lower()
    
    def test_dma_filtering(self, service):
        """Test DMA filtering works"""
        filters = POIFilters(dma=577)
        pois, total = service.get_pois(filters, page=1, limit=10)
        
        # All results should have DMA 577
        for poi in pois:
            if poi.dma:  # Handle null values
                assert poi.dma == 577
    
    def test_status_filtering(self, service):
        """Test open/closed status filtering"""
        filters = POIFilters(is_open=True)
        pois, total = service.get_pois(filters, page=1, limit=10)
        
        # All results should be open
        for poi in pois:
            assert poi.is_open == True
    
    def test_summary_stats(self, service):
        """Test summary statistics calculation"""
        stats = service.get_summary_stats(POIFilters())
        
        assert stats.total_venues > 0
        assert stats.total_foot_traffic > 0
        assert isinstance(stats.total_venues, int)
        assert isinstance(stats.total_foot_traffic, int)
    
    def test_filtered_summary_stats(self, service):
        """Test summary stats with filters applied"""
        # Get stats for all venues
        all_stats = service.get_summary_stats(POIFilters())
        
        # Get stats for just Walmart
        walmart_stats = service.get_summary_stats(POIFilters(chain_name="Walmart"))
        
        # Walmart stats should be less than total
        assert walmart_stats.total_venues <= all_stats.total_venues
        assert walmart_stats.total_foot_traffic <= all_stats.total_foot_traffic
    
    def test_unique_values(self, service):
        """Test getting unique filter values"""
        chains = service.get_unique_values("chain_name")
        categories = service.get_unique_values("sub_category")
        
        assert isinstance(chains, list)
        assert isinstance(categories, list)
        assert len(chains) > 0
        assert len(categories) > 0
        
        # Should include common chains
        chain_names = [c.lower() for c in chains]
        assert any("walmart" in name for name in chain_names)
    
    def test_dma_values_parsing(self, service):
        """Test DMA values are properly parsed as integers"""
        dmas = service.get_dma_values()
        
        assert isinstance(dmas, list)
        assert len(dmas) > 0
        
        # All should be integers
        for dma in dmas:
            assert isinstance(dma, int)
            assert dma > 0
