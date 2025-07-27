from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from styles.booking_styles import get_booking_styles
import sqlite3

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from pathlib import Path
import sqlite3
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
        back_btn = QPushButton("← Back to Home")
        back_btn.setObjectName("backButton")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFixedSize(180, 40)  # Optimal size for back button
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn, 0, Qt.AlignCenter)
        
    def load_locations(self):
        """Load locations from database with error handling"""
        try:
            db_path = Path(__file__).parent.parent / "database" / "student_app.db"
            conn = sqlite3.connect(str(db_path))
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
        btn.setObjectName("bookButton")  # Reuses the book button style from booking_styles
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

class RoomBookingWidget(QWidget):
    def __init__(self, main_window, location_id):
        super().__init__()
        self.main_window = main_window
        self.location_id = location_id
        self.location_name = self.get_location_name(location_id)  # Get name from DB

        layout = QVBoxLayout(self)

        # Show location name instead of ID
        title = QLabel(f"🗓️ Book a Room at {self.location_name}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # Add room booking UI components here
        self.setup_room_booking_ui(layout)

        back_btn = QPushButton("← Back to Locations")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)

    def get_location_name(self, location_id):
        """Fetch location name from database"""
        conn = sqlite3.connect("database/student_app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM locations WHERE id=?", (location_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else f"Location {location_id}"

    def setup_room_booking_ui(self, layout):
        """Setup room selection and booking components"""
        # Add your room booking interface here
        # Example:
        rooms_label = QLabel("Available Rooms:")
        layout.addWidget(rooms_label)
        
        # Add room list, booking form, etc.

    def go_back(self):
        self.main_window.pages.setCurrentWidget(self.main_window.location_selection_page)