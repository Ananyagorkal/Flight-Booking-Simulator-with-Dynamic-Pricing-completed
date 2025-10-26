#!/usr/bin/env python3
"""
Simple startup script for the Flight Booking Simulator
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✅ Required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def setup_database():
    """Setup the database"""
    print("🗄️ Setting up database...")
    try:
        result = subprocess.run([sys.executable, "setup_simple.py"], 
                              capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print("✅ Database setup completed")
            return True
        else:
            print(f"❌ Database setup failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def start_server():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    try:
        # Change to backend directory
        os.chdir("backend")
        
        # Start the server
        subprocess.Popen([
            sys.executable, "main_sqlite.py"
        ])
        
        print("✅ Backend server started on http://localhost:8000")
        return True
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def open_frontend():
    """Open the frontend in browser"""
    print("🌐 Opening frontend...")
    try:
        frontend_path = Path("frontend/index.html").absolute()
        webbrowser.open(f"file://{frontend_path}")
        print("✅ Frontend opened in browser")
        return True
    except Exception as e:
        print(f"❌ Failed to open frontend: {e}")
        return False

def main():
    print("🎫 Flight Booking Simulator - Simple Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Setup database
    if not setup_database():
        return
    
    # Start server
    if not start_server():
        return
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Open frontend
    if not open_frontend():
        print("💡 You can manually open frontend/index.html in your browser")
    
    print("\n🎉 Flight Booking Simulator is ready!")
    print("\n📋 What you can do:")
    print("1. Search for flights")
    print("2. Apply coupon codes (WELCOME10, SAVE500, etc.)")
    print("3. Complete bookings with passenger details")
    print("4. Test payment methods")
    print("\n🔧 Server running on: http://localhost:8000")
    print("📱 Frontend: frontend/index.html")
    print("\nPress Ctrl+C to stop the server")

if __name__ == "__main__":
    try:
        main()
        # Keep the script running
        input("\nPress Enter to stop the server...")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

