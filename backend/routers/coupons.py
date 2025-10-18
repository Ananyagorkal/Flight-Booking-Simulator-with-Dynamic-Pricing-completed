from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from config_sqlite import get_db, Coupon
from models import CouponCreate, Coupon, CouponValidation, CouponValidationResponse, CouponListResponse

router = APIRouter()

@router.get("/", response_model=CouponListResponse)
async def get_available_coupons(db: Session = Depends(get_db)):
    """Get all available coupons"""
    now = datetime.utcnow()
    coupons = db.query(Coupon).filter(
        Coupon.is_active == True,
        Coupon.valid_from <= now,
        Coupon.valid_until >= now
    ).all()
    
    return CouponListResponse(coupons=coupons)

@router.get("/{coupon_code}", response_model=Coupon)
async def get_coupon_by_code(coupon_code: str, db: Session = Depends(get_db)):
    """Get coupon details by code"""
    coupon = db.query(Coupon).filter(
        Coupon.code == coupon_code.upper(),
        Coupon.is_active == True
    ).first()
    
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    now = datetime.utcnow()
    if coupon.valid_from > now or coupon.valid_until < now:
        raise HTTPException(status_code=400, detail="Coupon is not valid at this time")
    
    return coupon

@router.post("/apply", response_model=CouponValidationResponse)
async def apply_coupon(coupon_data: CouponValidation, db: Session = Depends(get_db)):
    """Apply coupon to a booking"""
    coupon = db.query(Coupon).filter(
        Coupon.code == coupon_data.coupon_code.upper(),
        Coupon.is_active == True
    ).first()
    
    if not coupon:
        return CouponValidationResponse(
            valid=False,
            message="Invalid coupon code"
        )
    
    now = datetime.utcnow()
    if coupon.valid_from > now or coupon.valid_until < now:
        return CouponValidationResponse(
            valid=False,
            message="Coupon has expired"
        )
    
    if coupon_data.booking_amount < coupon.min_amount:
        return CouponValidationResponse(
            valid=False,
            message=f"Minimum booking amount of ₹{coupon.min_amount} required"
        )
    
    # Calculate discount
    if coupon.discount_type.value == "percentage":
        discount_amount = (coupon_data.booking_amount * coupon.discount_value) / 100
        discount_amount = min(discount_amount, coupon.max_discount)
    else:  # fixed
        discount_amount = min(coupon.discount_value, coupon.max_discount)
    
    final_amount = coupon_data.booking_amount - discount_amount
    
    return CouponValidationResponse(
        valid=True,
        message="Coupon applied successfully",
        coupon_details=coupon,
        discount_amount=discount_amount,
        final_amount=final_amount,
        original_amount=coupon_data.booking_amount,
        savings=discount_amount
    )

@router.post("/", response_model=Coupon)
async def create_coupon(coupon_data: CouponCreate, db: Session = Depends(get_db)):
    """Create a new coupon (admin endpoint)"""
    # Check if coupon code already exists
    existing_coupon = db.query(Coupon).filter(Coupon.code == coupon_data.code.upper()).first()
    if existing_coupon:
        raise HTTPException(status_code=400, detail="Coupon code already exists")
    
    coupon = Coupon(
        code=coupon_data.code.upper(),
        name=coupon_data.name,
        description=coupon_data.description,
        discount_type=coupon_data.discount_type,
        discount_value=coupon_data.discount_value,
        min_amount=coupon_data.min_amount,
        max_discount=coupon_data.max_discount,
        valid_from=coupon_data.valid_from,
        valid_until=coupon_data.valid_until,
        is_active=coupon_data.is_active
    )
    
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    
    return coupon
