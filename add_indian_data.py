#!/usr/bin/env python3
"""
Add Indian airports and airlines to the database
"""

import sqlite3
from datetime import datetime, timedelta
import random

def add_indian_data():
    """Add Indian airports and airlines"""
    conn = sqlite3.connect('flight_booking.db')
    cursor = conn.cursor()
    
    try:
        # Add Indian airports
        indian_airports = [
            ('DEL', 'Indira Gandhi International Airport', 'New Delhi', 'India', 'Asia/Kolkata'),
            ('BOM', 'Chhatrapati Shivaji Maharaj International Airport', 'Mumbai', 'India', 'Asia/Kolkata'),
            ('BLR', 'Kempegowda International Airport', 'Bangalore', 'India', 'Asia/Kolkata'),
            ('MAA', 'Chennai International Airport', 'Chennai', 'India', 'Asia/Kolkata'),
            ('CCU', 'Netaji Subhash Chandra Bose International Airport', 'Kolkata', 'India', 'Asia/Kolkata'),
            ('HYD', 'Rajiv Gandhi International Airport', 'Hyderabad', 'India', 'Asia/Kolkata'),
            ('AMD', 'Sardar Vallabhbhai Patel International Airport', 'Ahmedabad', 'India', 'Asia/Kolkata'),
            ('COK', 'Cochin International Airport', 'Kochi', 'India', 'Asia/Kolkata'),
            ('GOI', 'Dabolim Airport', 'Goa', 'India', 'Asia/Kolkata'),
            ('PNQ', 'Pune Airport', 'Pune', 'India', 'Asia/Kolkata')
        ]
        
        for airport in indian_airports:
            cursor.execute("""
                INSERT OR IGNORE INTO airports (code, name, city, country, timezone)
                VALUES (?, ?, ?, ?, ?)
            """, airport)
        
        # Add Indian airlines
        indian_airlines = [
            ('AI', 'Air India', 'https://example.com/air-india.png'),
            ('6E', 'IndiGo', 'https://example.com/indigo.png'),
            ('SG', 'SpiceJet', 'https://example.com/spicejet.png'),
            ('G8', 'GoAir', 'https://example.com/goair.png'),
            ('I5', 'AirAsia India', 'https://example.com/airasia.png'),
            ('UK', 'Vistara', 'https://example.com/vistara.png'),
            ('9W', 'Jet Airways', 'https://example.com/jetairways.png'),
            ('S2', 'TruJet', 'https://example.com/trujet.png')
        ]
        
        for airline in indian_airlines:
            cursor.execute("""
                INSERT OR IGNORE INTO airlines (code, name, logo_url)
                VALUES (?, ?, ?)
            """, airline)
        
        # Get airport and airline IDs
        cursor.execute("SELECT id, code FROM airports WHERE country = 'India'")
        indian_airport_ids = {row[1]: row[0] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id, code FROM airlines WHERE code IN ('AI', '6E', 'SG', 'G8', 'I5', 'UK', '9W', 'S2')")
        indian_airline_ids = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Add Indian domestic flights
        indian_flights = []
        routes = [
            ('DEL', 'BOM'), ('BOM', 'DEL'), ('DEL', 'BLR'), ('BLR', 'DEL'),
            ('DEL', 'MAA'), ('MAA', 'DEL'), ('DEL', 'CCU'), ('CCU', 'DEL'),
            ('BOM', 'BLR'), ('BLR', 'BOM'), ('BOM', 'MAA'), ('MAA', 'BOM'),
            ('BOM', 'HYD'), ('HYD', 'BOM'), ('BLR', 'HYD'), ('HYD', 'BLR'),
            ('DEL', 'HYD'), ('HYD', 'DEL'), ('DEL', 'AMD'), ('AMD', 'DEL'),
            ('BOM', 'COK'), ('COK', 'BOM'), ('BLR', 'COK'), ('COK', 'BLR'),
            ('DEL', 'GOI'), ('GOI', 'DEL'), ('BOM', 'GOI'), ('GOI', 'BOM')
        ]
        
        flight_id = 51  # Start from 51
        for dep_code, arr_code in routes:
            if dep_code in indian_airport_ids and arr_code in indian_airport_ids:
                for airline_code in ['AI', '6E', 'SG', 'G8', 'I5', 'UK']:
                    if airline_code in indian_airline_ids:
                        # Create multiple flights for each route
                        for i in range(3):  # 3 flights per route per airline
                            dep_time = datetime.now() + timedelta(days=random.randint(1, 30), hours=random.randint(6, 22))
                            duration = random.randint(60, 300)  # 1-5 hours
                            arr_time = dep_time + timedelta(minutes=duration)
                            
                            flight_number = f"{airline_code}{random.randint(100, 9999)}"
                            
                            base_price = random.randint(3000, 15000)  # Indian domestic flight prices
                            total_seats = random.randint(120, 200)  # Indian domestic aircraft capacity
                            available_seats = random.randint(20, total_seats)
                            
                            cursor.execute("""
                                INSERT INTO flights (
                                    flight_number, airline_id, departure_airport_id, arrival_airport_id,
                                    departure_time, arrival_time, duration_minutes, base_price, total_seats, available_seats, status
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                flight_number,
                                indian_airline_ids[airline_code],
                                indian_airport_ids[dep_code],
                                indian_airport_ids[arr_code],
                                dep_time.isoformat(),
                                arr_time.isoformat(),
                                duration,
                                base_price,
                                total_seats,
                                available_seats,
                                'SCHEDULED'
                            ))
                            
                            flight_id += 1
        
        # Add seat inventory for Indian flights
        cursor.execute("SELECT id FROM flights WHERE id >= 51")
        indian_flight_ids = [row[0] for row in cursor.fetchall()]
        
        for flight_id in indian_flight_ids:
            seat_classes = ['economy', 'premium_economy', 'business', 'first']
            for seat_class in seat_classes:
                total_seats = random.randint(50, 200)
                available_seats = random.randint(20, total_seats)
                booked_seats = total_seats - available_seats
                
                cursor.execute("""
                    INSERT INTO seat_inventory (
                        flight_id, seat_class, total_seats, available_seats, booked_seats, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    flight_id, seat_class, total_seats, available_seats, booked_seats,
                    datetime.now().isoformat()
                ))
        
        conn.commit()
        print("Indian airports, airlines, and flights added successfully!")
        print(f"Added {len(indian_airports)} Indian airports")
        print(f"Added {len(indian_airlines)} Indian airlines")
        print(f"Added {len(indian_flight_ids)} Indian domestic flights")
        
    except Exception as e:
        print(f"Error adding Indian data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_indian_data()
