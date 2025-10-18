from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db, Flight, Airport, Airline, SeatInventory
from models import FlightCreate, AirportCreate, AirlineCreate, SeatInventoryCreate

router = APIRouter()

@router.post("/flights/", response_model=dict)
async def create_flight(flight_data: FlightCreate, db: Session = Depends(get_db)):
    """Create a new flight (admin endpoint)"""
    try:
        flight = Flight(**flight_data.dict())
        db.add(flight)
        db.commit()
        db.refresh(flight)
        return {"message": "Flight created successfully", "flight_id": flight.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create flight: {str(e)}")

@router.post("/airports/", response_model=dict)
async def create_airport(airport_data: AirportCreate, db: Session = Depends(get_db)):
    """Create a new airport (admin endpoint)"""
    try:
        airport = Airport(**airport_data.dict())
        db.add(airport)
        db.commit()
        db.refresh(airport)
        return {"message": "Airport created successfully", "airport_id": airport.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create airport: {str(e)}")

@router.post("/airlines/", response_model=dict)
async def create_airline(airline_data: AirlineCreate, db: Session = Depends(get_db)):
    """Create a new airline (admin endpoint)"""
    try:
        airline = Airline(**airline_data.dict())
        db.add(airline)
        db.commit()
        db.refresh(airline)
        return {"message": "Airline created successfully", "airline_id": airline.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create airline: {str(e)}")

@router.post("/seat-inventory/", response_model=dict)
async def create_seat_inventory(inventory_data: SeatInventoryCreate, db: Session = Depends(get_db)):
    """Create seat inventory for a flight (admin endpoint)"""
    try:
        inventory = SeatInventory(**inventory_data.dict())
        db.add(inventory)
        db.commit()
        db.refresh(inventory)
        return {"message": "Seat inventory created successfully", "inventory_id": inventory.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create seat inventory: {str(e)}")

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics (admin endpoint)"""
    from database import Booking
    
    total_flights = db.query(Flight).count()
    total_bookings = db.query(Booking).count()
    confirmed_bookings = db.query(Booking).filter(Booking.status == "confirmed").count()
    cancelled_bookings = db.query(Booking).filter(Booking.status == "cancelled").count()
    
    return {
        "total_flights": total_flights,
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "booking_success_rate": (confirmed_bookings / total_bookings * 100) if total_bookings > 0 else 0
    }

@router.get("/flights/{flight_id}/inventory")
async def get_flight_inventory(flight_id: int, db: Session = Depends(get_db)):
    """Get seat inventory for a specific flight"""
    inventory = db.query(SeatInventory).filter(SeatInventory.flight_id == flight_id).all()
    
    if not inventory:
        raise HTTPException(status_code=404, detail="No inventory found for this flight")
    
    return [
        {
            "seat_class": item.seat_class.value,
            "total_seats": item.total_seats,
            "available_seats": item.available_seats,
            "booked_seats": item.booked_seats,
            "last_updated": item.last_updated
        }
        for item in inventory
    ]
