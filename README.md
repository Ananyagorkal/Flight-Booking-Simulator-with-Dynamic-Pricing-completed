# Flight Booking Simulator with Dynamic Pricing

A comprehensive web-based flight booking system that demonstrates dynamic pricing algorithms, real-time seat inventory management, and concurrent booking transactions.

## Features

- **Dynamic Pricing Engine**: Prices adjust based on demand, time to departure, and seat availability
- **Real-time Flight Search**: Search flights with filtering and sorting capabilities
- **Concurrent Booking Management**: Handle multiple simultaneous bookings with proper transaction control
- **Responsive Web Interface**: Modern, mobile-friendly frontend
- **PNR Generation**: Automatic Passenger Name Record generation
- **Booking Confirmation**: Downloadable receipts and booking confirmations

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Pricing Engine**: Custom algorithm with demand simulation
- **Concurrency Control**: Database-level transaction management

## Project Structure

```
Flight Booking Simulator with Dynamic Pricing/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database models and configuration
│   ├── models.py               # Pydantic models for API
│   ├── config.py               # Application configuration
│   ├── sample_data.py          # Sample data generator
│   ├── routers/
│   │   ├── flights.py          # Flight search and management APIs
│   │   ├── bookings.py         # Booking management APIs
│   │   ├── pricing.py          # Dynamic pricing APIs
│   │   └── admin.py            # Administrative APIs
│   └── services/
│       ├── pricing_engine.py   # Dynamic pricing algorithm
│       └── booking_service.py  # Booking workflow management
├── frontend/
│   ├── index.html              # Main application interface
│   ├── styles.css              # Responsive styling
│   └── script.js               # Frontend JavaScript logic
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- MySQL 5.7+
- pip (Python package manager)

### Backend Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Configuration**
   - Create a MySQL database named `flight_booking`
   - Update the database URL in `backend/config.py` if needed
   - Default connection: `mysql+pymysql://root:password@localhost:3306/flight_booking`

3. **Run the Application**
   ```bash
   cd backend
   python main.py
   ```

4. **Populate Sample Data**
   ```bash
   python sample_data.py
   ```

### Frontend Setup

The frontend is a static web application. Simply open `frontend/index.html` in a web browser or serve it using a local web server.

## API Endpoints

### Flight Search
- `GET /api/flights/search` - Search flights with filters
- `GET /api/flights/{flight_id}` - Get flight details
- `GET /api/flights/airports/` - Get all airports
- `GET /api/flights/airlines/` - Get all airlines

### Booking Management
- `POST /api/bookings/` - Create a new booking
- `GET /api/bookings/pnr/{pnr}` - Get booking by PNR
- `DELETE /api/bookings/pnr/{pnr}` - Cancel a booking
- `GET /api/bookings/history/{email}` - Get booking history

### Dynamic Pricing
- `POST /api/pricing/calculate` - Calculate dynamic price
- `GET /api/pricing/flight/{flight_id}/class/{seat_class}` - Get current price
- `GET /api/pricing/trend/{flight_id}/{seat_class}` - Get price trend
- `GET /api/pricing/compare/{flight_id}` - Compare prices across classes

### Administrative
- `POST /api/admin/flights/` - Create flight (admin)
- `POST /api/admin/airports/` - Create airport (admin)
- `POST /api/admin/airlines/` - Create airline (admin)
- `GET /api/admin/dashboard/stats` - Get system statistics

## Dynamic Pricing Algorithm

The pricing engine considers multiple factors:

1. **Base Price**: Set by airline for each route and seat class
2. **Demand Factor**: Simulated based on time of day, day of week, and market conditions
3. **Time Factor**: Price increases as departure date approaches
4. **Seat Availability Factor**: Higher prices when fewer seats are available

### Pricing Formula
```
Final Price = Base Price × Demand Factor × Time Factor × Seat Availability Factor
```

### Seat Class Multipliers
- Economy: 1.0x
- Premium Economy: 1.5x
- Business: 2.5x
- First Class: 4.0x

## Database Schema

### Core Tables
- **airports**: Airport information (code, name, city, country, timezone)
- **airlines**: Airline information (code, name, logo)
- **flights**: Flight details (route, schedule, pricing, status)
- **bookings**: Passenger bookings (PNR, passenger info, pricing)
- **seat_inventory**: Seat availability by class
- **pricing_history**: Historical pricing data

## Key Features Implementation

### 1. Concurrency Control
- Database transactions ensure seat availability consistency
- Optimistic locking prevents double-booking
- Rollback mechanism for failed transactions

### 2. Dynamic Pricing
- Real-time price calculation based on multiple factors
- Historical pricing tracking for trend analysis
- Demand simulation for realistic pricing behavior

### 3. Booking Workflow
- Multi-step booking process with validation
- Automatic PNR generation (6-character alphanumeric)
- Seat assignment based on availability and class
- Email confirmation and receipt generation

### 4. User Interface
- Responsive design for mobile and desktop
- Real-time search with dynamic results
- Interactive booking modal with price breakdown
- Booking confirmation with printable receipts

## Usage Examples

### Search Flights
```javascript
// Search for flights from JFK to LAX
const searchParams = {
    departure_airport: 'JFK',
    arrival_airport: 'LAX',
    departure_date: '2024-01-15',
    passengers: 2,
    seat_class: 'economy'
};
```

### Create Booking
```javascript
const bookingData = {
    flight_id: 123,
    passenger_name: 'John Doe',
    passenger_email: 'john@example.com',
    passenger_phone: '+1234567890',
    seat_class: 'economy'
};
```

### Get Pricing
```javascript
// Get current price for a flight and seat class
const pricing = await fetch('/api/pricing/flight/123/class/economy');
```

## Development Notes

### Adding New Features
1. Create new API endpoints in appropriate router files
2. Update database models if needed
3. Implement business logic in service classes
4. Update frontend JavaScript for new functionality

### Testing
- Use the sample data generator to create test scenarios
- Test concurrent bookings to verify transaction handling
- Verify pricing calculations with different parameters

### Deployment
- Configure production database settings
- Set up proper CORS origins for security
- Use environment variables for sensitive configuration
- Consider using Redis for session management in production

## Troubleshooting

### Common Issues
1. **Database Connection**: Ensure MySQL is running and credentials are correct
2. **CORS Errors**: Check that frontend and backend are on compatible ports
3. **Pricing Not Updating**: Verify that pricing engine is being called correctly
4. **Booking Failures**: Check seat availability and transaction handling

### Debug Mode
Set `DEBUG=True` in configuration to enable detailed error logging and database query output.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. Please ensure you have proper licensing for any production use.
