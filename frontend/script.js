// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Global variables
let currentFlights = [];
let selectedFlight = null;
let currentPricing = null;
let appliedCoupon = null;
let availableCoupons = [];
let paymentMethods = [];
let banks = [];
let currentBooking = null;
let currentPayment = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadAirports();
    loadAvailableCoupons();
    loadPaymentMethods();
    loadBanks();
    setupEventListeners();
    setDefaultDates();
});

// Load airports from API
async function loadAirports() {
    try {
        const response = await fetch(`${API_BASE_URL}/flights/airports/`);
        const airports = await response.json();
        
        const departureSelect = document.getElementById('departureAirport');
        const arrivalSelect = document.getElementById('arrivalAirport');
        
        airports.forEach(airport => {
            const option1 = new Option(`${airport.code} - ${airport.name}`, airport.code);
            const option2 = new Option(`${airport.code} - ${airport.name}`, airport.code);
            departureSelect.add(option1);
            arrivalSelect.add(option2);
        });
    } catch (error) {
        console.error('Error loading airports:', error);
        showNotification('Error loading airports. Please refresh the page.', 'error');
    }
}

// Set default dates
function setDefaultDates() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    document.getElementById('departureDate').value = tomorrow.toISOString().split('T')[0];
}

// Load available coupons
async function loadAvailableCoupons() {
    try {
        const response = await fetch(`${API_BASE_URL}/coupons/`);
        const data = await response.json();
        availableCoupons = data.coupons;
        displayAvailableCoupons();
    } catch (error) {
        console.error('Error loading coupons:', error);
    }
}

// Display available coupons
function displayAvailableCoupons() {
    const searchSection = document.querySelector('.search-section');
    if (!searchSection) return;
    
    const couponsHtml = `
        <div class="available-coupons">
            <h4><i class="fas fa-ticket-alt"></i> Available Coupons</h4>
            <div class="coupons-grid">
                ${availableCoupons.slice(0, 3).map(coupon => `
                    <div class="coupon-card">
                        <div class="coupon-code">${coupon.code}</div>
                        <div class="coupon-description">${coupon.description}</div>
                        <div class="coupon-conditions">Min. ₹${coupon.min_amount} | Max. ₹${coupon.max_discount} off</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    searchSection.insertAdjacentHTML('beforeend', couponsHtml);
}

// Load payment methods
async function loadPaymentMethods() {
    try {
        const response = await fetch(`${API_BASE_URL}/payments/methods`);
        const data = await response.json();
        paymentMethods = data.payment_methods;
    } catch (error) {
        console.error('Error loading payment methods:', error);
    }
}

// Load banks for net banking
async function loadBanks() {
    try {
        const response = await fetch(`${API_BASE_URL}/payments/banks`);
        const data = await response.json();
        banks = data.banks;
    } catch (error) {
        console.error('Error loading banks:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Search form
    document.getElementById('searchForm').addEventListener('submit', handleSearch);
    
    // Modal close buttons
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', closeModal);
    });
    
    // Click outside modal to close
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            closeModal();
        }
    });
    
    // Booking form
    document.getElementById('bookingForm').addEventListener('submit', handleBooking);
    
    // Coupon check button
    document.getElementById('checkCouponBtn').addEventListener('click', checkCoupon);
    
    // Apply coupon button
    document.getElementById('applyCouponBtn').addEventListener('click', applyCoupon);
    
    // Payment form
    document.getElementById('paymentForm').addEventListener('submit', handlePayment);
    
    // Back to booking button
    document.getElementById('backToBookingBtn').addEventListener('click', backToBooking);
    
    // Card number formatting
    document.getElementById('cardNumber').addEventListener('input', formatCardNumber);
    document.getElementById('cardExpiry').addEventListener('input', formatCardExpiry);
    document.getElementById('cardCVV').addEventListener('input', formatCardCVV);
}

// Handle flight search
async function handleSearch(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const searchParams = {
        departure_airport: formData.get('departureAirport') || document.getElementById('departureAirport').value,
        arrival_airport: formData.get('arrivalAirport') || document.getElementById('arrivalAirport').value,
        departure_date: document.getElementById('departureDate').value,
        return_date: document.getElementById('returnDate').value || null,
        passengers: parseInt(document.getElementById('passengers').value),
        seat_class: document.getElementById('seatClass').value || null
    };
    
    if (searchParams.departure_airport === searchParams.arrival_airport) {
        showNotification('Departure and arrival airports cannot be the same.', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const queryParams = new URLSearchParams();
        Object.keys(searchParams).forEach(key => {
            if (searchParams[key] !== null && searchParams[key] !== '') {
                queryParams.append(key, searchParams[key]);
            }
        });
        
        const response = await fetch(`${API_BASE_URL}/flights/search?${queryParams}`);
        const data = await response.json();
        
        if (data.flights && data.flights.length > 0) {
            currentFlights = data.flights;
            displayFlights(data.flights);
            document.getElementById('resultsSection').style.display = 'block';
            document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
        } else {
            showNotification('No flights found for your search criteria.', 'info');
        }
    } catch (error) {
        console.error('Search error:', error);
        showNotification('Error searching flights. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

// Display flight results
async function displayFlights(flights) {
    const resultsContainer = document.getElementById('flightResults');
    resultsContainer.innerHTML = '';
    
    for (const flight of flights) {
        const flightCard = await createFlightCard(flight);
        resultsContainer.appendChild(flightCard);
    }
}

// Create flight card
async function createFlightCard(flight) {
    const card = document.createElement('div');
    card.className = 'flight-card fade-in';
    
    // Get pricing for economy class (default)
    let pricing = null;
    try {
        const pricingResponse = await fetch(`${API_BASE_URL}/pricing/flight/${flight.id}/class/economy`);
        pricing = await pricingResponse.json();
    } catch (error) {
        console.error('Error fetching pricing:', error);
    }
    
    const departureTime = new Date(flight.departure_time).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
    });
    const arrivalTime = new Date(flight.arrival_time).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
    });
    
    const duration = Math.floor(flight.duration_minutes / 60) + 'h ' + (flight.duration_minutes % 60) + 'm';
    
    card.innerHTML = `
        <div class="flight-header">
            <div class="flight-info">
                <div class="airline-logo">${flight.airline?.code || 'XX'}</div>
                <div class="flight-details">
                    <h3>${flight.flight_number}</h3>
                    <p>${flight.airline?.name || 'Airline'}</p>
                </div>
            </div>
            <div class="price-section">
                <div class="price">₹${pricing ? pricing.total_price.toFixed(0) : flight.base_price.toFixed(0)}</div>
                <div class="price-breakdown">per passenger</div>
                <button class="book-btn" onclick="openBookingModal(${flight.id})">
                    <i class="fas fa-shopping-cart"></i> Book Now
                </button>
            </div>
        </div>
        
        <div class="flight-route">
            <div class="route-segment">
                <div class="time">${departureTime}</div>
                <div class="airport">${flight.departure_airport?.code || 'DEP'}</div>
            </div>
            <div class="route-arrow">
                <i class="fas fa-arrow-right"></i>
                <div style="font-size: 12px; margin-top: 5px;">${duration}</div>
            </div>
            <div class="route-segment">
                <div class="time">${arrivalTime}</div>
                <div class="airport">${flight.arrival_airport?.code || 'ARR'}</div>
            </div>
        </div>
        
        <div class="flight-details">
            <p><strong>From:</strong> ${flight.departure_airport?.name || 'Departure Airport'}</p>
            <p><strong>To:</strong> ${flight.arrival_airport?.name || 'Arrival Airport'}</p>
            <p><strong>Available Seats:</strong> ${flight.available_seats}</p>
            <p><strong>Status:</strong> ${flight.status}</p>
        </div>
    `;
    
    return card;
}

// Open booking modal
async function openBookingModal(flightId) {
    selectedFlight = currentFlights.find(f => f.id === flightId);
    if (!selectedFlight) return;
    
    // Get pricing for selected seat class
    const seatClass = document.getElementById('selectedSeatClass').value;
    try {
        const response = await fetch(`${API_BASE_URL}/pricing/flight/${flightId}/class/${seatClass}`);
        currentPricing = await response.json();
        updatePriceDetails();
    } catch (error) {
        console.error('Error fetching pricing:', error);
        showNotification('Error fetching pricing information.', 'error');
        return;
    }
    
    document.getElementById('bookingModal').style.display = 'block';
}

// Update price details in modal
function updatePriceDetails() {
    if (!currentPricing) return;
    
    const priceDetails = document.getElementById('priceDetails');
    priceDetails.innerHTML = `
        <div class="price-item">
            <span>Base Price:</span>
            <span>₹${currentPricing.base_price.toFixed(0)}</span>
        </div>
        <div class="price-item">
            <span>Demand Factor:</span>
            <span>${(currentPricing.demand_factor * 100).toFixed(1)}%</span>
        </div>
        <div class="price-item">
            <span>Time Factor:</span>
            <span>${(currentPricing.time_factor * 100).toFixed(1)}%</span>
        </div>
        <div class="price-item">
            <span>Availability Factor:</span>
            <span>${(currentPricing.seat_availability_factor * 100).toFixed(1)}%</span>
        </div>
        <div class="price-item price-total">
            <span>Total Price:</span>
            <span>₹${currentPricing.total_price.toFixed(0)}</span>
        </div>
    `;
}

// Handle booking submission
async function handleBooking(event) {
    event.preventDefault();
    
    if (!selectedFlight || !currentPricing) {
        showNotification('Please select a flight first.', 'error');
        return;
    }
    
    const formData = new FormData(event.target);
    const bookingData = {
        flight_id: selectedFlight.id,
        passenger_name: formData.get('passengerName') || document.getElementById('passengerName').value,
        passenger_email: formData.get('passengerEmail') || document.getElementById('passengerEmail').value,
        passenger_phone: formData.get('passengerPhone') || document.getElementById('passengerPhone').value,
        seat_class: document.getElementById('selectedSeatClass').value
    };
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/bookings/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookingData)
        });
        
        if (response.ok) {
            const confirmation = await response.json();
            showNotification('🎉 Booking created! Proceeding to payment...', 'success');
            closeModal();
            
            // Store booking data for payment page
            const bookingData = {
                flight: selectedFlight,
                passengers: document.getElementById('passengerCount').value,
                seatClass: document.getElementById('selectedSeatClass').value,
                price: currentPricing.total_price,
                finalPrice: currentPricing.total_price,
                passengerName: formData.get('passengerName'),
                passengerEmail: formData.get('passengerEmail'),
                passengerPhone: formData.get('passengerPhone'),
                coupon: null
            };
            
            localStorage.setItem('bookingData', JSON.stringify(bookingData));
            window.location.href = 'payment.html';
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Booking failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Booking error:', error);
        showNotification('Error processing booking. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

// Show booking confirmation
function showBookingConfirmation(confirmation) {
    closeModal();
    
    const bookingDetails = document.getElementById('bookingDetails');
    bookingDetails.innerHTML = `
        <h3>Booking Details</h3>
        <div class="detail-row">
            <span>PNR:</span>
            <span><strong>${confirmation.pnr}</strong></span>
        </div>
        <div class="detail-row">
            <span>Booking Reference:</span>
            <span>${confirmation.booking_reference}</span>
        </div>
        <div class="detail-row">
            <span>Passenger Name:</span>
            <span><strong>${confirmation.passenger_name}</strong></span>
        </div>
        <div class="detail-row">
            <span>Passenger Email:</span>
            <span>${confirmation.passenger_email || 'N/A'}</span>
        </div>
        <div class="detail-row">
            <span>Passenger Phone:</span>
            <span>${confirmation.passenger_phone || 'N/A'}</span>
        </div>
        <div class="detail-row">
            <span>Flight:</span>
            <span>${confirmation.flight_details.flight_number}</span>
        </div>
        <div class="detail-row">
            <span>Route:</span>
            <span>${confirmation.flight_details.departure_airport?.code} → ${confirmation.flight_details.arrival_airport?.code}</span>
        </div>
        <div class="detail-row">
            <span>Departure:</span>
            <span>${new Date(confirmation.flight_details.departure_time).toLocaleString()}</span>
        </div>
        <div class="detail-row">
            <span>Arrival:</span>
            <span>${new Date(confirmation.flight_details.arrival_time).toLocaleString()}</span>
        </div>
        <div class="detail-row">
            <span>Seat Class:</span>
            <span>${confirmation.seat_class}</span>
        </div>
        <div class="detail-row">
            <span>Seat Number:</span>
            <span>${confirmation.seat_number || 'TBD'}</span>
        </div>
        <div class="detail-row">
            <span>Total Paid:</span>
            <span><strong>₹${confirmation.price_paid.toFixed(0)}</strong></span>
        </div>
        <div class="detail-row">
            <span>Status:</span>
            <span style="color: #28a745;"><strong>${confirmation.status.toUpperCase()}</strong></span>
        </div>
    `;
    
    document.getElementById('confirmationModal').style.display = 'block';
}

// Close modal
function closeModal() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
}

// Print booking
function printBooking() {
    window.print();
}

// Show loading spinner
function showLoading(show) {
    document.getElementById('loadingSpinner').style.display = show ? 'block' : 'none';
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#17a2b8'};
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        max-width: 300px;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Coupon Functions
async function checkCoupon() {
    const couponCode = document.getElementById('couponCode').value.trim();
    if (!couponCode) {
        showNotification('Please enter a coupon code', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/coupons/${couponCode}`);
        const coupon = await response.json();
        
        showNotification(`✅ ${coupon.name}: ${coupon.description}`, 'success');
    } catch (error) {
        showNotification('❌ Invalid coupon code', 'error');
    }
}

async function applyCoupon() {
    const couponCode = document.getElementById('bookingCouponCode').value.trim();
    if (!couponCode) {
        showNotification('Please enter a coupon code', 'error');
        return;
    }
    
    if (!currentPricing) {
        showNotification('Please select a flight first', 'error');
        return;
    }
    
    try {
        const couponData = {
            coupon_code: couponCode,
            booking_amount: currentPricing.total_price,
            seat_class: document.getElementById('selectedSeatClass').value,
            passengers: 1
        };
        
        const response = await fetch(`${API_BASE_URL}/coupons/apply`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(couponData)
        });
        
        const result = await response.json();
        
        if (result.valid) {
            appliedCoupon = result;
            updateFinalPricing();
            showNotification(`🎉 Coupon applied! You saved ₹${result.savings}`, 'success');
        } else {
            showNotification(`❌ ${result.message}`, 'error');
        }
    } catch (error) {
        console.error('Coupon application error:', error);
        showNotification('Error applying coupon. Please try again.', 'error');
    }
}

function updateFinalPricing() {
    if (!currentPricing) return;
    
    const finalPricing = document.getElementById('finalPricing');
    if (!finalPricing) return;
    
    let originalAmount = currentPricing.total_price;
    let discountAmount = 0;
    let finalAmount = originalAmount;
    
    if (appliedCoupon) {
        discountAmount = appliedCoupon.discount_amount;
        finalAmount = appliedCoupon.final_amount;
    }
    
    finalPricing.innerHTML = `
        <h4><i class="fas fa-calculator"></i> Final Pricing</h4>
        <div class="pricing-breakdown">
            <span>Original Price:</span>
            <span>₹${originalAmount.toFixed(0)}</span>
        </div>
        ${discountAmount > 0 ? `
            <div class="pricing-breakdown">
                <span>Discount (${appliedCoupon.coupon_details.code}):</span>
                <span class="savings-highlight">-₹${discountAmount.toFixed(0)}</span>
            </div>
        ` : ''}
        <div class="pricing-total">
            <span>Total Amount:</span>
            <span>₹${finalAmount.toFixed(0)}</span>
        </div>
        ${discountAmount > 0 ? `
            <div class="pricing-breakdown">
                <span>You Save:</span>
                <span class="savings-highlight">₹${discountAmount.toFixed(0)}</span>
            </div>
        ` : ''}
    `;
}

// Update price details to include coupon section
function updatePriceDetails() {
    if (!currentPricing) return;
    
    const priceDetails = document.getElementById('priceDetails');
    priceDetails.innerHTML = `
        <div class="price-item">
            <span>Base Price:</span>
            <span>₹${currentPricing.base_price.toFixed(0)}</span>
        </div>
        <div class="price-item">
            <span>Demand Factor:</span>
            <span>${(currentPricing.demand_factor * 100).toFixed(1)}%</span>
        </div>
        <div class="price-item">
            <span>Time Factor:</span>
            <span>${(currentPricing.time_factor * 100).toFixed(1)}%</span>
        </div>
        <div class="price-item">
            <span>Availability Factor:</span>
            <span>${(currentPricing.seat_availability_factor * 100).toFixed(1)}%</span>
        </div>
        <div class="price-item price-total">
            <span>Total Price:</span>
            <span>₹${currentPricing.total_price.toFixed(0)}</span>
        </div>
    `;
    
    // Update final pricing
    updateFinalPricing();
}

// Payment Functions
function showPaymentModal(booking) {
    currentBooking = booking;
    const modal = document.getElementById('paymentModal');
    const paymentDetails = document.getElementById('paymentDetails');
    
    // Display payment summary
    const finalAmount = appliedCoupon ? appliedCoupon.final_amount : currentPricing.total_price;
    
    paymentDetails.innerHTML = `
        <div class="payment-item">
            <span>Flight:</span>
            <span>${booking.flight_number}</span>
        </div>
        <div class="payment-item">
            <span>Passenger:</span>
            <span>${booking.passenger_name}</span>
        </div>
        <div class="payment-item">
            <span>Seat Class:</span>
            <span>${booking.seat_class}</span>
        </div>
        ${appliedCoupon ? `
            <div class="payment-item">
                <span>Original Price:</span>
                <span>₹${appliedCoupon.original_amount.toFixed(0)}</span>
            </div>
            <div class="payment-item">
                <span>Discount (${appliedCoupon.coupon_details.code}):</span>
                <span class="savings-highlight">-₹${appliedCoupon.discount_amount.toFixed(0)}</span>
            </div>
        ` : ''}
        <div class="payment-item payment-total">
            <span>Total Amount:</span>
            <span>₹${finalAmount.toFixed(0)}</span>
        </div>
    `;
    
    // Display payment methods
    displayPaymentMethods();
    
    modal.style.display = 'block';
}

function displayPaymentMethods() {
    const methodsList = document.getElementById('paymentMethodsList');
    methodsList.innerHTML = paymentMethods.map(method => `
        <div class="payment-method" data-method="${method.id}">
            <i class="${method.icon}"></i>
            <h4>${method.name}</h4>
            <p>${method.description}</p>
        </div>
    `).join('');
    
    // Add click handlers
    document.querySelectorAll('.payment-method').forEach(method => {
        method.addEventListener('click', selectPaymentMethod);
    });
}

function selectPaymentMethod(event) {
    // Remove previous selection
    document.querySelectorAll('.payment-method').forEach(method => {
        method.classList.remove('selected');
    });
    
    // Add selection to clicked method
    event.currentTarget.classList.add('selected');
    
    const methodId = event.currentTarget.dataset.method;
    
    // Hide all payment forms
    document.querySelectorAll('.payment-form').forEach(form => {
        form.style.display = 'none';
    });
    
    // Show relevant form
    if (methodId === 'credit_card' || methodId === 'debit_card') {
        document.getElementById('cardForm').style.display = 'block';
    } else if (methodId === 'upi') {
        document.getElementById('upiForm').style.display = 'block';
    } else if (methodId === 'netbanking') {
        document.getElementById('netbankingForm').style.display = 'block';
        populateBanks();
    } else if (methodId === 'wallet') {
        document.getElementById('walletForm').style.display = 'block';
    } else if (methodId === 'emi') {
        document.getElementById('emiForm').style.display = 'block';
        calculateEMI();
    }
}

function populateBanks() {
    const bankSelect = document.getElementById('bankSelect');
    bankSelect.innerHTML = '<option value="">Choose your bank</option>' +
        banks.map(bank => `<option value="${bank.code}">${bank.name}</option>`).join('');
}

function calculateEMI() {
    const finalAmount = appliedCoupon ? appliedCoupon.final_amount : currentPricing.total_price;
    
    document.getElementById('emi3Amount').textContent = Math.ceil(finalAmount / 3).toFixed(0);
    document.getElementById('emi6Amount').textContent = Math.ceil(finalAmount / 6).toFixed(0);
    document.getElementById('emi12Amount').textContent = Math.ceil(finalAmount / 12).toFixed(0);
}

async function handlePayment(event) {
    event.preventDefault();
    
    const selectedMethod = document.querySelector('.payment-method.selected');
    if (!selectedMethod) {
        showNotification('Please select a payment method', 'error');
        return;
    }
    
    const methodId = selectedMethod.dataset.method;
    const finalAmount = appliedCoupon ? appliedCoupon.final_amount : currentPricing.total_price;
    
    try {
        // Initiate payment
        const paymentData = {
            booking_id: currentBooking.id,
            amount: finalAmount,
            payment_method: methodId,
            currency: 'INR'
        };
        
        const response = await fetch(`${API_BASE_URL}/payments/initiate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(paymentData)
        });
        
        const paymentInit = await response.json();
        currentPayment = paymentInit;
        
        // Process payment
        const processData = {
            payment_id: paymentInit.payment_id,
            payment_method: methodId,
            card_details: getCardDetails(),
            upi_details: getUPIDetails(),
            netbanking_details: getNetbankingDetails()
        };
        
        const processResponse = await fetch(`${API_BASE_URL}/payments/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(processData)
        });
        
        const result = await processResponse.json();
        
        if (result.success) {
            showNotification('🎉 Payment successful! Booking confirmed.', 'success');
            closeModal();
            showBookingConfirmation(currentBooking, result);
        } else {
            showNotification(`❌ Payment failed: ${result.message}`, 'error');
        }
        
    } catch (error) {
        console.error('Payment error:', error);
        showNotification('Payment processing failed. Please try again.', 'error');
    }
}

function getCardDetails() {
    return {
        card_number: document.getElementById('cardNumber').value,
        card_name: document.getElementById('cardName').value,
        card_expiry: document.getElementById('cardExpiry').value,
        card_cvv: document.getElementById('cardCVV').value
    };
}

function getUPIDetails() {
    return {
        upi_id: document.getElementById('upiId').value
    };
}

function getNetbankingDetails() {
    return {
        bank_code: document.getElementById('bankSelect').value
    };
}

function backToBooking() {
    document.getElementById('paymentModal').style.display = 'none';
    document.getElementById('bookingModal').style.display = 'block';
}

// Card formatting functions
function formatCardNumber(event) {
    let value = event.target.value.replace(/\s/g, '').replace(/[^0-9]/gi, '');
    let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
    if (formattedValue.length > 19) formattedValue = formattedValue.substr(0, 19);
    event.target.value = formattedValue;
}

function formatCardExpiry(event) {
    let value = event.target.value.replace(/\D/g, '');
    if (value.length >= 2) {
        value = value.substring(0, 2) + '/' + value.substring(2, 4);
    }
    event.target.value = value;
}

function formatCardCVV(event) {
    let value = event.target.value.replace(/\D/g, '');
    if (value.length > 4) value = value.substring(0, 4);
    event.target.value = value;
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
