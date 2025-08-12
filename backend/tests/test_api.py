"""
Simple API tests for POI endpoints - covers assignment requirements only.
"""
import pytest
from starlette.testclient import TestClient
from main import app

# Create test client using Starlette's TestClient directly
client = TestClient(app)


class TestPOIAPI:
    """Test core POI API functionality"""
    
    def test_health_check(self):
        """Test basic health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "data_loaded" in data
    
    def test_get_pois_basic(self):
        """Test basic POI listing"""
        response = client.get("/api/v1/pois")
        assert response.status_code == 200
        data = response.json()
        
        # Check pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert data["page"] == 1
        assert data["limit"] == 20
        assert len(data["items"]) <= 20
    
    def test_chain_filter(self):
        """Test chain name filtering (assignment requirement)"""
        response = client.get("/api/v1/pois?chain_name=Walmart")
        assert response.status_code == 200
        data = response.json()
        
        # All results should be Walmart
        for item in data["items"]:
            assert "walmart" in item["chain_name"].lower()
    
    def test_dma_filter(self):
        """Test DMA filtering (assignment requirement)"""
        response = client.get("/api/v1/pois?dma=577")
        assert response.status_code == 200
        data = response.json()
        
        # All results should have DMA 577
        for item in data["items"]:
            if item["dma"]:  # Handle null DMA values
                assert item["dma"] == 577
    
    def test_open_status_filter(self):
        """Test open/closed status filtering (assignment requirement)"""
        response = client.get("/api/v1/pois?is_open=true")
        assert response.status_code == 200
        data = response.json()
        
        # All results should be open
        for item in data["items"]:
            assert item["is_open"] == True
    
    def test_pagination(self):
        """Test pagination functionality"""
        # Test first page
        response1 = client.get("/api/v1/pois?limit=5&page=1")
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["items"]) <= 5
        
        # Test second page
        response2 = client.get("/api/v1/pois?limit=5&page=2")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Items should be different
        if len(data2["items"]) > 0:
            assert data1["items"][0]["entity_id"] != data2["items"][0]["entity_id"]
    
    def test_summary_stats(self):
        """Test summary statistics (assignment requirement)"""
        response = client.get("/api/v1/pois/summary")
        assert response.status_code == 200
        data = response.json()
        
        # Check required metrics
        assert "total_venues" in data
        assert "total_foot_traffic" in data
        assert isinstance(data["total_venues"], int)
        assert isinstance(data["total_foot_traffic"], int)
        assert data["total_venues"] > 0
    
    def test_filter_options(self):
        """Test filter option endpoints"""
        # Test chains
        response = client.get("/api/v1/pois/filters/chains")
        assert response.status_code == 200
        data = response.json()
        assert "chains" in data
        assert len(data["chains"]) > 0
        
        # Test DMAs
        response = client.get("/api/v1/pois/filters/dmas")
        assert response.status_code == 200
        data = response.json()
        assert "dmas" in data
        assert len(data["dmas"]) > 0
        
        # Test categories
        response = client.get("/api/v1/pois/filters/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
    
    def test_csv_export(self):
        """Test CSV export functionality"""
        response = client.get("/api/v1/pois/export/csv?limit=5")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        
        # Check CSV content
        content = response.content.decode()
        lines = content.split('\n')
        assert len(lines) >= 2  # Header + at least one data row
        assert "Entity ID" in lines[0]  # Check header
    
    def test_search_functionality(self):
        """Test search across multiple fields"""
        response = client.get("/api/v1/pois?search=Target")
        assert response.status_code == 200
        data = response.json()
        
        # Should find Target stores
        if data["total"] > 0:
            found_target = False
            for item in data["items"]:
                if "target" in item["chain_name"].lower() or "target" in item["name"].lower():
                    found_target = True
                    break
            assert found_target
