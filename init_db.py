import sqlite3

# Create/connect to database
conn = sqlite3.connect("student_app.db")
cursor = conn.cursor()

# USERS TABLE
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY UNIQUE,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT DEFAULT 'user'
)
''')

# FEATURES TABLE
cursor.execute('''
CREATE TABLE IF NOT EXISTS features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

# ROOMS TABLE
cursor.execute('''
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    capacity INTEGER,
    feature_id INTEGER,
    FOREIGN KEY (feature_id) REFERENCES features(id)
)
''')

# BOOKINGS TABLE
cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    room_id INTEGER,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
)
''')

# BOOKING STUDENTS TABLE
cursor.execute('''
CREATE TABLE IF NOT EXISTS booking_students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER,
    student_id TEXT NOT NULL,
    student_name TEXT NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
)
''')


# Sample Data
# --- USERS ---
cursor.execute("INSERT OR IGNORE INTO users (id, password, name, role) VALUES (1001, 'pass123', 'Alice Tan', 'user')")
cursor.execute("INSERT OR IGNORE INTO users (id, password, name, role) VALUES (1002, 'mypassword', 'Bob Lee', 'user')")
cursor.execute("INSERT OR IGNORE INTO users (id, password, name, role) VALUES (1003, 'secret321', 'Carmen Ng', 'user')")
cursor.execute("INSERT OR IGNORE INTO users (id, password, name, role) VALUES (9999, 'admin123', 'Admin User', 'admin')")

# --- FEATURES ---
cursor.execute("INSERT INTO features (name) VALUES ('1 PC')")
cursor.execute("INSERT INTO features (name) VALUES ('Projector')")
cursor.execute("INSERT INTO features (name) VALUES ('Whiteboard')")
cursor.execute("INSERT INTO features (name) VALUES ('Air-Conditioned')")

# --- ROOMS ---
cursor.execute("INSERT INTO rooms (id, name, location, capacity, feature_id) VALUES (1, 'Room A', 'Block A, Level 1', 4, 1)")
cursor.execute("INSERT INTO rooms (id, name, location, capacity, feature_id) VALUES (2, 'Room B', 'Block B, Level 2', 6, 2)")
cursor.execute("INSERT INTO rooms (id, name, location, capacity, feature_id) VALUES (3, 'Room C', 'Library', 2, 3)")

# --- BOOKINGS ---
cursor.execute("INSERT INTO bookings (user_id, room_id, date, start_time, end_time) VALUES (1001, 1, '2025-07-25', '10:00', '12:00')")

# --- Get booking ID just inserted ---
cursor.execute("SELECT id FROM bookings WHERE user_id = 1001 AND room_id = 1 AND date = '2025-07-25'")
booking_id = cursor.fetchone()[0]

# --- BOOKING STUDENTS ---
cursor.execute(f"INSERT INTO booking_students (booking_id, student_id, student_name) VALUES ({booking_id}, '1002', 'Bob Lee')")
cursor.execute(f"INSERT INTO booking_students (booking_id, student_id, student_name) VALUES ({booking_id}, '1003', 'Carmen Ng')")

# Save and close
conn.commit()
conn.close()

print("✅ Multi-user room booking database created successfully!")
