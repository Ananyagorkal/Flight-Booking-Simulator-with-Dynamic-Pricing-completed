#!/usr/bin/env python3
"""
Simplified startup script that works with minimal dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def install_basic_packages():
    """Install only the essential packages"""
    print("Installing basic packages...")
    
    packages = [
        "fastapi",
        "uvicorn[standard]", 
        "python-multipart",
        "python-dotenv"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"SUCCESS: {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"WARNING: Failed to install {package}: {e}")
            print("Continuing with available packages...")

def create_simple_server():
    """Create a simple server that works without database"""
    print("Creating simple server...")
    
    server_code = '''
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
from datetime import datetime, timedelta
import random

app = FastAPI(
    title="Flight Booking Simulator API",
    description="Simple flight booking system",
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

# In-memory storage
flights_db = []
bookings_db = []

def generate_sample_flights():
    """Generate sample flights"""
    airports = [
        {"code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York"},
        {"code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles"},
        {"code": "LHR", "name": "London Heathrow Airport", "city": "London"},
        {"code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris"},
        {"code": "NRT", "name": "Narita International Airport", "city": "Tokyo"}
    ]
    
    airlines = [
        {"code": "AA", "name": "American Airlines"},
        {"code": "DL", "name": "Delta Air Lines"},
        {"code": "UA", "name": "United Airlines"},
        {"code": "BA", "name": "British Airways"}
    ]
    
    flights = []
    for i in range(20):
        dep_airport = random.choice(airports)
        arr_airport = random.choice([a for a in airports if a != dep_airport])
        airline = random.choice(airlines)
        
        dep_time = datetime.now() + timedelta(days=random.randint(1, 30), hours=random.randint(6, 22))
        arr_time = dep_time + timedelta(hours=random.randint(2, 8))
        
        base_price = random.randint(200, 1000)
        demand_factor = random.uniform(0.8, 1.5)
        time_factor = random.uniform(1.0, 1.8)
        availability_factor = random.uniform(1.0, 1.3)
        
        flight = {
            "id": i + 1,
            "flight_number": f"{airline['code']}{random.randint(100, 999)}",
            "airline": airline,
            "departure_airport": dep_airport,
            "arrival_airport": arr_airport,
            "departure_time": dep_time.isoformat(),
            "arrival_time": arr_time.isoformat(),
            "duration_minutes": int((arr_time - dep_time).total_seconds() / 60),
            "base_price": base_price,
            "current_price": round(base_price * demand_factor * time_factor * availability_factor, 2),
            "total_seats": random.randint(100, 300),
            "available_seats": random.randint(50, 250),
            "status": "scheduled"
        }
        flights.append(flight)
    
    return flights

# Initialize sample data
flights_db = generate_sample_flights()

@app.get("/")
async def root():
    return {"message": "Flight Booking Simulator API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/flights/search")
async def search_flights(
    departure_airport: str = None,
    arrival_airport: str = None,
    departure_date: str = None,
    passengers: int = 1
):
    """Search for flights"""
    filtered_flights = flights_db.copy()
    
    if departure_airport:
        filtered_flights = [f for f in filtered_flights if f["departure_airport"]["code"] == departure_airport]
    
    if arrival_airport:
        filtered_flights = [f for f in filtered_flights if f["arrival_airport"]["code"] == arrival_airport]
    
    return {
        "flights": filtered_flights[:10],  # Limit to 10 results
        "total_count": len(filtered_flights),
        "page": 1,
        "page_size": 10
    }

@app.get("/api/flights/airports/")
async def get_airports():
    """Get all airports"""
    airports = [
        {"id": 1, "code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "USA"},
        {"id": 2, "code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "USA"},
        {"id": 3, "code": "LHR", "name": "London Heathrow Airport", "city": "London", "country": "UK"},
        {"id": 4, "code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France"},
        {"id": 5, "code": "NRT", "name": "Narita International Airport", "city": "Tokyo", "country": "Japan"}
    ]
    return airports

@app.get("/api/flights/airlines/")
async def get_airlines():
    """Get all airlines"""
    airlines = [
        {"id": 1, "code": "AA", "name": "American Airlines", "logo_url": None},
        {"id": 2, "code": "DL", "name": "Delta Air Lines", "logo_url": None},
        {"id": 3, "code": "UA", "name": "United Airlines", "logo_url": None},
        {"id": 4, "code": "BA", "name": "British Airways", "logo_url": None}
    ]
    return airlines

@app.post("/api/bookings/")
async def create_booking(booking_data: dict):
    """Create a booking"""
    import string
    pnr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    booking = {
        "pnr": pnr,
        "booking_reference": booking_ref,
        "passenger_name": booking_data.get("passenger_name", "Demo Passenger"),
        "flight_details": next((f for f in flights_db if f["id"] == booking_data.get("flight_id")), None),
        "seat_class": booking_data.get("seat_class", "economy"),
        "seat_number": f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
        "price_paid": random.randint(200, 1000),
        "booking_date": datetime.now().isoformat(),
        "status": "confirmed"
    }
    
    bookings_db.append(booking)
    return booking

@app.get("/api/pricing/flight/{flight_id}/class/{seat_class}")
async def get_pricing(flight_id: int, seat_class: str):
    """Get pricing for a flight and seat class"""
    flight = next((f for f in flights_db if f["id"] == flight_id), None)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    multipliers = {"economy": 1.0, "premium_economy": 1.5, "business": 2.5, "first": 4.0}
    multiplier = multipliers.get(seat_class, 1.0)
    
    base_price = flight["base_price"]
    current_price = flight["current_price"]
    
    return {
        "flight_id": flight_id,
        "seat_class": seat_class,
        "base_price": base_price * multiplier,
        "current_price": current_price * multiplier,
        "total_price": current_price * multiplier,
        "demand_factor": 1.2,
        "time_factor": 1.1,
        "seat_availability_factor": 1.05
    }

if __name__ == "__main__":
    print("Starting Simple Flight Booking Simulator...")
    print("Backend API: http://localhost:8000")
    print("Frontend: Open frontend/index.html in your browser")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
'''
    
    with open("simple_server.py", "w", encoding="utf-8") as f:
        f.write(server_code)
    
    print("SUCCESS: Simple server created")

def main():
    """Main function"""
    print("Flight Booking Simulator - Simple Version")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("frontend").exists():
        print("ERROR: Frontend directory not found")
        return
    
    # Install basic packages
    install_basic_packages()
    
    # Create simple server
    create_simple_server()
    
    # Start server
    print("\nStarting server...")
    try:
        import uvicorn
        from simple_server import app
        
        print("Backend API: http://localhost:8000")
        print("Frontend: Open frontend/index.html in your browser")
        print("API Documentation: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the server")
        
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    except ImportError:
        print("ERROR: FastAPI not installed. Please run:")
        print("pip install fastapi uvicorn")
    except Exception as e:
        print(f"ERROR: Error starting server: {e}")

if __name__ == "__main__":
    main()
