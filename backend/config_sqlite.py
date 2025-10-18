from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for easier setup (no separate database server needed)
DATABASE_URL = "sqlite:///./flight_booking.db"

engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class FlightStatus(enum.Enum):
    SCHEDULED = "scheduled"
    ON_TIME = "on_time"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    DEPARTED = "departed"
    ARRIVED = "arrived"

class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class SeatClass(enum.Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"

class DiscountType(enum.Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"

# Database Models
class Airport(Base):
    __tablename__ = "airports"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    timezone = Column(String(50), nullable=False)
    
    # Relationships
    departure_flights = relationship("Flight", foreign_keys="Flight.departure_airport_id", back_populates="departure_airport")
    arrival_flights = relationship("Flight", foreign_keys="Flight.arrival_airport_id", back_populates="arrival_airport")

class Airline(Base):
    __tablename__ = "airlines"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(2), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    logo_url = Column(String(255))
    
    # Relationships
    flights = relationship("Flight", back_populates="airline")

class Flight(Base):
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(10), nullable=False)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    departure_airport_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    arrival_airport_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(Enum(FlightStatus), default=FlightStatus.SCHEDULED)
    base_price = Column(Float, nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    airline = relationship("Airline", back_populates="flights")
    departure_airport = relationship("Airport", foreign_keys=[departure_airport_id], back_populates="departure_flights")
    arrival_airport = relationship("Airport", foreign_keys=[arrival_airport_id], back_populates="arrival_flights")
    bookings = relationship("Booking", back_populates="flight")
    pricing_history = relationship("PricingHistory", back_populates="flight")

class PricingHistory(Base):
    __tablename__ = "pricing_history"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    seat_class = Column(Enum(SeatClass), nullable=False)
    price = Column(Float, nullable=False)
    demand_factor = Column(Float, nullable=False)
    time_factor = Column(Float, nullable=False)
    seat_availability_factor = Column(Float, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    flight = relationship("Flight", back_populates="pricing_history")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    pnr = Column(String(6), unique=True, index=True, nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    passenger_name = Column(String(100), nullable=False)
    passenger_email = Column(String(100), nullable=False)
    passenger_phone = Column(String(20), nullable=False)
    seat_class = Column(Enum(SeatClass), nullable=False)
    seat_number = Column(String(10))
    price_paid = Column(Float, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    booking_reference = Column(String(20), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    flight = relationship("Flight", back_populates="bookings")

class SeatInventory(Base):
    __tablename__ = "seat_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    seat_class = Column(Enum(SeatClass), nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    booked_seats = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    discount_type = Column(Enum(DiscountType), nullable=False)
    discount_value = Column(Float, nullable=False)
    min_amount = Column(Float, nullable=False)
    max_discount = Column(Float, nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
