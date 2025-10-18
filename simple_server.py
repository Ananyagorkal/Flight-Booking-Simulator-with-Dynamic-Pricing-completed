#!/usr/bin/env python3
"""
Simple working server for Flight Booking Simulator
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import sys
import os
import sqlite3
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

app = FastAPI(title="Flight Booking Simulator API")

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

@app.get("/")
async def root():
    return {"message": "Flight Booking Simulator API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/flights/airports/")
async def get_airports():
    """Get all airports"""
    try:
        conn = sqlite3.connect('flight_booking.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM airports")
        airports = cursor.fetchall()
        
        result = []
        for airport in airports:
            result.append({
                "id": airport['id'],
                "code": airport['code'],
                "name": airport['name'],
                "city": airport['city'],
                "country": airport['country']
            })
        
        conn.close()
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/coupons/")
async def get_coupons():
    """Get all coupons"""
    try:
        conn = sqlite3.connect('flight_booking.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM coupons WHERE is_active = 1")
        coupons = cursor.fetchall()
        
        result = {
            "coupons": []
        }
        for coupon in coupons:
            result["coupons"].append({
                "id": coupon['id'],
                "code": coupon['code'],
                "name": coupon['name'],
                "description": coupon['description'],
                "discount_type": coupon['discount_type'],
                "discount_value": coupon['discount_value'],
                "min_amount": coupon['min_amount'],
                "max_discount": coupon['max_discount']
            })
        
        conn.close()
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/payments/methods")
async def get_payment_methods():
    """Get payment methods"""
    return {
        "payment_methods": [
            {"id": 1, "name": "Credit Card", "type": "card"},
            {"id": 2, "name": "Debit Card", "type": "card"},
            {"id": 3, "name": "Net Banking", "type": "netbanking"},
            {"id": 4, "name": "UPI", "type": "upi"},
            {"id": 5, "name": "Wallet", "type": "wallet"}
        ]
    }

@app.get("/api/payments/banks")
async def get_banks():
    """Get banks"""
    return {
        "banks": [
            {"id": 1, "name": "State Bank of India", "code": "SBI"},
            {"id": 2, "name": "HDFC Bank", "code": "HDFC"},
            {"id": 3, "name": "ICICI Bank", "code": "ICICI"},
            {"id": 4, "name": "Axis Bank", "code": "AXIS"},
            {"id": 5, "name": "Kotak Mahindra Bank", "code": "KOTAK"}
        ]
    }

@app.get("/api/flights/search")
async def search_flights(
    departure_airport: str,
    arrival_airport: str,
    departure_date: str,
    return_date: str = None,
    passengers: int = 1
):
    """Search for flights"""
    try:
        conn = sqlite3.connect('flight_booking.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get departure and arrival airports
        cursor.execute("SELECT * FROM airports WHERE code = ?", (departure_airport.upper(),))
        dep_airport = cursor.fetchone()
        
        cursor.execute("SELECT * FROM airports WHERE code = ?", (arrival_airport.upper(),))
        arr_airport = cursor.fetchone()
        
        if not dep_airport or not arr_airport:
            conn.close()
            return {"flights": [], "total_count": 0, "page": 1, "page_size": 10}
        
        # Search for flights
        cursor.execute("""
            SELECT f.*, a1.name as dep_airport_name, a1.city as dep_city, 
                   a2.name as arr_airport_name, a2.city as arr_city,
                   al.name as airline_name, al.code as airline_code
            FROM flights f
            JOIN airports a1 ON f.departure_airport_id = a1.id
            JOIN airports a2 ON f.arrival_airport_id = a2.id
            JOIN airlines al ON f.airline_id = al.id
            WHERE f.departure_airport_id = ? AND f.arrival_airport_id = ?
            AND f.status = 'SCHEDULED'
            ORDER BY f.departure_time
        """, (dep_airport[0], arr_airport[0]))
        
        flights = cursor.fetchall()
        
        result = []
        for flight in flights:
            # Calculate dynamic pricing
            base_price = flight[7] if len(flight) > 7 else 5000  # Use actual base_price from database
            result.append({
                "id": flight[0],
                "flight_number": flight[1],
                "airline": {
                    "id": flight[2],
                    "name": flight[12],
                    "code": flight[13]
                },
                "departure_airport": {
                    "id": flight[2],
                    "code": departure_airport.upper(),
                    "name": flight[8],
                    "city": flight[9]
                },
                "arrival_airport": {
                    "id": flight[3],
                    "code": arrival_airport.upper(),
                    "name": flight[10],
                    "city": flight[11]
                },
                "departure_time": flight[4],
                "arrival_time": flight[5],
                "duration": flight[6],
                "status": flight[9] if len(flight) > 9 else 'SCHEDULED',
                "base_price": base_price,
                "current_price": base_price
            })
        
        conn.close()
        return {
            "flights": result,
            "total_count": len(result),
            "page": 1,
            "page_size": 10
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/coupons/apply")
async def apply_coupon(coupon_data: dict):
    """Apply coupon code"""
    try:
        conn = sqlite3.connect('flight_booking.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        coupon_code = coupon_data.get('code', '').upper()
        amount = coupon_data.get('amount', 0)
        
        cursor.execute("""
            SELECT * FROM coupons 
            WHERE code = ? AND is_active = 1 
            AND valid_from <= datetime('now') 
            AND valid_until >= datetime('now')
        """, (coupon_code,))
        
        coupon = cursor.fetchone()
        
        if not coupon:
            conn.close()
            return {"valid": False, "message": "Invalid or expired coupon code"}
        
        if amount < coupon['min_amount']:
            conn.close()
            return {"valid": False, "message": f"Minimum amount required: ₹{coupon['min_amount']}"}
        
        # Calculate discount
        if coupon['discount_type'] == 'PERCENTAGE':
            discount = (amount * coupon['discount_value']) / 100
            discount = min(discount, coupon['max_discount'])
        else:  # FIXED
            discount = min(coupon['discount_value'], coupon['max_discount'])
        
        final_amount = max(0, amount - discount)
        
        conn.close()
        return {
            "valid": True,
            "discount": discount,
            "final_amount": final_amount,
            "coupon": {
                "code": coupon['code'],
                "name": coupon['name'],
                "discount_type": coupon['discount_type'],
                "discount_value": coupon['discount_value']
            }
        }
        
    except Exception as e:
        return {"valid": False, "message": str(e)}

if __name__ == "__main__":
    print("Starting Flight Booking Simulator Server")
    print("Server will be available at: http://localhost:8000")
    print("Frontend: Open frontend/index.html in your browser")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
