from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.customer import Base
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@postgres:5432/customer_db')

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
