from sqlalchemy.orm import Session
from database import SessionLocal, Coupon, DiscountType
from datetime import datetime, timedelta

def create_sample_coupons():
    """Create sample coupons for testing"""
    db = SessionLocal()
    
    try:
        # Check if coupons already exist
        existing_coupons = db.query(Coupon).count()
        if existing_coupons > 0:
            print("Sample coupons already exist. Skipping creation.")
            return
        
        # Create sample coupons
        sample_coupons = [
            Coupon(
                code="WELCOME10",
                name="Welcome Discount",
                description="10% off on your first booking",
                discount_type=DiscountType.PERCENTAGE,
                discount_value=10.0,
                min_amount=5000.0,
                max_discount=2000.0,
                valid_from=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=365),
                is_active=True
            ),
            Coupon(
                code="SAVE500",
                name="Fixed Discount",
                description="₹500 off on bookings above ₹10000",
                discount_type=DiscountType.FIXED,
                discount_value=500.0,
                min_amount=10000.0,
                max_discount=500.0,
                valid_from=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=180),
                is_active=True
            ),
            Coupon(
                code="EARLY20",
                name="Early Bird",
                description="20% off on advance bookings",
                discount_type=DiscountType.PERCENTAGE,
                discount_value=20.0,
                min_amount=8000.0,
                max_discount=5000.0,
                valid_from=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=90),
                is_active=True
            ),
            Coupon(
                code="STUDENT15",
                name="Student Discount",
                description="15% off for students",
                discount_type=DiscountType.PERCENTAGE,
                discount_value=15.0,
                min_amount=3000.0,
                max_discount=3000.0,
                valid_from=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=60),
                is_active=True
            ),
            Coupon(
                code="FLASH1000",
                name="Flash Sale",
                description="₹1000 off on all bookings",
                discount_type=DiscountType.FIXED,
                discount_value=1000.0,
                min_amount=15000.0,
                max_discount=1000.0,
                valid_from=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=7),
                is_active=True
            )
        ]
        
        for coupon in sample_coupons:
            db.add(coupon)
        
        db.commit()
        print("Sample coupons created successfully!")
        
    except Exception as e:
        print(f"Error creating sample coupons: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_coupons()
