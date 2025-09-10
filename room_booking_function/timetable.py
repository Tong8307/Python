from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox, QHBoxLayout,
    QDateEdit, QTableWidget, QTableWidgetItem, QAbstractItemView, QAbstractScrollArea, QGridLayout, QToolTip
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from database.db_manager import get_rooms_by_location, get_bookings_for_timetable
from styles.timetable_styles import get_timetable_styles

class TimetablePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.location_id = main_window.location_id
        self.location_name = main_window.location_name
        self.user_capacity = 1

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

        # Filters
        filter_layout = QHBoxLayout()
        lbl_date = QLabel("Select Date:")
        lbl_date.setObjectName("formLabel")
        self.date_edit = QDateEdit()
        self.date_edit.setObjectName("dateEdit")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDateRange(QDate.currentDate(), QDate.currentDate().addDays(6))
        self.date_edit.dateChanged.connect(self.show_timetable)

        lbl_cap = QLabel("Minimum Capacity:")
        lbl_cap.setObjectName("formLabel")
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setObjectName("capacitySpin")
        self.capacity_spin.setMinimum(1)
        self.capacity_spin.setMaximum(10)  # max 10
        self.capacity_spin.setValue(1)
        self.capacity_spin.valueChanged.connect(self.on_capacity_changed)

        filter_layout.addWidget(lbl_date)
        filter_layout.addWidget(self.date_edit)
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

        # Left header (rooms)
        self.left_header = QTableWidget()
        self.left_header.verticalHeader().hide()
        self.left_header.horizontalHeader().hide()
        self.left_header.setFixedWidth(160)
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

    def show_timetable(self):
        selected_date = self.date_edit.date().toString("yyyy-MM-dd")
        rooms = get_rooms_by_location(self.location_id)
        filtered_rooms = [(r, n, c) for (r, n, c) in rooms if c >= self.user_capacity]

        # Clear previous content
        self.table.setRowCount(0)
        self.left_header.setRowCount(0)
        self.top_header.setColumnCount(0)

        if not filtered_rooms:
            # Show "No rooms available" message
            self.table.setRowCount(1)
            self.table.setColumnCount(5)  # Use multiple columns for the message
            self.table.setSpan(0, 0, 1, 5)  # Make the message span all columns
            item = QTableWidgetItem("No rooms available with the selected capacity")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(0, 0, item)
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

        # Fill left header
        for row, (room_id, room_name, capacity) in enumerate(filtered_rooms):
            item = QTableWidgetItem(f"{room_name}")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled)
            self.left_header.setItem(row, 0, item)
            self.left_header.item(row, 0).setBackground(QColor("#DBDEF5"))
            self.left_header.item(row, 0).setForeground(QColor("#000000"))

        # Fill main grid
        for row, (room_id, room_name, capacity) in enumerate(filtered_rooms):
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
                # Tooltip on hover
                item.setToolTip(
                    f"Room: {room_name}\nCapacity: {capacity}\nStatus: {item.data(Qt.UserRole).capitalize()}"
                )
                self.table.setItem(row, col, item)

        # Column/row sizes
        self.left_header.setColumnWidth(0, 160)
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
