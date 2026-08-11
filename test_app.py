import unittest
import time
from app import app
from models.db import query_db

class BusTicketSystemTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret'
        self.client = app.test_client()

        # Clean up test artifacts and release all seats on bus 1
        try:
            query_db("DELETE FROM passengers", commit=True)
            query_db("DELETE FROM bookings", commit=True)
            query_db("DELETE FROM users WHERE email NOT IN ('admin@busgo.com', 'user@busgo.com')", commit=True)
            query_db("UPDATE buses SET available_seats = total_seats WHERE id = 1", commit=True)
        except Exception:
            pass

    def test_01_homepage_and_search(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Book Your Journey', response.data)

        # Search Buses
        res_search = self.client.get('/buses?source=Kolhapur&destination=Pune&travel_date=2026-08-15&passengers=2')
        self.assertEqual(res_search.status_code, 200)
        self.assertIn(b'Shree Travels', res_search.data)

    def test_02_auth_and_booking_flow(self):
        timestamp = int(time.time())
        email = f"traveler_{timestamp}@test.com"

        # Register user
        reg_res = self.client.post('/register', data={
            'name': 'Test Traveler',
            'email': email,
            'phone': '9988776655',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        }, follow_redirects=True)
        self.assertEqual(reg_res.status_code, 200)

        # Login user
        login_res = self.client.post('/login', data={
            'email': email,
            'password': 'Password@123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Welcome back', login_res.data)

        # Book Ticket (Bus ID 1: Kolhapur to Pune)
        book_res = self.client.post('/book/confirm', data={
            'bus_id': 1,
            'passengers_count': 2,
            'selected_seats': 'A1,A2',
            'passenger_1_name': 'Traveler One',
            'passenger_1_age': 25,
            'passenger_1_gender': 'Male',
            'passenger_1_phone': '9988776655',
            'passenger_2_name': 'Traveler Two',
            'passenger_2_age': 24,
            'passenger_2_gender': 'Female',
            'passenger_2_phone': '9988776655'
        }, follow_redirects=True)

        self.assertEqual(book_res.status_code, 200)
        self.assertIn(b'BUS-', book_res.data)
        self.assertIn(b'A1', book_res.data)
        self.assertIn(b'A2', book_res.data)

        # Double-booking prevention test (Attempting to re-book A1)
        book_conflict = self.client.post('/book/confirm', data={
            'bus_id': 1,
            'passengers_count': 1,
            'selected_seats': 'A1',
            'passenger_1_name': 'Conflict Traveler',
            'passenger_1_age': 30,
            'passenger_1_gender': 'Male',
            'passenger_1_phone': '9900000000'
        }, follow_redirects=True)
        self.assertIn(b'already been booked', book_conflict.data)

    def test_03_admin_access_and_crud(self):
        # Non-admin forbidden test
        res_user_admin = self.client.get('/admin', follow_redirects=True)
        self.assertIn(b'Please log in', res_user_admin.data)

        # Admin login
        admin_login = self.client.post('/login', data={
            'email': 'admin@busgo.com',
            'password': 'Admin@123'
        }, follow_redirects=True)
        self.assertEqual(admin_login.status_code, 200)

        # Access Dashboard
        dash_res = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b'Admin Dashboard', dash_res.data)

        # Clean old test bus if present
        query_db("DELETE FROM buses WHERE bus_number = 'MH20XY9999'", commit=True)

        # Add Bus
        add_bus_res = self.client.post('/admin/buses/add', data={
            'bus_number': 'MH20XY9999',
            'operator_name': 'Test Operator',
            'source': 'Kolhapur',
            'destination': 'Mumbai',
            'departure_time': '07:00 AM',
            'arrival_time': '03:00 PM',
            'travel_date': '2026-08-20',
            'bus_type': 'AC Sleeper',
            'total_seats': 40,
            'price': 900.00
        }, follow_redirects=True)
        self.assertEqual(add_bus_res.status_code, 200)
        self.assertIn(b'MH20XY9999', add_bus_res.data)

if __name__ == '__main__':
    unittest.main()
