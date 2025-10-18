#!/usr/bin/env python3
"""
Test script to verify coupon functionality and passenger details display
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = 'http://localhost:8000/api'

def test_coupon_endpoints():
    """Test coupon-related endpoints"""
    print("Testing Coupon Endpoints...")
    
    try:
        # Test 1: Get available coupons
        print("\n1. Testing GET /api/coupons/")
        response = requests.get(f"{API_BASE_URL}/coupons/")
        if response.status_code == 200:
            coupons = response.json()
            print(f"✅ Successfully retrieved {len(coupons['coupons'])} coupons")
            for coupon in coupons['coupons'][:3]:  # Show first 3
                print(f"   - {coupon['code']}: {coupon['name']}")
        else:
            print(f"❌ Failed to get coupons: {response.status_code}")
        
        # Test 2: Get specific coupon
        print("\n2. Testing GET /api/coupons/WELCOME10")
        response = requests.get(f"{API_BASE_URL}/coupons/WELCOME10")
        if response.status_code == 200:
            coupon = response.json()
            print(f"✅ Successfully retrieved coupon: {coupon['name']}")
        else:
            print(f"❌ Failed to get coupon: {response.status_code}")
        
        # Test 3: Apply coupon
        print("\n3. Testing POST /api/coupons/apply")
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
                print(f"✅ Coupon applied successfully!")
                print(f"   - Original: ₹{result['original_amount']}")
                print(f"   - Discount: ₹{result['discount_amount']}")
                print(f"   - Final: ₹{result['final_amount']}")
            else:
                print(f"❌ Coupon validation failed: {result['message']}")
        else:
            print(f"❌ Failed to apply coupon: {response.status_code}")
        
        # Test 4: Test invalid coupon
        print("\n4. Testing invalid coupon")
        invalid_coupon_data = {
            "coupon_code": "INVALID123",
            "booking_amount": 15000.0,
            "seat_class": "economy",
            "passengers": 1
        }
        response = requests.post(f"{API_BASE_URL}/coupons/apply", json=invalid_coupon_data)
        if response.status_code == 200:
            result = response.json()
            if not result['valid']:
                print(f"✅ Correctly rejected invalid coupon: {result['message']}")
            else:
                print(f"❌ Should have rejected invalid coupon")
        else:
            print(f"❌ Failed to test invalid coupon: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error testing coupons: {e}")

def test_payment_endpoints():
    """Test payment-related endpoints"""
    print("\nTesting Payment Endpoints...")
    
    try:
        # Test payment methods
        print("\n1. Testing GET /api/payments/methods")
        response = requests.get(f"{API_BASE_URL}/payments/methods")
        if response.status_code == 200:
            methods = response.json()
            print(f"✅ Successfully retrieved {len(methods['payment_methods'])} payment methods")
            for method in methods['payment_methods'][:3]:
                print(f"   - {method['name']}: {method['description']}")
        else:
            print(f"❌ Failed to get payment methods: {response.status_code}")
        
        # Test banks
        print("\n2. Testing GET /api/payments/banks")
        response = requests.get(f"{API_BASE_URL}/payments/banks")
        if response.status_code == 200:
            banks = response.json()
            print(f"✅ Successfully retrieved {len(banks['banks'])} banks")
            for bank in banks['banks'][:3]:
                print(f"   - {bank['name']} ({bank['code']})")
        else:
            print(f"❌ Failed to get banks: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error testing payments: {e}")

def main():
    print("🧪 Testing Flight Booking Simulator Fixes")
    print("=" * 50)
    
    # Test coupon functionality
    test_coupon_endpoints()
    
    # Test payment functionality
    test_payment_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
    print("\nTo test the full application:")
    print("1. Start the backend server: python backend/main.py")
    print("2. Open frontend/index.html in a browser")
    print("3. Try booking a flight and applying coupons")

if __name__ == "__main__":
    main()
