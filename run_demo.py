#!/usr/bin/env python3
"""
Demo script to run the Flight Booking Simulator
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def main():
    print("🎫 Flight Booking Simulator - Demo")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists("flight_booking.db"):
        print("📊 Setting up database...")
        subprocess.run([sys.executable, "setup_simple.py"])
        print("✅ Database setup complete")
    
    # Start the server
    print("🚀 Starting backend server...")
    try:
        # Change to backend directory and start server
        os.chdir("backend")
        server_process = subprocess.Popen([
            sys.executable, "main_sqlite.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Backend server started on http://localhost:8000")
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Open frontend
        print("🌐 Opening frontend...")
        os.chdir("..")
        frontend_path = Path("frontend/index.html").absolute()
        webbrowser.open(f"file://{frontend_path}")
        
        print("\n🎉 Flight Booking Simulator is ready!")
        print("\n📋 What you can do:")
        print("1. Search for flights")
        print("2. Apply coupon codes:")
        print("   - WELCOME10: 10% off (min ₹5000)")
        print("   - SAVE500: ₹500 off (min ₹10000)")
        print("   - EARLY20: 20% off (min ₹8000)")
        print("   - STUDENT15: 15% off (min ₹3000)")
        print("   - FLASH1000: ₹1000 off (min ₹15000)")
        print("3. Complete bookings with passenger details")
        print("4. Test payment methods")
        print("\n🔧 Server running on: http://localhost:8000")
        print("📱 Frontend: frontend/index.html")
        print("\nPress Ctrl+C to stop the server")
        
        # Keep the script running
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n👋 Stopping server...")
            server_process.terminate()
            print("✅ Server stopped")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
