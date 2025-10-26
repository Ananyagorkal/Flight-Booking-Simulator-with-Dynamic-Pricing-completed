#!/usr/bin/env python3
"""
Test the flight search functionality
"""

import urllib.request
import urllib.parse
import json

API_BASE_URL = "http://localhost:8000/api"

def test_search():
    """Test flight search with different parameters"""
    print("Testing Flight Search...")
    
    # Test 1: Search for Delhi to Mumbai
    print("\n1. Testing Delhi to Mumbai...")
    params = urllib.parse.urlencode({
        "departure_airport": "DEL",
        "arrival_airport": "BOM"
    })
    
    try:
        with urllib.request.urlopen(f"{API_BASE_URL}/flights/search?{params}") as response:
            data = json.loads(response.read().decode())
            print(f"Found {data['total_count']} flights")
            if data['flights']:
                flight = data['flights'][0]
                print(f"  Sample: {flight['flight_number']} - {flight['departure_airport']['code']} to {flight['arrival_airport']['code']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Search for Mumbai to Bangalore
    print("\n2. Testing Mumbai to Bangalore...")
    params = urllib.parse.urlencode({
        "departure_airport": "BOM",
        "arrival_airport": "BLR"
    })
    
    try:
        with urllib.request.urlopen(f"{API_BASE_URL}/flights/search?{params}") as response:
            data = json.loads(response.read().decode())
            print(f"Found {data['total_count']} flights")
            if data['flights']:
                flight = data['flights'][0]
                print(f"  Sample: {flight['flight_number']} - {flight['departure_airport']['code']} to {flight['arrival_airport']['code']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Search for Delhi to Dubai (International)
    print("\n3. Testing Delhi to Dubai (International)...")
    params = urllib.parse.urlencode({
        "departure_airport": "DEL",
        "arrival_airport": "DXB"
    })
    
    try:
        with urllib.request.urlopen(f"{API_BASE_URL}/flights/search?{params}") as response:
            data = json.loads(response.read().decode())
            print(f"Found {data['total_count']} flights")
            if data['flights']:
                flight = data['flights'][0]
                print(f"  Sample: {flight['flight_number']} - {flight['departure_airport']['code']} to {flight['arrival_airport']['code']}")
                print(f"  Price: ₹{flight.get('current_price', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Get all flights
    print("\n4. Testing get all flights...")
    try:
        with urllib.request.urlopen(f"{API_BASE_URL}/flights/") as response:
            data = json.loads(response.read().decode())
            print(f"Total flights available: {data['total_count']}")
            print("Sample routes:")
            for i, flight in enumerate(data['flights'][:5]):
                print(f"  {i+1}. {flight['flight_number']}: {flight['departure_airport']['code']} → {flight['arrival_airport']['code']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
