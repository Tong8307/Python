from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox, QHBoxLayout,
    QDateEdit, QTableWidget, QTableWidgetItem, QAbstractItemView, 
    QAbstractScrollArea, QGridLayout, QToolTip, QComboBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from database.db_manager import get_rooms_by_location, get_bookings_for_timetable, get_features
from styles.timetable_styles import get_timetable_styles

class TimetablePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.location_id = main_window.location_id
        self.location_name = main_window.location_name
        self.user_capacity = 1
        self.selected_feature = "all"  # Default to show all features

        # Setup UI
        self.timetable()
        self.setStyleSheet(get_timetable_styles())
        QToolTip.setFont(self.font())

    def timetable(self):
        layout = QVBoxLayout(self)

        # Header
        title = QLabel(f"Timetable: {self.location_name}")
        title.setObjectName("bookingHeader")
        title.setAlignment(Qt.AlignLeft)
        layout.addWidget(title)

        # Feature filter on first line
        feature_layout = QHBoxLayout()
        lbl_feature = QLabel("Feature:")
        lbl_feature.setObjectName("formLabel")
        self.feature_combo = QComboBox()
        self.feature_combo.setObjectName("featureCombo")
        self.feature_combo.setMinimumWidth(450)  # Wide enough for full feature names
        
        # Add "All Features" option
        self.feature_combo.addItem("All Features", "all")
        
        # Add features from database with full names
        features = get_features()
        for feature_id, feature_name in features:
            self.feature_combo.addItem(feature_name, feature_id)
        
        self.feature_combo.currentIndexChanged.connect(self.on_feature_changed)

        feature_layout.addWidget(lbl_feature)
        feature_layout.addWidget(self.feature_combo)
        feature_layout.addStretch()
        layout.addLayout(feature_layout)

        # Date and Capacity filters on second line
        filter_layout = QHBoxLayout()
        
        # Date filter
        lbl_date = QLabel("Date:")
        lbl_date.setObjectName("formLabel")
        self.date_edit = QDateEdit()
        self.date_edit.setObjectName("dateEdit")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDateRange(QDate.currentDate(), QDate.currentDate().addDays(6))
        self.date_edit.dateChanged.connect(self.show_timetable)

        # Capacity filter
        lbl_cap = QLabel("Capacity:")
        lbl_cap.setObjectName("formLabel")
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setObjectName("capacitySpin")
        self.capacity_spin.setMinimum(1)
        self.capacity_spin.setMaximum(10) 
        self.capacity_spin.setValue(1)
        self.capacity_spin.valueChanged.connect(self.on_capacity_changed)

        # Add filters to layout with proper spacing
        filter_layout.addWidget(lbl_date)
        filter_layout.addWidget(self.date_edit)
        filter_layout.addSpacing(20)  # Add spacing between filters
        
        filter_layout.addWidget(lbl_cap)
        filter_layout.addWidget(self.capacity_spin)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Legend
        legend = QLabel("🟩 Available   🟥 Booked")
        legend.setAlignment(Qt.AlignCenter)
        legend.setObjectName("legendItem")
        layout.addWidget(legend)

        # Grid layout for frozen headers
        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)

        # Top header (time)
        self.top_header = QTableWidget()
        self.top_header.verticalHeader().hide()
        self.top_header.horizontalHeader().hide()
        self.top_header.setFixedHeight(40)
        self.top_header.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.top_header.setShowGrid(False)
        self.top_header.setFrameShape(QTableWidget.NoFrame)

        # Left header (rooms) - Make it wider to accommodate feature names
        self.left_header = QTableWidget()
        self.left_header.verticalHeader().hide()
        self.left_header.horizontalHeader().hide()
        self.left_header.setFixedWidth(150)  # Width for room names only
        self.left_header.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.left_header.setShowGrid(False)
        self.left_header.setFrameShape(QTableWidget.NoFrame)

        # Main table (internal cells with borders)
        self.table = QTableWidget()
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().hide()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFrameShape(QTableWidget.NoFrame)

        # Add to layout
        self.grid_layout.addWidget(self.top_header, 0, 1)
        self.grid_layout.addWidget(self.left_header, 1, 0)
        self.grid_layout.addWidget(self.table, 1, 1)

        # Sync scrollbars
        self.table.verticalScrollBar().valueChanged.connect(
            self.left_header.verticalScrollBar().setValue
        )
        self.table.horizontalScrollBar().valueChanged.connect(
            self.top_header.horizontalScrollBar().setValue
        )

        # Load timetable
        self.show_timetable()

    def on_capacity_changed(self, cap):
        self.user_capacity = cap
        self.show_timetable()
        
    def on_feature_changed(self, index):
        self.selected_feature = self.feature_combo.currentData()
        self.show_timetable()

    def show_timetable(self):
        selected_date = self.date_edit.date().toString("yyyy-MM-dd")
        rooms = get_rooms_by_location(self.location_id)
        
        # Filter rooms by capacity and feature
        filtered_rooms = []
        for room_data in rooms:
            # Handle both old (3 values) and new (5 values) format
            if len(room_data) == 3:
                room_id, room_name, capacity = room_data
                feature_id, feature_name = "unknown", "Unknown Feature"
            elif len(room_data) >= 5:
                room_id, room_name, capacity, feature_id, feature_name = room_data[:5]
            else:
                continue  # Skip invalid data
                
            # Check capacity
            if capacity < self.user_capacity:
                continue
                
            # Check feature filter
            if self.selected_feature != "all" and feature_id != self.selected_feature:
                continue
                
            filtered_rooms.append((room_id, room_name, capacity, feature_id, feature_name))

        # Clear previous content
        self.table.setRowCount(0)
        self.left_header.setRowCount(0)
        self.top_header.setColumnCount(0)

        if not filtered_rooms:
            # Show "No rooms available" message with styling
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            item = QTableWidgetItem("No rooms available with the selected filters")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            item.setBackground(QColor("#f8f9fa"))  # Light gray background
            item.setForeground(QColor("#6c757d"))  # Muted text color
            self.table.setItem(0, 0, item)
            
            # Set column width to span the entire table
            self.table.setColumnWidth(0, 800)
            self.table.setRowHeight(0, 60)  # Make the message row taller
            
            return

        # Time slots
        time_slots = [
            f"{h:02d}:{m:02d}" for h in range(8, 19) for m in (0, 30) if not (h == 18 and m == 30)
        ]
        rows, cols = len(filtered_rooms), len(time_slots)

        # Configure tables
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.left_header.setRowCount(rows)
        self.left_header.setColumnCount(1)
        self.top_header.setRowCount(1)
        self.top_header.setColumnCount(cols)

        # Fill top header
        for col, ts in enumerate(time_slots):
            item = QTableWidgetItem(ts)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            self.top_header.setItem(0, col, item)
            self.top_header.item(0, col).setBackground(QColor("#DBDEF5"))
            self.top_header.item(0, col).setForeground(QColor("#000000"))

        # Fill left header with room names only
        for row, (room_id, room_name, capacity, feature_id, feature_name) in enumerate(filtered_rooms):
            item = QTableWidgetItem(room_name)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            self.left_header.setItem(row, 0, item)
            self.left_header.item(row, 0).setBackground(QColor("#DBDEF5"))
            self.left_header.item(row, 0).setForeground(QColor("#000000"))

        # Fill main grid
        for row, (room_id, room_name, capacity, feature_id, feature_name) in enumerate(filtered_rooms):
            bookings = get_bookings_for_timetable(room_id, selected_date)
            for col, ts in enumerate(time_slots):
                booked = any(
                    status == "booked" and self.is_time_in_slot(ts, start, end)
                    for start, end, status, _ in bookings
                )
                item = QTableWidgetItem("")  # no text
                item.setFlags(Qt.ItemIsEnabled)
                if booked:
                    item.setBackground(QColor("#dc3545"))  # Red for booked
                    item.setData(Qt.UserRole, "booked")
                else:
                    item.setBackground(QColor("#28a745"))  # Green for available
                    item.setData(Qt.UserRole, "available")
                
                # Enhanced tooltip with feature information
                tooltip_text = (
                    f"Room: {room_name}\n"
                    f"Capacity: {capacity}\n"
                    f"Feature: {feature_name}\n"
                    f"Status: {item.data(Qt.UserRole).capitalize()}"
                )
                item.setToolTip(tooltip_text)
                self.table.setItem(row, col, item)

        # Column/row sizes
        self.left_header.setColumnWidth(0, 150)  # Width for room names only
        for col in range(cols):
            self.top_header.setColumnWidth(col, 80)
            self.table.setColumnWidth(col, 80)
        for row in range(rows):
            self.left_header.setRowHeight(row, 40)
            self.table.setRowHeight(row, 40)

    def is_time_in_slot(self, slot, start, end):
        def to_min(t):
            h, m = map(int, t.split(":"))
            return h * 60 + m
        return to_min(start) <= to_min(slot) < to_min(end)

    def showEvent(self, e):
        super().showEvent(e)
        self.show_timetable()