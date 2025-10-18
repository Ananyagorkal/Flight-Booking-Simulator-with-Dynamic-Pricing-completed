from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enums
class FlightStatus(str, Enum):
    SCHEDULED = "scheduled"
    ON_TIME = "on_time"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    DEPARTED = "departed"
    ARRIVED = "arrived"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class SeatClass(str, Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"

# Base models
class AirportBase(BaseModel):
    code: str
    name: str
    city: str
    country: str
    timezone: str

class AirportCreate(AirportBase):
    pass

class Airport(AirportBase):
    id: int
    
    class Config:
        from_attributes = True

class AirlineBase(BaseModel):
    code: str
    name: str
    logo_url: Optional[str] = None

class AirlineCreate(AirlineBase):
    pass

class Airline(AirlineBase):
    id: int
    
    class Config:
        from_attributes = True

class FlightBase(BaseModel):
    flight_number: str
    airline_id: int
    departure_airport_id: int
    arrival_airport_id: int
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    base_price: float
    total_seats: int

class FlightCreate(FlightBase):
    pass

class FlightUpdate(BaseModel):
    status: Optional[FlightStatus] = None
    available_seats: Optional[int] = None

class Flight(FlightBase):
    id: int
    status: FlightStatus
    available_seats: int
    created_at: datetime
    updated_at: datetime
    airline: Optional[Airline] = None
    departure_airport: Optional[Airport] = None
    arrival_airport: Optional[Airport] = None
    
    class Config:
        from_attributes = True

class FlightSearch(BaseModel):
    departure_airport: str
    arrival_airport: str
    departure_date: datetime
    return_date: Optional[datetime] = None
    passengers: int = 1
    seat_class: Optional[SeatClass] = None

class BookingBase(BaseModel):
    flight_id: int
    passenger_name: str
    passenger_email: str
    passenger_phone: str
    seat_class: SeatClass
    seat_number: Optional[str] = None

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    seat_number: Optional[str] = None

class Booking(BookingBase):
    id: int
    pnr: str
    price_paid: float
    status: BookingStatus
    booking_reference: str
    created_at: datetime
    updated_at: datetime
    flight: Optional[Flight] = None
    
    class Config:
        from_attributes = True

class PricingRequest(BaseModel):
    flight_id: int
    seat_class: SeatClass
    passengers: int = 1

class PricingResponse(BaseModel):
    flight_id: int
    seat_class: SeatClass
    base_price: float
    current_price: float
    demand_factor: float
    time_factor: float
    seat_availability_factor: float
    total_price: float

class SeatInventoryBase(BaseModel):
    flight_id: int
    seat_class: SeatClass
    total_seats: int
    available_seats: int

class SeatInventoryCreate(SeatInventoryBase):
    pass

class SeatInventory(SeatInventoryBase):
    id: int
    booked_seats: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    flights: List[Flight]
    total_count: int
    page: int
    page_size: int

class BookingConfirmation(BaseModel):
    pnr: str
    booking_reference: str
    passenger_name: str
    passenger_email: str
    passenger_phone: str
    flight_details: Flight
    seat_class: SeatClass
    seat_number: Optional[str]
    price_paid: float
    booking_date: datetime
    status: BookingStatus

# Coupon Models
class CouponBase(BaseModel):
    code: str
    name: str
    description: str
    discount_type: str  # 'percentage' or 'fixed'
    discount_value: float
    min_amount: float
    max_discount: float
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True

class CouponCreate(CouponBase):
    pass

class Coupon(CouponBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CouponValidation(BaseModel):
    coupon_code: str
    booking_amount: float
    seat_class: SeatClass
    passengers: int = 1

class CouponValidationResponse(BaseModel):
    valid: bool
    message: str
    coupon_details: Optional[Coupon] = None
    discount_amount: float = 0
    final_amount: float = 0
    original_amount: float = 0
    savings: float = 0

class CouponListResponse(BaseModel):
    coupons: List[Coupon]

# Payment Models
class PaymentMethod(BaseModel):
    id: str
    name: str
    description: str
    icon: str

class PaymentMethodsResponse(BaseModel):
    payment_methods: List[PaymentMethod]

class Bank(BaseModel):
    code: str
    name: str

class BanksResponse(BaseModel):
    banks: List[Bank]