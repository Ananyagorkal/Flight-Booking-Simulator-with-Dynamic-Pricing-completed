#!/usr/bin/env python3
"""
Test coupon functionality
"""

import requests
import json

def test_coupons():
    base_url = "http://localhost:8000/api"
    
    print("🧪 Testing Coupon System...")
    print("=" * 50)
    
    # Test 1: Get all coupons
    print("\n1. Testing GET /coupons/")
    try:
        response = requests.get(f"{base_url}/coupons/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data.get('coupons', []))} coupons")
            for coupon in data.get('coupons', []):
                print(f"   - {coupon['code']}: {coupon['name']} ({coupon['discount_type']} {coupon['discount_value']}%)")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Apply coupon
    print("\n2. Testing POST /coupons/apply")
    try:
        payload = {
            "code": "WELCOME10",
            "amount": 10000
        }
        response = requests.post(f"{base_url}/coupons/apply", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Coupon applied")
            print(f"   - Valid: {data.get('valid', False)}")
            print(f"   - Discount: ₹{data.get('discount', 0)}")
            print(f"   - Final Amount: ₹{data.get('final_amount', 0)}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Test invalid coupon
    print("\n3. Testing invalid coupon")
    try:
        payload = {
            "code": "INVALID123",
            "amount": 10000
        }
        response = requests.post(f"{base_url}/coupons/apply", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Invalid coupon handled")
            print(f"   - Valid: {data.get('valid', False)}")
            print(f"   - Message: {data.get('message', 'No message')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Coupon testing completed!")

if __name__ == "__main__":
    test_coupons()
