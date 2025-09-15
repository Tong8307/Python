from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import sqlite3
from styles.booking_styles import get_booking_styles
from database.db_manager import get_locations

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
        title.setObjectName("bookingHeader")
        main_layout.addWidget(title)

        #Label to inform user select location
        subtitle = QLabel("Please select a location: ")
        subtitle.setObjectName("bookingSubheader")
        main_layout.addWidget(subtitle)
        
        # Add a styled divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setObjectName("divider")
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
            return get_locations()
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
    
    #Redirect to the booking widget
    def go_to_booking(self, location_id):
        try:
            self.main_window.open_room_booking_page(location_id)
        except Exception as e:
            print(f"Navigation error: {e}") 
    
    #Go back to the home
    def go_back(self):
        self.main_window.pages.setCurrentWidget(self.main_window.feature_grid_page)