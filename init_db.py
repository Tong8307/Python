import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("student_app.db")
cursor = conn.cursor()

# --- USERS TABLE
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY UNIQUE,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT DEFAULT 'user'
)
''')

# --- LOCATIONS TABLE (for dropdown selection)
cursor.execute('''
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')

# --- FEATURES TABLE (room features like Projector, PC)
cursor.execute('''
CREATE TABLE IF NOT EXISTS features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

# --- ROOMS TABLE (uses dropdown-selected location_id & feature_id)
cursor.execute('''
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    location_id INTEGER,
    capacity INTEGER,
    feature_id INTEGER,
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (feature_id) REFERENCES features(id)
)
''')

# --- BOOKINGS TABLE
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

# --- BOOKING STUDENTS TABLE
cursor.execute('''
CREATE TABLE IF NOT EXISTS booking_students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER,
    student_id TEXT NOT NULL,
    student_name TEXT NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
)
''')

# ----------------------
# 📌 Insert Sample Data
# ----------------------

# USERS (including admin)
cursor.execute("INSERT OR IGNORE INTO users (id, password, name, role) VALUES (1001, 'pass123', 'Alice Tan', 'user')")
cursor.execute("INSERT OR IGNORE INTO users (id, password, name, role) VALUES (1002, 'mypassword', 'Bob Lee', 'user')")
cursor.execute("INSERT OR IGNORE INTO users (id, password, name, role) VALUES (1003, 'secret321', 'Carmen Ng', 'user')")
cursor.execute("INSERT OR IGNORE INTO users (id, password, name, role) VALUES (9999, 'admin123', 'Admin User', 'admin')")

# LOCATIONS (dropdown options)
cursor.execute("INSERT INTO locations (name) VALUES ('Cyber Centre Discussion Room')")
cursor.execute("INSERT INTO locations (name) VALUES ('Library Discussion Room')")
cursor.execute("INSERT INTO locations (name) VALUES ('Arena Discussion Room')")

# FEATURES (dropdown options)
cursor.execute("INSERT INTO features (name) VALUES ('1 PC')")
cursor.execute("INSERT INTO features (name) VALUES ('Projector')")
cursor.execute("INSERT INTO features (name) VALUES ('Whiteboard')")
cursor.execute("INSERT INTO features (name) VALUES ('Air-Conditioned')")

# Get inserted location & feature IDs
cursor.execute("SELECT id FROM locations WHERE name = 'Cyber Centre Discussion Room'")
loc1 = cursor.fetchone()[0] #Get the id of the location no need to manually assign / Fetchone means get the first row of the results
cursor.execute("SELECT id FROM locations WHERE name = 'Library Discussion Room'")
loc2 = cursor.fetchone()[0]
cursor.execute("SELECT id FROM locations WHERE name = 'Arena Discussion Room'")
loc3 = cursor.fetchone()[0]

# Insert rooms (with dropdown-friendly location_id, feature_id)
cursor.execute("INSERT INTO rooms (id, name, location_id, capacity, feature_id) VALUES (1, 'Room A', ?, 4, 1)", (loc1,))
cursor.execute("INSERT INTO rooms (id, name, location_id, capacity, feature_id) VALUES (2, 'Room B', ?, 6, 2)", (loc2,))
cursor.execute("INSERT INTO rooms (id, name, location_id, capacity, feature_id) VALUES (3, 'Room C', ?, 2, 3)", (loc3,))

# BOOKINGS
cursor.execute("INSERT INTO bookings (user_id, room_id, date, start_time, end_time) VALUES (1001, 1, '2025-07-25', '10:00', '12:00')")

# Get booking ID for Alice
cursor.execute("SELECT id FROM bookings WHERE user_id = 1001 AND room_id = 1 AND date = '2025-07-25'")
booking_id = cursor.fetchone()[0]

# BOOKING STUDENTS
cursor.execute("INSERT INTO booking_students (booking_id, student_id, student_name) VALUES (?, '1002', 'Bob Lee')", (booking_id,))
cursor.execute("INSERT INTO booking_students (booking_id, student_id, student_name) VALUES (?, '1003', 'Carmen Ng')", (booking_id,))

# Commit and close
conn.commit()
conn.close()

print("✅ Fully revised student_app.db created — ready for dropdown UI!")
