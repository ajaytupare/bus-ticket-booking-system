from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from datetime import datetime
from models.bus_model import BusModel
from models.user_model import UserModel
from routes.auth import login_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    sources = BusModel.get_distinct_sources()
    destinations = BusModel.get_distinct_destinations()
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', sources=sources, destinations=destinations, today_date=today_date)

@user_bp.route('/buses')
def search_buses():
    source = request.args.get('source', '').strip()
    destination = request.args.get('destination', '').strip()
    travel_date = request.args.get('travel_date', '').strip()
    passengers = int(request.args.get('passengers', 1))

    sources = BusModel.get_distinct_sources()
    destinations = BusModel.get_distinct_destinations()

    if not source or not destination or not travel_date:
        # If parameters missing, show all upcoming buses
        buses = BusModel.get_all()
        flash('Showing all available routes.', 'info')
    else:
        buses = BusModel.search_buses(source, destination, travel_date, passengers)

    return render_template('user/buses.html', buses=buses, search_params={
        'source': source,
        'destination': destination,
        'travel_date': travel_date,
        'passengers': passengers
    }, sources=sources, destinations=destinations)

@user_bp.route('/bus/<int:bus_id>')
def bus_details(bus_id):
    bus = BusModel.get_by_id(bus_id)
    if not bus:
        flash('Bus not found.', 'danger')
        return redirect(url_for('user.search_buses'))

    booked_seats = BusModel.get_booked_seats(bus_id)
    return render_template('user/bus_details.html', bus=bus, booked_seats=booked_seats)

@user_bp.route('/profile')
@login_required
def profile():
    user = UserModel.get_by_id(session['user_id'])
    return render_template('user/profile.html', user=user)
