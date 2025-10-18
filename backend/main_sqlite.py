from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

# Use SQLite configuration
from config_sqlite import engine, Base
from routers import flights, bookings, pricing, admin, coupons, payments
from services.pricing_engine import PricingEngine
from services.booking_service import BookingService

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Flight Booking Simulator API",
    description="A comprehensive flight booking system with dynamic pricing",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(flights.router, prefix="/api/flights", tags=["flights"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(pricing.router, prefix="/api/pricing", tags=["pricing"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(coupons.router, prefix="/api/coupons", tags=["coupons"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return {"message": "Flight Booking Simulator API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main_sqlite:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
