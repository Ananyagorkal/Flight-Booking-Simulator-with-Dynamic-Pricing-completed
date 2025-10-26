#!/usr/bin/env python3
"""
Quick test without any external dependencies
"""

import urllib.request
import json

def quick_test():
    """Quick test of the API"""
    print("Testing Flight Booking Simulator...")
    
    try:
        # Test health endpoint
        with urllib.request.urlopen("http://localhost:8000/health") as response:
            data = json.loads(response.read().decode())
            print(f"✓ Health check: {data['status']}")
        
        # Test airports
        with urllib.request.urlopen("http://localhost:8000/api/flights/airports/") as response:
            airports = json.loads(response.read().decode())
            print(f"✓ Found {len(airports)} airports")
        
        # Test flight search
        with urllib.request.urlopen("http://localhost:8000/api/flights/search?departure_airport=JFK&arrival_airport=LAX") as response:
            search_result = json.loads(response.read().decode())
            print(f"✓ Found {search_result['total_count']} flights")
            
            if search_result['flights']:
                flight = search_result['flights'][0]
                print(f"  Sample flight: {flight['flight_number']} - ${flight.get('current_price', 'N/A')}")
        
        print("\n🎉 All tests passed! Your system is working!")
        print("\nNext steps:")
        print("1. Open frontend/index.html in your browser")
        print("2. Visit http://localhost:8000/docs for API docs")
        print("3. Try searching for flights and making bookings")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure the server is running:")
        print("python minimal_server.py")

if __name__ == "__main__":
    quick_test()

