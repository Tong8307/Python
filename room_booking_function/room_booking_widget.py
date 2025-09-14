from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QPushButton,
                            QStackedWidget, QLabel)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from styles.booking_styles import get_booking_styles
from database.db_manager import get_location_name
from .feature_button import FeatureButton
from .new_booking import NewBookingPage
from .my_bookings import MyBookingsPage
from .timetable import TimetablePage
from .guidelines import GuidelinesPage
from .studentInfo import StudentInfoPage

class RoomBookingWidget(QWidget):
    def __init__(self, main_window, location_id, user_id):
        super().__init__()
        self.main_window = main_window
        self.location_id = location_id

        #Which location is being booked from previous section
        self.location_name = self.get_location_name(location_id)

        #the student who logged in
        self.current_user_id = user_id
        
        # Apply styles
        self.setStyleSheet(get_booking_styles())
        
        # Main layout and stacked widget for different views
        self.main_layout = QVBoxLayout(self)
        self.pages = QStackedWidget()
        self.main_layout.addWidget(self.pages)
        
        # Create all pages
        self.create_feature_grid_page()
        self.create_pages()
        
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
            # Use "booking" size type for booking page
            btn = FeatureButton(icon, text, size_type="booking")
            btn.clicked.connect(handler)
            grid_layout.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid_layout)
        layout.addStretch()
        self.pages.addWidget(self.feature_grid_page)

    def create_pages(self):
        """Create all the feature pages"""
        # Pass self (RoomBookingWidget) instead of self.main_window
        self.new_booking_page = NewBookingPage(self, self.location_id, self.location_name, self.current_user_id)
        self.my_bookings_page = MyBookingsPage(self)
        self.timetable_page = TimetablePage(self)
        self.guidelines_page = GuidelinesPage(self)
        
        self.pages.addWidget(self.new_booking_page)
        self.pages.addWidget(self.my_bookings_page)
        self.pages.addWidget(self.timetable_page)
        self.pages.addWidget(self.guidelines_page)

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
        self.pages.setCurrentWidget(self.new_booking_page)

    def show_my_bookings(self):
        self.pages.setCurrentWidget(self.my_bookings_page)

    def show_timetable(self):
        self.pages.setCurrentWidget(self.timetable_page)
        self.timetable_page.show_timetable()

    def show_guidelines(self):
        self.pages.setCurrentWidget(self.guidelines_page)
        self.guidelines_page.show_guidelines()
        
    def show_feature_grid(self):
        """Public method to show the feature grid page"""
        self.pages.setCurrentWidget(self.feature_grid_page)

    def get_location_name(self, location_id):
        """Get location name from database using db_manager"""
        try:
            return get_location_name(location_id)
        except Exception:
            return f"Location {location_id}"
        
    def show_student_info_page(self, student_inputs):
        """Show student info page when requested from booking page"""
        # Create student info page if it doesn't exist
        self.student_info_page = StudentInfoPage(self, student_inputs)
        
        # Add to stacked widget if not already added
        if self.pages.indexOf(self.student_info_page) == -1:
            self.pages.addWidget(self.student_info_page)
        
        # Show the student info page
        self.pages.setCurrentWidget(self.student_info_page)