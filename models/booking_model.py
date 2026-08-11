import random
import string
from models.db import query_db, get_db

class BookingModel:
    @staticmethod
    def generate_reference():
        chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        return f"BUS-{chars}"

    @staticmethod
    def create_booking(user_id, bus_id, selected_seats, passenger_list, total_amount):
        """
        Creates a booking atomically:
        1. Checks if any selected seat is already confirmed.
        2. Creates booking entry.
        3. Creates passenger entries for assigned seats.
        4. Decrements available seats in buses table.
        """
        conn, engine = get_db()
        cursor = conn.cursor()

        try:
            # Step 1: Check seat collision
            placeholder = '%s' if engine == 'mysql' else '?'
            seat_placeholders = ','.join([placeholder] * len(selected_seats))
            
            check_query = f"""
                SELECT p.seat_number 
                FROM passengers p
                JOIN bookings bk ON p.booking_id = bk.id
                WHERE bk.bus_id = {placeholder} 
                  AND bk.status = 'Confirmed' 
                  AND p.seat_number IN ({seat_placeholders})
            """
            
            check_params = [bus_id] + selected_seats
            cursor.execute(check_query, check_params)
            
            already_booked = cursor.fetchall()
            if already_booked:
                conn.rollback()
                conn.close()
                return False, "One or more selected seats have already been booked by another user."

            # Step 2: Check available seats count
            bus_query = f"SELECT available_seats FROM buses WHERE id = {placeholder}"
            cursor.execute(bus_query, (bus_id,))
            bus_row = cursor.fetchone()
            
            if engine == 'sqlite':
                bus_row = dict(bus_row)
                
            if not bus_row or bus_row['available_seats'] < len(selected_seats):
                conn.rollback()
                conn.close()
                return False, "Not enough available seats on this bus."

            # Step 3: Insert booking
            ref_code = BookingModel.generate_reference()
            ins_booking_query = f"""
                INSERT INTO bookings (user_id, bus_id, booking_reference, total_amount, status)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, 'Confirmed')
            """
            cursor.execute(ins_booking_query, (user_id, bus_id, ref_code, float(total_amount)))
            booking_id = cursor.lastrowid

            # Step 4: Insert passengers
            ins_passenger_query = f"""
                INSERT INTO passengers (booking_id, name, age, gender, phone, seat_number)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """
            for p in passenger_list:
                cursor.execute(ins_passenger_query, (booking_id, p['name'], int(p['age']), p['gender'], p.get('phone', ''), p['seat_number']))

            # Step 5: Update bus available_seats
            upd_bus_query = f"UPDATE buses SET available_seats = available_seats - {placeholder} WHERE id = {placeholder}"
            cursor.execute(upd_bus_query, (len(selected_seats), bus_id))

            conn.commit()
            conn.close()
            return True, booking_id
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return False, f"Booking transaction failed: {str(e)}"

    @staticmethod
    def get_by_id(booking_id):
        b_str = str(booking_id).strip()
        if b_str.isdigit():
            query = """
                SELECT bk.*, b.operator_name, b.bus_number, b.source, b.destination, 
                       b.departure_time, b.arrival_time, b.travel_date, b.bus_type, b.price,
                       u.name as user_name, u.email as user_email, u.phone as user_phone
                FROM bookings bk
                JOIN buses b ON bk.bus_id = b.id
                JOIN users u ON bk.user_id = u.id
                WHERE bk.id = ? OR bk.booking_reference = ?
            """
            booking = query_db(query, (int(b_str), b_str), one=True)
        else:
            query = """
                SELECT bk.*, b.operator_name, b.bus_number, b.source, b.destination, 
                       b.departure_time, b.arrival_time, b.travel_date, b.bus_type, b.price,
                       u.name as user_name, u.email as user_email, u.phone as user_phone
                FROM bookings bk
                JOIN buses b ON bk.bus_id = b.id
                JOIN users u ON bk.user_id = u.id
                WHERE bk.booking_reference = ?
            """
            booking = query_db(query, (b_str,), one=True)

        if booking:
            passengers_query = "SELECT * FROM passengers WHERE booking_id = ? ORDER BY seat_number ASC"
            booking['passengers'] = query_db(passengers_query, (booking['id'],))
        return booking

    @staticmethod
    def get_user_bookings(user_id):
        query = """
            SELECT bk.*, b.operator_name, b.bus_number, b.source, b.destination, 
                   b.departure_time, b.arrival_time, b.travel_date, b.bus_type,
                   (SELECT COUNT(*) FROM passengers WHERE booking_id = bk.id) as passenger_count,
                   (SELECT GROUP_CONCAT(seat_number) FROM (SELECT seat_number, booking_id FROM passengers) WHERE booking_id = bk.id) as seat_numbers
            FROM bookings bk
            JOIN buses b ON bk.bus_id = b.id
            WHERE bk.user_id = ?
            ORDER BY bk.booking_date DESC
        """
        return query_db(query, (user_id,))

    @staticmethod
    def get_all():
        query = """
            SELECT bk.*, b.operator_name, b.bus_number, b.source, b.destination, b.travel_date,
                   u.name as user_name, u.email as user_email,
                   (SELECT GROUP_CONCAT(seat_number) FROM (SELECT seat_number, booking_id FROM passengers) WHERE booking_id = bk.id) as seat_numbers
            FROM bookings bk
            JOIN buses b ON bk.bus_id = b.id
            JOIN users u ON bk.user_id = u.id
            ORDER BY bk.booking_date DESC
        """
        return query_db(query)

    @staticmethod
    def cancel_booking(booking_id, user_id=None):
        conn, engine = get_db()
        cursor = conn.cursor()
        placeholder = '%s' if engine == 'mysql' else '?'
        b_str = str(booking_id).strip()

        try:
            # Check eligibility by ID or Reference
            if b_str.isdigit():
                if user_id:
                    cursor.execute(f"SELECT * FROM bookings WHERE (id = {placeholder} OR booking_reference = {placeholder}) AND user_id = {placeholder}", (int(b_str), b_str, user_id))
                else:
                    cursor.execute(f"SELECT * FROM bookings WHERE id = {placeholder} OR booking_reference = {placeholder}", (int(b_str), b_str))
            else:
                if user_id:
                    cursor.execute(f"SELECT * FROM bookings WHERE booking_reference = {placeholder} AND user_id = {placeholder}", (b_str, user_id))
                else:
                    cursor.execute(f"SELECT * FROM bookings WHERE booking_reference = {placeholder}", (b_str,))

            row = cursor.fetchone()
            if engine == 'sqlite' and row:
                row = dict(row)

            if not row:
                conn.close()
                return False, "Booking not found or access denied."

            if row['status'] == 'Cancelled':
                conn.close()
                return False, "Booking is already cancelled."

            # Count seats to restore
            cursor.execute(f"SELECT COUNT(*) as count FROM passengers WHERE booking_id = {placeholder}", (row['id'],))
            pass_count_row = cursor.fetchone()
            pass_count = pass_count_row['count'] if engine == 'mysql' else dict(pass_count_row)['count']

            # Update status
            cursor.execute(f"UPDATE bookings SET status = 'Cancelled' WHERE id = {placeholder}", (row['id'],))

            # Restore bus available_seats
            cursor.execute(f"UPDATE buses SET available_seats = available_seats + {placeholder} WHERE id = {placeholder}", (pass_count, row['bus_id']))

            conn.commit()
            conn.close()
            return True, "Booking cancelled successfully."
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return False, f"Cancellation failed: {str(e)}"

    @staticmethod
    def update_status(booking_id, status):
        query = "UPDATE bookings SET status = ? WHERE id = ?"
        return query_db(query, (status, booking_id), commit=True)

    @staticmethod
    def get_dashboard_stats():
        stats = {
            'total_users': query_db("SELECT COUNT(*) as cnt FROM users WHERE role = 'user'", one=True)['cnt'],
            'total_buses': query_db("SELECT COUNT(*) as cnt FROM buses", one=True)['cnt'],
            'total_bookings': query_db("SELECT COUNT(*) as cnt FROM bookings", one=True)['cnt'],
            'confirmed_bookings': query_db("SELECT COUNT(*) as cnt FROM bookings WHERE status = 'Confirmed'", one=True)['cnt'],
            'cancelled_bookings': query_db("SELECT COUNT(*) as cnt FROM bookings WHERE status = 'Cancelled'", one=True)['cnt'],
            'total_revenue': query_db("SELECT SUM(total_amount) as total FROM bookings WHERE status = 'Confirmed'", one=True)['total'] or 0.0
        }
        return stats
