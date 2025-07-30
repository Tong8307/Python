import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect('student_app.db')
cursor = conn.cursor()

# 1. Users (students only)
cursor.execute("""
CREATE TABLE users (
    student_id TEXT PRIMARY KEY,  
    name TEXT NOT NULL,
    password TEXT NOT NULL
);
""")

# 2. Locations (e.g. Library, Block A)
cursor.execute("""
CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

# 3. Rooms (belong to a location)
cursor.execute("""
CREATE TABLE rooms (
    id TEXT PRIMARY KEY,
    location_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (location_id) REFERENCES locations(id)
)
""")

# 4. Features (projector, whiteboard, etc.)
cursor.execute("""
CREATE TABLE features (
    id TEXT PRIMARY KEY ,
    name TEXT NOT NULL
)
""")

# 5. Bookings (one student creates a booking)
cursor.execute("""
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id TEXT NOT NULL,
    feature_id TEXT,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    status TEXT CHECK(status IN ('pending', 'approved', 'rejected', 'cancelled')) NOT NULL DEFAULT 'pending',
    created_by INTEGER NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (feature_id) REFERENCES features(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
)
""")

# 6. Booking_Students (who joined this booking)
cursor.execute("""
CREATE TABLE booking_students (
    booking_id INTEGER NOT NULL,
    student_id TEXT NOT NULL,
    PRIMARY KEY (booking_id, student_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (student_id) REFERENCES users(id)
)
""")

cursor.executemany("INSERT INTO locations (name) VALUES (?)", [
    ('Cyber Centre Discussion Room',),
    ('Library Discussion Room',),
    ('Arena Discussion Room',)
])

# Insert Rooms
cursor.executemany("INSERT INTO rooms (id, location_id, name) VALUES (?, ?, ?)", [
    ('R101', 1, 'Room C204'),
    ('R102', 1, 'Room C280'),
    ('R201', 2, 'Room L222'),
    ('R202', 2, 'Room L888'),
    ('R301', 3, 'Room A012'),
    ('R302', 3, 'Room A125')
])

# Insert Features
cursor.executemany("INSERT INTO features (id, name) VALUES (?, ?)", [
    ('F01', 'Discussion Room (1PC)'),
    ('F02', 'Discussion Room (2PCS)'),
    ('F03', 'Discussion Room (2PCS)'),
    ('F04', 'Discussion Room with Projector (2PCS)'),
    ('F05', 'Discussion Room with Projector (2PCS) [HDMI]')
])

# Insert Users
cursor.executemany("INSERT INTO users (student_id, name, password) VALUES (?, ?, ?)", [
    ('24WMD0624', 'Eun Eun Bond', 'pass123'),
    ('24WMD0345', 'Yu Yu Bond', 'abc456'),
    ('24WMD0188', 'Lim Mei Mei', 'xyz789'),
    ('24WMD0199', 'John Tan', 'johnpwd'),
    ('24WMD0222', 'Nur Aisyah', 'aisyah@123')
])

# Insert Bookings
cursor.executemany("""
    INSERT INTO bookings (room_id, feature_id, date, start_time, end_time, status, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", [
    ('R101', 'F01', '2025-08-01', '10:00', '12:00', 'approved', '24WMD0624'),
    ('R202', 'F03', '2025-08-02', '14:00', '16:00', 'pending', '24WMD0345'),
    ('R201', 'F02', '2025-08-03', '09:00', '11:00', 'cancelled', '24WMD0188'),
    ('R301', 'F04', '2025-08-04', '15:00', '17:00', 'approved', '24WMD0199')
])

# Insert Booking Students (participants)
cursor.executemany("INSERT INTO booking_students (booking_id, student_id) VALUES (?, ?)", [
    (1, '24WMD0624'),
    (1, '24WMD0345'),
    (2, '24WMD0345'),
    (2, '24WMD0222'),
    (3, '24WMD0188'),
    (4, '24WMD0199'),
    (4, '24WMD0624')
])


conn.commit()
conn.close()
