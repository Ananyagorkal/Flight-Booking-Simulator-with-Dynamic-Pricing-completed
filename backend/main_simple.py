from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# Simple in-memory database for demo
flights_db = []
bookings_db = []

app = FastAPI(
    title="Flight Booking Simulator API",
    description="A simple flight booking system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return {"message": "Flight Booking Simulator API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/flights/search")
async def search_flights():
    # Return sample flights
    sample_flights = [
        {
            "id": 1,
            "flight_number": "AA100",
            "departure_airport": {"code": "JFK", "name": "John F. Kennedy International Airport"},
            "arrival_airport": {"code": "LAX", "name": "Los Angeles International Airport"},
            "departure_time": "2024-01-15T08:00:00",
            "arrival_time": "2024-01-15T11:00:00",
            "base_price": 299.99,
            "available_seats": 150,
            "status": "scheduled"
        }
    ]
    return {"flights": sample_flights, "total_count": 1, "page": 1, "page_size": 10}

@app.get("/api/flights/airports/")
async def get_airports():
    return [
        {"id": 1, "code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "USA"},
        {"id": 2, "code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "USA"},
        {"id": 3, "code": "LHR", "name": "London Heathrow Airport", "city": "London", "country": "UK"}
    ]

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

