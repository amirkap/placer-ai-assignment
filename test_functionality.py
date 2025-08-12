#!/usr/bin/env python3
"""
Simple test script to verify the Placer.ai POI Analytics functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.data_service import DataService
from backend.app.schemas.poi import POIFilters

def test_data_loading():
    """Test data loading and basic functionality"""
    print("🔍 Testing Data Loading...")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'Bigbox Stores Metrics.csv')
    service = DataService(csv_path)
    
    if service.df is None or service.df.empty:
        print("❌ Failed to load data")
        return False
    
    print(f"✅ Loaded {len(service.df)} POI records")
    return True

def test_filtering():
    """Test filtering functionality"""
    print("\n🔍 Testing Filtering...")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'Bigbox Stores Metrics.csv')
    service = DataService(csv_path)
    
    # Test basic filter
    filters = POIFilters(chain_name="Walmart")
    pois, total = service.get_pois(filters, page=1, limit=10)
    
    print(f"✅ Walmart filter: Found {total} locations, returned {len(pois)} in first page")
    
    # Test multiple filters
    filters = POIFilters(chain_name="Target", is_open=True)
    pois, total = service.get_pois(filters, page=1, limit=10)
    
    print(f"✅ Target + Open filter: Found {total} locations")
    
    return True

def test_summary_stats():
    """Test summary statistics"""
    print("\n🔍 Testing Summary Statistics...")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'Bigbox Stores Metrics.csv')
    service = DataService(csv_path)
    
    filters = POIFilters()
    stats = service.get_summary_stats(filters)
    
    print(f"✅ Total venues: {stats.total_venues}")
    print(f"✅ Total foot traffic: {stats.total_foot_traffic:,}")
    print(f"✅ Total sales: ${stats.total_sales:,.2f}")
    print(f"✅ Open venues: {stats.open_venues}")
    print(f"✅ Closed venues: {stats.closed_venues}")
    
    return True

def test_analytics():
    """Test analytics functions"""
    print("\n🔍 Testing Analytics...")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'Bigbox Stores Metrics.csv')
    service = DataService(csv_path)
    
    # Test chain performance
    chain_performance = service.get_chain_performance_analytics()
    chains = chain_performance['chain_performance']
    
    print(f"✅ Chain performance: Analyzed {len(chains)} chains")
    if chains:
        top_chain = chains[0]
        print(f"✅ Sample chain: {top_chain['chain_name']} - {top_chain['total_venues']} venues")
    
    # Test DMA distribution
    dma_dist = service.get_dma_distribution()
    dmas = dma_dist['dma_distribution']
    
    print(f"✅ DMA distribution: Analyzed {len(dmas)} DMAs")
    
    return True

def test_export():
    """Test export functionality"""
    print("\n🔍 Testing Export...")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'Bigbox Stores Metrics.csv')
    service = DataService(csv_path)
    
    filters = POIFilters(chain_name="Walmart")
    export_df = service.get_export_data(filters)
    
    print(f"✅ Export: Generated {len(export_df)} rows with {len(export_df.columns)} columns")
    print(f"✅ Export columns: {list(export_df.columns)[:5]}...")
    
    return True

def test_autocomplete():
    """Test autocomplete functionality"""
    print("\n🔍 Testing Autocomplete...")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'Bigbox Stores Metrics.csv')
    service = DataService(csv_path)
    
    suggestions = service.get_autocomplete_suggestions("Wal")
    print(f"✅ Autocomplete for 'Wal': {suggestions[:3]}...")
    
    suggestions = service.get_autocomplete_suggestions("New", "city")
    print(f"✅ City autocomplete for 'New': {suggestions[:3]}...")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Placer.ai POI Analytics Functionality\n")
    
    tests = [
        test_data_loading,
        test_filtering,
        test_summary_stats,
        test_analytics,
        test_export,
        test_autocomplete
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("\n🚀 To start the application:")
        print("   ./start.sh")
        print("\n📖 Or manually:")
        print("   Backend: cd backend && python main.py")
        print("   Frontend: cd frontend && npm start")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
