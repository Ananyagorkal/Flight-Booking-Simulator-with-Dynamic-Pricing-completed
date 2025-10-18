"""
Sample data generator for Flight Booking Simulator (SQLite version)
Run this script to populate the database with sample data
"""

from sqlalchemy.orm import Session
from config_sqlite import SessionLocal, Airport, Airline, Flight, SeatInventory
from datetime import datetime, timedelta
import random

def create_sample_data():
    db = SessionLocal()
    
    try:
        # Create airports
        airports_data = [
            {"code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "USA", "timezone": "America/New_York"},
            {"code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "USA", "timezone": "America/Los_Angeles"},
            {"code": "LHR", "name": "London Heathrow Airport", "city": "London", "country": "UK", "timezone": "Europe/London"},
            {"code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France", "timezone": "Europe/Paris"},
            {"code": "NRT", "name": "Narita International Airport", "city": "Tokyo", "country": "Japan", "timezone": "Asia/Tokyo"},
            {"code": "DXB", "name": "Dubai International Airport", "city": "Dubai", "country": "UAE", "timezone": "Asia/Dubai"},
            {"code": "SIN", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore", "timezone": "Asia/Singapore"},
            {"code": "HKG", "name": "Hong Kong International Airport", "city": "Hong Kong", "country": "Hong Kong", "timezone": "Asia/Hong_Kong"},
            {"code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany", "timezone": "Europe/Berlin"},
            {"code": "AMS", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands", "timezone": "Europe/Amsterdam"},
        ]
        
        airports = []
        for airport_data in airports_data:
            airport = Airport(**airport_data)
            db.add(airport)
            airports.append(airport)
        
        db.commit()
        
        # Create airlines
        airlines_data = [
            {"code": "AA", "name": "American Airlines", "logo_url": "https://example.com/aa-logo.png"},
            {"code": "DL", "name": "Delta Air Lines", "logo_url": "https://example.com/dl-logo.png"},
            {"code": "UA", "name": "United Airlines", "logo_url": "https://example.com/ua-logo.png"},
            {"code": "BA", "name": "British Airways", "logo_url": "https://example.com/ba-logo.png"},
            {"code": "AF", "name": "Air France", "logo_url": "https://example.com/af-logo.png"},
            {"code": "JL", "name": "Japan Airlines", "logo_url": "https://example.com/jl-logo.png"},
            {"code": "EK", "name": "Emirates", "logo_url": "https://example.com/ek-logo.png"},
            {"code": "SQ", "name": "Singapore Airlines", "logo_url": "https://example.com/sq-logo.png"},
            {"code": "LH", "name": "Lufthansa", "logo_url": "https://example.com/lh-logo.png"},
            {"code": "KL", "name": "KLM Royal Dutch Airlines", "logo_url": "https://example.com/kl-logo.png"},
        ]
        
        airlines = []
        for airline_data in airlines_data:
            airline = Airline(**airline_data)
            db.add(airline)
            airlines.append(airline)
        
        db.commit()
        
        # Create flights
        base_prices = [200, 300, 400, 500, 600, 800, 1000, 1200, 1500, 2000]
        flight_numbers = ["100", "200", "300", "400", "500", "600", "700", "800", "900", "1000"]
        
        flights = []
        for i in range(50):  # Create 50 sample flights
            departure_airport = random.choice(airports)
            arrival_airport = random.choice([a for a in airports if a.id != departure_airport.id])
            airline = random.choice(airlines)
            
            # Generate departure time (next 30 days)
            departure_time = datetime.now() + timedelta(
                days=random.randint(1, 30),
                hours=random.randint(6, 22),
                minutes=random.choice([0, 15, 30, 45])
            )
            
            # Generate arrival time (1-12 hours later)
            duration_hours = random.randint(1, 12)
            arrival_time = departure_time + timedelta(hours=duration_hours)
            
            flight_data = {
                "flight_number": f"{airline.code}{random.choice(flight_numbers)}",
                "airline_id": airline.id,
                "departure_airport_id": departure_airport.id,
                "arrival_airport_id": arrival_airport.id,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration_minutes": duration_hours * 60,
                "base_price": random.choice(base_prices),
                "total_seats": random.randint(100, 300),
                "available_seats": random.randint(50, 250),
                "status": "SCHEDULED"
            }
            
            flight = Flight(**flight_data)
            db.add(flight)
            flights.append(flight)
        
        db.commit()
        
        # Create seat inventory for each flight
        seat_classes = ["economy", "premium_economy", "business", "first"]
        seat_class_ratios = {
            "economy": 0.7,
            "premium_economy": 0.15,
            "business": 0.1,
            "first": 0.05
        }
        
        for flight in flights:
            for seat_class, ratio in seat_class_ratios.items():
                total_seats = int(flight.total_seats * ratio)
                available_seats = int(flight.available_seats * ratio)
                booked_seats = total_seats - available_seats
                
                if total_seats > 0:  # Only create inventory if there are seats
                    inventory = SeatInventory(
                        flight_id=flight.id,
                        seat_class=seat_class,
                        total_seats=total_seats,
                        available_seats=available_seats,
                        booked_seats=booked_seats
                    )
                    db.add(inventory)
        
        db.commit()
        print("Sample data created successfully!")
        print(f"Created {len(airports)} airports")
        print(f"Created {len(airlines)} airlines")
        print(f"Created {len(flights)} flights")
        print(f"Created seat inventory for all flights")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
