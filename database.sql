-- Bus Ticket Booking System Database Schema
-- Database: bus_ticket_booking

CREATE DATABASE IF NOT EXISTS bus_ticket_booking;
USE bus_ticket_booking;

-- Table: users
DROP TABLE IF EXISTS passengers;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS buses;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: buses
CREATE TABLE buses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bus_number VARCHAR(50) NOT NULL UNIQUE,
    operator_name VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    departure_time VARCHAR(20) NOT NULL,
    arrival_time VARCHAR(20) NOT NULL,
    travel_date DATE NOT NULL,
    bus_type VARCHAR(50) NOT NULL,
    total_seats INT NOT NULL DEFAULT 40,
    available_seats INT NOT NULL DEFAULT 40,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: bookings
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    bus_id INT NOT NULL,
    booking_reference VARCHAR(20) NOT NULL UNIQUE,
    total_amount DECIMAL(10, 2) NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Confirmed', 'Cancelled', 'Completed') DEFAULT 'Confirmed',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bus_id) REFERENCES buses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: passengers
CREATE TABLE passengers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    phone VARCHAR(20),
    seat_number VARCHAR(10) NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample Seed Data
-- Note: Admin Password: Admin@123 | Customer Password: User@123
INSERT INTO users (id, name, email, phone, password, role) VALUES
(1, 'System Admin', 'admin@busgo.com', '9876543210', 'scrypt:32768:8:1$7fR3j2pL8k9M$4d51ea5c3a37ecbcfeb3d4dfa6fb699cf59371ff635b71fa0df9857d425ad877d9eb0155b9e07fb6a1ad8797f6c6d59ce66324a35ea2ffbc3b4ec8b9e67dcb7f', 'admin'),
(2, 'Ajay Kumar', 'user@busgo.com', '9123456789', 'scrypt:32768:8:1$9mQ2k8pL7k1N$1f88efbc1f9b33a595bc18f59d57a2c6d48259b1a591244fbfa8bc911293a591ad0955ffb012356d78ef8a9bc6d542ef89104928ab591a56bc91024bc6f81a7b', 'user');

INSERT INTO buses (bus_number, operator_name, source, destination, departure_time, arrival_time, travel_date, bus_type, total_seats, available_seats, price) VALUES
('MH12AB1234', 'Shree Travels', 'Kolhapur', 'Pune', '08:00 AM', '01:00 PM', '2026-08-15', 'AC Sleeper', 40, 40, 650.00),
('MH09CD5678', 'VRL Travels', 'Kolhapur', 'Pune', '10:30 PM', '04:30 AM', '2026-08-15', 'AC Seater', 40, 40, 550.00),
('MH14EF9012', 'Neeta Tours', 'Kolhapur', 'Mumbai', '09:00 PM', '06:00 AM', '2026-08-15', 'Non-AC Sleeper', 40, 40, 750.00),
('MH12GH3456', 'Purple Metrolink', 'Pune', 'Mumbai', '07:00 AM', '11:00 AM', '2026-08-15', 'AC Seater', 40, 40, 450.00),
('MH15IJ7890', 'MSRTC Shivneri', 'Mumbai', 'Nashik', '06:00 AM', '10:30 AM', '2026-08-16', 'AC Sleeper', 40, 40, 500.00),
('MH09KL2345', 'Konduskar Travels', 'Kolhapur', 'Goa', '11:00 PM', '06:00 AM', '2026-08-16', 'AC Sleeper', 40, 40, 850.00),
('MH12MN6789', 'Zingbus Premium', 'Pune', 'Mumbai', '04:00 PM', '08:00 PM', '2026-08-16', 'AC Sleeper', 40, 40, 600.00);
