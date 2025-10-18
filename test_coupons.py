#!/usr/bin/env python3
"""
Test the coupon system functionality
"""

import urllib.request
import urllib.parse
import json

API_BASE_URL = "http://localhost:8000/api"

def test_coupons():
    """Test coupon system functionality"""
    print("🎫 Testing Coupon System...")
    
    # Test 1: Get all coupons
    print("\n1. Getting all available coupons...")
    try:
        with urllib.request.urlopen(f"{API_BASE_URL}/coupons/") as response:
            data = json.loads(response.read().decode())
            print(f"Found {data['total_count']} coupons:")
            for coupon in data['coupons'][:3]:
                print(f"  - {coupon['code']}: {coupon['name']} ({coupon['description']})")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Validate a valid coupon
    print("\n2. Testing valid coupon validation...")
    try:
        coupon_data = {
            "coupon_code": "WELCOME20",
            "booking_amount": 10000,
            "seat_class": "economy",
            "passengers": 1
        }
        
        data = json.dumps(coupon_data).encode('utf-8')
        req = urllib.request.Request(
            f"{API_BASE_URL}/coupons/validate",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            if result['valid']:
                print(f"✅ {result['message']}")
                print(f"   Discount: ₹{result['discount_amount']}")
            else:
                print(f"❌ {result['message']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Apply a coupon
    print("\n3. Testing coupon application...")
    try:
        coupon_data = {
            "coupon_code": "SAVE500",
            "booking_amount": 5000,
            "seat_class": "economy",
            "passengers": 1
        }
        
        data = json.dumps(coupon_data).encode('utf-8')
        req = urllib.request.Request(
            f"{API_BASE_URL}/coupons/apply",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            if result['valid']:
                print(f"✅ {result['message']}")
                print(f"   Original: ₹{result['original_amount']}")
                print(f"   Discount: ₹{result['discount_amount']}")
                print(f"   Final: ₹{result['final_amount']}")
                print(f"   Savings: ₹{result['savings']}")
            else:
                print(f"❌ {result['message']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Test invalid coupon
    print("\n4. Testing invalid coupon...")
    try:
        coupon_data = {
            "coupon_code": "INVALID",
            "booking_amount": 5000,
            "seat_class": "economy",
            "passengers": 1
        }
        
        data = json.dumps(coupon_data).encode('utf-8')
        req = urllib.request.Request(
            f"{API_BASE_URL}/coupons/validate",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"❌ {result['message']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Test minimum amount requirement
    print("\n5. Testing minimum amount requirement...")
    try:
        coupon_data = {
            "coupon_code": "WELCOME20",
            "booking_amount": 2000,  # Below minimum
            "seat_class": "economy",
            "passengers": 1
        }
        
        data = json.dumps(coupon_data).encode('utf-8')
        req = urllib.request.Request(
            f"{API_BASE_URL}/coupons/validate",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"❌ {result['message']}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n🎉 Coupon system test completed!")
    print("\nAvailable coupon codes to try:")
    print("  - WELCOME20: 20% off (min ₹5000)")
    print("  - SAVE500: ₹500 off (min ₹3000)")
    print("  - FIRSTCLASS: ₹2000 off Business/First (min ₹15000)")
    print("  - EARLYBIRD: 15% off (min ₹10000)")
    print("  - STUDENT10: 10% off (min ₹2000)")
    print("  - FAMILY: ₹1000 off for 3+ passengers (min ₹15000)")

if __name__ == "__main__":
    test_coupons()
