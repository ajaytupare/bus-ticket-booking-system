# BusGo - Bus Ticket Booking System

A complete, full-stack web application built with **Python 3**, **Flask**, **MySQL**, **Bootstrap 5**, and **Jinja2**.

This platform provides an end-to-end online bus ticketing system allowing customers to search buses, select seats visually, book digital tickets, and manage booking histories, alongside a secure Admin Panel for fleet management, user monitoring, and live revenue analytics.

---

## 🚀 Key Features

### 👤 Customer Features
- **Account Management**: Secure Registration, Password Hashing (`Werkzeug`), Login & Session persistence.
- **Bus Search**: Filter buses by Source, Destination, Travel Date, and Passenger capacity.
- **Dynamic Bus Filtering**: Client-side & server-side filters for AC, Non-AC, Sleeper, Seater, and Price sorting.
- **Visual Seat Selection**: Interactive 40-seat layout (Driver position, Front/Back markers, Available/Selected/Booked states).
- **Seat Rules & Fare Engine**: Real-time fare calculation (`Price × Passengers`) and strict seat count enforcers.
- **Transaction Safety**: Atomic database transactions (`START TRANSACTION ... COMMIT`) preventing seat collision.
- **Digital Ticket Generation**: Printable ticket with reference ID (`BUS-XXXXXXX`), passenger details, and barcode.
- **Booking Management**: History log with instant ticket viewing and booking cancellation (releases seats back to available inventory).

### 👑 Admin Features
- **Dashboard Analytics**: Real-time stats (Total Users, Total Buses, Total Bookings, Confirmed, Cancelled, Total Revenue).
- **Bus Fleet CRUD**: Add new buses, update routes/timings/prices, delete buses.
- **User Directory**: View registered customer list and accounts.
- **Master Booking Log**: View all customer reservations and update booking status inline (`Confirmed`, `Completed`, `Cancelled`).

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Flask
- **Database**: MySQL (with automatic SQLite fallback for zero-config local testing)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Template Engine**: Jinja2
- **Authentication**: Flask Sessions, Werkzeug Password Hashing
- **Database Connector**: `PyMySQL` / `mysql-connector-python` / `SQLAlchemy`

---

## 📁 Recommended Project Structure

```
Bus_Ticket_Booking_System/
│
├── app.py                  # Main Flask application & blueprint initialization
├── config.py               # Environment & database configuration
├── database.sql            # Full MySQL database schema & seed dataset
├── requirements.txt        # Python package dependencies
├── README.md               # Documentation & setup guide
│
├── models/                 # Database access layer
│   ├── __init__.py
│   ├── db.py               # Thread-safe DB manager & query abstraction
│   ├── user_model.py       # User CRUD & auth queries
│   ├── bus_model.py        # Bus search, seat mapping & CRUD
│   └── booking_model.py    # Atomic booking transactions & dashboard stats
│
├── routes/                 # Request routing & controllers
│   ├── __init__.py
│   ├── auth.py             # Auth blueprints & role decorators (@admin_required)
│   ├── user.py             # Homepage, bus search, bus details, profile
│   ├── booking.py          # Seat booking, ticket rendering, history, API
│   └── admin.py            # Admin dashboard, bus CRUD, users, bookings
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Master layout template with navbar & footer
│   ├── index.html          # Hero section & bus search form
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── user/
│   │   ├── buses.html
│   │   ├── bus_details.html
│   │   ├── booking.html
│   │   ├── ticket.html
│   │   ├── bookings.html
│   │   └── profile.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── buses.html
│   │   ├── add_bus.html
│   │   ├── edit_bus.html
│   │   ├── users.html
│   │   └── bookings.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
└── static/                 # Static assets
    ├── css/
    │   └── style.css       # Custom styles, seat matrix UI & print CSS
    └── js/
        ├── main.js         # Client-side filtering & navbar scripts
        ├── booking.js      # Visual seat selection & passenger form generator
        └── admin.js        # Admin panel utilities
```

---

## 🗄️ Database Design (`database.sql`)

### 1. `users` Table
| Column | Type | Description |
|---|---|---|
| `id` | INT (PK, AUTO_INCREMENT) | Primary Key |
| `name` | VARCHAR(100) | Full Name |
| `email` | VARCHAR(100) UNIQUE | Login Email |
| `phone` | VARCHAR(20) | Contact Phone |
| `password` | VARCHAR(255) | Werkzeug Password Hash |
| `role` | ENUM('user', 'admin') | Account Access Role |
| `created_at` | TIMESTAMP | Registration Timestamp |

### 2. `buses` Table
| Column | Type | Description |
|---|---|---|
| `id` | INT (PK, AUTO_INCREMENT) | Primary Key |
| `bus_number` | VARCHAR(50) UNIQUE | Bus License Number |
| `operator_name` | VARCHAR(100) | Travel Operator Name |
| `source` | VARCHAR(100) | Origin City |
| `destination` | VARCHAR(100) | Destination City |
| `departure_time` | VARCHAR(20) | Departure Time |
| `arrival_time` | VARCHAR(20) | Arrival Time |
| `travel_date` | DATE | Date of Journey |
| `bus_type` | VARCHAR(50) | AC/Non-AC Sleeper/Seater |
| `total_seats` | INT | Total Capacity (e.g., 40) |
| `available_seats` | INT | Remaining Free Seats |
| `price` | DECIMAL(10,2) | Fare Per Seat |

### 3. `bookings` Table
| Column | Type | Description |
|---|---|---|
| `id` | INT (PK, AUTO_INCREMENT) | Primary Key |
| `user_id` | INT (FK -> users.id) | Customer ID |
| `bus_id` | INT (FK -> buses.id) | Bus ID |
| `booking_reference` | VARCHAR(20) UNIQUE | Unique Code (e.g., BUS-8F42K91) |
| `total_amount` | DECIMAL(10,2) | Total Booking Fare |
| `booking_date` | TIMESTAMP | Reservation Timestamp |
| `status` | ENUM('Confirmed', 'Cancelled', 'Completed') | Booking Status |

### 4. `passengers` Table
| Column | Type | Description |
|---|---|---|
| `id` | INT (PK, AUTO_INCREMENT) | Primary Key |
| `booking_id` | INT (FK -> bookings.id) | Associated Booking ID |
| `name` | VARCHAR(100) | Passenger Name |
| `age` | INT | Passenger Age |
| `gender` | VARCHAR(10) | Gender |
| `phone` | VARCHAR(20) | Contact Phone |
| `seat_number` | VARCHAR(10) | Assigned Seat (e.g., A1, A2) |

---

## ⚡ Quick Start & Setup Instructions

### 1. Prerequisites
- Python 3.9+ installed
- MySQL Server (Optional: SQLite fallback automatically initializes if MySQL is offline)

### 2. Installation
```bash
# Navigate to project directory
cd e:\Bus-ticket-booking-system-PJ

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Database Setup (MySQL)
```sql
-- Login to MySQL CLI or Workbench and run database.sql
mysql -u root -p < database.sql
```

*Note: Update `.env` or `config.py` with your MySQL credentials (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`).*

### 4. Running the Application
```bash
python app.py
```
Open your web browser and navigate to: **`http://127.0.0.1:5000/`**

---

## 🔑 Pre-seeded Test Credentials

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@busgo.com` | `Admin@123` |
| **Customer** | `user@busgo.com` | `User@123` |

---

## 🧪 Verification & Testing Workflow

1. **User Flow**:
   - Register a new account or log in with `user@busgo.com` / `User@123`.
   - Search buses for route **Kolhapur → Pune** on date **2026-08-15** with **2 Passengers**.
   - Pick 2 available seats on the interactive seat grid (e.g., `A1, A2`).
   - Fill in passenger names/ages and confirm booking.
   - View the generated printable **Digital Ticket**.
   - Check **My Bookings** and test booking cancellation.

2. **Admin Flow**:
   - Log in with `admin@busgo.com` / `Admin@123`.
   - View **Admin Dashboard** live metrics (Users, Buses, Revenue).
   - Navigate to **Manage Buses** → Add a new bus route.
   - View **Master Bookings** and update booking status.
   - Verify non-admin users attempting to open `/admin` are blocked.
"# bus-ticket-booking-system" 
