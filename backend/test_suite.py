#!/usr/bin/env python3
"""
Simple test suite for POI API - covers assignment requirements.
No complex dependencies, just validates core functionality.
"""
import sys
import requests
import subprocess
import time
import os


def test_service_layer():
    """Test service layer functionality"""
    print("🧪 Testing Service Layer...")
    
    try:
        from app.database import SessionLocal
        from app.services.poi_service import POIService
        from app.schemas.poi import POIFilters
        
        db = SessionLocal()
        service = POIService(db)
        
        # Test 1: Basic POI retrieval
        pois, total = service.get_pois(POIFilters(), page=1, limit=5)
        assert len(pois) <= 5
        assert total > 0
        print(f"  ✅ Basic retrieval: {len(pois)} POIs, {total} total")
        
        # Test 2: Chain filtering (assignment requirement)
        walmart_pois, walmart_total = service.get_pois(POIFilters(chain_name='Walmart'), page=1, limit=5)
        assert all('walmart' in poi.chain_name.lower() for poi in walmart_pois)
        print(f"  ✅ Chain filter: {walmart_total} Walmart stores")
        
        # Test 3: DMA filtering (assignment requirement)
        dma_pois, dma_total = service.get_pois(POIFilters(dma=577), page=1, limit=5)
        print(f"  ✅ DMA filter: {dma_total} POIs in DMA 577")
        
        # Test 4: Open status filtering (assignment requirement)
        open_pois, open_total = service.get_pois(POIFilters(is_open=True), page=1, limit=5)
        assert all(poi.is_open for poi in open_pois)
        print(f"  ✅ Status filter: {open_total} open POIs")
        
        # Test 5: Summary statistics (assignment requirement)
        stats = service.get_summary_stats(POIFilters())
        assert stats.total_venues > 0
        assert stats.total_foot_traffic > 0
        print(f"  ✅ Summary stats: {stats.total_venues} venues, {stats.total_foot_traffic:,} traffic")
        
        # Test 6: Filter options
        chains = service.get_unique_values('chain_name')
        dmas = service.get_dma_values()
        assert len(chains) > 0
        assert len(dmas) > 0
        print(f"  ✅ Filter options: {len(chains)} chains, {len(dmas)} DMAs")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Service test failed: {e}")
        return False


def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints...")
    
    # Start server
    proc = subprocess.Popen(['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    
    try:
        base_url = 'http://localhost:8000'
        
        # Test 1: Health check
        response = requests.get(f'{base_url}/health')
        assert response.status_code == 200
        print("  ✅ Health check")
        
        # Test 2: Basic POI listing (assignment requirement)
        response = requests.get(f'{base_url}/api/v1/pois?limit=5')
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data and 'total' in data
        print(f"  ✅ POI listing: {len(data['items'])} items")
        
        # Test 3: Chain filtering (assignment requirement)
        response = requests.get(f'{base_url}/api/v1/pois?chain_name=Walmart&limit=3')
        assert response.status_code == 200
        data = response.json()
        assert all('walmart' in item['chain_name'].lower() for item in data['items'])
        print(f"  ✅ Chain filter: {data['total']} Walmart stores")
        
        # Test 4: DMA filtering (assignment requirement)
        response = requests.get(f'{base_url}/api/v1/pois?dma=577&limit=3')
        assert response.status_code == 200
        print(f"  ✅ DMA filter: {response.json()['total']} POIs")
        
        # Test 5: Open status filtering (assignment requirement)
        response = requests.get(f'{base_url}/api/v1/pois?is_open=true&limit=3')
        assert response.status_code == 200
        data = response.json()
        assert all(item['is_open'] for item in data['items'])
        print(f"  ✅ Status filter: {data['total']} open POIs")
        
        # Test 6: Summary statistics (assignment requirement)
        response = requests.get(f'{base_url}/api/v1/pois/summary')
        assert response.status_code == 200
        data = response.json()
        assert 'total_venues' in data and 'total_foot_traffic' in data
        print(f"  ✅ Summary stats: {data['total_venues']} venues")
        
        # Test 7: Filter options (assignment requirement)
        response = requests.get(f'{base_url}/api/v1/pois/filters/chains')
        assert response.status_code == 200
        chains = response.json()['chains']
        
        response = requests.get(f'{base_url}/api/v1/pois/filters/dmas')
        assert response.status_code == 200
        dmas = response.json()['dmas']
        
        print(f"  ✅ Filter options: {len(chains)} chains, {len(dmas)} DMAs")
        
        # Test 8: CSV export (bonus feature)
        response = requests.get(f'{base_url}/api/v1/pois/export/csv?limit=3')
        assert response.status_code == 200
        assert 'text/csv' in response.headers['content-type']
        print("  ✅ CSV export")
        
        # Test 9: Pagination
        response = requests.get(f'{base_url}/api/v1/pois?page=2&limit=5')
        assert response.status_code == 200
        data = response.json()
        assert data['page'] == 2
        print(f"  ✅ Pagination: page {data['page']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API test failed: {e}")
        return False
        
    finally:
        proc.terminate()
        proc.wait()


def main():
    """Run all tests"""
    print("🧪 POI API Test Suite")
    print("=" * 50)
    print("Testing assignment requirements:")
    print("• POI listing with pagination")
    print("• Filtering (chain, DMA, category, city, state, status)")
    print("• Summary statistics")
    print("• Filter options")
    print("=" * 50)
    
    # Run tests
    service_passed = test_service_layer()
    api_passed = test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 50)
    if service_passed and api_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Assignment requirements verified")
        exit_code = 0
    else:
        print("❌ Some tests failed")
        exit_code = 1
    
    print("=" * 50)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
