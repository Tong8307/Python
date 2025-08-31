from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                            QPushButton, QFrame, QScrollArea, QComboBox,
                            QDateEdit, QGridLayout, QSizePolicy, QSpinBox,
                            QHeaderView, QTableWidget, QTableWidgetItem, QAbstractScrollArea)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QBrush
from database.db_manager import get_rooms_by_location, get_bookings_for_timetable

class TimetablePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.location_id = main_window.location_id
        self.location_name = main_window.location_name
        self.user_capacity = 1  # Default capacity
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel(f"Timetable: {self.location_name}")
        title.setObjectName("bookingHeader")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        # Date selection
        date_layout = QVBoxLayout()
        date_label = QLabel("Select Date:")
        date_label.setObjectName("formLabel")
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDateRange(QDate.currentDate(), QDate.currentDate().addDays(6))
        self.date_edit.dateChanged.connect(self.show_timetable)
        self.date_edit.setObjectName("dateEdit")
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        
        # Capacity selection
        capacity_layout = QVBoxLayout()
        capacity_label = QLabel("Number of Students:")
        capacity_label.setObjectName("formLabel")
        
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setMinimum(1)
        self.capacity_spin.setMaximum(10)
        self.capacity_spin.setValue(1)
        self.capacity_spin.valueChanged.connect(self.on_capacity_changed)
        self.capacity_spin.setObjectName("capacitySpin")
        
        capacity_layout.addWidget(capacity_label)
        capacity_layout.addWidget(self.capacity_spin)
        
        filter_layout.addLayout(date_layout)
        filter_layout.addLayout(capacity_layout)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_label = QLabel("Legend:")
        legend_label.setStyleSheet("font-weight: bold; color: #2b2f36;")
        legend_layout.addWidget(legend_label)
        legend_layout.setSpacing(15)
        
        # Available legend
        available_legend = QFrame()
        available_legend.setFixedSize(20, 20)
        available_legend.setStyleSheet("background: #28a745; border: 2px solid #218838; border-radius: 4px;")
        legend_layout.addWidget(available_legend)
        available_text = QLabel("Available (Meets capacity)")
        available_text.setStyleSheet("color: #2b2f36;")
        legend_layout.addWidget(available_text)
        
        # Limited legend
        limited_legend = QFrame()
        limited_legend.setFixedSize(20, 20)
        limited_legend.setStyleSheet("background: #ffc107; border: 2px solid #e0a800; border-radius: 4px;")
        legend_layout.addWidget(limited_legend)
        limited_text = QLabel("Limited (Smaller capacity)")
        limited_text.setStyleSheet("color: #2b2f36;")
        legend_layout.addWidget(limited_text)
        
        # Booked legend
        booked_legend = QFrame()
        booked_legend.setFixedSize(20, 20)
        booked_legend.setStyleSheet("background: #dc3545; border: 2px solid #c82333; border-radius: 4px;")
        legend_layout.addWidget(booked_legend)
        booked_text = QLabel("Booked")
        booked_text.setStyleSheet("color: #2b2f36;")
        legend_layout.addWidget(booked_text)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        # Info text
        info_label = QLabel("Rooms are filtered based on your selected capacity. Hover over cells for details.")
        info_label.setStyleSheet("color: #6c757d; font-style: italic; margin: 5px 0;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Main container for the timetable with fixed headers
        main_timetable_container = QWidget()
        main_layout = QVBoxLayout(main_timetable_container)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Fixed room headers (top row)
        self.room_headers_widget = QWidget()
        self.room_headers_layout = QHBoxLayout(self.room_headers_widget)
        self.room_headers_layout.setSpacing(0)
        self.room_headers_layout.setContentsMargins(0, 0, 0, 0)
        self.room_headers_layout.addSpacing(80)  # Space for time column
        
        # Scroll area for the main content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll")
        
        # Content widget that will scroll
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Grid for the actual timetable content
        self.timetable_grid = QGridLayout()
        self.timetable_grid.setSpacing(0)
        
        self.content_layout.addLayout(self.timetable_grid)
        self.scroll_area.setWidget(self.content_widget)
        
        # Connect scroll bars to synchronize headers
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self.sync_room_headers)
        
        main_layout.addWidget(self.room_headers_widget)
        main_layout.addWidget(self.scroll_area)
        
        layout.addWidget(main_timetable_container)
        
        # Load timetable initially
        self.show_timetable()
    
    def sync_room_headers(self, value):
        """Sync room headers with horizontal scrolling"""
        self.room_headers_widget.move(-value, self.room_headers_widget.y())
    
    def on_capacity_changed(self, capacity):
        """Handle capacity change"""
        self.user_capacity = capacity
        self.show_timetable()
        
    def show_timetable(self):
        """Display the timetable for selected date and capacity"""
        # Clear existing content
        for i in reversed(range(self.room_headers_layout.count())):
            if i > 0:  # Keep the spacer
                widget = self.room_headers_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
        
        for i in reversed(range(self.timetable_grid.count())):
            widget = self.timetable_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        selected_date = self.date_edit.date().toString("yyyy-MM-dd")
        
        # Get all rooms for this location
        rooms = get_rooms_by_location(self.location_id)
        
        if not rooms:
            no_rooms_label = QLabel("No rooms available for this location.")
            no_rooms_label.setAlignment(Qt.AlignCenter)
            no_rooms_label.setStyleSheet("font-size: 16px; color: #666; padding: 50px;")
            self.timetable_grid.addWidget(no_rooms_label, 0, 0)
            return
        
        # Filter rooms based on capacity
        filtered_rooms = []
        for room_id, room_name, capacity in rooms:
            if capacity >= self.user_capacity:
                filtered_rooms.append((room_id, room_name, capacity))
        
        if not filtered_rooms:
            no_suitable_label = QLabel(f"No rooms available with capacity for {self.user_capacity} students.")
            no_suitable_label.setAlignment(Qt.AlignCenter)
            no_suitable_label.setStyleSheet("font-size: 16px; color: #dc3545; padding: 50px; font-weight: bold;")
            self.timetable_grid.addWidget(no_suitable_label, 0, 0)
            return
        
        # Time slots (8:00 to 18:00 in 30-minute intervals)
        time_slots = []
        for hour in range(8, 19):
            for minute in [0, 30]:
                if hour == 18 and minute == 30:
                    continue
                time_slots.append(f"{hour:02d}:{minute:02d}")
        
        # Create room headers
        for col, (room_id, room_name, capacity) in enumerate(filtered_rooms):
            room_header = QLabel(f"{room_name}\nCap: {capacity}")
            room_header.setAlignment(Qt.AlignCenter)
            room_header.setFixedSize(120, 60)
            room_header.setStyleSheet("""
                font-weight: bold; 
                background: #f0f4ff; 
                color: #1565c0;
                border: 1px solid #d0d8ff;
                padding: 5px;
            """)
            room_header.setToolTip(f"Room: {room_name}\nCapacity: {capacity} students")
            self.room_headers_layout.addWidget(room_header)
        
        # Create time column (fixed)
        for row, time_slot in enumerate(time_slots):
            time_label = QLabel(time_slot)
            time_label.setAlignment(Qt.AlignCenter)
            time_label.setFixedSize(80, 40)
            time_label.setStyleSheet("""
                font-weight: bold; 
                background: #f8f9fa; 
                color: #495057;
                border: 1px solid #e9ecef;
                padding: 5px;
            """)
            self.timetable_grid.addWidget(time_label, row, 0)
        
        # Create booking cells
        for row, time_slot in enumerate(time_slots):
            for col, (room_id, room_name, capacity) in enumerate(filtered_rooms):
                # Get bookings for this room
                bookings = get_bookings_for_timetable(room_id, selected_date)
                
                # Check if this time slot is booked
                is_booked = False
                for booking in bookings:
                    start_time, end_time, status, created_by = booking
                    if status == 'booked' and self.is_time_in_slot(time_slot, start_time, end_time):
                        is_booked = True
                        break
                
                # Create cell
                cell = QFrame()
                cell.setFixedSize(120, 40)
                
                if is_booked:
                    cell.setStyleSheet("""
                        background: #dc3545;
                        border: 1px solid #c82333;
                    """)
                    cell.setToolTip("This time slot is already booked")
                else:
                    if capacity >= self.user_capacity:
                        cell.setStyleSheet("""
                            background: #28a745;
                            border: 1px solid #218838;
                        """)
                        cell.setToolTip(f"Available - Capacity: {capacity} students (Meets your requirement)")
                    else:
                        cell.setStyleSheet("""
                            background: #ffc107;
                            border: 1px solid #e0a800;
                        """)
                        cell.setToolTip(f"Limited - Capacity: {capacity} students (Smaller than your requirement)")
                
                self.timetable_grid.addWidget(cell, row, col + 1)
    
    def is_time_in_slot(self, time_slot, start_time, end_time):
        """Check if a time slot falls within a booking period"""
        def time_to_minutes(time_str):
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        
        slot_minutes = time_to_minutes(time_slot)
        start_minutes = time_to_minutes(start_time)
        end_minutes = time_to_minutes(end_time)
        
        return start_minutes <= slot_minutes < end_minutes
    
    def showEvent(self, event):
        """Reload timetable when the page is shown"""
        super().showEvent(event)
        self.show_timetable()