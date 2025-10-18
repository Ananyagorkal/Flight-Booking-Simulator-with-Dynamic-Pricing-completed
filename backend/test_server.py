#!/usr/bin/env python3
"""
Simple test server to verify the setup
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_sqlite import engine, Base, get_db, Airport, Airline, Flight
from sqlalchemy.orm import Session

app = FastAPI(title="Flight Booking Test API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/")
async def root():
    return {"message": "Flight Booking Simulator API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/flights/airports/")
async def get_airports():
    """Get all airports"""
    try:
        db = next(get_db())
        airports = db.query(Airport).all()
        return [
            {
                "id": airport.id,
                "code": airport.code,
                "name": airport.name,
                "city": airport.city,
                "country": airport.country
            }
            for airport in airports
        ]
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/coupons/")
async def get_coupons():
    """Get all coupons"""
    try:
        from config_sqlite import Coupon
        db = next(get_db())
        coupons = db.query(Coupon).filter(Coupon.is_active == True).all()
        return {
            "coupons": [
                {
                    "id": coupon.id,
                    "code": coupon.code,
                    "name": coupon.name,
                    "description": coupon.description,
                    "discount_type": coupon.discount_type.value,
                    "discount_value": coupon.discount_value,
                    "min_amount": coupon.min_amount,
                    "max_discount": coupon.max_discount
                }
                for coupon in coupons
            ]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Start server
    print("🚀 Starting test server on http://localhost:8000")
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
