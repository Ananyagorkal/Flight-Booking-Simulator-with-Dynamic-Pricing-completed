#!/usr/bin/env python3
"""
Simple setup script using SQLite (no MySQL required)
"""

import sys
import os
sys.path.append('backend')

# Use SQLite configuration
from backend.config_sqlite import SessionLocal, engine, Base, Coupon, DiscountType
from backend.sample_data_sqlite import create_sample_data
from datetime import datetime, timedelta

def create_sample_coupons_sqlite():
    """Create sample coupons for SQLite"""
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
        print("✅ Sample coupons created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample coupons: {e}")
        db.rollback()
    finally:
        db.close()

def setup_database_sqlite():
    """Setup SQLite database with sample data"""
    print("Setting up SQLite database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created")
        
        # Create sample data
        print("Creating sample data...")
        create_sample_data()
        print("Sample data created")
        
        # Create sample coupons
        print("Creating sample coupons...")
        create_sample_coupons_sqlite()
        print("Sample coupons created")
        
        print("\nDatabase setup completed successfully!")
        print("\nYou can now:")
        print("1. Start the backend server: python backend/main.py")
        print("2. Open frontend/index.html in a browser")
        print("3. Test the flight booking system with coupons")
        print("\nNote: Using SQLite database (flight_booking.db) - no MySQL required!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    setup_database_sqlite()
