from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                            QPushButton, QFrame, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt
from database.db_manager import get_bookings_by_user_all_locations, update_booking_status, update_expired_bookings, get_students_in_booking

class AllBookingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # Keep reference to main window
        
        layout = QVBoxLayout(self)
            
        title = QLabel("My Bookings - All Locations")
        title.setObjectName("bookingHeader")
        layout.addWidget(title)
        
        # Create scroll area for bookings list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # Hide both horizontal and vertical scroll bars
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Alternatively, you can make them always invisible
        self.scroll_area.horizontalScrollBar().setVisible(False)
        self.scroll_area.verticalScrollBar().setVisible(False)
        self.scroll_area.setObjectName("scroll")
            
        # Container for bookings
        self.bookings_container = QWidget()
        self.bookings_layout = QVBoxLayout(self.bookings_container)
        self.bookings_layout.setSpacing(15)
        self.bookings_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll_area.setWidget(self.bookings_container)
        layout.addWidget(self.scroll_area)
    
    def load_bookings(self):
        """Load and display user's bookings from ALL locations"""
        # Get current user ID from main window
        current_user_id = self.main_window.user_id
        
        if not current_user_id:
            print("Error: No user ID available. Please login first.")
            return
            
        print(f"Loading bookings for user: {current_user_id}")
        
        # First, update expired bookings to 'completed' status
        updated_count = update_expired_bookings()
        if updated_count > 0:
            print(f"Updated {updated_count} expired bookings to 'completed' status")
        
        # Clear existing bookings
        for i in reversed(range(self.bookings_layout.count())): 
            widget = self.bookings_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Get bookings from database WITHOUT location filter
        bookings = get_bookings_by_user_all_locations(current_user_id)
        print(f"Found {len(bookings)} bookings")
        
        if not bookings:
            no_bookings_label = QLabel("You don't have any bookings yet.")
            no_bookings_label.setAlignment(Qt.AlignCenter)
            no_bookings_label.setStyleSheet("font-size: 16px; color: #666; padding: 50px;")
            self.bookings_layout.addWidget(no_bookings_label)
            return
        
        for booking in bookings:
            booking_id, room_name, location_name, date, start_time, end_time, status = booking
            
            # Get all students in this booking
            students = get_students_in_booking(booking_id)
            
            # Create booking card
            booking_card = QFrame()
            booking_card.setObjectName("bookingCard")
            booking_card.setStyleSheet("""
                QFrame#bookingCard {
                    background: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 15px;
                }
                QLabel {
                    font-size: 14px;
                    color: #333333;
                }
                QLabel#statusBooked {
                    color: #28a745;
                    font-weight: bold;
                }
                QLabel#statusCancelled {
                    color: #dc3545;
                    font-weight: bold;
                }
                QLabel#statusCompleted {
                    color: #6c757d;
                    font-weight: bold;
                }
            """)
            
            card_layout = QVBoxLayout(booking_card)
            
            # Booking details - top section
            details_layout = QHBoxLayout()
            
            # Left side - room, location, date, time info
            info_layout = QVBoxLayout()
            
            room_label = QLabel(f"Room: {room_name}")
            room_label.setStyleSheet("font-weight: bold; font-size: 16px;")
            
            location_label = QLabel(f"Location: {location_name}")
            location_label.setStyleSheet("font-size: 14px; color: #555;")
            
            date_label = QLabel(f"Date: {date}")
            time_label = QLabel(f"Time: {start_time} - {end_time}")
            
            status_label = QLabel(f"Status: {status.capitalize()}")
            if status == "booked":
                status_label.setObjectName("statusBooked")
            elif status == "cancelled":
                status_label.setObjectName("statusCancelled")
            else:  # completed
                status_label.setObjectName("statusCompleted")
            
            info_layout.addWidget(room_label)
            info_layout.addWidget(location_label)
            info_layout.addWidget(date_label)
            info_layout.addWidget(time_label)
            info_layout.addWidget(status_label)
            
            # Right side - cancel button (only for booked status AND if user is the creator)
            button_layout = QVBoxLayout()
            button_layout.setAlignment(Qt.AlignCenter)
            
            # Check if user is the creator of this booking (only creators can cancel)
            is_creator = self.is_booking_creator(booking_id, current_user_id)
            
            if status == "booked" and is_creator:
                cancel_btn = QPushButton("Cancel Booking")
                cancel_btn.setObjectName("cancelButton")
                cancel_btn.setStyleSheet("""
                    QPushButton#cancelButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: bold;
                        min-width: 100px;
                    }
                    QPushButton#cancelButton:hover {
                        background-color: #c82333;
                    }
                    QPushButton#cancelButton:pressed {
                        background-color: #bd2130;
                    }
                """)
                cancel_btn.clicked.connect(lambda checked, bid=booking_id: self.cancel_booking(bid))
                button_layout.addWidget(cancel_btn)
            elif status == "booked":
                # User is participant but not creator - show info text
                participant_label = QLabel("(Participant)")
                participant_label.setStyleSheet("color: #6c757d; font-style: italic;")
                button_layout.addWidget(participant_label)
            
            details_layout.addLayout(info_layout, 3)
            details_layout.addLayout(button_layout, 1)
            
            card_layout.addLayout(details_layout)
            
            # Students section - bottom section (show all students)
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            separator.setStyleSheet("background-color: #e0e0e0; margin: 8px 0;")
            card_layout.addWidget(separator)
            
            students_label = QLabel("Students in this booking:")
            students_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #555;")
            card_layout.addWidget(students_label)
            
            # List all students
            for student_id, student_name in students:
                # Highlight current user
                if student_id == current_user_id:
                    student_info = QLabel(f"• {student_name} ({student_id}) - You")
                    student_info.setStyleSheet("font-size: 13px; color: #283593; font-weight: bold; margin-left: 10px;")
                else:
                    student_info = QLabel(f"• {student_name} ({student_id})")
                    student_info.setStyleSheet("font-size: 13px; color: #666; margin-left: 10px;")
                card_layout.addWidget(student_info)
            
            self.bookings_layout.addWidget(booking_card)
        
        self.bookings_layout.addStretch()

    def is_booking_creator(self, booking_id, user_id):
        """Check if the current user is the creator of this booking"""
        from database.db_manager import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT created_by FROM bookings WHERE id = ?", (booking_id,))
        result = cursor.fetchone()
        conn.close()
        return result and result[0] == user_id
    
    def cancel_booking(self, booking_id):
        """Cancel a booking (only available to creator)"""
        reply = QMessageBox.question(
            self, 
            "Confirm Cancellation", 
            "Are you sure you want to cancel this booking?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                update_booking_status(booking_id, "cancelled")
                QMessageBox.information(self, "Success", "Booking cancelled successfully!")
                self.load_bookings()  # Reload to reflect changes
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to cancel booking: {str(e)}")

    def showEvent(self, event):
        """Reload bookings when the page is shown"""
        super().showEvent(event)
        self.load_bookings()