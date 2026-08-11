from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.bus_model import BusModel
from models.user_model import UserModel
from models.booking_model import BookingModel
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard():
    stats = BookingModel.get_dashboard_stats()
    recent_bookings = BookingModel.get_all()[:5]  # Top 5 recent bookings
    return render_template('admin/dashboard.html', stats=stats, recent_bookings=recent_bookings)

@admin_bp.route('/buses')
@admin_required
def buses():
    buses_list = BusModel.get_all()
    return render_template('admin/buses.html', buses=buses_list)

@admin_bp.route('/buses/add', methods=['GET', 'POST'])
@admin_required
def add_bus():
    if request.method == 'POST':
        bus_number = request.form.get('bus_number', '').strip().upper()
        operator_name = request.form.get('operator_name', '').strip()
        source = request.form.get('source', '').strip()
        destination = request.form.get('destination', '').strip()
        departure_time = request.form.get('departure_time', '').strip()
        arrival_time = request.form.get('arrival_time', '').strip()
        travel_date = request.form.get('travel_date', '').strip()
        bus_type = request.form.get('bus_type', '').strip()
        total_seats = request.form.get('total_seats', type=int)
        price = request.form.get('price', type=float)

        if not bus_number or not operator_name or not source or not destination or not travel_date or not price:
            flash('All required fields must be completed.', 'danger')
            return render_template('admin/add_bus.html')

        try:
            BusModel.add_bus(bus_number, operator_name, source, destination, departure_time, arrival_time, travel_date, bus_type, total_seats, price)
            flash(f'Bus {bus_number} added successfully!', 'success')
            return redirect(url_for('admin.buses'))
        except Exception as e:
            flash(f'Error adding bus: {str(e)}', 'danger')
            return render_template('admin/add_bus.html')

    return render_template('admin/add_bus.html')

@admin_bp.route('/buses/edit/<int:bus_id>', methods=['GET', 'POST'])
@admin_required
def edit_bus(bus_id):
    bus = BusModel.get_by_id(bus_id)
    if not bus:
        flash('Bus not found.', 'danger')
        return redirect(url_for('admin.buses'))

    if request.method == 'POST':
        bus_number = request.form.get('bus_number', '').strip().upper()
        operator_name = request.form.get('operator_name', '').strip()
        source = request.form.get('source', '').strip()
        destination = request.form.get('destination', '').strip()
        departure_time = request.form.get('departure_time', '').strip()
        arrival_time = request.form.get('arrival_time', '').strip()
        travel_date = request.form.get('travel_date', '').strip()
        bus_type = request.form.get('bus_type', '').strip()
        total_seats = request.form.get('total_seats', type=int)
        price = request.form.get('price', type=float)

        try:
            BusModel.update_bus(bus_id, bus_number, operator_name, source, destination, departure_time, arrival_time, travel_date, bus_type, total_seats, price)
            flash(f'Bus {bus_number} updated successfully!', 'success')
            return redirect(url_for('admin.buses'))
        except Exception as e:
            flash(f'Error updating bus: {str(e)}', 'danger')
            return render_template('admin/edit_bus.html', bus=bus)

    return render_template('admin/edit_bus.html', bus=bus)

@admin_bp.route('/buses/delete/<int:bus_id>', methods=['POST'])
@admin_required
def delete_bus(bus_id):
    try:
        BusModel.delete_bus(bus_id)
        flash('Bus deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting bus: {str(e)}', 'danger')
    return redirect(url_for('admin.buses'))

@admin_bp.route('/users')
@admin_required
def users():
    users_list = UserModel.get_all()
    return render_template('admin/users.html', users=users_list)

@admin_bp.route('/bookings')
@admin_required
def bookings():
    bookings_list = BookingModel.get_all()
    return render_template('admin/bookings.html', bookings=bookings_list)

@admin_bp.route('/bookings/status/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    new_status = request.form.get('status', '').strip()
    if new_status in ['Confirmed', 'Cancelled', 'Completed']:
        if new_status == 'Cancelled':
            BookingModel.cancel_booking(booking_id)
        else:
            BookingModel.update_status(booking_id, new_status)
        flash('Booking status updated successfully.', 'success')
    else:
        flash('Invalid status specified.', 'danger')
    return redirect(url_for('admin.bookings'))
