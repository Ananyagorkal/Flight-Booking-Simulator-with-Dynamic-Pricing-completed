#!/usr/bin/env python3
"""
Simple script to open the website in your default browser
"""

import webbrowser
import os
from pathlib import Path

def open_website():
    """Open the website in the default browser"""
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Path to the HTML file
    html_file = current_dir / "frontend" / "index.html"
    
    # Check if file exists
    if html_file.exists():
        print("Opening Flight Booking Simulator...")
        print(f"File location: {html_file}")
        
        # Open in default browser
        webbrowser.open(f"file://{html_file.absolute()}")
        print("Website opened in your default browser!")
        
        print("\nIf the website doesn't load properly:")
        print("1. Make sure the server is running: python minimal_server.py")
        print("2. Try visiting: http://localhost:8000/static/index.html")
        print("3. Or try: http://localhost:8000/docs")
        
    else:
        print("ERROR: HTML file not found!")
        print(f"Looking for: {html_file}")
        print("Make sure you're in the correct directory.")

if __name__ == "__main__":
    open_website()
