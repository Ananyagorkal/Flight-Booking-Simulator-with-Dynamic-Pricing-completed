from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config_sqlite import get_db
from models import BookingCreate, BookingConfirmation, Booking as BookingModel
from services.booking_service import BookingService

router = APIRouter()
booking_service = BookingService()

@router.post("/", response_model=BookingConfirmation)
async def create_booking(booking_data: BookingCreate, db: Session = Depends(get_db)):
    """Create a new flight booking"""
    try:
        confirmation = booking_service.create_booking(booking_data, db)
        return confirmation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")

@router.get("/pnr/{pnr}", response_model=BookingConfirmation)
async def get_booking_by_pnr(pnr: str, db: Session = Depends(get_db)):
    """Get booking details by PNR"""
    confirmation = booking_service.get_booking_by_pnr(pnr, db)
    if not confirmation:
        raise HTTPException(status_code=404, detail="Booking not found")
    return confirmation

@router.delete("/pnr/{pnr}")
async def cancel_booking(pnr: str, db: Session = Depends(get_db)):
    """Cancel a booking by PNR"""
    success = booking_service.cancel_booking(pnr, db)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to cancel booking")
    return {"message": "Booking cancelled successfully", "pnr": pnr}

@router.get("/history/{passenger_email}", response_model=List[BookingConfirmation])
async def get_booking_history(passenger_email: str, db: Session = Depends(get_db)):
    """Get booking history for a passenger"""
    bookings = booking_service.get_booking_history(passenger_email, db)
    return bookings

@router.get("/", response_model=List[BookingModel])
async def get_all_bookings(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """Get all bookings with pagination (admin endpoint)"""
    from database import Booking
    
    offset = (page - 1) * page_size
    bookings = db.query(Booking).offset(offset).limit(page_size).all()
    
    return [BookingModel.from_orm(booking) for booking in bookings]
