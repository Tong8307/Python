from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QScrollArea, QFrame, QGridLayout, QDateEdit,
                            QTimeEdit, QComboBox, QMessageBox, QLineEdit,
                            QStackedWidget)
from PyQt5.QtCore import Qt, QSize, QDate, QTime
from PyQt5.QtGui import QIcon,QPixmap
import sqlite3
from datetime import datetime, timedelta
from styles.booking_styles import get_booking_styles

class LocationSelectionWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Apply the booking styles to this widget
        self.setStyleSheet(get_booking_styles())
        
        # Main layout with proper spacing
        main_layout = QVBoxLayout(self)
        
        # Header using booking style
        title = QLabel("Room Booking")
        title.setObjectName("bookingHeader")  # Uses the styled header from booking_styles
        main_layout.addWidget(title)

        subtitle = QLabel("Please select a location: ")
        subtitle.setObjectName("bookingSubheader")  # Uses the styled header from booking_styles
        main_layout.addWidget(subtitle)
        
        # Add a styled divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setObjectName("divider")  # Uses the divider style from booking_styles
        main_layout.addWidget(divider)
        
        # Scrollable area for locations
        scroll = QScrollArea()
        scroll.setObjectName("scroll")
        scroll.setWidgetResizable(True)
        
        # Container for location buttons
        locations_container = QWidget()
        locations_layout = QVBoxLayout(locations_container)
        locations_container.setStyleSheet("background-color: #f5f7fa;")
        locations_layout.setSpacing(15)
        locations_layout.setContentsMargins(10, 10, 10, 10)
        
        # Load locations from database
        locations = self.load_locations()
        for loc_id, loc_name in locations:
            btn = self.create_location_button(loc_id, loc_name)
            locations_layout.addWidget(btn)
            
        locations_layout.addStretch()
        scroll.setWidget(locations_container)
        main_layout.addWidget(scroll)
        
        # Back button with enhanced styling
        back_btn = QPushButton()
        back_btn.setIcon(QIcon("Photo/back.png"))
        back_btn.setText(" Back to Home")
        back_btn.setFixedSize(750, 40)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setObjectName("iconBackButton")
        back_btn.setIconSize(QSize(16, 16))
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn, 0, Qt.AlignCenter)
        
    def load_locations(self):
        """Load locations from database with error handling"""
        try:
            conn = sqlite3.connect(str("database/student_app.db"))
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM locations ORDER BY name")
            locations = cursor.fetchall()
            conn.close()
            return locations
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
            
    def create_location_button(self, loc_id, loc_name):
        """Create a location button with consistent styling"""
        btn = QPushButton(loc_name)
        btn.setStyleSheet("""
        QPushButton {
            background-color: white;
            color: #283593;
            border: 2px solid #283593;
            border-radius: 8px;
            padding: 15px;
            font-size: 20px;
            font-weight: 500;
            min-width: 250px;
            margin: 5px;
        }
        QPushButton:hover {
            background-color: #E8EAF6;
            border: 2px solid #1A237E;
        }
        """)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.go_to_booking(loc_id))
        return btn
        
    def go_to_booking(self, location_id):
        try:
            self.main_window.open_room_booking_page(location_id)
        except Exception as e:
            print(f"Navigation error: {e}")
            
    def go_back(self):
        self.main_window.pages.setCurrentWidget(self.main_window.feature_grid_page)

class FeatureButton(QPushButton): 
    def __init__(self, icon_path, text, parent=None):
        super().__init__(parent) # Initialize QPushButton
        self.setObjectName("FeatureButton") # CSS identifier
        self.setFixedSize(350, 300)
        self.setCursor(Qt.PointingHandCursor) # Mouse cursor style

        # Container for icon + text
        container = QWidget(self)
        container.setGeometry(0, 0, 350, 300)

        layout = QVBoxLayout(container) # Vertical layout
        layout.setContentsMargins(50, 50, 50, 30) # Padding
        layout.setSpacing(10)

        # Icon setup
        icon_label = QLabel()
        icon_label.setObjectName("iconLabel")
        icon_pixmap = QPixmap(icon_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation) # Load/resize image
        icon_label.setPixmap(icon_pixmap) # Display icon
        icon_label.setAlignment(Qt.AlignCenter)

        text_label = QLabel(text)
        text_label.setObjectName("textLabel")
        text_label.setWordWrap(True)  # breaking long lines of text into multiple lines
        text_label.setAlignment(Qt.AlignCenter) 

        # Widget: Any visual element (buttons, labels, layouts, etc.)
        # Add widget insert all the visual element to the layout
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        
class RoomBookingWidget(QWidget):
    def __init__(self, main_window, location_id):
        super().__init__()
        self.main_window = main_window
        self.location_id = location_id
        self.location_name = self.get_location_name(location_id)
        self.current_user_id = "1001"  # Would normally come from login
        
        # Apply styles
        self.setStyleSheet(get_booking_styles())
        
        # Main layout and stacked widget for different views
        self.main_layout = QVBoxLayout(self)
        self.pages = QStackedWidget()
        self.main_layout.addWidget(self.pages)
        
        # Create all pages
        self.create_feature_grid_page()
        self.create_new_booking_page()
        self.create_my_bookings_page()
        
        # Show feature grid by default
        self.pages.setCurrentWidget(self.feature_grid_page)
        
        # Back button (shown on all pages)
        self.setup_back_button()

    def create_feature_grid_page(self):
        """Create the main feature selection grid"""
        self.feature_grid_page = QWidget()
        layout = QVBoxLayout(self.feature_grid_page)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        title = QLabel(f"Room Booking: {self.location_name}")
        title.setContentsMargins(10, 0, 0, 10)
        title.setObjectName("bookingHeader")
        layout.addWidget(title)

        # Feature grid
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setVerticalSpacing(35)

        features = [
            ("Photo/history.png", "My Bookings", self.show_my_bookings),
            ("Photo/room_icon.png", "New Booking", self.show_new_booking),
            ("Photo/timetable.png", "Timetable", self.show_timetable),
            ("Photo/user-guide.png", "Guidelines", self.show_guidelines),
        ]

        for i, (icon, text, handler) in enumerate(features):
            btn = FeatureButton(icon, text)
            btn.clicked.connect(handler)
            grid_layout.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid_layout)
        layout.addStretch()
        self.pages.addWidget(self.feature_grid_page)

    def create_new_booking_page(self):
        """Create the new booking form page"""
        self.new_booking_page = QWidget()
        layout = QVBoxLayout(self.new_booking_page)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        title = QLabel(f"New Booking: {self.location_name}")
        title.setObjectName("bookingHeader")
        layout.addWidget(title)

        # Booking form widgets
        self.setup_booking_form(layout)
        self.pages.addWidget(self.new_booking_page)

    def setup_booking_form(self, layout):
        """Setup the actual booking form components"""
        # Date selection
        date_label = QLabel("Booking Date:")
        date_label.setObjectName("formLabel")
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        layout.addWidget(date_label)
        layout.addWidget(self.date_edit)

        # Time selection
        time_layout = QHBoxLayout()
        
        start_label = QLabel("Start Time:")
        start_label.setObjectName("formLabel")
        self.start_time = QTimeEdit()
        self.start_time.setDisplayFormat("HH:mm")
        self.start_time.setTime(QTime(9, 0))
        
        end_label = QLabel("End Time:")
        end_label.setObjectName("formLabel")
        self.end_time = QTimeEdit()
        self.end_time.setDisplayFormat("HH:mm")
        self.end_time.setTime(QTime(11, 0))  # Default 2 hour duration
        
        time_layout.addWidget(start_label)
        time_layout.addWidget(self.start_time)
        time_layout.addWidget(end_label)
        time_layout.addWidget(self.end_time)
        layout.addLayout(time_layout)

        # Room selection
        room_label = QLabel("Select Room:")
        room_label.setObjectName("formLabel")
        self.room_combo = QComboBox()
        self.load_rooms()
        layout.addWidget(room_label)
        layout.addWidget(self.room_combo)

        # Student IDs
        student_label = QLabel("Student IDs (comma separated):")
        student_label.setObjectName("formLabel")
        self.student_input = QLineEdit()
        layout.addWidget(student_label)
        layout.addWidget(self.student_input)

        # Submit button
        submit_btn = QPushButton("Submit Booking")
        submit_btn.setObjectName("submitButton")
        submit_btn.clicked.connect(self.submit_booking)
        layout.addWidget(submit_btn, 0, Qt.AlignCenter)

    def create_my_bookings_page(self):
        """Page showing user's existing bookings"""
        self.my_bookings_page = QWidget()
        layout = QVBoxLayout(self.my_bookings_page)
        
        title = QLabel("My Bookings")
        title.setObjectName("bookingHeader")
        layout.addWidget(title)
        
        # TODO: Add actual bookings list
        layout.addWidget(QLabel("Your bookings will appear here"))
        self.pages.addWidget(self.my_bookings_page)

    def setup_back_button(self):
        """Back button shown on all pages"""
        self.back_btn = QPushButton()
        self.back_btn.setIcon(QIcon("Photo/back.png"))
        self.back_btn.setText(" Back")
        self.back_btn.setFixedSize(750, 40)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setObjectName("iconBackButton")
        self.back_btn.setIconSize(QSize(16, 16))
        self.back_btn.clicked.connect(self.handle_back)
        self.main_layout.addWidget(self.back_btn, 0, Qt.AlignCenter)

    def handle_back(self):
        """Handle back button navigation"""
        if self.pages.currentWidget() != self.feature_grid_page:
            self.pages.setCurrentWidget(self.feature_grid_page)
        else:
            self.main_window.pages.setCurrentWidget(self.main_window.location_selection_page)

    # Feature navigation methods
    def show_new_booking(self):
        self.load_rooms()  # Refresh room list
        self.pages.setCurrentWidget(self.new_booking_page)

    def show_my_bookings(self):
        self.pages.setCurrentWidget(self.my_bookings_page)

    def show_timetable(self):
        QMessageBox.information(self, "Coming Soon", "Timetable view will be implemented in the next version")

    def show_guidelines(self):
        guidelines = """
        Booking Guidelines:
        1. Maximum booking duration: 2 hours
        2. Bookings can be made up to 2 weeks in advance
        3. Please cancel unused bookings
        4. Maximum 3 active bookings per user
        """
        QMessageBox.information(self, "Booking Guidelines", guidelines)

    # Booking functionality methods
    def load_rooms(self):
        """Load available rooms for current location"""
        self.room_combo.clear()
        try:
            conn = sqlite3.connect("database/student_app.db")
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.id, r.name, r.capacity 
                FROM rooms r 
                WHERE r.location_id = ?
                ORDER BY r.name
            ''', (self.location_id,))
            
            for room_id, room_name, capacity in cursor.fetchall():
                self.room_combo.addItem(f"{room_name} (Capacity: {capacity})", room_id)
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Could not load rooms: {str(e)}")
        finally:
            conn.close()

    def validate_booking(self):
        """Validate booking details before submission"""
        # Check duration is exactly 2 hours
        start = self.start_time.time()
        end = self.end_time.time()
        duration = QTime(0, 0).secsTo(end) - QTime(0, 0).secsTo(start)
        if duration != 7200:
            QMessageBox.warning(self, "Invalid Duration", 
                              "Booking duration must be exactly 2 hours.")
            return False
        
        # Check room availability
        date = self.date_edit.date().toString("yyyy-MM-dd")
        start_str = start.toString("HH:mm")
        end_str = end.toString("HH:mm")
        room_id = self.room_combo.currentData()
        
        try:
            conn = sqlite3.connect("database/student_app.db")
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM bookings 
                WHERE room_id = ? AND date = ? 
                AND ((start_time < ? AND end_time > ?) OR 
                    (start_time >= ? AND start_time < ?))
            ''', (room_id, date, end_str, start_str, start_str, end_str))
            
            if cursor.fetchone():
                QMessageBox.warning(self, "Room Unavailable", 
                                  "This room is already booked during the selected time.")
                return False
            return True
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Database error: {str(e)}")
            return False
        finally:
            conn.close()

    def submit_booking(self):
        """Handle booking submission"""
        if not self.validate_booking():
            return
            
        date = self.date_edit.date().toString("yyyy-MM-dd")
        start = self.start_time.time().toString("HH:mm")
        end = self.end_time.time().toString("HH:mm")
        room_id = self.room_combo.currentData()
        student_ids = [s.strip() for s in self.student_input.text().split(",") if s.strip()]
        
        try:
            conn = sqlite3.connect("database/student_app.db")
            cursor = conn.cursor()
            
            # Create booking
            cursor.execute('''
                INSERT INTO bookings (user_id, room_id, date, start_time, end_time) 
                VALUES (?, ?, ?, ?, ?)
            ''', (self.current_user_id, room_id, date, start, end))
            
            booking_id = cursor.lastrowid
            
            # Add students
            for student_id in student_ids:
                cursor.execute('''
                    INSERT INTO booking_students (booking_id, student_id, student_name) 
                    VALUES (?, ?, ?)
                ''', (booking_id, student_id, f"Student {student_id}"))
            
            conn.commit()
            QMessageBox.information(self, "Success", "Booking created successfully!")
            self.pages.setCurrentWidget(self.feature_grid_page)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
        finally:
            conn.close()

    def get_location_name(self, location_id):
        """Get location name from database"""
        try:
            conn = sqlite3.connect("database/student_app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM locations WHERE id=?", (location_id,))
            result = cursor.fetchone()
            return result[0] if result else f"Location {location_id}"
        except sqlite3.Error:
            return f"Location {location_id}"
        finally:
            conn.close()