from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.bus_model import BusModel
from models.booking_model import BookingModel
from routes.auth import login_required

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book/<int:bus_id>')
@login_required
def book_bus(bus_id):
    bus = BusModel.get_by_id(bus_id)
    if not bus:
        flash('Selected bus is no longer available.', 'danger')
        return redirect(url_for('user.search_buses'))

    passengers_count = int(request.args.get('passengers', 1))
    booked_seats = BusModel.get_booked_seats(bus_id)

    return render_template('user/booking.html', bus=bus, passengers_count=passengers_count, booked_seats=booked_seats)

@booking_bp.route('/book/confirm', methods=['POST'])
@login_required
def confirm_booking():
    user_id = session['user_id']
    bus_id = request.form.get('bus_id', type=int)
    passengers_count = request.form.get('passengers_count', type=int)
    selected_seats_raw = request.form.get('selected_seats', '')

    if not bus_id or not selected_seats_raw:
        flash('Invalid booking submission. Please select your seats.', 'danger')
        return redirect(url_for('user.search_buses'))

    selected_seats = [s.strip() for s in selected_seats_raw.split(',') if s.strip()]

    if len(selected_seats) != passengers_count:
        flash(f'Please select exactly {passengers_count} seat(s).', 'warning')
        return redirect(url_for('booking.book_bus', bus_id=bus_id, passengers=passengers_count))

    bus = BusModel.get_by_id(bus_id)
    if not bus:
        flash('Bus not found.', 'danger')
        return redirect(url_for('user.search_buses'))

    # Extract passenger details from form inputs
    passenger_list = []
    for i in range(1, passengers_count + 1):
        p_name = request.form.get(f'passenger_{i}_name', '').strip()
        p_age = request.form.get(f'passenger_{i}_age', type=int)
        p_gender = request.form.get(f'passenger_{i}_gender', '').strip()
        p_phone = request.form.get(f'passenger_{i}_phone', '').strip()
        p_seat = selected_seats[i - 1]

        if not p_name or not p_age or not p_gender:
            flash(f'Please fill in all details for Passenger {i}.', 'danger')
            return redirect(url_for('booking.book_bus', bus_id=bus_id, passengers=passengers_count))

        passenger_list.append({
            'name': p_name,
            'age': p_age,
            'gender': p_gender,
            'phone': p_phone,
            'seat_number': p_seat
        })

    total_amount = float(bus['price']) * len(selected_seats)

    # Perform atomic DB booking transaction
    success, result = BookingModel.create_booking(user_id, bus_id, selected_seats, passenger_list, total_amount)

    if success:
        booking_id = result
        flash('Booking confirmed successfully! Here is your digital ticket.', 'success')
        return redirect(url_for('booking.ticket', booking_id=booking_id))
    else:
        error_msg = result
        flash(f'Booking Failed: {error_msg}', 'danger')
        return redirect(url_for('booking.book_bus', bus_id=bus_id, passengers=passengers_count))

@booking_bp.route('/ticket/<booking_id>')
@login_required
def ticket(booking_id):
    booking = BookingModel.get_by_id(booking_id)
    if not booking:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('booking.user_bookings'))

    # Authorization Check: Normal user can view their own ticket; admin can view any
    current_user_id = int(session.get('user_id', 0))
    booking_user_id = int(booking.get('user_id', 0))

    if session.get('role') != 'admin' and booking_user_id != current_user_id:
        flash('Unauthorized access to ticket.', 'danger')
        return redirect(url_for('booking.user_bookings'))

    return render_template('user/ticket.html', booking=booking)

@booking_bp.route('/bookings')
@login_required
def user_bookings():
    bookings = BookingModel.get_user_bookings(session['user_id'])
    return render_template('user/bookings.html', bookings=bookings)

@booking_bp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    user_id = session['user_id'] if session['role'] != 'admin' else None
    success, msg = BookingModel.cancel_booking(booking_id, user_id=user_id)
    
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
        
    return redirect(url_for('booking.user_bookings'))

# API JSON Endpoints
@booking_bp.route('/api/buses')
def api_buses():
    source = request.args.get('source', '').strip()
    destination = request.args.get('destination', '').strip()
    travel_date = request.args.get('travel_date', '').strip()
    passengers = int(request.args.get('passengers', 1))

    if source and destination and travel_date:
        buses = BusModel.search_buses(source, destination, travel_date, passengers)
    else:
        buses = BusModel.get_all()
        
    return jsonify({'status': 'success', 'count': len(buses), 'buses': buses})

@booking_bp.route('/api/bus/<int:bus_id>/seats')
def api_bus_seats(bus_id):
    bus = BusModel.get_by_id(bus_id)
    if not bus:
        return jsonify({'status': 'error', 'message': 'Bus not found'}), 404
        
    booked_seats = BusModel.get_booked_seats(bus_id)
    return jsonify({
        'status': 'success',
        'bus_id': bus_id,
        'total_seats': bus['total_seats'],
        'available_seats': bus['available_seats'],
        'booked_seats': booked_seats
    })
