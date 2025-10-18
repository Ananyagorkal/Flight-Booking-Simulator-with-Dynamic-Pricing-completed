from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from config_sqlite import get_db, Flight, Airport, Airline
from models import FlightSearch, SearchResponse, Flight as FlightModel
from services.pricing_engine import PricingEngine

router = APIRouter()
pricing_engine = PricingEngine()

@router.get("/search", response_model=SearchResponse)
async def search_flights(
    departure_airport: str = Query(..., description="Departure airport code"),
    arrival_airport: str = Query(..., description="Arrival airport code"),
    departure_date: str = Query(..., description="Departure date (YYYY-MM-DD)"),
    return_date: Optional[str] = Query(None, description="Return date (YYYY-MM-DD)"),
    passengers: int = Query(1, ge=1, le=9, description="Number of passengers"),
    seat_class: Optional[str] = Query(None, description="Seat class filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Page size"),
    db: Session = Depends(get_db)
):
    """Search for flights between airports"""
    try:
        # Parse dates
        dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
        ret_date = None
        if return_date:
            ret_date = datetime.strptime(return_date, "%Y-%m-%d")
        
        # Get airport IDs
        dep_airport = db.query(Airport).filter(Airport.code == departure_airport.upper()).first()
        arr_airport = db.query(Airport).filter(Airport.code == arrival_airport.upper()).first()
        
        if not dep_airport:
            raise HTTPException(status_code=404, detail=f"Departure airport {departure_airport} not found")
        if not arr_airport:
            raise HTTPException(status_code=404, detail=f"Arrival airport {arrival_airport} not found")
        
        # Build query for outbound flights
        query = db.query(Flight).filter(
            Flight.departure_airport_id == dep_airport.id,
            Flight.arrival_airport_id == arr_airport.id,
            Flight.departure_time >= dep_date,
            Flight.departure_time < dep_date + timedelta(days=1),
            Flight.status.in_(["scheduled", "on_time"])
        )
        
        # Apply seat class filter if provided
        if seat_class:
            # This would require joining with seat inventory
            pass
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        flights = query.offset(offset).limit(page_size).all()
        
        # Convert to response models
        flight_models = []
        for flight in flights:
            flight_model = FlightModel.from_orm(flight)
            flight_models.append(flight_model)
        
        return SearchResponse(
            flights=flight_models,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/{flight_id}", response_model=FlightModel)
async def get_flight(flight_id: int, db: Session = Depends(get_db)):
    """Get flight details by ID"""
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    return FlightModel.from_orm(flight)

@router.get("/")
async def get_all_flights(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Page size"),
    db: Session = Depends(get_db)
):
    """Get all flights with pagination"""
    query = db.query(Flight)
    total_count = query.count()
    
    offset = (page - 1) * page_size
    flights = query.offset(offset).limit(page_size).all()
    
    flight_models = [FlightModel.from_orm(flight) for flight in flights]
    
    return {
        "flights": flight_models,
        "total_count": total_count,
        "page": page,
        "page_size": page_size
    }

@router.get("/airports/", response_model=List[dict])
async def get_airports(db: Session = Depends(get_db)):
    """Get all airports"""
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

@router.get("/airlines/", response_model=List[dict])
async def get_airlines(db: Session = Depends(get_db)):
    """Get all airlines"""
    airlines = db.query(Airline).all()
    return [
        {
            "id": airline.id,
            "code": airline.code,
            "name": airline.name,
            "logo_url": airline.logo_url
        }
        for airline in airlines
    ]
