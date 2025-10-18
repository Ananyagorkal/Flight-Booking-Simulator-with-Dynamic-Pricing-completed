from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config_sqlite import get_db, Flight
from models import PricingRequest, PricingResponse
from services.pricing_engine import PricingEngine

router = APIRouter()
pricing_engine = PricingEngine()

@router.post("/calculate", response_model=PricingResponse)
async def calculate_price(pricing_request: PricingRequest, db: Session = Depends(get_db)):
    """Calculate dynamic price for a flight and seat class"""
    flight = db.query(Flight).filter(Flight.id == pricing_request.flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    try:
        pricing = pricing_engine.calculate_dynamic_price(flight, pricing_request.seat_class, db)
        return pricing
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price calculation failed: {str(e)}")

@router.get("/flight/{flight_id}/class/{seat_class}", response_model=PricingResponse)
async def get_current_price(
    flight_id: int, 
    seat_class: str, 
    db: Session = Depends(get_db)
):
    """Get current price for a flight and seat class"""
    from models import SeatClass
    
    try:
        seat_class_enum = SeatClass(seat_class)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid seat class")
    
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    try:
        pricing = pricing_engine.calculate_dynamic_price(flight, seat_class_enum, db)
        return pricing
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price calculation failed: {str(e)}")

@router.get("/trend/{flight_id}/{seat_class}")
async def get_price_trend(
    flight_id: int,
    seat_class: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get price trend for a flight over time"""
    from models import SeatClass
    
    try:
        seat_class_enum = SeatClass(seat_class)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid seat class")
    
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    try:
        trend = pricing_engine.get_price_trend(flight_id, seat_class_enum, db, days)
        return {"flight_id": flight_id, "seat_class": seat_class, "trend": trend}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get price trend: {str(e)}")

@router.get("/compare/{flight_id}")
async def compare_prices(flight_id: int, db: Session = Depends(get_db)):
    """Compare prices across all seat classes for a flight"""
    from models import SeatClass
    
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    try:
        prices = {}
        for seat_class in SeatClass:
            pricing = pricing_engine.calculate_dynamic_price(flight, seat_class, db)
            prices[seat_class.value] = {
                "base_price": pricing.base_price,
                "current_price": pricing.current_price,
                "total_price": pricing.total_price,
                "demand_factor": pricing.demand_factor,
                "time_factor": pricing.time_factor,
                "seat_availability_factor": pricing.seat_availability_factor
            }
        
        return {
            "flight_id": flight_id,
            "flight_number": flight.flight_number,
            "prices": prices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price comparison failed: {str(e)}")
