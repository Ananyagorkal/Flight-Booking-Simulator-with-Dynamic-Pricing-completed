from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import random
from datetime import datetime, timedelta

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
bookings_db = []
coupons_db = []
payments_db = []

# Initialize sample coupons
sample_coupons = [
    {
        "code": "WELCOME20",
        "name": "Welcome Discount",
        "description": "20% off on your first booking",
        "discount_type": "percentage",
        "discount_value": 20,
        "min_amount": 5000,
        "max_discount": 10000,
        "valid_from": "2024-01-01",
        "valid_until": "2024-12-31",
        "usage_limit": 1000,
        "used_count": 0,
        "is_active": True
    },
    {
        "code": "SAVE500",
        "name": "Flat Discount",
        "description": "₹500 off on domestic flights",
        "discount_type": "fixed",
        "discount_value": 500,
        "min_amount": 3000,
        "max_discount": 500,
        "valid_from": "2024-01-01",
        "valid_until": "2024-12-31",
        "usage_limit": 500,
        "used_count": 0,
        "is_active": True
    },
    {
        "code": "FIRSTCLASS",
        "name": "Premium Upgrade",
        "description": "₹2000 off on Business/First class",
        "discount_type": "fixed",
        "discount_value": 2000,
        "min_amount": 15000,
        "max_discount": 2000,
        "valid_from": "2024-01-01",
        "valid_until": "2024-12-31",
        "usage_limit": 100,
        "used_count": 0,
        "is_active": True
    },
    {
        "code": "EARLYBIRD",
        "name": "Early Bird Special",
        "description": "15% off on bookings made 30+ days in advance",
        "discount_type": "percentage",
        "discount_value": 15,
        "min_amount": 10000,
        "max_discount": 15000,
        "valid_from": "2024-01-01",
        "valid_until": "2024-12-31",
        "usage_limit": 200,
        "used_count": 0,
        "is_active": True
    },
    {
        "code": "STUDENT10",
        "name": "Student Discount",
        "description": "10% off for students",
        "discount_type": "percentage",
        "discount_value": 10,
        "min_amount": 2000,
        "max_discount": 5000,
        "valid_from": "2024-01-01",
        "valid_until": "2024-12-31",
        "usage_limit": 1000,
        "used_count": 0,
        "is_active": True
    },
    {
        "code": "FAMILY",
        "name": "Family Package",
        "description": "₹1000 off for 3+ passengers",
        "discount_type": "fixed",
        "discount_value": 1000,
        "min_amount": 15000,
        "max_discount": 1000,
        "valid_from": "2024-01-01",
        "valid_until": "2024-12-31",
        "usage_limit": 300,
        "used_count": 0,
        "is_active": True
    }
]

# Initialize coupons
coupons_db = sample_coupons.copy()

# Payment methods and configurations
payment_methods = [
    {
        "id": "credit_card",
        "name": "Credit Card",
        "icon": "fas fa-credit-card",
        "description": "Visa, Mastercard, American Express",
        "processing_fee": 0,
        "is_active": True
    },
    {
        "id": "debit_card",
        "name": "Debit Card",
        "icon": "fas fa-credit-card",
        "description": "Visa, Mastercard, RuPay",
        "processing_fee": 0,
        "is_active": True
    },
    {
        "id": "netbanking",
        "name": "Net Banking",
        "icon": "fas fa-university",
        "description": "All major Indian banks",
        "processing_fee": 0,
        "is_active": True
    },
    {
        "id": "upi",
        "name": "UPI",
        "icon": "fas fa-mobile-alt",
        "description": "PhonePe, Google Pay, Paytm, BHIM",
        "processing_fee": 0,
        "is_active": True
    },
    {
        "id": "wallet",
        "name": "Digital Wallet",
        "icon": "fas fa-wallet",
        "description": "Paytm, PhonePe, Amazon Pay",
        "processing_fee": 0,
        "is_active": True
    },
    {
        "id": "emi",
        "name": "EMI",
        "icon": "fas fa-calendar-alt",
        "description": "No Cost EMI available",
        "processing_fee": 0,
        "is_active": True
    }
]

# Sample banks for net banking
banks = [
    {"code": "SBI", "name": "State Bank of India"},
    {"code": "HDFC", "name": "HDFC Bank"},
    {"code": "ICICI", "name": "ICICI Bank"},
    {"code": "AXIS", "name": "Axis Bank"},
    {"code": "KOTAK", "name": "Kotak Mahindra Bank"},
    {"code": "PNB", "name": "Punjab National Bank"},
    {"code": "BOI", "name": "Bank of India"},
    {"code": "CANARA", "name": "Canara Bank"}
]

# Sample data with Indian and international flights
sample_flights = [
    # Domestic Indian Flights
    {
        "id": 1,
        "flight_number": "AI101",
        "airline": {"code": "AI", "name": "Air India"},
        "departure_airport": {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "New Delhi"},
        "arrival_airport": {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai"},
        "departure_time": "2024-01-15T08:00:00",
        "arrival_time": "2024-01-15T10:30:00",
        "duration_minutes": 150,
        "base_price": 4500,
        "current_price": 5400,
        "total_seats": 200,
        "available_seats": 150,
        "status": "scheduled"
    },
    {
        "id": 2,
        "flight_number": "6E201",
        "airline": {"code": "6E", "name": "IndiGo"},
        "departure_airport": {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai"},
        "arrival_airport": {"code": "BLR", "name": "Kempegowda International Airport", "city": "Bangalore"},
        "departure_time": "2024-01-15T14:00:00",
        "arrival_time": "2024-01-15T15:45:00",
        "duration_minutes": 105,
        "base_price": 3200,
        "current_price": 3800,
        "total_seats": 180,
        "available_seats": 120,
        "status": "scheduled"
    },
    {
        "id": 3,
        "flight_number": "SG301",
        "airline": {"code": "SG", "name": "SpiceJet"},
        "departure_airport": {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "New Delhi"},
        "arrival_airport": {"code": "CCU", "name": "Netaji Subhash Chandra Bose International Airport", "city": "Kolkata"},
        "departure_time": "2024-01-15T16:30:00",
        "arrival_time": "2024-01-15T18:45:00",
        "duration_minutes": 135,
        "base_price": 2800,
        "current_price": 3200,
        "total_seats": 150,
        "available_seats": 100,
        "status": "scheduled"
    },
    {
        "id": 4,
        "flight_number": "G8401",
        "airline": {"code": "G8", "name": "GoAir"},
        "departure_airport": {"code": "BLR", "name": "Kempegowda International Airport", "city": "Bangalore"},
        "arrival_airport": {"code": "HYD", "name": "Rajiv Gandhi International Airport", "city": "Hyderabad"},
        "departure_time": "2024-01-15T11:00:00",
        "arrival_time": "2024-01-15T12:15:00",
        "duration_minutes": 75,
        "base_price": 2500,
        "current_price": 2900,
        "total_seats": 120,
        "available_seats": 80,
        "status": "scheduled"
    },
    {
        "id": 5,
        "flight_number": "AI501",
        "airline": {"code": "AI", "name": "Air India"},
        "departure_airport": {"code": "MAA", "name": "Chennai International Airport", "city": "Chennai"},
        "arrival_airport": {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "New Delhi"},
        "departure_time": "2024-01-15T19:00:00",
        "arrival_time": "2024-01-15T21:30:00",
        "duration_minutes": 150,
        "base_price": 5200,
        "current_price": 6200,
        "total_seats": 200,
        "available_seats": 160,
        "status": "scheduled"
    },
    
    # International Flights from India
    {
        "id": 6,
        "flight_number": "EK501",
        "airline": {"code": "EK", "name": "Emirates"},
        "departure_airport": {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "New Delhi"},
        "arrival_airport": {"code": "DXB", "name": "Dubai International Airport", "city": "Dubai"},
        "departure_time": "2024-01-15T02:30:00",
        "arrival_time": "2024-01-15T05:45:00",
        "duration_minutes": 195,
        "base_price": 25000,
        "current_price": 32000,
        "total_seats": 300,
        "available_seats": 200,
        "status": "scheduled"
    },
    {
        "id": 7,
        "flight_number": "SQ201",
        "airline": {"code": "SQ", "name": "Singapore Airlines"},
        "departure_airport": {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai"},
        "arrival_airport": {"code": "SIN", "name": "Singapore Changi Airport", "city": "Singapore"},
        "departure_time": "2024-01-15T23:45:00",
        "arrival_time": "2024-01-16T07:30:00",
        "duration_minutes": 225,
        "base_price": 35000,
        "current_price": 42000,
        "total_seats": 250,
        "available_seats": 180,
        "status": "scheduled"
    },
    {
        "id": 8,
        "flight_number": "BA147",
        "airline": {"code": "BA", "name": "British Airways"},
        "departure_airport": {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "New Delhi"},
        "arrival_airport": {"code": "LHR", "name": "London Heathrow Airport", "city": "London"},
        "departure_time": "2024-01-15T13:20:00",
        "arrival_time": "2024-01-15T18:35:00",
        "duration_minutes": 315,
        "base_price": 65000,
        "current_price": 78000,
        "total_seats": 280,
        "available_seats": 150,
        "status": "scheduled"
    },
    {
        "id": 9,
        "flight_number": "LH761",
        "airline": {"code": "LH", "name": "Lufthansa"},
        "departure_airport": {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai"},
        "arrival_airport": {"code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt"},
        "departure_time": "2024-01-15T01:15:00",
        "arrival_time": "2024-01-15T06:40:00",
        "duration_minutes": 325,
        "base_price": 58000,
        "current_price": 72000,
        "total_seats": 300,
        "available_seats": 220,
        "status": "scheduled"
    },
    {
        "id": 10,
        "flight_number": "QR578",
        "airline": {"code": "QR", "name": "Qatar Airways"},
        "departure_airport": {"code": "BLR", "name": "Kempegowda International Airport", "city": "Bangalore"},
        "arrival_airport": {"code": "DOH", "name": "Hamad International Airport", "city": "Doha"},
        "departure_time": "2024-01-15T03:45:00",
        "arrival_time": "2024-01-15T06:20:00",
        "duration_minutes": 155,
        "base_price": 22000,
        "current_price": 28000,
        "total_seats": 200,
        "available_seats": 120,
        "status": "scheduled"
    },
    {
        "id": 11,
        "flight_number": "TG316",
        "airline": {"code": "TG", "name": "Thai Airways"},
        "departure_airport": {"code": "CCU", "name": "Netaji Subhash Chandra Bose International Airport", "city": "Kolkata"},
        "arrival_airport": {"code": "BKK", "name": "Suvarnabhumi Airport", "city": "Bangkok"},
        "departure_time": "2024-01-15T20:30:00",
        "arrival_time": "2024-01-16T01:15:00",
        "duration_minutes": 165,
        "base_price": 18000,
        "current_price": 22000,
        "total_seats": 180,
        "available_seats": 100,
        "status": "scheduled"
    },
    {
        "id": 12,
        "flight_number": "JL58",
        "airline": {"code": "JL", "name": "Japan Airlines"},
        "departure_airport": {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "New Delhi"},
        "arrival_airport": {"code": "NRT", "name": "Narita International Airport", "city": "Tokyo"},
        "departure_time": "2024-01-15T11:50:00",
        "arrival_time": "2024-01-15T23:30:00",
        "duration_minutes": 400,
        "base_price": 45000,
        "current_price": 55000,
        "total_seats": 250,
        "available_seats": 180,
        "status": "scheduled"
    },
    {
        "id": 13,
        "flight_number": "AA100",
        "airline": {"code": "AA", "name": "American Airlines"},
        "departure_airport": {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "New Delhi"},
        "arrival_airport": {"code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York"},
        "departure_time": "2024-01-15T15:30:00",
        "arrival_time": "2024-01-16T06:45:00",
        "duration_minutes": 555,
        "base_price": 85000,
        "current_price": 105000,
        "total_seats": 300,
        "available_seats": 120,
        "status": "scheduled"
    },
    {
        "id": 14,
        "flight_number": "QF68",
        "airline": {"code": "QF", "name": "Qantas"},
        "departure_airport": {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai"},
        "arrival_airport": {"code": "SYD", "name": "Sydney Kingsford Smith Airport", "city": "Sydney"},
        "departure_time": "2024-01-15T22:15:00",
        "arrival_time": "2024-01-16T14:20:00",
        "duration_minutes": 485,
        "base_price": 75000,
        "current_price": 95000,
        "total_seats": 280,
        "available_seats": 200,
        "status": "scheduled"
    },
    {
        "id": 15,
        "flight_number": "TK716",
        "airline": {"code": "TK", "name": "Turkish Airlines"},
        "departure_airport": {"code": "HYD", "name": "Rajiv Gandhi International Airport", "city": "Hyderabad"},
        "arrival_airport": {"code": "IST", "name": "Istanbul Airport", "city": "Istanbul"},
        "departure_time": "2024-01-15T04:20:00",
        "arrival_time": "2024-01-15T09:30:00",
        "duration_minutes": 310,
        "base_price": 35000,
        "current_price": 42000,
        "total_seats": 220,
        "available_seats": 150,
        "status": "scheduled"
    }
]

sample_airports = [
    # Indian Airports
    {"id": 1, "code": "DEL", "name": "Indira Gandhi International Airport", "city": "New Delhi", "country": "India"},
    {"id": 2, "code": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai", "country": "India"},
    {"id": 3, "code": "BLR", "name": "Kempegowda International Airport", "city": "Bangalore", "country": "India"},
    {"id": 4, "code": "CCU", "name": "Netaji Subhash Chandra Bose International Airport", "city": "Kolkata", "country": "India"},
    {"id": 5, "code": "HYD", "name": "Rajiv Gandhi International Airport", "city": "Hyderabad", "country": "India"},
    {"id": 6, "code": "MAA", "name": "Chennai International Airport", "city": "Chennai", "country": "India"},
    {"id": 7, "code": "AMD", "name": "Sardar Vallabhbhai Patel International Airport", "city": "Ahmedabad", "country": "India"},
    {"id": 8, "code": "PNQ", "name": "Pune Airport", "city": "Pune", "country": "India"},
    {"id": 9, "code": "GOI", "name": "Dabolim Airport", "city": "Goa", "country": "India"},
    {"id": 10, "code": "COK", "name": "Cochin International Airport", "city": "Kochi", "country": "India"},
    {"id": 11, "code": "JAI", "name": "Jaipur International Airport", "city": "Jaipur", "country": "India"},
    {"id": 12, "code": "LKO", "name": "Chaudhary Charan Singh International Airport", "city": "Lucknow", "country": "India"},
    {"id": 13, "code": "IXB", "name": "Bagdogra Airport", "city": "Siliguri", "country": "India"},
    {"id": 14, "code": "GAU", "name": "Lokpriya Gopinath Bordoloi International Airport", "city": "Guwahati", "country": "India"},
    {"id": 15, "code": "PAT", "name": "Jay Prakash Narayan Airport", "city": "Patna", "country": "India"},
    {"id": 16, "code": "IXC", "name": "Chandigarh Airport", "city": "Chandigarh", "country": "India"},
    {"id": 17, "code": "IXJ", "name": "Jammu Airport", "city": "Jammu", "country": "India"},
    {"id": 18, "code": "SXR", "name": "Srinagar Airport", "city": "Srinagar", "country": "India"},
    {"id": 19, "code": "IXL", "name": "Leh Kushok Bakula Rimpochee Airport", "city": "Leh", "country": "India"},
    {"id": 20, "code": "IXZ", "name": "Veer Savarkar International Airport", "city": "Port Blair", "country": "India"},
    
    # International Airports
    {"id": 21, "code": "DXB", "name": "Dubai International Airport", "city": "Dubai", "country": "UAE"},
    {"id": 22, "code": "SIN", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore"},
    {"id": 23, "code": "BKK", "name": "Suvarnabhumi Airport", "city": "Bangkok", "country": "Thailand"},
    {"id": 24, "code": "KUL", "name": "Kuala Lumpur International Airport", "city": "Kuala Lumpur", "country": "Malaysia"},
    {"id": 25, "code": "HKG", "name": "Hong Kong International Airport", "city": "Hong Kong", "country": "Hong Kong"},
    {"id": 26, "code": "NRT", "name": "Narita International Airport", "city": "Tokyo", "country": "Japan"},
    {"id": 27, "code": "ICN", "name": "Incheon International Airport", "city": "Seoul", "country": "South Korea"},
    {"id": 28, "code": "PEK", "name": "Beijing Capital International Airport", "city": "Beijing", "country": "China"},
    {"id": 29, "code": "PVG", "name": "Shanghai Pudong International Airport", "city": "Shanghai", "country": "China"},
    {"id": 30, "code": "LHR", "name": "London Heathrow Airport", "city": "London", "country": "UK"},
    {"id": 31, "code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France"},
    {"id": 32, "code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany"},
    {"id": 33, "code": "AMS", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands"},
    {"id": 34, "code": "FCO", "name": "Leonardo da Vinci International Airport", "city": "Rome", "country": "Italy"},
    {"id": 35, "code": "MAD", "name": "Adolfo Suárez Madrid-Barajas Airport", "city": "Madrid", "country": "Spain"},
    {"id": 36, "code": "ZUR", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland"},
    {"id": 37, "code": "VIE", "name": "Vienna International Airport", "city": "Vienna", "country": "Austria"},
    {"id": 38, "code": "ARN", "name": "Stockholm Arlanda Airport", "city": "Stockholm", "country": "Sweden"},
    {"id": 39, "code": "CPH", "name": "Copenhagen Airport", "city": "Copenhagen", "country": "Denmark"},
    {"id": 40, "code": "HEL", "name": "Helsinki Airport", "city": "Helsinki", "country": "Finland"},
    {"id": 41, "code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "USA"},
    {"id": 42, "code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "USA"},
    {"id": 43, "code": "ORD", "name": "Chicago O'Hare International Airport", "city": "Chicago", "country": "USA"},
    {"id": 44, "code": "SFO", "name": "San Francisco International Airport", "city": "San Francisco", "country": "USA"},
    {"id": 45, "code": "MIA", "name": "Miami International Airport", "city": "Miami", "country": "USA"},
    {"id": 46, "code": "BOS", "name": "Logan International Airport", "city": "Boston", "country": "USA"},
    {"id": 47, "code": "SEA", "name": "Seattle-Tacoma International Airport", "city": "Seattle", "country": "USA"},
    {"id": 48, "code": "DFW", "name": "Dallas/Fort Worth International Airport", "city": "Dallas", "country": "USA"},
    {"id": 49, "code": "ATL", "name": "Hartsfield-Jackson Atlanta International Airport", "city": "Atlanta", "country": "USA"},
    {"id": 50, "code": "DEN", "name": "Denver International Airport", "city": "Denver", "country": "USA"},
    {"id": 51, "code": "YYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada"},
    {"id": 52, "code": "YVR", "name": "Vancouver International Airport", "city": "Vancouver", "country": "Canada"},
    {"id": 53, "code": "SYD", "name": "Sydney Kingsford Smith Airport", "city": "Sydney", "country": "Australia"},
    {"id": 54, "code": "MEL", "name": "Melbourne Airport", "city": "Melbourne", "country": "Australia"},
    {"id": 55, "code": "AKL", "name": "Auckland Airport", "city": "Auckland", "country": "New Zealand"},
    {"id": 56, "code": "JNB", "name": "O.R. Tambo International Airport", "city": "Johannesburg", "country": "South Africa"},
    {"id": 57, "code": "CPT", "name": "Cape Town International Airport", "city": "Cape Town", "country": "South Africa"},
    {"id": 58, "code": "CAI", "name": "Cairo International Airport", "city": "Cairo", "country": "Egypt"},
    {"id": 59, "code": "IST", "name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey"},
    {"id": 60, "code": "DOH", "name": "Hamad International Airport", "city": "Doha", "country": "Qatar"}
]

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
    filtered_flights = sample_flights.copy()
    
    # Debug: Print search parameters
    print(f"Search parameters: departure={departure_airport}, arrival={arrival_airport}")
    
    if departure_airport:
        filtered_flights = [f for f in filtered_flights if f["departure_airport"]["code"] == departure_airport.upper()]
        print(f"After departure filter: {len(filtered_flights)} flights")
    
    if arrival_airport:
        filtered_flights = [f for f in filtered_flights if f["arrival_airport"]["code"] == arrival_airport.upper()]
        print(f"After arrival filter: {len(filtered_flights)} flights")
    
    # If no flights found, return some sample flights for demonstration
    if not filtered_flights:
        print("No flights found, returning sample flights")
        filtered_flights = sample_flights[:5]  # Return first 5 flights as samples
    
    return {
        "flights": filtered_flights[:10],  # Limit to 10 results
        "total_count": len(filtered_flights),
        "page": 1,
        "page_size": 10
    }

@app.get("/api/flights/")
async def get_all_flights():
    """Get all available flights"""
    return {
        "flights": sample_flights,
        "total_count": len(sample_flights),
        "page": 1,
        "page_size": len(sample_flights)
    }

@app.get("/api/flights/airports/")
async def get_airports():
    """Get all airports"""
    return sample_airports

@app.get("/api/flights/airlines/")
async def get_airlines():
    """Get all airlines"""
    return [
        # Indian Airlines
        {"id": 1, "code": "AI", "name": "Air India", "logo_url": None},
        {"id": 2, "code": "6E", "name": "IndiGo", "logo_url": None},
        {"id": 3, "code": "SG", "name": "SpiceJet", "logo_url": None},
        {"id": 4, "code": "G8", "name": "GoAir", "logo_url": None},
        {"id": 5, "code": "IX", "name": "Air India Express", "logo_url": None},
        {"id": 6, "code": "I5", "name": "AirAsia India", "logo_url": None},
        {"id": 7, "code": "UK", "name": "Vistara", "logo_url": None},
        {"id": 8, "code": "QP", "name": "Alliance Air", "logo_url": None},
        {"id": 9, "code": "S2", "name": "Jet Airways", "logo_url": None},
        
        # International Airlines
        {"id": 10, "code": "EK", "name": "Emirates", "logo_url": None},
        {"id": 11, "code": "QR", "name": "Qatar Airways", "logo_url": None},
        {"id": 12, "code": "EY", "name": "Etihad Airways", "logo_url": None},
        {"id": 13, "code": "SQ", "name": "Singapore Airlines", "logo_url": None},
        {"id": 14, "code": "TG", "name": "Thai Airways", "logo_url": None},
        {"id": 15, "code": "MH", "name": "Malaysia Airlines", "logo_url": None},
        {"id": 16, "code": "CX", "name": "Cathay Pacific", "logo_url": None},
        {"id": 17, "code": "JL", "name": "Japan Airlines", "logo_url": None},
        {"id": 18, "code": "KE", "name": "Korean Air", "logo_url": None},
        {"id": 19, "code": "CA", "name": "Air China", "logo_url": None},
        {"id": 20, "code": "MU", "name": "China Eastern", "logo_url": None},
        {"id": 21, "code": "BA", "name": "British Airways", "logo_url": None},
        {"id": 22, "code": "AF", "name": "Air France", "logo_url": None},
        {"id": 23, "code": "LH", "name": "Lufthansa", "logo_url": None},
        {"id": 24, "code": "KL", "name": "KLM Royal Dutch Airlines", "logo_url": None},
        {"id": 25, "code": "AZ", "name": "Alitalia", "logo_url": None},
        {"id": 26, "code": "IB", "name": "Iberia", "logo_url": None},
        {"id": 27, "code": "LX", "name": "Swiss International Air Lines", "logo_url": None},
        {"id": 28, "code": "OS", "name": "Austrian Airlines", "logo_url": None},
        {"id": 29, "code": "SK", "name": "SAS Scandinavian Airlines", "logo_url": None},
        {"id": 30, "code": "AY", "name": "Finnair", "logo_url": None},
        {"id": 31, "code": "AA", "name": "American Airlines", "logo_url": None},
        {"id": 32, "code": "DL", "name": "Delta Air Lines", "logo_url": None},
        {"id": 33, "code": "UA", "name": "United Airlines", "logo_url": None},
        {"id": 34, "code": "AC", "name": "Air Canada", "logo_url": None},
        {"id": 35, "code": "QF", "name": "Qantas", "logo_url": None},
        {"id": 36, "code": "NZ", "name": "Air New Zealand", "logo_url": None},
        {"id": 37, "code": "SA", "name": "South African Airways", "logo_url": None},
        {"id": 38, "code": "MS", "name": "EgyptAir", "logo_url": None},
        {"id": 39, "code": "TK", "name": "Turkish Airlines", "logo_url": None}
    ]

@app.post("/api/bookings/")
async def create_booking(booking_data: dict):
    """Create a booking"""
    import string
    pnr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    flight = next((f for f in sample_flights if f["id"] == booking_data.get("flight_id")), None)
    
    booking = {
        "pnr": pnr,
        "booking_reference": booking_ref,
        "passenger_name": booking_data.get("passenger_name", "Demo Passenger"),
        "flight_details": flight,
        "seat_class": booking_data.get("seat_class", "economy"),
        "seat_number": f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
        "price_paid": random.randint(2500, 8000),
        "booking_date": datetime.now().isoformat(),
        "status": "confirmed"
    }
    
    return booking

@app.get("/api/pricing/flight/{flight_id}/class/{seat_class}")
async def get_pricing(flight_id: int, seat_class: str):
    """Get pricing for a flight and seat class"""
    flight = next((f for f in sample_flights if f["id"] == flight_id), None)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    multipliers = {"economy": 1.0, "premium_economy": 1.5, "business": 2.5, "first": 4.0}
    multiplier = multipliers.get(seat_class, 1.0)
    
    base_price = flight["base_price"]
    current_price = flight["current_price"]
    
    # Apply Indian pricing factors
    demand_factor = 1.2
    time_factor = 1.1
    availability_factor = 1.05
    
    final_price = int(current_price * multiplier)
    
    return {
        "flight_id": flight_id,
        "seat_class": seat_class,
        "base_price": int(base_price * multiplier),
        "current_price": final_price,
        "total_price": final_price,
        "demand_factor": demand_factor,
        "time_factor": time_factor,
        "seat_availability_factor": availability_factor
    }

# Coupon System APIs
@app.get("/api/coupons/")
async def get_all_coupons():
    """Get all available coupons"""
    active_coupons = [c for c in coupons_db if c["is_active"]]
    return {
        "coupons": active_coupons,
        "total_count": len(active_coupons)
    }

@app.get("/api/coupons/{coupon_code}")
async def get_coupon(coupon_code: str):
    """Get coupon details by code"""
    coupon = next((c for c in coupons_db if c["code"].upper() == coupon_code.upper()), None)
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    if not coupon["is_active"]:
        raise HTTPException(status_code=400, detail="Coupon is not active")
    
    return coupon

@app.post("/api/coupons/validate")
async def validate_coupon(coupon_data: dict):
    """Validate a coupon code"""
    coupon_code = coupon_data.get("coupon_code", "").upper()
    booking_amount = coupon_data.get("booking_amount", 0)
    seat_class = coupon_data.get("seat_class", "economy")
    passengers = coupon_data.get("passengers", 1)
    
    coupon = next((c for c in coupons_db if c["code"] == coupon_code), None)
    
    if not coupon:
        return {
            "valid": False,
            "message": "Invalid coupon code",
            "discount_amount": 0
        }
    
    if not coupon["is_active"]:
        return {
            "valid": False,
            "message": "Coupon is not active",
            "discount_amount": 0
        }
    
    # Check usage limit
    if coupon["used_count"] >= coupon["usage_limit"]:
        return {
            "valid": False,
            "message": "Coupon usage limit exceeded",
            "discount_amount": 0
        }
    
    # Check minimum amount
    if booking_amount < coupon["min_amount"]:
        return {
            "valid": False,
            "message": f"Minimum booking amount of ₹{coupon['min_amount']} required",
            "discount_amount": 0
        }
    
    # Check date validity
    today = datetime.now().strftime("%Y-%m-%d")
    if today < coupon["valid_from"] or today > coupon["valid_until"]:
        return {
            "valid": False,
            "message": "Coupon has expired",
            "discount_amount": 0
        }
    
    # Calculate discount
    if coupon["discount_type"] == "percentage":
        discount_amount = int(booking_amount * coupon["discount_value"] / 100)
        discount_amount = min(discount_amount, coupon["max_discount"])
    else:  # fixed
        discount_amount = min(coupon["discount_value"], coupon["max_discount"])
    
    return {
        "valid": True,
        "message": "Coupon applied successfully",
        "discount_amount": discount_amount,
        "coupon_details": {
            "code": coupon["code"],
            "name": coupon["name"],
            "description": coupon["description"],
            "discount_type": coupon["discount_type"],
            "discount_value": coupon["discount_value"]
        }
    }

@app.post("/api/coupons/apply")
async def apply_coupon(coupon_data: dict):
    """Apply a coupon and return updated pricing"""
    coupon_code = coupon_data.get("coupon_code", "").upper()
    booking_amount = coupon_data.get("booking_amount", 0)
    
    # Validate coupon
    validation = await validate_coupon(coupon_data)
    
    if not validation["valid"]:
        return validation
    
    # Calculate final amount
    discount_amount = validation["discount_amount"]
    final_amount = max(0, booking_amount - discount_amount)
    
    # Update coupon usage count
    coupon = next((c for c in coupons_db if c["code"] == coupon_code), None)
    if coupon:
        coupon["used_count"] += 1
    
    return {
        "valid": True,
        "message": "Coupon applied successfully",
        "original_amount": booking_amount,
        "discount_amount": discount_amount,
        "final_amount": final_amount,
        "savings": discount_amount,
        "coupon_details": validation["coupon_details"]
    }

# Payment System APIs
@app.get("/api/payments/methods")
async def get_payment_methods():
    """Get all available payment methods"""
    active_methods = [method for method in payment_methods if method["is_active"]]
    return {
        "payment_methods": active_methods,
        "total_count": len(active_methods)
    }

@app.get("/api/payments/banks")
async def get_banks():
    """Get all available banks for net banking"""
    return {
        "banks": banks,
        "total_count": len(banks)
    }

@app.post("/api/payments/initiate")
async def initiate_payment(payment_data: dict):
    """Initiate a payment"""
    booking_id = payment_data.get("booking_id")
    amount = payment_data.get("amount", 0)
    payment_method = payment_data.get("payment_method")
    currency = payment_data.get("currency", "INR")
    
    if not booking_id or not amount or not payment_method:
        raise HTTPException(status_code=400, detail="Missing required payment data")
    
    # Generate payment ID
    import string
    payment_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    # Create payment record
    payment = {
        "payment_id": payment_id,
        "booking_id": booking_id,
        "amount": amount,
        "currency": currency,
        "payment_method": payment_method,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat()
    }
    
    payments_db.append(payment)
    
    return {
        "payment_id": payment_id,
        "status": "pending",
        "amount": amount,
        "currency": currency,
        "payment_method": payment_method,
        "expires_at": payment["expires_at"],
        "redirect_url": f"/payment/{payment_id}"
    }

@app.post("/api/payments/process")
async def process_payment(payment_data: dict):
    """Process a payment"""
    payment_id = payment_data.get("payment_id")
    payment_method = payment_data.get("payment_method")
    card_details = payment_data.get("card_details", {})
    upi_details = payment_data.get("upi_details", {})
    netbanking_details = payment_data.get("netbanking_details", {})
    
    # Find payment record
    payment = next((p for p in payments_db if p["payment_id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment["status"] != "pending":
        raise HTTPException(status_code=400, detail="Payment already processed")
    
    # Simulate payment processing
    success_rate = 0.85  # 85% success rate for demo
    
    if random.random() < success_rate:
        # Payment successful
        payment["status"] = "completed"
        payment["transaction_id"] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        payment["completed_at"] = datetime.now().isoformat()
        
        # Update booking status
        booking = next((b for b in bookings_db if b.get("id") == payment["booking_id"]), None)
        if booking:
            booking["status"] = "confirmed"
            booking["payment_status"] = "paid"
        
        return {
            "success": True,
            "payment_id": payment_id,
            "transaction_id": payment["transaction_id"],
            "status": "completed",
            "message": "Payment successful",
            "amount": payment["amount"],
            "currency": payment["currency"]
        }
    else:
        # Payment failed
        payment["status"] = "failed"
        payment["failed_at"] = datetime.now().isoformat()
        payment["failure_reason"] = random.choice([
            "Insufficient funds",
            "Card declined",
            "Network timeout",
            "Invalid card details"
        ])
        
        return {
            "success": False,
            "payment_id": payment_id,
            "status": "failed",
            "message": payment["failure_reason"],
            "retry_available": True
        }

@app.get("/api/payments/status/{payment_id}")
async def get_payment_status(payment_id: str):
    """Get payment status"""
    payment = next((p for p in payments_db if p["payment_id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {
        "payment_id": payment_id,
        "status": payment["status"],
        "amount": payment["amount"],
        "currency": payment["currency"],
        "payment_method": payment["payment_method"],
        "created_at": payment["created_at"],
        "transaction_id": payment.get("transaction_id"),
        "failure_reason": payment.get("failure_reason")
    }

@app.post("/api/payments/refund")
async def process_refund(refund_data: dict):
    """Process a refund"""
    payment_id = refund_data.get("payment_id")
    amount = refund_data.get("amount")
    reason = refund_data.get("reason", "Customer request")
    
    # Find payment record
    payment = next((p for p in payments_db if p["payment_id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment["status"] != "completed":
        raise HTTPException(status_code=400, detail="Payment not completed")
    
    # Generate refund ID
    import string
    refund_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    # Create refund record
    refund = {
        "refund_id": refund_id,
        "payment_id": payment_id,
        "amount": amount,
        "reason": reason,
        "status": "processing",
        "created_at": datetime.now().isoformat()
    }
    
    # Simulate refund processing (usually takes 3-5 business days)
    refund["status"] = "completed"
    refund["completed_at"] = datetime.now().isoformat()
    
    return {
        "refund_id": refund_id,
        "status": "completed",
        "amount": amount,
        "message": "Refund processed successfully",
        "estimated_credit": "3-5 business days"
    }

if __name__ == "__main__":
    print("Starting Flight Booking Simulator...")
    print("Backend API: http://localhost:8000")
    print("Frontend: Open frontend/index.html in your browser")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run("minimal_server:app", host="0.0.0.0", port=8000, reload=True)
