import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from config_sqlite import Flight, PricingHistory, SeatInventory, SeatClass
from models import PricingRequest, PricingResponse

class PricingEngine:
    def __init__(self):
        # Base multipliers for different seat classes
        self.seat_class_multipliers = {
            SeatClass.ECONOMY: 1.0,
            SeatClass.PREMIUM_ECONOMY: 1.5,
            SeatClass.BUSINESS: 2.5,
            SeatClass.FIRST: 4.0
        }
        
        # Demand simulation parameters
        self.demand_fluctuation_range = 0.3  # ±30% demand variation
        self.time_sensitivity = 0.02  # 2% price increase per day closer to departure
        
    def calculate_demand_factor(self, flight: Flight, seat_class: SeatClass) -> float:
        """Calculate demand factor based on historical data and simulation"""
        # Simulate demand based on time of day, day of week, and season
        departure_hour = flight.departure_time.hour
        departure_weekday = flight.departure_time.weekday()
        
        # Time-based demand patterns
        time_factor = 1.0
        if 6 <= departure_hour <= 9 or 17 <= departure_hour <= 20:  # Peak hours
            time_factor = 1.2
        elif 22 <= departure_hour or departure_hour <= 5:  # Off-peak hours
            time_factor = 0.8
            
        # Day of week factor
        weekday_factor = 1.0
        if departure_weekday in [0, 4, 5, 6]:  # Monday, Friday, Saturday, Sunday
            weekday_factor = 1.1
        elif departure_weekday in [1, 2, 3]:  # Tuesday, Wednesday, Thursday
            weekday_factor = 0.9
            
        # Random fluctuation to simulate market conditions
        random_factor = 1.0 + random.uniform(-self.demand_fluctuation_range, self.demand_fluctuation_range)
        
        return time_factor * weekday_factor * random_factor
    
    def calculate_time_factor(self, flight: Flight) -> float:
        """Calculate time factor based on days until departure"""
        now = datetime.utcnow()
        days_until_departure = (flight.departure_time - now).days
        
        if days_until_departure <= 0:
            return 2.0  # Last minute booking
        elif days_until_departure <= 1:
            return 1.8  # Same day booking
        elif days_until_departure <= 7:
            return 1.5  # Within a week
        elif days_until_departure <= 30:
            return 1.2  # Within a month
        else:
            return 1.0  # Early booking
    
    def calculate_seat_availability_factor(self, flight: Flight, seat_class: SeatClass, db: Session) -> float:
        """Calculate price factor based on seat availability"""
        # Get seat inventory for the specific class
        seat_inventory = db.query(SeatInventory).filter(
            SeatInventory.flight_id == flight.id,
            SeatInventory.seat_class == seat_class
        ).first()
        
        if not seat_inventory:
            return 1.0
            
        availability_ratio = seat_inventory.available_seats / seat_inventory.total_seats
        
        if availability_ratio <= 0.1:  # Less than 10% seats available
            return 1.5
        elif availability_ratio <= 0.25:  # Less than 25% seats available
            return 1.3
        elif availability_ratio <= 0.5:  # Less than 50% seats available
            return 1.1
        else:
            return 1.0
    
    def calculate_dynamic_price(self, flight: Flight, seat_class: SeatClass, db: Session) -> PricingResponse:
        """Calculate dynamic price for a flight and seat class"""
        # Get base price for the seat class
        base_price = flight.base_price * self.seat_class_multipliers[seat_class]
        
        # Calculate all factors
        demand_factor = self.calculate_demand_factor(flight, seat_class)
        time_factor = self.calculate_time_factor(flight)
        seat_availability_factor = self.calculate_seat_availability_factor(flight, seat_class, db)
        
        # Calculate final price
        current_price = base_price * demand_factor * time_factor * seat_availability_factor
        
        # Round to nearest dollar
        current_price = round(current_price, 2)
        
        # Store pricing history
        pricing_history = PricingHistory(
            flight_id=flight.id,
            seat_class=seat_class,
            price=current_price,
            demand_factor=demand_factor,
            time_factor=time_factor,
            seat_availability_factor=seat_availability_factor
        )
        db.add(pricing_history)
        db.commit()
        
        return PricingResponse(
            flight_id=flight.id,
            seat_class=seat_class,
            base_price=base_price,
            current_price=current_price,
            demand_factor=demand_factor,
            time_factor=time_factor,
            seat_availability_factor=seat_availability_factor,
            total_price=current_price
        )
    
    def get_pricing_for_flights(self, flights: List[Flight], seat_class: SeatClass, db: Session) -> List[PricingResponse]:
        """Get pricing for multiple flights"""
        pricing_responses = []
        for flight in flights:
            pricing = self.calculate_dynamic_price(flight, seat_class, db)
            pricing_responses.append(pricing)
        return pricing_responses
    
    def update_seat_inventory(self, flight_id: int, seat_class: SeatClass, seats_booked: int, db: Session):
        """Update seat inventory after booking"""
        seat_inventory = db.query(SeatInventory).filter(
            SeatInventory.flight_id == flight_id,
            SeatInventory.seat_class == seat_class
        ).first()
        
        if seat_inventory:
            seat_inventory.available_seats -= seats_booked
            seat_inventory.booked_seats += seats_booked
            seat_inventory.last_updated = datetime.utcnow()
            db.commit()
    
    def get_price_trend(self, flight_id: int, seat_class: SeatClass, db: Session, days: int = 7) -> List[Dict]:
        """Get price trend for a flight over time"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        pricing_history = db.query(PricingHistory).filter(
            PricingHistory.flight_id == flight_id,
            PricingHistory.seat_class == seat_class,
            PricingHistory.calculated_at >= since_date
        ).order_by(PricingHistory.calculated_at).all()
        
        return [
            {
                "date": ph.calculated_at.isoformat(),
                "price": ph.price,
                "demand_factor": ph.demand_factor,
                "time_factor": ph.time_factor,
                "seat_availability_factor": ph.seat_availability_factor
            }
            for ph in pricing_history
        ]
