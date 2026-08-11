import sqlite3
import os
import pymysql
from werkzeug.security import generate_password_hash
from config import Config

def get_mysql_connection():
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=3
        )
        return conn, 'mysql'
    except Exception as e:
        return None, str(e)

def get_sqlite_connection():
    conn = sqlite3.connect(Config.SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'

def get_db():
    if not Config.USE_SQLITE_FALLBACK:
        conn, engine = get_mysql_connection()
        if conn:
            return conn, engine
        raise ConnectionError("Could not connect to MySQL server.")
    
    # Try MySQL first
    conn, engine = get_mysql_connection()
    if conn:
        return conn, engine
    
    # Fallback to SQLite
    conn, engine = get_sqlite_connection()
    return conn, engine

def init_db():
    conn, engine = get_db()
    
    if engine == 'sqlite':
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS buses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bus_number TEXT NOT NULL UNIQUE,
                operator_name TEXT NOT NULL,
                source TEXT NOT NULL,
                destination TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                arrival_time TEXT NOT NULL,
                travel_date TEXT NOT NULL,
                bus_type TEXT NOT NULL,
                total_seats INTEGER DEFAULT 40,
                available_seats INTEGER DEFAULT 40,
                price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bus_id INTEGER NOT NULL,
                booking_reference TEXT NOT NULL UNIQUE,
                total_amount REAL NOT NULL,
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Confirmed',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (bus_id) REFERENCES buses(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passengers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT,
                seat_number TEXT NOT NULL,
                FOREIGN KEY (booking_id) REFERENCES bookings(id)
            )
        ''')
        conn.commit()

        # Seed data if empty
        cursor.execute("SELECT COUNT(*) as count FROM users")
        row = cursor.fetchone()
        if row['count'] == 0:
            admin_pass = generate_password_hash("Admin@123")
            user_pass = generate_password_hash("User@123")
            cursor.execute("INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, ?)",
                           ('System Admin', 'admin@busgo.com', '9876543210', admin_pass, 'admin'))
            cursor.execute("INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, ?)",
                           ('Ajay Kumar', 'user@busgo.com', '9123456789', user_pass, 'user'))
            
            sample_buses = [
                ('MH12AB1234', 'Shree Travels', 'Kolhapur', 'Pune', '08:00 AM', '01:00 PM', '2026-08-15', 'AC Sleeper', 40, 40, 650.00),
                ('MH09CD5678', 'VRL Travels', 'Kolhapur', 'Pune', '10:30 PM', '04:30 AM', '2026-08-15', 'AC Seater', 40, 40, 550.00),
                ('MH14EF9012', 'Neeta Tours', 'Kolhapur', 'Mumbai', '09:00 PM', '06:00 AM', '2026-08-15', 'Non-AC Sleeper', 40, 40, 750.00),
                ('MH12GH3456', 'Purple Metrolink', 'Pune', 'Mumbai', '07:00 AM', '11:00 AM', '2026-08-15', 'AC Seater', 40, 40, 450.00),
                ('MH15IJ7890', 'MSRTC Shivneri', 'Mumbai', 'Nashik', '06:00 AM', '10:30 AM', '2026-08-16', 'AC Sleeper', 40, 40, 500.00),
                ('MH09KL2345', 'Konduskar Travels', 'Kolhapur', 'Goa', '11:00 PM', '06:00 AM', '2026-08-16', 'AC Sleeper', 40, 40, 850.00),
                ('MH12MN6789', 'Zingbus Premium', 'Pune', 'Mumbai', '04:00 PM', '08:00 PM', '2026-08-16', 'AC Sleeper', 40, 40, 600.00)
            ]
            cursor.executemany('''
                INSERT INTO buses (bus_number, operator_name, source, destination, departure_time, arrival_time, travel_date, bus_type, total_seats, available_seats, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_buses)
            conn.commit()
        conn.close()
    else:
        # MySQL Initialization
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = %s AND table_name = 'users'", (Config.DB_NAME,))
        res = cursor.fetchone()
        if not res or res['count'] == 0:
            sql_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database.sql')
            if os.path.exists(sql_file):
                with open(sql_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    statements = content.split(';')
                    for stmt in statements:
                        if stmt.strip():
                            cursor.execute(stmt)
                conn.commit()
        conn.close()

def query_db(query, args=(), one=False, commit=False):
    conn, engine = get_db()
    cursor = conn.cursor()
    
    # Standardize parameter placeholders between SQLite (?) and PyMySQL (%s)
    if engine == 'mysql':
        query = query.replace('?', '%s')
    
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            if engine == 'sqlite':
                last_id = cursor.lastrowid
            else:
                last_id = cursor.lastrowid
            conn.close()
            return last_id
        
        if engine == 'sqlite':
            rv = [dict(row) for row in cursor.fetchall()]
        else:
            rv = cursor.fetchall()
            
        conn.close()
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        raise e
