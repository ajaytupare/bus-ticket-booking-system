import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'busgo-secret-key-2026-super-secure')
    
    # MySQL Database Config
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'bus_ticket_booking')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # Enable automatic SQLite fallback if MySQL is not reachable locally
    SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bus_ticket_booking.db')
    USE_SQLITE_FALLBACK = os.environ.get('USE_SQLITE_FALLBACK', 'True').lower() in ('true', '1', 't')
