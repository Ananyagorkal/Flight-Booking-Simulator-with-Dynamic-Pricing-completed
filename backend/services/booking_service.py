import string
import random
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from config_sqlite import Booking, Flight, SeatInventory, BookingStatus
from models import BookingCreate, BookingConfirmation
from services.pricing_engine import PricingEngine

class BookingService:
    def __init__(self):
        self.pricing_engine = PricingEngine()
    
    def generate_pnr(self) -> str:
        """Generate a unique 6-character PNR"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def generate_booking_reference(self) -> str:
        """Generate a unique booking reference"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    def assign_seat_number(self, flight_id: int, seat_class: str, db: Session) -> Optional[str]:
        """Assign a seat number based on availability and class"""
        # This is a simplified seat assignment
        # In a real system, you'd have a more complex seat map
        seat_inventory = db.query(SeatInventory).filter(
            SeatInventory.flight_id == flight_id,
            SeatInventory.seat_class == seat_class
        ).first()
        
        if not seat_inventory or seat_inventory.available_seats <= 0:
            return None
        
        # Generate seat number based on class
        if seat_class == "economy":
            seat_number = f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
        elif seat_class == "premium_economy":
            seat_number = f"{random.randint(1, 20)}{random.choice(['A', 'B', 'C', 'D'])}"
        elif seat_class == "business":
            seat_number = f"{random.randint(1, 10)}{random.choice(['A', 'B', 'C', 'D'])}"
        else:  # first
            seat_number = f"{random.randint(1, 5)}{random.choice(['A', 'B'])}"
        
        return seat_number
    
    def create_booking(self, booking_data: BookingCreate, db: Session) -> BookingConfirmation:
        """Create a new booking with concurrency control"""
        # Check if flight exists and is available
        flight = db.query(Flight).filter(Flight.id == booking_data.flight_id).first()
        if not flight:
            raise ValueError("Flight not found")
        
        if flight.status.value in ["cancelled", "departed", "arrived"]:
            raise ValueError("Flight is not available for booking")
        
        # Check seat availability
        seat_inventory = db.query(SeatInventory).filter(
            SeatInventory.flight_id == booking_data.flight_id,
            SeatInventory.seat_class == booking_data.seat_class
        ).first()
        
        if not seat_inventory or seat_inventory.available_seats <= 0:
            raise ValueError("No seats available for the selected class")
        
        # Calculate current price
        pricing = self.pricing_engine.calculate_dynamic_price(flight, booking_data.seat_class, db)
        
        # Generate unique identifiers
        pnr = self.generate_pnr()
        booking_reference = self.generate_booking_reference()
        
        # Ensure PNR is unique
        while db.query(Booking).filter(Booking.pnr == pnr).first():
            pnr = self.generate_pnr()
        
        # Ensure booking reference is unique
        while db.query(Booking).filter(Booking.booking_reference == booking_reference).first():
            booking_reference = self.generate_booking_reference()
        
        # Assign seat number
        seat_number = self.assign_seat_number(booking_data.flight_id, booking_data.seat_class.value, db)
        
        # Create booking
        booking = Booking(
            pnr=pnr,
            flight_id=booking_data.flight_id,
            passenger_name=booking_data.passenger_name,
            passenger_email=booking_data.passenger_email,
            passenger_phone=booking_data.passenger_phone,
            seat_class=booking_data.seat_class,
            seat_number=seat_number,
            price_paid=pricing.total_price,
            status=BookingStatus.CONFIRMED,
            booking_reference=booking_reference
        )
        
        try:
            db.add(booking)
            db.flush()  # Flush to get the booking ID
            
            # Update seat inventory atomically
            self.pricing_engine.update_seat_inventory(
                booking_data.flight_id, 
                booking_data.seat_class, 
                1, 
                db
            )
            
            # Update flight available seats
            flight.available_seats -= 1
            flight.updated_at = datetime.utcnow()
            
            db.commit()
            
            # Return booking confirmation
            return BookingConfirmation(
                pnr=booking.pnr,
                booking_reference=booking.booking_reference,
                passenger_name=booking.passenger_name,
                passenger_email=booking.passenger_email,
                passenger_phone=booking.passenger_phone,
                flight_details=flight,
                seat_class=booking.seat_class,
                seat_number=booking.seat_number,
                price_paid=booking.price_paid,
                booking_date=booking.created_at,
                status=booking.status
            )
            
        except IntegrityError:
            db.rollback()
            raise ValueError("Booking failed due to concurrency conflict. Please try again.")
    
    def get_booking_by_pnr(self, pnr: str, db: Session) -> Optional[BookingConfirmation]:
        """Get booking details by PNR"""
        booking = db.query(Booking).filter(Booking.pnr == pnr).first()
        if not booking:
            return None
        
        return BookingConfirmation(
            pnr=booking.pnr,
            booking_reference=booking.booking_reference,
            passenger_name=booking.passenger_name,
            passenger_email=booking.passenger_email,
            passenger_phone=booking.passenger_phone,
            flight_details=booking.flight,
            seat_class=booking.seat_class,
            seat_number=booking.seat_number,
            price_paid=booking.price_paid,
            booking_date=booking.created_at,
            status=booking.status
        )
    
    def cancel_booking(self, pnr: str, db: Session) -> bool:
        """Cancel a booking"""
        booking = db.query(Booking).filter(Booking.pnr == pnr).first()
        if not booking:
            return False
        
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
            return False
        
        # Update booking status
        booking.status = BookingStatus.CANCELLED
        booking.updated_at = datetime.utcnow()
        
        # Release seat back to inventory
        seat_inventory = db.query(SeatInventory).filter(
            SeatInventory.flight_id == booking.flight_id,
            SeatInventory.seat_class == booking.seat_class
        ).first()
        
        if seat_inventory:
            seat_inventory.available_seats += 1
            seat_inventory.booked_seats -= 1
            seat_inventory.last_updated = datetime.utcnow()
        
        # Update flight available seats
        flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
        if flight:
            flight.available_seats += 1
            flight.updated_at = datetime.utcnow()
        
        db.commit()
        return True
    
    def get_booking_history(self, passenger_email: str, db: Session) -> list:
        """Get booking history for a passenger"""
        bookings = db.query(Booking).filter(
            Booking.passenger_email == passenger_email
        ).order_by(Booking.created_at.desc()).all()
        
        return [
            BookingConfirmation(
                pnr=booking.pnr,
                booking_reference=booking.booking_reference,
                passenger_name=booking.passenger_name,
                passenger_email=booking.passenger_email,
                passenger_phone=booking.passenger_phone,
                flight_details=booking.flight,
                seat_class=booking.seat_class,
                seat_number=booking.seat_number,
                price_paid=booking.price_paid,
                booking_date=booking.created_at,
                status=booking.status
            )
            for booking in bookings
        ]
