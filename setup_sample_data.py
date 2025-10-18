#!/usr/bin/env python3
"""
Setup script to populate the database with sample data
"""

import sys
import os
sys.path.append('backend')

from backend.database import SessionLocal, engine, Base
from backend.sample_coupons import create_sample_coupons
from backend.sample_data import create_sample_data

def setup_database():
    """Setup database with sample data"""
    print("🗄️ Setting up database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
        
        # Create sample data
        print("📊 Creating sample data...")
        create_sample_data()
        print("✅ Sample data created")
        
        # Create sample coupons
        print("🎫 Creating sample coupons...")
        create_sample_coupons()
        print("✅ Sample coupons created")
        
        print("\n🎉 Database setup completed successfully!")
        print("\nYou can now:")
        print("1. Start the backend server: python backend/main.py")
        print("2. Open frontend/index.html in a browser")
        print("3. Test the flight booking system with coupons")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    setup_database()
