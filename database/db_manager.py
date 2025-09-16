import sqlite3
import hashlib
import secrets
import json

DB_PATH = "database/student_app.db"

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
    """Get all rooms for a specific location with feature information"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, r.name, r.capacity, f.id as feature_id, f.name as feature_name
        FROM rooms r 
        LEFT JOIN features f ON r.feature_id = f.id
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

def get_bookings_by_user_all_locations(user_id):
    """Get all bookings for a user across all locations"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, r.name, l.name, b.date, b.start_time, b.end_time, b.status
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN locations l ON r.location_id = l.id
        WHERE b.id IN (
            SELECT booking_id FROM booking_students WHERE student_id = ?
            UNION
            SELECT id FROM bookings WHERE created_by = ?
        )
        ORDER BY b.date DESC, b.start_time DESC
    """, (user_id, user_id))
    bookings = cursor.fetchall()
    conn.close()
    return bookings

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
    """Get all rooms for a specific location with feature information"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, r.name, r.capacity, f.id as feature_id, f.name as feature_name
        FROM rooms r 
        LEFT JOIN features f ON r.feature_id = f.id
        WHERE r.location_id = ?
        ORDER BY r.name
    ''', (location_id,))
    result = cursor.fetchall()
    conn.close()
    return result

# -----------------
# GPA HISTORY
# -----------------
def save_gpa_calculation(student_id, semester_credits, gpa, total_credits, cgpa, 
                       courses_data, current_cgpa, completed_credits):
    """Save a GPA calculation to the database using normalized tables"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")  # No seconds
        
        cursor.execute('''
            INSERT INTO gpa_history 
            (student_id, timestamp, semester_credits, gpa, total_credits, cgpa, 
             current_cgpa, completed_credits)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, current_time, semester_credits, gpa, total_credits, cgpa, 
              current_cgpa, completed_credits))
        
        gpa_history_id = cursor.lastrowid
        
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

# -----------------
# NOTES (for Notes Organizer)
# -----------------

# Defaults used when no per-user tool prefs exist yet
_DEFAULT_TOOL_PREFS = {
    "colors": {"pencil": "#555555", "pen": "#000000", "marker": "#ffeb3b"},
    "widths": {"pencil": 2, "pen": 4, "marker": 14, "eraser": 20},
    "alphas": {"pencil": 255, "pen": 255, "marker": 110},
    "eraser_mode": "normal"
}

def create_folder(name, parent_id=None, user_id=None):
    """Create a new folder and return its id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO folders (name, parent_id, user_id)
        VALUES (?, ?, ?)
    """, (name, parent_id, user_id))
    fid = cur.lastrowid
    conn.commit()
    conn.close()
    return fid

def get_folder(folder_id, user_id=None):
    """Fetch one folder as a dict (or None) only if it belongs to the user."""
    conn = get_connection()
    cur = conn.cursor()
    if user_id:
        cur.execute("""
            SELECT id, name, parent_id, user_id, color, created_at, updated_at
            FROM folders
            WHERE id = ? AND user_id = ?
        """, (folder_id, user_id))
    else:
        cur.execute("""
            SELECT id, name, parent_id, user_id, color, created_at, updated_at
            FROM folders
            WHERE id = ?
        """, (folder_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "parent_id": row[2],
        "user_id": row[3],
        "color": row[4],
        "created_at": row[5],
        "updated_at": row[6]
    }

def list_folders(parent_id=None, user_id=None):
    """Return a list of folders for a specific user."""
    conn = get_connection()
    cur = conn.cursor()
    
    if user_id:
        if parent_id is None:
            cur.execute("""
                SELECT id, name, parent_id, user_id, color, created_at, updated_at
                FROM folders
                WHERE user_id = ? AND parent_id IS NULL
                ORDER BY LOWER(name)
            """, (user_id,))
        else:
            cur.execute("""
                SELECT id, name, parent_id, user_id, color, created_at, updated_at
                FROM folders
                WHERE user_id = ? AND parent_id = ?
                ORDER BY LOWER(name)
            """, (user_id, parent_id))
    else:
        if parent_id is None:
            cur.execute("""
                SELECT id, name, parent_id, user_id, color, created_at, updated_at
                FROM folders
                WHERE parent_id IS NULL
                ORDER BY LOWER(name)
            """)
        else:
            cur.execute("""
                SELECT id, name, parent_id, user_id, color, created_at, updated_at
                FROM folders
                WHERE parent_id = ?
                ORDER BY LOWER(name)
            """, (parent_id,))
    
    rows = cur.fetchall()
    conn.close()
    return [{
        "id": r[0], "name": r[1], "parent_id": r[2], "user_id": r[3],
        "color": r[4], "created_at": r[5], "updated_at": r[6]
    } for r in rows]

def update_folder(folder_id, name, parent_id=None, user_id=None):
    """Update an existing folder. Bumps updated_at to now."""
    conn = get_connection()
    cur = conn.cursor()
    if user_id:
        if parent_id is None:
            cur.execute("""
                UPDATE folders
                SET name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (name, folder_id, user_id))
        else:
            cur.execute("""
                UPDATE folders
                SET name = ?, parent_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (name, parent_id, folder_id, user_id))
    else:
        if parent_id is None:
            cur.execute("""
                UPDATE folders
                SET name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name, folder_id))
        else:
            cur.execute("""
                UPDATE folders
                SET name = ?, parent_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name, parent_id, folder_id))
    conn.commit()
    conn.close()

def delete_folder(folder_id, user_id=None):
    """Delete one folder only if it belongs to the user."""
    conn = get_connection()
    cur = conn.cursor()
    if user_id:
        # First move notes to uncategorized
        cur.execute("""
            UPDATE notes SET folder_id = NULL 
            WHERE folder_id = ? AND user_id = ?
        """, (folder_id, user_id))
        # Then delete the folder
        cur.execute("""
            DELETE FROM folders 
            WHERE id = ? AND user_id = ?
        """, (folder_id, user_id))
    else:
        cur.execute("""
            UPDATE notes SET folder_id = NULL 
            WHERE folder_id = ?
        """, (folder_id,))
        cur.execute("""
            DELETE FROM folders 
            WHERE id = ?
        """, (folder_id,))
    conn.commit()
    conn.close()

def list_notes(user_id, order="updated_desc", limit=10):
    """Retrieve notes for a specific user with optional ordering and limit"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Build ORDER BY clause
        order_by = "updated_at DESC" if order == "updated_desc" else "created_at DESC"
        
        cursor.execute(f"""
            SELECT id, title, content, overlay, created_at, updated_at 
            FROM notes 
            WHERE user_id = ?
            ORDER BY {order_by}
            LIMIT ?
        """, (user_id, limit))
        
        notes = []
        for row in cursor.fetchall():
            notes.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'overlay': row[3],  # may be None or JSON string
                'created_at': row[4],
                'updated_at': row[5]
            })
        
        conn.close()
        return notes
    except sqlite3.Error as e:
        print(f"Database error in list_notes: {e}")
        return []

def get_note(note_id, user_id):
    """Get a specific note by ID, ensuring it belongs to the user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, content, overlay, created_at, updated_at 
            FROM notes 
            WHERE id = ? AND user_id = ?
        """, (note_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'overlay': row[3],  # JSON string or None
                'created_at': row[4],
                'updated_at': row[5]
            }
        return None
    except sqlite3.Error as e:
        print(f"Database error in get_note: {e}")
        return None
    
def create_note(title, content, user_id, overlay=None):
    """Create a new note for a user (overlay is optional JSON string)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if overlay is None:
            cursor.execute("""
                INSERT INTO notes (title, content, user_id) 
                VALUES (?, ?, ?)
            """, (title, content, user_id))
        else:
            cursor.execute("""
                INSERT INTO notes (title, content, overlay, user_id) 
                VALUES (?, ?, ?, ?)
            """, (title, content, overlay, user_id))
        
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return note_id
    except sqlite3.Error as e:
        print(f"Database error in create_note: {e}")
        return None

def update_note(note_id, title, content, overlay_or_user=None, user_id=None):
    """
    Update an existing note.

    Backward-compatible signatures:
      - update_note(id, title, content, user_id)                      # legacy: 4th arg = user_id
      - update_note(id, title, content, overlay_json, user_id=uid)    # new: overlay passed, user_id keyword

    IMPORTANT FIX:
    Detect overlay JSON **independently** of whether user_id is provided. Previously,
    when user_id was supplied as a keyword (your code path), overlay_or_user was ignored.
    """

    def _looks_like_json(payload) -> bool:
        if isinstance(payload, (bytes, bytearray)):
            try:
                payload = payload.decode("utf-8", "ignore")
            except Exception:
                return False
        if not isinstance(payload, str):
            return False
        s = payload.strip()
        if not s or s[0] not in "{[":
            return False
        try:
            json.loads(s)  # validate
            return True
        except Exception:
            return False

    try:
        conn = get_connection()
        cursor = conn.cursor()

        overlay = None
        uid = user_id

        # --- FIXED LOGIC: determine overlay independently of uid presence
        if _looks_like_json(overlay_or_user):
            overlay = overlay_or_user if isinstance(overlay_or_user, str) else overlay_or_user.decode("utf-8", "ignore")
        elif uid is None:
            # legacy path: treat 4th arg as user_id when it's not overlay JSON
            uid = overlay_or_user

        if uid is None:
            raise TypeError("update_note requires user_id (either as the legacy 4th argument or as the user_id= keyword).")

        if overlay is None:
            cursor.execute("""
                UPDATE notes 
                SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (title, content, note_id, uid))
        else:
            cursor.execute("""
                UPDATE notes 
                SET title = ?, content = ?, overlay = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (title, content, overlay, note_id, uid))

        conn.commit()
        changed = cursor.rowcount > 0
        conn.close()
        return changed
    except sqlite3.Error as e:
        print(f"Database error in update_note: {e}")
        return False


def update_note_overlay(note_id, overlay_json, user_id):
    """Update only the overlay JSON for a note (convenience helper)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notes 
            SET overlay = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        """, (overlay_json, note_id, user_id))
        conn.commit()
        ok = cursor.rowcount > 0
        conn.close()
        return ok
    except sqlite3.Error as e:
        print(f"Database error in update_note_overlay: {e}")
        return False

# --------- Notes Tool Preferences (per user) ----------
def get_notes_tool_prefs(user_id):
    """
    Load per-user tool preferences for the Notes editor.
    Returns a dict; falls back to sane defaults if no row exists or JSON is bad.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT data FROM notes_tool_prefs WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row or not row[0]:
            return dict(_DEFAULT_TOOL_PREFS)
        try:
            data = json.loads(row[0])
            # Merge with defaults to tolerate future schema changes
            merged = dict(_DEFAULT_TOOL_PREFS)
            merged.update({k: v for k, v in data.items() if k in ("colors", "widths", "alphas", "eraser_mode")})
            # Ensure nested dicts exist
            for k in ("colors", "widths", "alphas"):
                merged[k] = dict(_DEFAULT_TOOL_PREFS[k], **merged.get(k, {}))
            return merged
        except Exception:
            return dict(_DEFAULT_TOOL_PREFS)
    except sqlite3.Error as e:
        print(f"Database error in get_notes_tool_prefs: {e}")
        return dict(_DEFAULT_TOOL_PREFS)

def set_notes_tool_prefs(user_id, prefs_dict):
    """
    Upsert per-user tool preferences as JSON.
    Expects a dict like:
      {"colors": {...}, "widths": {...}, "alphas": {...}, "eraser_mode": "normal|lasso"}
    """
    try:
        payload = json.dumps(prefs_dict or {}, ensure_ascii=False)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notes_tool_prefs (user_id, data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                data = excluded.data,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, payload))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error in set_notes_tool_prefs: {e}")
        return False
