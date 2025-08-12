from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Database configuration - using SQLite for simplicity
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./poi_database.db")

# Create engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified")

def drop_tables():
    """Drop all database tables (for testing)"""
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped")
