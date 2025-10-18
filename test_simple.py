#!/usr/bin/env python3
"""
Simple test script for the SQLite version
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = 'http://localhost:8000/api'

def test_basic_endpoints():
    """Test basic API endpoints"""
    print("Testing Flight Booking Simulator (SQLite Version)")
    print("=" * 60)
    
    try:
        # Test 1: Health check
        print("\n1. Testing health check...")
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("Server is running")
        else:
            print(f"Server health check failed: {response.status_code}")
            return
        
        # Test 2: Get available coupons
        print("\n2. Testing coupon endpoints...")
        response = requests.get(f"{API_BASE_URL}/coupons/")
        if response.status_code == 200:
            coupons = response.json()
            print(f"Found {len(coupons['coupons'])} coupons")
            for coupon in coupons['coupons'][:3]:
                print(f"   - {coupon['code']}: {coupon['name']}")
        else:
            print(f"Failed to get coupons: {response.status_code}")
        
        # Test 3: Test coupon validation
        print("\n3. Testing coupon validation...")
        coupon_data = {
            "coupon_code": "WELCOME10",
            "booking_amount": 15000.0,
            "seat_class": "economy",
            "passengers": 1
        }
        response = requests.post(f"{API_BASE_URL}/coupons/apply", json=coupon_data)
        if response.status_code == 200:
            result = response.json()
            if result['valid']:
                print(f"Coupon validation successful!")
                print(f"   - Original: ₹{result['original_amount']}")
                print(f"   - Discount: ₹{result['discount_amount']}")
                print(f"   - Final: ₹{result['final_amount']}")
            else:
                print(f"Coupon validation failed: {result['message']}")
        else:
            print(f"Failed to validate coupon: {response.status_code}")
        
        # Test 4: Payment methods
        print("\n4. Testing payment methods...")
        response = requests.get(f"{API_BASE_URL}/payments/methods")
        if response.status_code == 200:
            methods = response.json()
            print(f"Found {len(methods['payment_methods'])} payment methods")
        else:
            print(f"Failed to get payment methods: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("\nAvailable Coupons:")
        print("   - WELCOME10: 10% off (min ₹5000)")
        print("   - SAVE500: ₹500 off (min ₹10000)")
        print("   - EARLY20: 20% off (min ₹8000)")
        print("   - STUDENT15: 15% off (min ₹3000)")
        print("   - FLASH1000: ₹1000 off (min ₹15000)")
        
    except requests.exceptions.ConnectionError:
        print("Cannot connect to API. Make sure the server is running:")
        print("   python backend/main_sqlite.py")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_basic_endpoints()