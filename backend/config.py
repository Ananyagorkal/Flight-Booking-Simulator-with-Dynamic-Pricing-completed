import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/flight_booking")

# Application configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# API configuration
API_V1_STR = "/api"
PROJECT_NAME = "Flight Booking Simulator"

# CORS settings
BACKEND_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]
