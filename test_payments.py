#!/usr/bin/env python3
"""
Test the payment system functionality
"""

import urllib.request
import urllib.parse
import json

API_BASE_URL = "http://localhost:8000/api"

def test_payments():
    """Test payment system functionality"""
    print("💳 Testing Payment System...")
    
    # Test 1: Get payment methods
    print("\n1. Getting payment methods...")
    try:
        with urllib.request.urlopen(f"{API_BASE_URL}/payments/methods") as response:
            data = json.loads(response.read().decode())
            print(f"Found {data['total_count']} payment methods:")
            for method in data['payment_methods']:
                print(f"  - {method['name']}: {method['description']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get banks
    print("\n2. Getting banks for net banking...")
    try:
        with urllib.request.urlopen(f"{API_BASE_URL}/payments/banks") as response:
            data = json.loads(response.read().decode())
            print(f"Found {data['total_count']} banks:")
            for bank in data['banks'][:5]:  # Show first 5
                print(f"  - {bank['name']} ({bank['code']})")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Initiate payment
    print("\n3. Testing payment initiation...")
    try:
        payment_data = {
            "booking_id": "TEST123",
            "amount": 5000,
            "payment_method": "credit_card",
            "currency": "INR"
        }
        
        data = json.dumps(payment_data).encode('utf-8')
        req = urllib.request.Request(
            f"{API_BASE_URL}/payments/initiate",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"✅ Payment initiated: {result['payment_id']}")
            print(f"   Amount: ₹{result['amount']}")
            print(f"   Method: {result['payment_method']}")
            print(f"   Status: {result['status']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Process payment (simulate success)
    print("\n4. Testing payment processing...")
    try:
        process_data = {
            "payment_id": "TEST123",  # This will fail as it doesn't exist
            "payment_method": "credit_card",
            "card_details": {
                "card_number": "4111111111111111",
                "card_name": "John Doe",
                "card_expiry": "12/25",
                "card_cvv": "123"
            }
        }
        
        data = json.dumps(process_data).encode('utf-8')
        req = urllib.request.Request(
            f"{API_BASE_URL}/payments/process",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            if result.get('success'):
                print(f"✅ Payment successful: {result['message']}")
                print(f"   Transaction ID: {result['transaction_id']}")
            else:
                print(f"❌ Payment failed: {result['message']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Test UPI payment
    print("\n5. Testing UPI payment...")
    try:
        upi_data = {
            "payment_id": "TEST123",
            "payment_method": "upi",
            "upi_details": {
                "upi_id": "test@paytm"
            }
        }
        
        data = json.dumps(upi_data).encode('utf-8')
        req = urllib.request.Request(
            f"{API_BASE_URL}/payments/process",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"UPI Payment result: {result.get('message', 'Unknown')}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n🎉 Payment system test completed!")
    print("\nAvailable payment methods:")
    print("  - Credit Card (Visa, Mastercard, Amex)")
    print("  - Debit Card (Visa, Mastercard, RuPay)")
    print("  - Net Banking (All major Indian banks)")
    print("  - UPI (PhonePe, Google Pay, Paytm, BHIM)")
    print("  - Digital Wallet (Paytm, PhonePe, Amazon Pay)")
    print("  - EMI (3, 6, 12 months)")

if __name__ == "__main__":
    test_payments()
