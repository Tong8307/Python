import sys
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QMessageBox, QGridLayout, QStackedWidget
)
from PyQt5.QtGui import QPixmap, QFont, QPainter, QBrush
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QEvent

from styles.styles import *
from login import LoginWidget 
from database.db_manager import get_connection

# Update these imports to match the new file structure
from room_booking_function.location_selection import LocationSelectionWidget
from room_booking_function.room_booking_widget import RoomBookingWidget
from room_booking_function.feature_button import FeatureButton
from room_booking_function.guidelines import GuidelinesPage
from room_booking_function.all_booking import AllBookingsPage

# Academic feature
from gpa_calculator_function.gpa_calculator_widget import GPACalculatorWidget

# Notes features
from notes_organizer_function.dashboard import DashboardWidget
from notes_organizer_function.notes_organizer import NoteOrganizerWidget

class SlidingMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("slidingMenu")
        self.setFixedWidth(350)
        self.is_logged_in = False
        self.current_user_id = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 40, 0, 0)
        layout.setSpacing(0)

        profile_widget = QWidget()
        profile_widget.setObjectName("profileWidget")
        profile_layout = QVBoxLayout(profile_widget)
        profile_layout.setContentsMargins(0, 70, 0, 70)

        self.avatar = QLabel()
        self.avatar.setObjectName("avatarLabel")
        self.avatar.setFixedSize(150, 150)
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setCursor(Qt.PointingHandCursor)

        # Create default avatar
        self.default_avatar = QPixmap(150, 150)
        self.default_avatar.fill(Qt.transparent)
        painter = QPainter(self.default_avatar)
        painter.setBrush(QBrush(Qt.gray))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 150, 150)
        painter.setFont(QFont("Arial", 40))
        painter.setPen(Qt.white)
        painter.drawText(self.default_avatar.rect(), Qt.AlignCenter, "👤")
        painter.end()
        self.avatar.setPixmap(self.default_avatar)

        self.name_label = QLabel("Please Login")
        self.name_label.setObjectName("profileName")
        self.id_label = QLabel("ID: Not logged in")
        self.id_label.setObjectName("profileID")

        profile_layout.addWidget(self.avatar, 0, Qt.AlignCenter)
        profile_layout.addWidget(self.name_label, 0, Qt.AlignCenter)
        profile_layout.addWidget(self.id_label, 0, Qt.AlignCenter)
        layout.addWidget(profile_widget)

        menu_items = [
            ("Home", "home"),
            ("Notes", "notes"),
            ("Booking Guidelines", "Booking Guidelines"),
            ("My Bookings (All Locations)", "all_bookings"),
            ("Logout", "logout")
        ]

        for text, action in menu_items:
            btn = QPushButton(text)
            btn.setObjectName("menuOptions")
            btn.setCursor(Qt.PointingHandCursor)
            
            if action == "logout":
                btn.clicked.connect(self.show_logout_dialog)
            elif action == "home":
                btn.clicked.connect(self.go_to_home)
            elif action == "Booking Guidelines":
                btn.clicked.connect(self.show_guidelines)
            elif action == "all_bookings": 
                btn.clicked.connect(self.show_all_bookings)
            elif action == "notes":
                # Directly connect to the notes opening method
                btn.clicked.connect(self.open_notes_from_menu)
            else:
                btn.clicked.connect(lambda checked, a=action: self.handle_menu_action(a))
            layout.addWidget(btn)

    def open_notes_from_menu(self):
        """Open notes directly from menu"""
        if not self.is_logged_in:
            QMessageBox.warning(self, "Login Required", 
                            "Please login first to access notes.")
            return
        
        main_window = self.parent()
        if isinstance(main_window, MainWindow):
            # Use the existing open_notes_page method
            main_window.open_notes_page()
            main_window.hide_menu()  # Hide menu after selection

    def handle_menu_action(self, action):
        """Handle menu actions that require login"""
        if not self.is_logged_in:
            QMessageBox.warning(self, "Login Required", 
                               "Please login first to access this feature.")
            return
        print(f"Menu action: {action}")

    def show_logout_dialog(self):
        if not self.is_logged_in:
            QMessageBox.information(self, "Already Logged Out", 
                                   "You are already logged out. Please login first.")
            return
            
        reply = QMessageBox.question(self, "Logout",
                                     "Are you sure you want to log out?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.parent().logout()

    def go_to_home(self):
        if not self.is_logged_in:
            QMessageBox.warning(self, "Login Required", 
                               "Please login first to access the home page.")
            return
            
        main_window = self.parent()
        if isinstance(main_window, MainWindow):
            main_window.pages.setCurrentWidget(main_window.feature_grid_page)
            main_window.hide_menu()

    def load_profile_picture(self, profile_picture_filename):
        """Load profile picture from Photo directory based on filename from database"""
        if profile_picture_filename:
            image_path = f"Photo/{profile_picture_filename}"
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Create circular avatar
                    circular = QPixmap(150, 150)
                    circular.fill(Qt.transparent)
                    painter = QPainter(circular)
                    painter.setRenderHint(QPainter.Antialiasing)
                    painter.setBrush(QBrush(pixmap.scaled(150, 150, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(0, 0, 150, 150)
                    painter.end()
                    self.avatar.setPixmap(circular)
                    return
        
        # If no image found, use default avatar
        self.avatar.setPixmap(self.default_avatar)

    def update_profile_info(self, name, student_id):
        """Update profile information with user data"""
        self.name_label.setText(name)
        self.id_label.setText(f"ID: {student_id}")
        self.is_logged_in = True
        self.current_user_id = student_id
        
        # Load profile picture from database filename
        from database.db_manager import get_profile_picture
        profile_picture_filename = get_profile_picture(student_id)
        self.load_profile_picture(profile_picture_filename)

    def show_guidelines(self):
        """Navigate to guidelines page through main window"""
        if not self.is_logged_in:
            QMessageBox.warning(self, "Login Required", 
                            "Please login first to access the guidelines.")
            return
            
        main_window = self.parent()
        if isinstance(main_window, MainWindow):
            main_window.show_guidelines()

    def show_all_bookings(self):
        """Show all bookings across all locations"""
        if not self.is_logged_in:
            QMessageBox.warning(self, "Login Required", 
                            "Please login first to view your bookings.")
            return
            
        main_window = self.parent()
        if isinstance(main_window, MainWindow):
            main_window.hide_menu()
            main_window.pages.setCurrentWidget(main_window.all_bookings_page)
            # Refresh the bookings when shown
            main_window.all_bookings_page.load_bookings()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize database tables
        self.initialize_database()
        
        self.user_id = None
        self.user_name = None
        
        self.setWindowTitle("TARUMT Student Assistant App")
        self.setFixedSize(800, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Creates a header bar 
        header = QWidget()
        header.setObjectName("headerWidget")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)

        self.menu_btn = QPushButton("☰")
        self.menu_btn.setObjectName("menuButton")
        self.menu_btn.setStyleSheet(get_menu_button_style())
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.clicked.connect(self.toggle_menu)
        self.menu_btn.setVisible(False)  # Hide menu button initially

        title = QLabel("TARUMT Student Assistant App")
        title.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(self.menu_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addWidget(header)

        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)

        # Create login page first
        self.login_page = LoginWidget(self)
        self.login_page.login_successful.connect(self.handle_login_success)
        self.pages.addWidget(self.login_page)

        # Initialize main app pages (will be created after login)
        self.feature_grid_page = None
        self.location_selection_page = None
        self.gpa_calculator_widget = None
        
        # Initialize sliding menu (but keep it hidden until login)
        self.sliding_menu = SlidingMenu(self)
        self.sliding_menu.move(-self.sliding_menu.width(), 60)
        self.sliding_menu.setFixedHeight(self.height() - 60)
        self.menu_shown = False

        # Install event filter on the main window
        self.installEventFilter(self)
        
        # Also install event filter on all pages to capture clicks
        self.pages.installEventFilter(self)

        # Create a transparent overlay that covers the entire window
        self.overlay = QWidget(self)
        self.overlay.setObjectName("menuOverlay")
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 30);")  # Semi-transparent
        self.overlay.hide()
        self.overlay.installEventFilter(self)

        self.guidelines_page = GuidelinesPage(self)
        self.pages.addWidget(self.guidelines_page)

        self.all_bookings_page = AllBookingsPage(self)
        self.pages.addWidget(self.all_bookings_page)

    def initialize_database(self):
        """Initialize database tables if they don't exist"""
        try:
            # Just check if database is accessible
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            conn.close()
            
            if table_count == 0:
                print("Database appears empty. Please run init_db.py first!")
                QMessageBox.warning(self, "Database Error", 
                                  "Database is empty. Please run init_db.py to initialize the database.")
        except Exception as e:
            print(f"Database initialization error: {e}")
            QMessageBox.critical(self, "Database Error", 
                               f"Could not initialize database: {str(e)}")

    def handle_login_success(self, student_id, name):
        """Handle successful login"""
        self.user_id = student_id
        self.user_name = name
        
        # Initialize main app pages
        self.initialize_main_app()
        
        # Update profile info in sliding menu
        self.sliding_menu.update_profile_info(name, student_id)
        
        # Show menu button
        self.menu_btn.setVisible(True)
        
        # Switch to main app
        self.pages.setCurrentWidget(self.feature_grid_page)

    def initialize_main_app(self):
        """Initialize main application pages after login"""
        if self.feature_grid_page is None:
            self.feature_grid_page = self.create_feature_grid()
            self.pages.addWidget(self.feature_grid_page)
            
        if self.location_selection_page is None:
            self.location_selection_page = LocationSelectionWidget(self)
            self.pages.addWidget(self.location_selection_page)
        
        if self.gpa_calculator_widget is None:
            self.gpa_calculator_widget = GPACalculatorWidget(self, self.user_id)
            self.pages.addWidget(self.gpa_calculator_widget)

    def create_feature_grid(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(30)
        grid_layout.setVerticalSpacing(30)

        features = [
            ("Photo/note_icon.png", "Note Organizer"),
            ("Photo/discussion.png", "Room Booking"),
            ("Photo/academic.png", "Academic Tools"),
            ("Photo/QA_icon.png", "Q & A sessions"),
        ]

        for i, (icon, text) in enumerate(features):
            # Use "main" size type for main page
            btn = FeatureButton(icon, text, size_type="main")
            btn.clicked.connect(lambda checked, t=text: self.handle_feature_click(t))
            row = i // 2
            col = i % 2
            grid_layout.addWidget(btn, row, col)

        layout.addLayout(grid_layout)
        layout.addStretch()
        return page

    def handle_feature_click(self, feature_name):
        if feature_name == "Room Booking":
            self.pages.setCurrentWidget(self.location_selection_page)
        elif feature_name == "Academic Tools":
            self.pages.setCurrentWidget(self.gpa_calculator_widget)
        elif feature_name == "Note Organizer":
            # ALWAYS create a new dashboard with the current user_id
            # Remove old dashboard if it exists
            if hasattr(self, 'dashboard'):
                try:
                    if self.pages.indexOf(self.dashboard) != -1:
                        self.pages.removeWidget(self.dashboard)
                    self.dashboard.deleteLater()
                except Exception as e:
                    print(f"Error removing old dashboard: {e}")
                delattr(self, 'dashboard')
            
            # Create new dashboard with current user_id and proper back callback
            self.dashboard = DashboardWidget(
                user_id=self.user_id,  # Use current user ID
                on_add_note_clicked=self.open_notes_page,
                on_back_clicked=self.back_to_main_from_dashboard  # Add this callback
            )
            self.pages.addWidget(self.dashboard)
            self.pages.setCurrentWidget(self.dashboard)
        else:
            self.show_qna()

    def open_notes_page(self, note_id=None):
        if not hasattr(self, 'notes_page'):
            # Pass user_id to the notes organizer
            self.notes_page = NoteOrganizerWidget(
                on_return_callback=self.back_to_dashboard, 
                user_id=self.user_id  # This is correct
            )
            self.pages.addWidget(self.notes_page)
        
        self.pages.setCurrentWidget(self.notes_page)
        
        # If a specific note ID is provided, try to open it
        if note_id is not None:
            try:
                # Use the public method instead of private method
                self.notes_page._open_by_id(note_id)
            except Exception as e:
                QMessageBox.warning(self, "Open Note", f"Could not open the selected note.\n{str(e)}")

    def back_to_main_from_dashboard(self):
        """Callback for dashboard back button - returns to main feature grid"""
        self.pages.setCurrentWidget(self.feature_grid_page)
        
    def back_to_dashboard(self):
        """Callback for notes organizer - returns to dashboard"""
        # Make sure we have a current dashboard
        if not hasattr(self, 'dashboard'):
            self.dashboard = DashboardWidget(
                user_id=self.user_id,
                on_add_note_clicked=self.open_notes_page,
                on_back_clicked=self.back_to_main_from_dashboard  # Add this callback
            )
            self.pages.addWidget(self.dashboard)
        
        self.pages.setCurrentWidget(self.dashboard)
        
        # Refresh the dashboard to show current user's data
        try:
            self.dashboard._refresh_folders()
            self.dashboard._refilter_notes()
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")


    def show_qna(self):
        QMessageBox.information(
            self,
            "Coming Soon",
            "✨ This feature is not available yet.\n\n"
            "The Q & A sessions module is still under development and "
            "will be added in a future update.\n\n"
            "Stay tuned for more exciting features!"
        )
        
    def toggle_menu(self):
        # Don't show menu if not logged in
        if not self.user_id:
            QMessageBox.information(self, "Login Required", 
                                   "Please login first to access the menu.")
            return
            
        if self.menu_shown:
            self.hide_menu()
        else:
            self.show_menu()

    def show_menu(self):
        self.anim = QPropertyAnimation(self.sliding_menu, b"pos")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.setStartValue(self.sliding_menu.pos())
        self.anim.setEndValue(QPoint(0, 60))
        self.anim.start()
        self.menu_shown = True
        
        # Show the overlay
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.overlay.show()
        self.overlay.raise_()
        self.sliding_menu.raise_()

    def hide_menu(self):
        self.anim = QPropertyAnimation(self.sliding_menu, b"pos")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.setStartValue(self.sliding_menu.pos())
        self.anim.setEndValue(QPoint(-self.sliding_menu.width(), 60))
        self.anim.start()
        self.menu_shown = False
        
        # Hide the overlay
        self.overlay.hide()

    def eventFilter(self, obj, event):
        if self.menu_shown and event.type() == QEvent.MouseButtonPress:
            # Get the global mouse position
            mouse_pos = event.globalPos()
            
            # Get the menu's geometry in global coordinates
            menu_global_rect = self.sliding_menu.frameGeometry()
            menu_global_rect.moveTopLeft(self.sliding_menu.mapToGlobal(QPoint(0, 0)))
            
            # Check if the click is outside the menu
            if not menu_global_rect.contains(mouse_pos):
                self.hide_menu()
                return True
        
        return super().eventFilter(obj, event)
    
    def show_guidelines(self):
        """Show guidelines page from main window"""
        self.pages.setCurrentWidget(self.guidelines_page)
        self.hide_menu()  # Hide the sliding menu
            
    def open_room_booking_page(self, location_id):
        # Clean up previous booking widget if exists
        if hasattr(self, 'room_booking_widget_by_location'):
            self.pages.removeWidget(self.room_booking_widget_by_location)
            self.room_booking_widget_by_location.deleteLater()

        # Create and show new booking page with user_id
        self.room_booking_widget_by_location = RoomBookingWidget(self, location_id, self.user_id)
        self.pages.addWidget(self.room_booking_widget_by_location)
        self.pages.setCurrentWidget(self.room_booking_widget_by_location)

    def logout(self):
        # Reset user info
        self.user_id = None
        self.user_name = None
        
        # Reset profile info
        self.sliding_menu.name_label.setText("Please Login")
        self.sliding_menu.id_label.setText("ID: Not logged in")
        self.sliding_menu.is_logged_in = False
        self.sliding_menu.current_user_id = None
        self.sliding_menu.avatar.setPixmap(self.sliding_menu.default_avatar)
        
        # Hide menu button when logged out
        self.menu_btn.setVisible(False)
        
        # Clear main app pages SAFELY - ADD DASHBOARD TO THE LIST
        widgets_to_remove = [
            self.feature_grid_page,
            self.location_selection_page,
            self.gpa_calculator_widget
        ]
        
        # Add dashboard if it exists
        if hasattr(self, 'dashboard'):
            widgets_to_remove.append(self.dashboard)
            delattr(self, 'dashboard')
        
        # Add notes page if it exists
        if hasattr(self, 'notes_page'):
            widgets_to_remove.append(self.notes_page)
            delattr(self, 'notes_page')
        
        for widget in widgets_to_remove:
            if widget is not None:
                try:
                    if self.pages.indexOf(widget) != -1:
                        self.pages.removeWidget(widget)
                    widget.deleteLater()
                except Exception as e:
                    print(f"Error removing widget: {e}")
        
        # Reset references
        self.feature_grid_page = None
        self.location_selection_page = None
        self.gpa_calculator_widget = None
        
        # Hide menu
        self.hide_menu()
        
        # Show login page
        self.pages.setCurrentWidget(self.login_page)
        self.login_page.clear_form()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())