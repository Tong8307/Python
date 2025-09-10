import sqlite3
import hashlib
import secrets

def hash_password(password, salt=None):
    """Hash password with salt using SHA-256"""
    if salt is None:
        salt = secrets.token_hex(16)  # Generate 16-byte random salt (32 characters)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt

# Connect to SQLite database (or create it)
conn = sqlite3.connect('student_app.db')
cursor = conn.cursor()

# 1. Users (students only) - UPDATED with password hashing
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    student_id TEXT PRIMARY KEY,  
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    profile_picture TEXT
);
""")

# 2. Locations (e.g. Library, Block A)
cursor.execute("""
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

# 3. Rooms (belong to a location)
cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms (
    id TEXT PRIMARY KEY,
    location_id INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    name TEXT NOT NULL,
    feature_id TEXT,
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (feature_id) REFERENCES features(id)
)
""")

# 4. Features (projector, whiteboard, etc.)
cursor.execute("""
CREATE TABLE IF NOT EXISTS features (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
""")

# 5. Bookings (one student creates a booking)
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id TEXT NOT NULL,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    status TEXT CHECK(status IN ('booked', 'cancelled', 'completed')) NOT NULL DEFAULT 'booked',
    created_by TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (created_by) REFERENCES users(student_id)
)
""")

# 6. Booking_Students (who joined this booking)
cursor.execute("""
CREATE TABLE IF NOT EXISTS booking_students (
    booking_id INTEGER NOT NULL,
    student_id TEXT NOT NULL,
    student_name TEXT,
    PRIMARY KEY (booking_id, student_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (student_id) REFERENCES users(student_id)
)
""")

# 7. GPA History Table (main record)
cursor.execute("""
CREATE TABLE IF NOT EXISTS gpa_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    semester_credits INTEGER,
    gpa REAL,
    total_credits INTEGER,
    cgpa REAL,
    current_cgpa REAL,
    completed_credits INTEGER,
    FOREIGN KEY (student_id) REFERENCES users(student_id)
)
""")

# 8. GPA Courses Table (individual courses)
cursor.execute("""
CREATE TABLE IF NOT EXISTS gpa_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gpa_history_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    credits INTEGER NOT NULL,
    grade TEXT NOT NULL,
    FOREIGN KEY (gpa_history_id) REFERENCES gpa_history(id) ON DELETE CASCADE
)
""")


# Insert Locations
cursor.executemany("INSERT OR IGNORE INTO locations (id, name) VALUES (?, ?)", [
    (1, 'Cyber Centre Discussion Room'),
    (2, 'Library Discussion Room'),
    (3, 'Arena Discussion Room')
])

# Insert Features
cursor.executemany("INSERT OR IGNORE INTO features (id, name) VALUES (?, ?)", [
    ('F01', 'Discussion Room (1PC)'),
    ('F02', 'Discussion Room (2PCS)'),
    ('F03', 'Discussion Room (2PCS)'),
    ('F04', 'Discussion Room with Projector (2PCS)'),
    ('F05', 'Discussion Room with Projector (2PCS) [HDMI]')
])

# Insert Rooms with feature_id
cursor.executemany("INSERT OR IGNORE INTO rooms (id, location_id, capacity, name, feature_id) VALUES (?, ?, ?, ?, ?)", [
    ('R101', 1, 6, 'Room C204', 'F01'),
    ('R102', 1, 8, 'Room C280', 'F02'),
    ('R201', 2, 4, 'Room L222', 'F03'),
    ('R202', 2, 10, 'Room L888', 'F04'),
    ('R301', 3, 5, 'Room A012', 'F05'),
    ('R302', 3, 12, 'Room A125', 'F05'),
    ('R303', 3, 5, 'Room A012', 'F02'),
    ('R304', 3, 10, 'Room A124', 'F01'),
    ('R305', 3, 2, 'Room A028', 'F03'),
    ('R306', 3, 3, 'Room A129', 'F04'),
    ('R307', 3, 6, 'Room A038', 'F02'),
    ('R308', 3, 5, 'Room A175', 'F03')
])

# Insert Users with hashed passwords
users_data = [
    ('24WMD0624', 'Eun Eun Bond', 'pass123', 'user1.png'),
    ('24WMD0345', 'Yu Yu Bond', 'abc456', 'user2.png'),
    ('24WMD0188', 'Tong Tong Bond', '123456', 'user3.png'),
    ('24WMD0199', 'John Tan', 'johnpwd', 'user4.png'),
    ('24WMD0222', 'Nur Aisyah', 'aisyah@123', 'user5.png')
]

for student_id, name, password, profile_picture in users_data:
    password_hash, password_salt = hash_password(password)
    cursor.execute(
        "INSERT OR IGNORE INTO users (student_id, name, password_hash, password_salt, profile_picture) VALUES (?, ?, ?, ?, ?)",
        (student_id, name, password_hash, password_salt, profile_picture)
    )

# Clear existing bookings and booking_students to avoid conflicts
cursor.execute("DELETE FROM booking_students")
cursor.execute("DELETE FROM bookings")

# Insert Bookings
cursor.executemany("""
    INSERT INTO bookings (room_id, date, start_time, end_time, status, created_by)
    VALUES (?, ?, ?, ?, ?, ?)
""", [
    ('R101', '2025-08-01', '10:00', '12:00', 'booked', '24WMD0624'),
    ('R202', '2025-08-02', '14:00', '16:00', 'booked', '24WMD0345'),
    ('R201', '2025-08-03', '09:00', '11:00', 'cancelled', '24WMD0188'),
    ('R301', '2025-08-04', '15:00', '17:00', 'booked', '24WMD0199')
])

# Insert Booking Students (participants)
cursor.executemany("INSERT INTO booking_students (booking_id, student_id, student_name) VALUES (?, ?, ?)", [
    (1, '24WMD0624', 'Eun Eun Bond'),
    (1, '24WMD0345', 'Yu Yu Bond'),
    (2, '24WMD0345', 'Yu Yu Bond'),
    (2, '24WMD0222', 'Nur Aisyah'),
    (3, '24WMD0188', 'Lim Mei Mei'),
    (4, '24WMD0199', 'John Tan'),
    (4, '24WMD0624', 'Eun Eun Bond')
])

print("Database initialized successfully!")

conn.commit()
conn.close()