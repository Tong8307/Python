import sqlite3
import hashlib
import secrets

DB_PATH = "database/student_app.db"

# Password Salt
# If a password is like a plain hamburger 🍔, the salt is like special seasoning that makes each hamburger unique.
# User A: password "cat" + salt "x1y2" → hash "def456"
# User B: password "cat" + salt "z3w4" → hash "ghi789"  ← DIFFERENT!

# -----------------
# Password Hashing
# -----------------
def hash_password(password, salt=None):
    """Hash password with salt using SHA-256"""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt

def verify_password(stored_hash, stored_salt, password):
    """Verify password against stored hash and salt"""
    hashed, _ = hash_password(password, stored_salt)
    return hashed == stored_hash

# -----------------
# Connection helper
# -----------------
def get_connection():
    return sqlite3.connect(DB_PATH)

# -----------------
# USERS
# -----------------
def get_user(student_id, password):
    """Login: check if user exists with matching password."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT student_id, name, password_hash, password_salt FROM users WHERE student_id = ?",
        (student_id,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result:
        student_id, name, stored_hash, stored_salt = result
        if verify_password(stored_hash, stored_salt, password):
            return student_id, name
    return None

def create_user(student_id, name, password):
    """Create new user with hashed password"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        password_hash, password_salt = hash_password(password)
        cursor.execute(
            "INSERT INTO users (student_id, name, password_hash, password_salt) VALUES (?, ?, ?, ?)",
            (student_id, name, password_hash, password_salt)
        )
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_profile_picture(student_id):
    """Get user's profile picture path from database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT profile_picture FROM users WHERE student_id = ?",
        (student_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else None

# -----------------
# LOCATIONS
# -----------------
def get_locations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM locations ORDER BY name")
    result = cursor.fetchall()
    conn.close()
    return result

def get_location_name(location_id):
    """Get location name from database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM locations WHERE id=?", (location_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else f"Location {location_id}"

# -----------------
# ROOMS
# -----------------
def get_rooms_by_location(location_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, r.name, r.capacity 
        FROM rooms r 
        WHERE r.location_id = ?
        ORDER BY r.name
    ''', (location_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def check_room_availability(room_id, date, start, end):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM bookings 
        WHERE room_id = ? AND date = ?
        AND ((start_time < ? AND end_time > ?) OR 
             (start_time >= ? AND start_time < ?))
    ''', (room_id, date, end, start, start, end))
    result = cursor.fetchone()
    conn.close()
    return result is None

# -----------------
# FEATURES
# -----------------
def get_features():
    """Get all available features"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM features ORDER BY name")
    result = cursor.fetchall()
    conn.close()
    return result

def get_rooms_by_feature(location_id, feature_id):
    """Get rooms that have a specific feature"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, r.name, r.capacity 
        FROM rooms r 
        WHERE r.location_id = ? AND r.feature_id = ?
        ORDER BY r.capacity, r.name
    ''', (location_id, feature_id))
    result = cursor.fetchall()
    conn.close()
    return result

# -----------------
# BOOKINGS
# -----------------
def create_booking_with_students(created_by, room_id, date, start, end, student_ids):
    """Create booking and add students in one transaction"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create booking
        cursor.execute('''
            INSERT INTO bookings (created_by, room_id, date, start_time, end_time) 
            VALUES (?, ?, ?, ?, ?)
        ''', (created_by, room_id, date, start, end))
        
        booking_id = cursor.lastrowid
        
        # Add students with their actual names
        for student_id in student_ids:
            student_name = get_student_name(student_id)
            if student_name:
                cursor.execute('''
                    INSERT INTO booking_students (booking_id, student_id, student_name) 
                    VALUES (?, ?, ?)
                ''', (booking_id, student_id, student_name))
        
        conn.commit()
        return booking_id
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_booking_creator(booking_id):
    """Get the creator (student_id) of a booking"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT created_by FROM bookings WHERE id = ?", (booking_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_bookings_by_user(student_id, location_id=None):
    """Get bookings for a user (both created by and participated in), optionally filtered by location"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if location_id:
        # Filter by specific location - include both created by AND participated in
        cursor.execute('''
            SELECT DISTINCT b.id, r.name, b.date, b.start_time, b.end_time, b.status
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            JOIN booking_students bs ON b.id = bs.booking_id
            WHERE (b.created_by = ? OR bs.student_id = ?) 
            AND r.location_id = ?
            ORDER BY 
                CASE 
                    WHEN b.status = 'booked' THEN 1
                    WHEN b.status = 'completed' THEN 2
                    WHEN b.status = 'cancelled' THEN 3
                END,
                b.date DESC,
                b.start_time DESC
        ''', (student_id, student_id, location_id))
    else:
        # Get all bookings (no location filter) - include both created by AND participated in
        cursor.execute('''
            SELECT DISTINCT b.id, r.name, b.date, b.start_time, b.end_time, b.status
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            JOIN booking_students bs ON b.id = bs.booking_id
            WHERE b.created_by = ? OR bs.student_id = ?
            ORDER BY 
                CASE 
                    WHEN b.status = 'booked' THEN 1
                    WHEN b.status = 'completed' THEN 2
                    WHEN b.status = 'cancelled' THEN 3
                END,
                b.date DESC,
                b.start_time DESC
        ''', (student_id, student_id))
    
    result = cursor.fetchall()
    conn.close()
    return result

def update_booking_status(booking_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
    conn.commit()
    conn.close()

def delete_booking(booking_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()


def update_expired_bookings():
    """Update bookings that have passed to 'completed' status"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get current date and time
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")
    
    # Update bookings where date is in past OR date is today but end_time has passed
    cursor.execute('''
        UPDATE bookings 
        SET status = 'completed' 
        WHERE status = 'booked' 
        AND (date < ? OR (date = ? AND end_time <= ?))
    ''', (current_date, current_date, current_time))
    
    conn.commit()
    conn.close()
    return cursor.rowcount  # Return number of updated bookings


# -----------------
# BOOKING STUDENTS
# -----------------
def add_booking_student(booking_id, student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO booking_students (booking_id, student_id) VALUES (?, ?)",
        (booking_id, student_id)
    )
    conn.commit()
    conn.close()

def get_students_in_booking(booking_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.student_id, u.name 
        FROM booking_students bs
        JOIN users u ON bs.student_id = u.student_id
        WHERE bs.booking_id = ?
    ''', (booking_id,))
    result = cursor.fetchall()
    conn.close()
    return result

# -----------------
# STUDENTS
# -----------------
def check_student_exists(student_id):
    """Check if a student ID exists in the database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM users WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_student_name(student_id):
    """Get student name from database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE student_id = ?", (student_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Database error in get_student_name: {e}")
        return None

# -----------------
# CHECK AVAILABILITY
# -----------------
def check_room_availability(room_id, date, start, end):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM bookings 
        WHERE room_id = ? AND date = ? AND status = 'booked'
        AND ((start_time < ? AND end_time > ?) OR 
             (start_time >= ? AND start_time < ?))
    ''', (room_id, date, end, start, start, end))
    result = cursor.fetchone()
    conn.close()
    return result is None

def find_best_available_room(location_id, feature_id, min_capacity, date, start, end):
    """Find the best available room that matches criteria (smallest sufficient capacity)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, r.name, r.capacity 
        FROM rooms r 
        WHERE r.location_id = ? AND r.feature_id = ? AND r.capacity >= ?
        AND r.id NOT IN (
            SELECT room_id FROM bookings 
            WHERE date = ? AND status = 'booked'
            AND ((start_time < ? AND end_time > ?) OR 
                 (start_time >= ? AND start_time < ?))
        )
        ORDER BY r.capacity, r.name
        LIMIT 1
    ''', (location_id, feature_id, min_capacity, date, end, start, start, end))
    result = cursor.fetchone()
    conn.close()
    return result

# -----------------
# Time Table
# -----------------

def get_bookings_for_timetable(room_id, date):
    """Get all bookings for a room on a specific date for timetable display"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT start_time, end_time, status, created_by 
        FROM bookings 
        WHERE room_id = ? AND date = ? AND status = 'booked'
        ORDER BY start_time
    ''', (room_id, date))
    result = cursor.fetchall()
    conn.close()
    return result

def get_rooms_by_location(location_id):
    """Get all rooms for a specific location"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, capacity 
        FROM rooms 
        WHERE location_id = ?
        ORDER BY name
    ''', (location_id,))
    result = cursor.fetchall()
    conn.close()
    return result

# -----------------
# GPA HISTORY
# -----------------
# Add these functions to your db_manager.py

def save_gpa_calculation(student_id, semester_credits, gpa, total_credits, cgpa, 
                       courses_data, current_cgpa, completed_credits):
    """Save a GPA calculation to the database using normalized tables"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get current local time in Python (without seconds)
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")  # ← No seconds
        
        # Insert main GPA record with Python's local time
        cursor.execute('''
            INSERT INTO gpa_history 
            (student_id, timestamp, semester_credits, gpa, total_credits, cgpa, 
             current_cgpa, completed_credits)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, current_time, semester_credits, gpa, total_credits, cgpa, 
              current_cgpa, completed_credits))
        
        gpa_history_id = cursor.lastrowid
        
        # Insert individual courses
        for course in courses_data:
            cursor.execute('''
                INSERT INTO gpa_courses (gpa_history_id, name, credits, grade)
                VALUES (?, ?, ?, ?)
            ''', (gpa_history_id, course['name'], course['credits'], course['grade']))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error in save_gpa_calculation: {e}")
        return False

def get_gpa_history(student_id, limit=10):
    """Retrieve GPA history for a student with courses"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get main GPA records
        cursor.execute('''
            SELECT id, timestamp, semester_credits, gpa, total_credits, cgpa, 
                   current_cgpa, completed_credits
            FROM gpa_history 
            WHERE student_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (student_id, limit))
        
        history = []
        for row in cursor.fetchall():
            gpa_history_id = row[0]
            
            # Get courses for this GPA calculation
            cursor.execute('''
                SELECT name, credits, grade 
                FROM gpa_courses 
                WHERE gpa_history_id = ?
                ORDER BY name
            ''', (gpa_history_id,))
            
            courses_data = []
            for course_row in cursor.fetchall():
                courses_data.append({
                    'name': course_row[0],
                    'credits': course_row[1],
                    'grade': course_row[2]
                })
            
            history.append({
                'id': gpa_history_id,
                'timestamp': row[1],
                'semester_credits': row[2],
                'gpa': row[3],
                'total_credits': row[4],
                'cgpa': row[5],
                'current_cgpa': row[6],
                'completed_credits': row[7],
                'courses_data': courses_data
            })
        
        conn.close()
        return history
    except sqlite3.Error as e:
        print(f"Database error in get_gpa_history: {e}")
        return []
