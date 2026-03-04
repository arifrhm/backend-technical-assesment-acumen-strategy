from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import os

from database import init_db, get_db
from models.customer import Customer
from services.ingestion import IngestionService

app = FastAPI(title="FastAPI Pipeline Service", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


@app.post("/api/ingest")
async def ingest_data(db: Session = Depends(get_db)):
    """
    Fetch all data from Flask API and upsert into PostgreSQL.
    """
    try:
        ingestion_service = IngestionService()
        result = await ingestion_service.ingest_and_save(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers")
def get_customers(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get paginated list of customers from database.
    Query params: page (default: 1), limit (default: 10)
    """
    try:
        # Get total count
        total = db.query(Customer).count()

        # Calculate pagination
        offset = (page - 1) * limit

        # Get paginated data
        customers = db.query(Customer).offset(offset).limit(limit).all()

        return {
            "data": [customer.to_dict() for customer in customers],
            "total": total,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """
    Get a single customer by ID.
    Returns 404 if customer not found.
    """
    try:
        customer = db.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()

        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

        return customer.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    """
    try:
        customer_count = db.query(Customer).count()
        return {
            "status": "healthy",
            "service": "fastapi-pipeline-service",
            "database": "connected",
            "total_customers": customer_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "fastapi-pipeline-service",
            "error": str(e)
        }
