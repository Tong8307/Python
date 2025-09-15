import os
import sqlite3
import hashlib
import secrets


def hash_password(password, salt=None):
    """Hash password with salt using SHA-256"""
    if salt is None:
        salt = secrets.token_hex(16)  # Generate 16-byte random salt (32 characters)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt

# ---------- Connect (DB inside /database) ----------
DB_PATH = os.path.join(os.path.dirname(__file__), "student_app.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

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

# 9. Folders
cursor.execute("""
CREATE TABLE IF NOT EXISTS folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (length(name) <= 50),
    parent_id INTEGER,
    user_id TEXT,  -- Add this column
    color TEXT DEFAULT '#FFFFFF',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES folders(id),
    FOREIGN KEY (user_id) REFERENCES users(student_id)  -- Add foreign key
)
""") 

# 10. Notes
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_id INTEGER NULL,
    title TEXT NOT NULL CHECK (length(title) <= 50),
    content TEXT,
    cover_path TEXT,
    file_path TEXT,
    user_id TEXT,  -- Add this column
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (folder_id) REFERENCES folders(id),
    FOREIGN KEY (user_id) REFERENCES users(student_id)  -- Add foreign key
)
""")

# Helpful indexes for notes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_title   ON notes(title)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_updated ON notes(updated_at)")

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
    # Location 1 additional rooms
    ('R111', 1, 4, 'Room C209', 'F01'),
    ('R112', 1, 8, 'Room C285', 'F02'),
    ('R113', 1, 2, 'Room C210', 'F03'),
    ('R114', 1, 6, 'Room C286', 'F04'),
    ('R115', 1, 10, 'Room C211', 'F05'),
    ('R116', 1, 3, 'Room C287', 'F01'),
    ('R117', 1, 7, 'Room C212', 'F02'),
    ('R118', 1, 5, 'Room C288', 'F03'),
    ('R119', 1, 1, 'Room C213', 'F04'),
    ('R120', 1, 9, 'Room C289', 'F05'),
    
    # Location 2 additional rooms
    ('R211', 2, 5, 'Room L227', 'F01'),
    ('R212', 2, 9, 'Room L893', 'F02'),
    ('R213', 2, 3, 'Room L228', 'F03'),
    ('R214', 2, 7, 'Room L894', 'F04'),
    ('R215', 2, 1, 'Room L229', 'F05'),
    ('R216', 2, 6, 'Room L895', 'F01'),
    ('R217', 2, 4, 'Room L230', 'F02'),
    ('R218', 2, 8, 'Room L896', 'F03'),
    ('R219', 2, 2, 'Room L231', 'F04'),
    ('R220', 2, 10, 'Room L897', 'F05'),
    
    # Location 3 additional rooms
    ('R319', 3, 7, 'Room A033', 'F01'),
    ('R320', 3, 2, 'Room A181', 'F02'),
    ('R321', 3, 9, 'Room A034', 'F03'),
    ('R322', 3, 4, 'Room A182', 'F04'),
    ('R323', 3, 8, 'Room A035', 'F05'),
    ('R324', 3, 3, 'Room A183', 'F01'),
    ('R325', 3, 6, 'Room A036', 'F02'),
    ('R326', 3, 1, 'Room A184', 'F03'),
    ('R327', 3, 5, 'Room A037', 'F04'),
    ('R328', 3, 10, 'Room A185', 'F05'),
    ('R329', 3, 4, 'Room A038', 'F01'),
    ('R330', 3, 7, 'Room A186', 'F02'),
    ('R331', 3, 2, 'Room A039', 'F03'),
    ('R332', 3, 8, 'Room A187', 'F04'),
    ('R333', 3, 5, 'Room A040', 'F05'),
    ('R334', 3, 3, 'Room A188', 'F01'),
    ('R335', 3, 6, 'Room A041', 'F02'),
    ('R336', 3, 9, 'Room A189', 'F03'),
    ('R337', 3, 1, 'Room A042', 'F04'),
    ('R338', 3, 10, 'Room A190', 'F05')
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

# Insert Bookings and store their real IDs
booking_data = [
    ('R111', '2025-08-01', '10:00', '12:00', 'booked', '24WMD0624'),
    ('R112', '2025-08-02', '14:00', '16:00', 'booked', '24WMD0345'),
    ('R113', '2025-08-03', '09:00', '11:00', 'cancelled', '24WMD0188'),
    ('R320', '2025-08-04', '15:00', '17:00', 'booked', '24WMD0199')
]

booking_ids = []
for room_id, date, start_time, end_time, status, created_by in booking_data:
    cursor.execute(
        "INSERT INTO bookings (room_id, date, start_time, end_time, status, created_by) VALUES (?, ?, ?, ?, ?, ?)",
        (room_id, date, start_time, end_time, status, created_by)
    )
    booking_ids.append(cursor.lastrowid)  # get actual AUTOINCREMENT ID

# Insert Booking Students using actual booking IDs
booking_students_data = [
    (booking_ids[0], '24WMD0624', 'Eun Eun Bond'),
    (booking_ids[0], '24WMD0345', 'Yu Yu Bond'),
    (booking_ids[1], '24WMD0345', 'Yu Yu Bond'),
    (booking_ids[1], '24WMD0222', 'Nur Aisyah'),
    (booking_ids[2], '24WMD0188', 'Tong Tong Bond'),
    (booking_ids[3], '24WMD0199', 'John Tan')
]

for booking_id, student_id, student_name in booking_students_data:
    cursor.execute(
        "INSERT INTO booking_students (booking_id, student_id, student_name) VALUES (?, ?, ?)",
        (booking_id, student_id, student_name)
    )

# ---------- Seed a welcome note if notes is empty ----------
cursor.execute("SELECT COUNT(*) FROM notes")
if cursor.fetchone()[0] == 0:
    # Create welcome notes for each user
    for student_id, name, password, profile_picture in users_data:
        cursor.execute(
            "INSERT INTO notes (folder_id, title, content, user_id) VALUES (?, ?, ?, ?)",
            (None, "Welcome to Your Notes App", "👋 Welcome! Use the + button to add notes. You can organize notes into folders anytime.", student_id)
        )

conn.commit()
conn.close()
print(f"Database initialized successfully at: {DB_PATH}")