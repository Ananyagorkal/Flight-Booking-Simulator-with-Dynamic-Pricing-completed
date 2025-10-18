#!/usr/bin/env python3
"""
Simple server startup script
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def main():
    print("Flight Booking Simulator - Starting Server")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists("flight_booking.db"):
        print("Setting up database...")
        try:
            result = subprocess.run([sys.executable, "setup_simple.py"], 
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0:
                print("Database setup complete")
            else:
                print(f"Database setup failed: {result.stderr}")
                return
        except Exception as e:
            print(f"Error setting up database: {e}")
            return
    
    # Start the server
    print("Starting backend server...")
    try:
        # Change to backend directory
        os.chdir("backend")
        
        # Start the server
        print("Server starting on http://localhost:8000")
        print("Open frontend/index.html in your browser to test")
        print("Press Ctrl+C to stop the server")
        
        # Start server
        subprocess.run([sys.executable, "test_server.py"])
        
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()