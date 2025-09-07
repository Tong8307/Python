from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QDateEdit, QTimeEdit, QComboBox, QMessageBox, 
                            QLineEdit, QSpinBox, QPushButton, QScrollArea,
                            QFrame, QSizePolicy, QCheckBox)
from PyQt5.QtCore import Qt, QDate, QTime, QTimer
from PyQt5.QtGui import QFont
import sqlite3
from database.db_manager import (get_features, find_best_available_room, 
                                check_student_exists, create_booking_with_students,
                                get_student_name)
from styles.booking_styles import get_booking_styles

class NewBookingPage(QWidget):
    def __init__(self, main_window, location_id, location_name, user_id):
        super().__init__()
        self.main_window = main_window
        self.location_id = location_id
        self.location_name = location_name
        self.current_user_id = user_id
        
        # Create main scroll area for the entire form
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_scroll.setObjectName("scroll")
        
        # Main container widget
        main_container = QWidget()
        main_container.setObjectName("bookingWidget")
        layout = QVBoxLayout(main_container)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        title = QLabel(f"New Booking: {self.location_name}")
        title.setObjectName("bookingHeader")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Initialize time widgets first
        self.start_time = QTimeEdit()
        self.end_time = QTimeEdit()
        self.date_edit = QDateEdit()
        
        # Now setup time constraints
        self.setup_time_constraints()
        
        # Booking form widgets
        self.setup_booking_form(layout)
        
        # Set the main container as the scroll area's widget
        main_scroll.setWidget(main_container)
        
        # Set main scroll as the main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(main_scroll)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Store the selected room info
        self.selected_room_id = None
        self.selected_room_name = None
        self.selected_room_capacity = None
        
        # Store student input fields
        self.student_inputs = []
        
        # Apply styles
        self.apply_styles()
        
    def apply_styles(self):
        """Apply the CSS styles to all widgets"""
        self.setStyleSheet(get_booking_styles())
        
    def setup_time_constraints(self):
        """Set time constraints for booking"""
        # Set time limits (8 AM to 6 PM)
        self.start_time.setTimeRange(QTime(8, 0), QTime(18, 0))
        self.end_time.setTimeRange(QTime(8, 0), QTime(18, 0))
        
        # Set date limits (current date to 1 week ahead)
        today = QDate.currentDate()
        max_date = today.addDays(7)
        self.date_edit.setDateRange(today, max_date)
        
    def setup_booking_form(self, layout):
        """Setup the actual booking form components"""

        # ---------- Feature selection ----------
        feature_label = QLabel("Select Feature:")
        feature_label.setObjectName("formLabel")
        self.feature_combo = QComboBox()
        self.feature_combo.setObjectName("featureCombo")
        self.load_features()
        self.feature_combo.currentIndexChanged.connect(self.update_room_info)

        feature_group = QVBoxLayout()
        feature_group.setSpacing(0)
        feature_group.addWidget(feature_label)
        feature_group.addWidget(self.feature_combo)
        layout.addLayout(feature_group)

        # ---------- Number of students ----------
        students_label = QLabel("Number of Students (including yourself, max 10):")
        students_label.setObjectName("formLabel")
        self.students_spin = QSpinBox()
        self.students_spin.setObjectName("studentsSpin")
        self.students_spin.setMinimum(1)
        self.students_spin.setMaximum(10)
        self.students_spin.setValue(1)
        self.students_spin.valueChanged.connect(self.on_student_count_changed)

        students_group = QVBoxLayout()
        students_group.setSpacing(0)
        students_group.addWidget(students_label)
        students_group.addWidget(self.students_spin)
        layout.addLayout(students_group)

        # ---------- Date selection ----------
        date_label = QLabel("Booking Date:")
        date_label.setObjectName("formLabel")
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.dateChanged.connect(self.update_room_info)

        date_group = QVBoxLayout()
        date_group.setSpacing(0)
        date_group.addWidget(date_label)
        date_group.addWidget(self.date_edit)
        layout.addLayout(date_group)

        # ---------- Time selection ----------
        time_layout = QHBoxLayout()

        start_label = QLabel("Start Time:")
        start_label.setObjectName("formLabel")
        self.start_time.setDisplayFormat("HH:mm")
        self.start_time.setTime(QTime(8, 0))  # Default to 08:00
        self.start_time.timeChanged.connect(self.on_time_changed)

        end_label = QLabel("End Time:")
        end_label.setObjectName("formLabel")
        self.end_time.setDisplayFormat("HH:mm")
        self.end_time.setTime(QTime(10, 0))  # Default to 10:00
        self.end_time.timeChanged.connect(self.on_time_changed)

        time_layout.addWidget(start_label)
        time_layout.addWidget(self.start_time)
        time_layout.addWidget(end_label)
        time_layout.addWidget(self.end_time)
        layout.addLayout(time_layout)

        # ---------- Student information section ----------
        student_section_label = QLabel("Student Information:")
        student_section_label.setObjectName("formLabel")
        layout.addWidget(student_section_label)

        # Scroll area for student inputs
        self.student_scroll = QScrollArea()
        self.student_scroll.setWidgetResizable(True)
        self.student_scroll.setMinimumHeight(150)
        self.student_scroll.setMaximumHeight(300)
        self.student_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.student_scroll.setObjectName("studentScroll")

        self.student_container = QWidget()
        self.student_layout = QVBoxLayout(self.student_container)
        self.student_layout.setSpacing(10)
        self.student_layout.setContentsMargins(5, 5, 5, 5)

        self.student_scroll.setWidget(self.student_container)
        layout.addWidget(self.student_scroll)

        # Initialize student inputs
        self.update_student_inputs(1)

        # ---------- Terms checkbox ----------
        self.terms_checkbox = QCheckBox("I have read and agree to the booking guidelines")
        self.terms_checkbox.setObjectName("termsCheckbox")
        layout.addWidget(self.terms_checkbox)

        # ---------- Submit button ----------
        submit_btn = QPushButton("Submit Booking")
        submit_btn.setObjectName("submitButton")
        submit_btn.clicked.connect(self.submit_booking)
        layout.addWidget(submit_btn, 0, Qt.AlignCenter)


    def on_time_changed(self):
        """Handle time changes and enforce specific time intervals"""
        # Round start time to nearest hour or half-hour
        start_time = self.start_time.time()
        minutes = start_time.minute()
        
        if minutes < 15:
            rounded_minutes = 0
        elif minutes < 45:
            rounded_minutes = 30
        else:
            rounded_minutes = 0
            start_time = start_time.addSecs(3600)  # Add 1 hour
        
        rounded_start = QTime(start_time.hour(), rounded_minutes)
        self.start_time.setTime(rounded_start)
        
        # Round end time to nearest hour or half-hour
        end_time = self.end_time.time()
        minutes = end_time.minute()
        
        if minutes < 15:
            rounded_minutes = 0
        elif minutes < 45:
            rounded_minutes = 30
        else:
            rounded_minutes = 0
            end_time = end_time.addSecs(3600)  # Add 1 hour
        
        rounded_end = QTime(end_time.hour(), rounded_minutes)
        self.end_time.setTime(rounded_end)
        
        # Ensure end time is after start time
        if rounded_start >= rounded_end:
            self.end_time.setTime(rounded_start.addSecs(3600))  # Set to 1 hour after start
        
        self.update_room_info()

    def on_student_count_changed(self, count):
        """Handle changes in student count"""
        self.update_student_inputs(count)
        self.update_room_info()
    
    def update_student_inputs(self, count):
        """Update the student input fields based on the count"""
        # Clear existing inputs
        for i in reversed(range(self.student_layout.count())): 
            widget = self.student_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.student_inputs = []
        
        # Add input for the booking user (read-only)
        user_frame = QFrame()
        user_frame.setObjectName("userFrame")
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(10, 5, 10, 5)
        
        user_id_label = QLabel("Your Student ID:")
        user_id_label.setObjectName("formLabel")
        user_id_value = QLabel(self.current_user_id)
        user_id_value.setObjectName("readOnlyField")
        
        user_name_label = QLabel("Your Name:")
        user_name_label.setObjectName("formLabel")
        user_name = get_student_name(self.current_user_id)
        user_name_value = QLabel(user_name if user_name else "Unknown")
        user_name_value.setObjectName("readOnlyField")
        
        user_layout.addWidget(user_id_label)
        user_layout.addWidget(user_id_value)
        user_layout.addWidget(user_name_label)
        user_layout.addWidget(user_name_value)
        user_layout.addStretch()
        
        self.student_layout.addWidget(user_frame)
        
        # Add inputs for additional students
        for i in range(1, count):
            student_frame = QFrame()
            student_frame.setObjectName("studentFrame")
            student_layout = QHBoxLayout(student_frame)
            student_layout.setContentsMargins(10, 5, 10, 5)
            
            # Student ID input
            id_label = QLabel(f"Student {i+1} ID:")
            id_label.setObjectName("formLabel")
            id_input = QLineEdit()
            id_input.setPlaceholderText("Enter student ID")
            id_input.textChanged.connect(self.on_student_id_changed)
            
            # Student Name (will be auto-filled or manually entered)
            name_label = QLabel(f"Student {i+1} Name:")
            name_label.setObjectName("formLabel")
            name_input = QLineEdit()
            name_input.setPlaceholderText("Name will auto-fill from ID")
            name_input.setReadOnly(True)
            
            student_layout.addWidget(id_label)
            student_layout.addWidget(id_input)
            student_layout.addWidget(name_label)
            student_layout.addWidget(name_input)
            student_layout.addStretch()
            
            self.student_layout.addWidget(student_frame)
            self.student_inputs.append((id_input, name_input))
        
        # Add stretch to push content to the top
        self.student_layout.addStretch()
    
    def on_student_id_changed(self, text):
        """Auto-fill student name when ID is entered"""
        sender = self.sender()
        if text.strip() and len(text.strip()) >= 3:  # Only search if ID has reasonable length
            # Find the corresponding name input
            for id_input, name_input in self.student_inputs:
                if id_input == sender:
                    student_name = get_student_name(text.strip())
                    if student_name:
                        name_input.setText(student_name)
                    else:
                        name_input.clear()
                    break
    
    def load_features(self):
        """Load available features from database"""
        self.feature_combo.clear()
        try:
            features = get_features()
            for feature_id, feature_name in features:
                self.feature_combo.addItem(feature_name, feature_id)
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Could not load features: {str(e)}")

    def update_room_info(self):
        """Find the best available room based on selection (internal use only)"""
        feature_id = self.feature_combo.currentData()
        num_students = self.students_spin.value()
        
        if not feature_id:
            self.selected_room_id = None
            return
            
        try:
            date = self.date_edit.date().toString("yyyy-MM-dd")
            start_str = self.start_time.time().toString("HH:mm")
            end_str = self.end_time.time().toString("HH:mm")
            
            # Find the best available room
            room = find_best_available_room(
                self.location_id, feature_id, num_students, date, start_str, end_str
            )
            
            if room:
                room_id, room_name, capacity = room
                
                # Double-check if the room is actually available
                from database.db_manager import check_room_availability
                is_available = check_room_availability(room_id, date, start_str, end_str)
                
                if is_available:
                    self.selected_room_id = room_id
                    self.selected_room_name = room_name
                    self.selected_room_capacity = capacity
                else:
                    self.selected_room_id = None
            else:
                self.selected_room_id = None
                
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Could not find available room: {str(e)}")
            self.selected_room_id = None

    def validate_students(self):
        """Validate that all student IDs exist in the database and are filled"""
        invalid_students = []
        missing_names = []
        empty_fields = []
        
        # Check additional students
        for i, (id_input, name_input) in enumerate(self.student_inputs):
            student_id = id_input.text().strip()
            
            # Check if field is empty
            if not student_id:
                empty_fields.append(f"Student {i+2} ID")
                continue
                
            # Validate student ID exists
            if not check_student_exists(student_id):
                invalid_students.append(student_id)
            elif not name_input.text().strip():
                missing_names.append(student_id)
        
        return invalid_students, missing_names, empty_fields

    def validate_booking(self):
        """Validate booking details before submission"""
        # Check terms and conditions
        if not self.terms_checkbox.isChecked():
            QMessageBox.warning(self, "Agreement Required", 
                            "Please agree to the booking guidelines before submitting.")
            return False
        
        # Check time constraints (8 AM to 6 PM)
        start = self.start_time.time()
        end = self.end_time.time()
        
        if start < QTime(8, 0) or end > QTime(18, 0):
            QMessageBox.warning(self, "Invalid Time", 
                            "Bookings are only available from 8:00 AM to 6:00 PM.")
            return False
        
        # Check if times are on the hour or half-hour
        if start.minute() not in [0, 30] or end.minute() not in [0, 30]:
            QMessageBox.warning(self, "Invalid Time", 
                            "Bookings must start and end on the hour or half-hour (e.g., 08:00, 08:30).")
            return False
        
        # Check duration is at most 2 hours
        duration = QTime(0, 0).secsTo(end) - QTime(0, 0).secsTo(start)
        if duration > 7200:
            QMessageBox.warning(self, "Invalid Duration", 
                            "Booking duration cannot exceed 2 hours.")
            return False
        
        # Check if end time is after start time
        if start >= end:
            QMessageBox.warning(self, "Invalid Time", 
                            "End time must be after start time.")
            return False
        
        # Check date constraint (within 1 week)
        selected_date = self.date_edit.date()
        max_date = QDate.currentDate().addDays(7)
        if selected_date > max_date:
            QMessageBox.warning(self, "Invalid Date", 
                            "Bookings can only be made up to 1 week in advance.")
            return False
        
        # Check if a room was found
        if not self.selected_room_id:
            QMessageBox.warning(self, "No Room Available", 
                            "No available room found for the selected criteria.")
            return False
        
        # Check if room is already booked for the selected time
        date = self.date_edit.date().toString("yyyy-MM-dd")
        start_str = self.start_time.time().toString("HH:mm")
        end_str = self.end_time.time().toString("HH:mm")
        
        from database.db_manager import check_room_availability
        is_available = check_room_availability(self.selected_room_id, date, start_str, end_str)
        
        if not is_available:
            QMessageBox.warning(self, "Room Already Booked", 
                            f"Room {self.selected_room_name} is already booked for the selected time slot.")
            return False
        
        # Validate student IDs
        invalid_students, missing_names, empty_fields = self.validate_students()
        
        if empty_fields:
            QMessageBox.warning(self, "Missing Information", 
                            f"Please fill out all student ID fields: {', '.join(empty_fields)}")
            return False
            
        if invalid_students:
            QMessageBox.warning(self, "Invalid Student IDs", 
                            f"The following student IDs are invalid: {', '.join(invalid_students)}")
            return False
        
        if missing_names:
            QMessageBox.warning(self, "Missing Student Names", 
                            f"Could not find names for the following IDs: {', '.join(missing_names)}")
            return False
        
        # Check if number of students exceeds room capacity
        total_students = self.students_spin.value()
        if total_students > self.selected_room_capacity:
            QMessageBox.warning(self, "Capacity Exceeded", 
                            f"Number of students ({total_students}) exceeds room capacity ({self.selected_room_capacity}).")
            return False
        
        return True
    
    def get_student_data(self):
        """Get all student IDs including the booking user"""
        student_ids = [self.current_user_id]  # Always include the booking user
        
        # Add additional students
        for id_input, _ in self.student_inputs:
            student_id = id_input.text().strip()
            if student_id and student_id not in student_ids:
                student_ids.append(student_id)
        
        return student_ids

    def submit_booking(self):
        """Handle booking submission using db_manager"""
        if not self.validate_booking():
            return
            
        date = self.date_edit.date().toString("yyyy-MM-dd")
        start = self.start_time.time().toString("HH:mm")
        end = self.end_time.time().toString("HH:mm")
        student_ids = self.get_student_data()
        
        try:
            # Ensure status is set to 'booked' to avoid database constraint error
            booking_id = create_booking_with_students(
                self.current_user_id, self.selected_room_id, date, start, end, student_ids
            )
            QMessageBox.information(self, "Success", 
                                f"Room {self.selected_room_name} booked successfully for {len(student_ids)} students!")
            # Reset form
            self.students_spin.setValue(1)
            # Now this will call show_feature_grid on RoomBookingWidget
            self.main_window.show_feature_grid()
        except sqlite3.Error as e:
            error_msg = str(e)
            if "CHECK constraint failed: status IN ('booked', 'cancelled')" in error_msg:
                QMessageBox.critical(self, "Database Error", 
                                 "There was a database constraint error. Please contact support.")
            else:
                QMessageBox.critical(self, "Error", f"Database error: {error_msg}")