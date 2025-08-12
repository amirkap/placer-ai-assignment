"""
Test configuration and fixtures.
"""
import pytest
import sys
import os

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment - ensure database exists"""
    from app.database import create_tables
    create_tables()
    yield
