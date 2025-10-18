from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import PaymentMethodsResponse, PaymentMethod, BanksResponse, Bank

router = APIRouter()

@router.get("/methods", response_model=PaymentMethodsResponse)
async def get_payment_methods():
    """Get available payment methods"""
    payment_methods = [
        PaymentMethod(
            id="credit_card",
            name="Credit Card",
            description="Pay with Visa, Mastercard, or American Express",
            icon="fas fa-credit-card"
        ),
        PaymentMethod(
            id="debit_card",
            name="Debit Card",
            description="Pay with your debit card",
            icon="fas fa-credit-card"
        ),
        PaymentMethod(
            id="upi",
            name="UPI",
            description="Pay using UPI ID",
            icon="fas fa-mobile-alt"
        ),
        PaymentMethod(
            id="netbanking",
            name="Net Banking",
            description="Pay using net banking",
            icon="fas fa-university"
        ),
        PaymentMethod(
            id="wallet",
            name="Digital Wallet",
            description="Pay using digital wallets",
            icon="fas fa-wallet"
        ),
        PaymentMethod(
            id="emi",
            name="EMI",
            description="Pay in installments",
            icon="fas fa-calendar-alt"
        )
    ]
    
    return PaymentMethodsResponse(payment_methods=payment_methods)

@router.get("/banks", response_model=BanksResponse)
async def get_banks():
    """Get available banks for net banking"""
    banks = [
        Bank(code="SBI", name="State Bank of India"),
        Bank(code="HDFC", name="HDFC Bank"),
        Bank(code="ICICI", name="ICICI Bank"),
        Bank(code="AXIS", name="Axis Bank"),
        Bank(code="KOTAK", name="Kotak Mahindra Bank"),
        Bank(code="PNB", name="Punjab National Bank"),
        Bank(code="BOI", name="Bank of India"),
        Bank(code="BOB", name="Bank of Baroda"),
        Bank(code="CANARA", name="Canara Bank"),
        Bank(code="UNION", name="Union Bank of India")
    ]
    
    return BanksResponse(banks=banks)

@router.post("/initiate")
async def initiate_payment(payment_data: dict):
    """Initiate payment process"""
    # This is a mock implementation
    # In a real system, you would integrate with payment gateways
    return {
        "payment_id": f"PAY_{payment_data.get('booking_id', '123')}_{payment_data.get('amount', '1000')}",
        "status": "initiated",
        "message": "Payment initiated successfully"
    }

@router.post("/process")
async def process_payment(payment_data: dict):
    """Process payment"""
    # This is a mock implementation
    # In a real system, you would validate payment details and process the payment
    return {
        "success": True,
        "transaction_id": f"TXN_{payment_data.get('payment_id', '123')}",
        "message": "Payment processed successfully"
    }
