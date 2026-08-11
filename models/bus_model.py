from models.db import query_db

class BusModel:
    @staticmethod
    def search_buses(source, destination, travel_date, passengers=1):
        query = """
            SELECT * FROM buses 
            WHERE LOWER(source) = LOWER(?) 
              AND LOWER(destination) = LOWER(?) 
              AND travel_date = ? 
              AND available_seats >= ?
            ORDER BY departure_time ASC
        """
        return query_db(query, (source.strip(), destination.strip(), travel_date, passengers))

    @staticmethod
    def get_by_id(bus_id):
        query = "SELECT * FROM buses WHERE id = ?"
        return query_db(query, (bus_id,), one=True)

    @staticmethod
    def get_all():
        query = "SELECT * FROM buses ORDER BY travel_date DESC, departure_time ASC"
        return query_db(query)

    @staticmethod
    def add_bus(bus_number, operator_name, source, destination, departure_time, arrival_time, travel_date, bus_type, total_seats, price):
        query = """
            INSERT INTO buses 
            (bus_number, operator_name, source, destination, departure_time, arrival_time, travel_date, bus_type, total_seats, available_seats, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return query_db(query, (bus_number.upper().strip(), operator_name.strip(), source.strip(), destination.strip(), 
                                departure_time.strip(), arrival_time.strip(), travel_date, bus_type.strip(), 
                                int(total_seats), int(total_seats), float(price)), commit=True)

    @staticmethod
    def update_bus(bus_id, bus_number, operator_name, source, destination, departure_time, arrival_time, travel_date, bus_type, total_seats, price):
        # Calculate seat adjustments if total seats modified
        existing = BusModel.get_by_id(bus_id)
        if not existing:
            return False
            
        booked_count = existing['total_seats'] - existing['available_seats']
        new_available = max(0, int(total_seats) - booked_count)
        
        query = """
            UPDATE buses 
            SET bus_number = ?, operator_name = ?, source = ?, destination = ?, departure_time = ?, 
                arrival_time = ?, travel_date = ?, bus_type = ?, total_seats = ?, available_seats = ?, price = ?
            WHERE id = ?
        """
        return query_db(query, (bus_number.upper().strip(), operator_name.strip(), source.strip(), destination.strip(),
                                departure_time.strip(), arrival_time.strip(), travel_date, bus_type.strip(), 
                                int(total_seats), new_available, float(price), bus_id), commit=True)

    @staticmethod
    def delete_bus(bus_id):
        query = "DELETE FROM buses WHERE id = ?"
        return query_db(query, (bus_id,), commit=True)

    @staticmethod
    def get_booked_seats(bus_id):
        query = """
            SELECT p.seat_number 
            FROM passengers p
            JOIN bookings bk ON p.booking_id = bk.id
            WHERE bk.bus_id = ? AND bk.status = 'Confirmed'
        """
        rows = query_db(query, (bus_id,))
        return [r['seat_number'] for r in rows] if rows else []

    @staticmethod
    def count_all():
        res = query_db("SELECT COUNT(*) as total FROM buses", one=True)
        return res['total'] if res else 0

    @staticmethod
    def get_distinct_sources():
        rows = query_db("SELECT DISTINCT source FROM buses ORDER BY source ASC")
        return [r['source'] for r in rows] if rows else []

    @staticmethod
    def get_distinct_destinations():
        rows = query_db("SELECT DISTINCT destination FROM buses ORDER BY destination ASC")
        return [r['destination'] for r in rows] if rows else []
